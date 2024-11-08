from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_autoscaling as autoscaling,
    aws_cloudfront as cloudfront,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.openvpn_vpn.base import CdkOpenvpnVpnBaseStack
from cdk_sih.internal_domain.openvpn_vpn.user import CdkOpenvpnVpnUserStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkOpenvpnVpnServerStack(Stack):
    def __init__(
        self,
        base_stack: CdkOpenvpnVpnBaseStack,
        component: str,
        elastic_ip: ec2.CfnEIP,
        factory: CdkConstructsFactory,
        project_name: str,
        user_stack: CdkOpenvpnVpnUserStack,
        vpc_default: bool,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self, default=vpc_default)
        factory.set_attrs_project_name_comp(self, project_name, component, inc_cfn_output=True)

        factory.set_attrs_from_alt_stack(self, base_stack, factory.ALB_PORT_)
        factory.set_attrs_kms_key_stack(self, alt_stack=base_stack)

        self.price_class: cloudfront.PriceClass = factory.get_cloudfront_dist_price_class(self, default=True)
        self.schedule_window: dict[str, dict[str, int]] = factory.schedules.window_vpn

        comp_subdomain = getattr(base_stack, factory.COMP_SUBDOMAIN_)
        self.fqdn: str = factory.join_sep_dot([comp_subdomain, getattr(base_stack, factory.HOSTED_ZONE_NAME_)])

        project_name_comp_props: list[str] = factory.get_attr_project_name_comp_props(self)

        # Application Load Balancer (ALB) for OpenVPN Server
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

        # Target group for OpenVPN Server ALB - to make resources containers discoverable by the ALB
        alb_target_group: elasticloadbalancing.ApplicationTargetGroup = (
            factory.elasticloadbalancing_application_target_group(
                self,
                elasticloadbalancing.TargetType.INSTANCE,
                target_group_name=factory.join_sep_score(project_name_comp_props + [factory.ALB_, factory.TG_]),
                target_group_protocol_https=True,
                health_check_protocol_https=True,
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

        # Network Load Balancer (NLB) for OpenVPN Server
        nlb: elasticloadbalancing.NetworkLoadBalancer = elasticloadbalancing.NetworkLoadBalancer(
            scope=self,
            id=factory.get_construct_id(self, [factory.NLB_], "NetworkLoadBalancer"),
            cross_zone_enabled=False,
            vpc=factory.get_attr_vpc(self),
            deletion_protection=True,
            internet_facing=True,
            load_balancer_name=factory.join_sep_score(project_name_comp_props + [factory.NLB_]),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        # Publish the OpenVPN Server NLB DNS name (for use in EC2 user data) as CloudFormation output.
        nlb_dns_name_cfn_output_id: str = factory.get_construct_id(
            self,
            [factory.NLB_, factory.DNS_, factory.NAME_],
            factory.CFN_OUTPUT_TYPE,
        )
        CfnOutput(
            scope=self,
            id=nlb_dns_name_cfn_output_id,
            description=f"The {base_stack.server_description} NLB DNS name (for use in EC2 user data) as CloudFormation output. "
            f"For example, openvpn-vpn-server-nlb-????????????????.elb.*.amazonaws.com",
            value=nlb.load_balancer_dns_name,
            export_name=nlb_dns_name_cfn_output_id,
        )

        nlb_target_groups: list[elasticloadbalancing.NetworkTargetGroup] = []
        tcp_protocol: elasticloadbalancing.Protocol = elasticloadbalancing.Protocol.TCP
        for p in [getattr(self, factory.ALB_PORT_), base_stack.nlb_port]:
            is_nlb: bool = bool(p == base_stack.nlb_port)
            protocol: elasticloadbalancing.Protocol = elasticloadbalancing.Protocol.UDP if is_nlb else tcp_protocol
            nlb_target_group: elasticloadbalancing.NetworkTargetGroup = elasticloadbalancing.NetworkTargetGroup(
                scope=self,
                id=factory.get_construct_id(self, [factory.NLB_, str(p), factory.TG_], "NetworkTargetGroup"),
                port=p,
                connection_termination=False,
                # preserve_client_ip=,
                # Default: False if the target group type is IP address and the
                #  target group protocol is TCP or TLS. Otherwise, True.
                protocol=protocol,
                proxy_protocol_v2=False,
                # targets=[],
                deregistration_delay=Duration.seconds(120),
                health_check=elasticloadbalancing.HealthCheck(
                    # enabled=,  # Default: - Determined automatically.
                    # healthy_grpc_codes="12",  # Health check matcher cannot be set for both 'HTTP' and 'GRPC' codes at the same time.
                    # healthy_http_codes=str(200),
                    healthy_threshold_count=2,  # Default: 3 for NLBs
                    interval=Duration.seconds(10),
                    # path=factory.SEP_FW_,
                    port=str(factory.SSH_PORT if is_nlb else p),  # Default: 'traffic-port'
                    protocol=tcp_protocol,
                    timeout=Duration.seconds(10),
                    unhealthy_threshold_count=2,
                ),
                target_group_name=factory.join_sep_score(project_name_comp_props + [factory.NLB_, str(p), factory.TG_]),
                target_type=elasticloadbalancing.TargetType.INSTANCE,
                vpc=factory.get_attr_vpc(self),
            )
            nlb.add_listener(
                id=factory.get_construct_id(self, [factory.NLB_, str(p)], "NetworkListener"),
                port=p,
                # alpn_policy=,  # Application-Layer Protocol Negotiation (ALPN) is a TLS extension. Default: - None
                # certificates=[certificate],
                # default_action=,  # Cannot be specified together with default_target_groups. Default: - None.
                # default_target_groups=,  # Cannot be specified together with default_action. Default: - None.
                protocol=protocol,
                # ssl_policy=elasticloadbalancing.SslPolicy.RECOMMENDED,
                # Default: - Current predefined security policy.
            ).add_action(
                _id=factory.get_construct_id(self, [factory.NLB_, str(p), factory.LISTENER_], "NetworkListenerAction"),
                action=elasticloadbalancing.NetworkListenerAction.forward(
                    target_groups=[nlb_target_group],
                    # stickiness_duration=,  # Target group stickiness cannot be configured on NLBs
                ),
            )
            nlb_target_groups.append(nlb_target_group)

        # IAM Role for OpenVPN Server EC2 instance
        role: iam.Role = factory.iam_role_ec2(
            self,
            f"Role for EC2 instance {factory.join_sep_score(factory.get_attr_project_name_comp_props(self) + [factory.get_attr_vpc_name(self), factory.PUBLIC_])}",
            custom_policies=[
                factory.iam_policy_statement_cloudformation_stack_all(
                    self, resource_name=factory.get_path([self.stack_name, factory.SEP_ASTERISK_])
                ),
                factory.iam_policy_statement_ec2_user_data(),
                factory.iam_policy_statement_kms_key_encrypt_decrypt(
                    self, resources=[factory.get_attr_kms_key_stack(self).key_arn]
                ),
                factory.iam_policy_statement_ssm_put_parameter(
                    self, resource_name=factory.get_path([self.stack_name, factory.SEP_ASTERISK_])
                ),
                factory.iam_policy_statement_secretsmanager_get_secret_value(
                    self, resource_name=factory.get_path([self.stack_name, factory.SEP_ASTERISK_])
                ),
            ]
            + [
                factory.iam_policy_statement_secretsmanager_get_secret_value(
                    self,
                    resource_name=factory.get_path(
                        [self.stack_name.replace(component.capitalize(), i.capitalize(), 1), factory.SEP_ASTERISK_]
                    ),
                )
                for i in [factory.BASE_, factory.USER_]
            ],
        )

        # Create a secret in AWS Secrets Manager for the OpenVPN Admin password
        admin_password_props: list[str] = [factory.ADMIN_, factory.PASSWORD_]
        admin_password_len: int = 64
        project_name_short: str = project_name.split(sep=factory.SEP_SCORE_, maxsplit=1)[0]
        admin_password_secret: secretsmanager.Secret = factory.secrets_manager_secret(
            self,
            admin_password_props,
            "The OpenVPN Admin password secret.",
            factory.get_path(
                [
                    self.stack_name,
                    factory.join_sep_under([i.upper() for i in admin_password_props]),
                    admin_password_len,
                ]
            ),
            encryption_key=factory.get_attr_kms_key_stack(base_stack),
            secret_string_template={
                factory.join_sep_under(v): k
                for k, v in {
                    project_name_short: [factory.ADMIN_, factory.USERNAME_],
                    f"{project_name_short}as": [factory.SSH_, factory.USERNAME_],
                }.items()
            },
            password_length=admin_password_len,
        )

        autoscaling_auto_scaling_group_: autoscaling.AutoScalingGroup = factory.autoscaling_auto_scaling_group_default(
            self,
            role,
            base_stack.ec2_sg,
            factory.lambda_function_sns_asg(self, use_vpc=False),
            instance_type=factory.ec2_instance_type_t3_micro(),
            machine_image=factory.ec2_machine_image_openvpn_server(),
            dependant_constructs=[user_stack.user_password_secret],
            application_target_groups=[alb_target_group],
            network_target_groups=nlb_target_groups,
            # TODO: (NEXT) Figure out how to make compatible with IMDSv2:
            #  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
            require_imdsv2=False,
        )
        autoscaling_auto_scaling_group_.node.add_dependency(admin_password_secret)

        self.public_ipv4_parameter_name: str = factory.get_path(
            [self.stack_name, factory.join_sep_score([factory.PUBLIC_, factory.IPV4_])], lead=True
        )

        for k, v in {base_stack: factory.BASE_, user_stack: factory.USER_}.items():
            factory.cfn_output_dependant_stack_name(self, k, v)

        factory.cfn_output_ec2_instance_eip_allocation_id(self, elastic_ip)
        factory.cfn_output_ec2_instance_public_ipv4_parameter_name(self, self.public_ipv4_parameter_name)
        factory.cfn_output_ec2_instance_vpc_name(self)
        factory.cfn_output_int_val(self, [factory.ADMIN_, factory.PASSWORD_, factory.LEN_], admin_password_len)
        factory.cfn_output_int_val(self, [factory.USER_, factory.PASSWORD_, factory.LEN_], user_stack.user_password_len)
