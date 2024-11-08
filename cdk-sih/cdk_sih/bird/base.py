from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_route53 as route53,
    aws_ssm as ssm,
)

from cdk_sih.client_vpn.endpoint import CdkClientVpnEndpointStack
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkBirdBaseStack(Stack):
    def __init__(
        self,
        bastion_host_private_ips: list[str],
        client_vpn_endpoint_stack: CdkClientVpnEndpointStack,
        component: str,
        deploy_env_preview_demo_meta: dict[str, str],
        elastic_ip_parameter_names: dict[str, str],
        factory: CdkConstructsFactory,
        project_name: str,
        project_name_comp_list: list[str],
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_client_vpn_endpoint_sg(self, client_vpn_endpoint_stack)
        factory.set_attrs_deploy_env_preview_demo_meta(self, deploy_env_preview_demo_meta)
        factory.set_attrs_elastic_ips_meta(self, elastic_ip_parameter_names)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_ports_default(self, alb_port=8000)

        self.bastion_host_private_ips: list[str] = bastion_host_private_ips

        # Celery Task Subscriptions List
        self.task_subscriptions: list[str] = ["gw_daily_tasks", "gw_regular_tasks"]

        # ---------- Route 53 ----------

        self.domain_name_com: str = factory.join_sep_empty([project_name, factory.DOT_COM_])
        self.hosted_zone_com: route53.HostedZone = factory.route53_hosted_zone_from_lookup(self, self.domain_name_com)

        self.domain_name_co_uk: str = factory.join_sep_empty([project_name, factory.DOT_CO_UK_])
        self.hosted_zone_co_uk: route53.HostedZone = factory.route53_hosted_zone_from_lookup(
            self, self.domain_name_co_uk
        )

        factory.set_attrs_hosted_zone(self, domain_name=self.domain_name_com)

        # ---------- ECR ----------

        self.repos: dict[str, ecr.Repository] = {p: factory.ecr_repository(self, p) for p in project_name_comp_list}

        # ---------- EC2 ----------

        factory.ec2_security_group_all(
            self,
            all_vpc_traffic=(
                [getattr(self, factory.ALB_PORT_)],
                factory.get_attr_vpc_cidr(self),
                factory.get_attr_vpc_name(self),
            ),
            ec_redis=True,
            db_server=True,
            s3_lambda=True,
        )

        # ---------- SSM ----------

        # MS Teams CI-CD Channel Webhook URL
        factory.ssm_string_parameter_webhook_url(self)

        # Version meta
        factory.ssm_string_parameter_version_meta(self)

        # Firebase account info
        self.firebase_account_info_param: ssm.IStringParameter = (
            factory.ssm_string_parameter_ecs_container_env_firebase_account_info(self)
        )

        # ---------- Secrets Manager ----------

        # ECS container API keys and passwords
        factory.secrets_manager_secret_ecs_container(self, "wxUi6m")

        # E-Commerce API key secrets
        factory.secrets_manager_secret_api_keys_e_commerce(self)

        # Secret key secrets
        factory.secrets_manager_secret_secret_keys_secret(self)

        # Token key secrets
        factory.secrets_manager_secret_api_keys_token(self)

        # ---------- SES ----------

        factory.ses_users(self)
