from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.pypi.base import CdkPypiBaseStack
from cdk_sih.internal_domain.pypi.storage import CdkPypiStorageStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkPypiServerStack(Stack):
    def __init__(
        self,
        base_stack: CdkPypiBaseStack,
        component: str,
        factory: CdkConstructsFactory,
        project_name: str,
        storage_stack: CdkPypiStorageStack,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component, inc_cfn_output=True)

        factory.set_attrs_from_alt_stack(self, base_stack, factory.ALB_PORT_)
        factory.set_attrs_kms_key_stack(self, alt_stack=base_stack)

        self.price_class: cloudfront.PriceClass = factory.get_cloudfront_dist_price_class(self, default=True)
        self.schedule_window: dict[str, dict[str, int]] = factory.schedules.window_pypi

        comp_subdomain = getattr(base_stack, factory.COMP_SUBDOMAIN_)
        self.fqdn: str = factory.join_sep_dot([comp_subdomain, getattr(base_stack, factory.HOSTED_ZONE_NAME_)])

        project_name_comp_props: list[str] = factory.get_attr_project_name_comp_props(self)

        # Application Load Balancer (ALB) for PyPi Server
        alb: elasticloadbalancing.ApplicationLoadBalancer = factory.elasticloadbalancing_application_load_balancer(
            self,
            base_stack.alb_sg,
            load_balancer_name=factory.join_sep_score(project_name_comp_props + [factory.ALB_]),
        )

        # CloudFront Distribution
        cf_origin_path: str = factory.SEP_FW_
        cf_origin_custom_header: str = factory.X_CUSTOM_HEADER_
        cf_origin_custom_header_secret: secretsmanager.Secret = factory.secrets_manager_secret_cf_origin_custom_header(
            self, cf_origin_custom_header, desc_insert=base_stack.server_description
        )
        factory.cloudfront_distribution(
            self,
            alb,
            getattr(base_stack, factory.HOSTED_ZONE_),
            comp_subdomain,
            cf_origin_path,
            origin_custom_headers=[(cf_origin_custom_header, cf_origin_custom_header_secret)],
            cf_stack_outputs_inc_comp=False,
            desc_insert=base_stack.server_description,
        )

        factory.set_attrs_url(self, cf_origin_path)
        factory.cfn_output_url(self, desc_insert=base_stack.server_description)

        # Target group for PyPi Server ALB - to make resources containers discoverable by the ALB
        alb_target_group: elasticloadbalancing.ApplicationTargetGroup = (
            factory.elasticloadbalancing_application_target_group(
                self,
                elasticloadbalancing.TargetType.INSTANCE,
                target_group_name=factory.join_sep_score(project_name_comp_props + [factory.ALB_, factory.TG_]),
            )
        )

        # Add listener to ALB - only allow HTTPS connections
        factory.elasticloadbalancing_application_listener(
            self,
            alb,
            [
                factory.acm_certificate(
                    self,
                    [factory.ALB_, factory.LISTENER_],
                    self.fqdn,
                    getattr(base_stack, factory.HOSTED_ZONE_),
                )
            ],
            [alb_target_group],
            [(cf_origin_custom_header, cf_origin_custom_header_secret)],
        )

        # Create a parameter in AWS Systems Manager Parameter Store to store the PyPi server index URL
        index_url_props: list[str] = [factory.INDEX_, factory.URL_]
        index_url_param_val: str = getattr(self, factory.URL_).replace(
            factory.SEP_COLON_FW_FW_,
            factory.join_sep_empty(
                [
                    factory.SEP_COLON_FW_FW_,
                    base_stack.username,
                    f"{factory.SEP_COLON_}<{factory.PASSWORD_.upper()}>{factory.SEP_AT_SIGN_}",
                ]
            ),
            1,
        )
        index_url_param_val = factory.join_sep_empty([index_url_param_val, factory.SIMPLE_])
        factory.ssm_string_parameter(
            self,
            index_url_props,
            f"The {base_stack.server_description} (index URL) secret.",
            factory.get_path(
                [factory.join_sep_under([base_stack.secret_name] + [i.upper() for i in index_url_props])], lead=True
            ),
            index_url_param_val,
            data_type=ssm.ParameterDataType.TEXT,
            tier=ssm.ParameterTier.STANDARD,
        )

        factory.autoscaling_auto_scaling_group_default(
            self,
            base_stack.role,
            base_stack.ec2_sg,
            factory.lambda_function_sns_asg(self, security_groups=[base_stack.ec2_sg]),
            instance_type=factory.ec2_instance_type_t3_small(),
            associate_public_ip_address=False,
            vpc_subnets_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            application_target_groups=[alb_target_group],
        )

        for k, v in {base_stack: factory.BASE_}.items():
            factory.cfn_output_dependant_stack_name(self, k, v)

        factory.cfn_output_ec2_instance_vpc_name(self)
        factory.cfn_output_efs_file_system_id(self, storage_stack.efs_file_system, "PyPi server EC2 instance")
        factory.cfn_output_server_description(self, base_stack.server_description)
