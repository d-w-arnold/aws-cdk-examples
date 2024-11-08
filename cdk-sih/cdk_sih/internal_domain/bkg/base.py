from aws_cdk import (
    Stack,
    aws_ecr as ecr,
)

from cdk_sih.client_vpn.endpoint import CdkClientVpnEndpointStack
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkBkgBaseStack(Stack):
    def __init__(
        self,
        bastion_host_private_ips: list[str],
        client_vpn_endpoint_stack: CdkClientVpnEndpointStack,
        component: str,
        component_sub_ports: dict[str, tuple[int, bool]],
        elastic_ip_parameter_names: dict[str, str],
        factory: CdkConstructsFactory,
        project_name: str,
        project_name_comp_list: list[str],
        vpc_stack: CdkVpcSihStack,
        disable_24_7_: bool = False,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_client_vpn_endpoint_sg(self, client_vpn_endpoint_stack)
        factory.set_attrs_disable_24_7_(self, disable_24_7_)
        factory.set_attrs_elastic_ips_meta(self, elastic_ip_parameter_names)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_ports_default(self)

        self.bastion_host_private_ips: list[str] = bastion_host_private_ips

        self.comp_sub_ports: dict[str, int] = {}
        for comp_sub, (comp_sub_port, api_container) in component_sub_ports.items():
            if api_container:
                setattr(self, factory.ALB_PORT_, comp_sub_port)
            self.comp_sub_ports[comp_sub] = comp_sub_port
        self.mq_rabbitmq_port: int = (
            5671  # https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/rabbitmq-basic-elements-broker.html#broker-attributes
        )

        # ---------- Route 53 ----------

        factory.set_attrs_hosted_zone(self)

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
            mq_rabbitmq=(factory.get_attr_vpc_cidr(self), factory.get_attr_vpc_name(self)),
        )

        # ---------- SSM ----------

        # MS Teams CI-CD Channel Webhook URL
        factory.ssm_string_parameter_webhook_url(self)

        # Version meta
        factory.ssm_string_parameter_version_meta(self)

        # ---------- Secrets Manager ----------

        # ECS container API keys and passwords
        factory.secrets_manager_secret_ecs_container(self, "qqlbqS")

        # ECS container API_KEYS secret
        factory.secrets_manager_secret_ecs_container(self, "qtGbwV", attr_name=factory.ECS_CONTAINER_API_KEYS_SECRET_)

        # ECS container SERVICE_ACCESS secret
        factory.secrets_manager_secret_ecs_container(
            self, "XHoGpj", attr_name=factory.ECS_CONTAINER_SERVICE_ACCESS_SECRET_
        )

        # Secret key secret
        factory.secrets_manager_secret_secret_keys_secret(self, singleton=True)

        # Token key secret
        factory.secrets_manager_secret_api_keys_token(self, singleton=True)

        # ---------- SES ----------

        factory.ses_users(self, external=False)
