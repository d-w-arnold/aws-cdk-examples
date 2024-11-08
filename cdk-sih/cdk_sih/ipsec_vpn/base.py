import os

from aws_cdk import Stack, aws_iam as iam, aws_logs as logs
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkIpsecVpnBaseStack(Stack):
    def __init__(
        self,
        component: str,
        factory: CdkConstructsFactory,
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_kms_key_stack(self)

        factory.load_dotenv_vpn(self)

        # IAM Role for IPsec VPN server EC2 instance
        server_stack_name: str = self.stack_name.replace(factory.BASE_.capitalize(), factory.SERVER_.capitalize(), 1)
        self.role: iam.Role = factory.iam_role_ec2(
            self,
            f"Role for EC2 instance {factory.join_sep_score(factory.get_attr_project_name_comp_props(self) + [factory.get_attr_vpc_name(self), factory.PUBLIC_])}",
            custom_policies=[
                factory.iam_policy_statement_cloudformation_stack_all(
                    self, resource_name=factory.get_path([server_stack_name, factory.SEP_ASTERISK_])
                ),
                factory.iam_policy_statement_ec2_user_data(),
                factory.iam_policy_statement_kms_key_encrypt_decrypt(
                    self, resources=[factory.get_attr_kms_key_stack(self).key_arn]
                ),
                factory.iam_policy_statement_secretsmanager_get_secret_value(
                    self,
                    resource_name=factory.get_path(
                        [
                            self.stack_name.replace(factory.BASE_.capitalize(), factory.PSK_.capitalize(), 1),
                            factory.SEP_ASTERISK_,
                        ]
                    ),
                ),
                factory.iam_policy_statement_ssm_put_parameter(
                    self, resource_name=factory.get_path([server_stack_name, factory.SEP_ASTERISK_])
                ),
            ],
        )

        # Copy environment variables to AWS Systems Manager Parameter Store
        #  and create secrets in AWS Secrets Manager as needed
        name_key: str = factory.NAME_
        desc_key: str = factory.DESC_
        vpn_user_key: str = "VPN_USER"
        vpn_users_add_key: str = "VPN_ADDL_USERS"
        for p in [
            {name_key: vpn_user_key, desc_key: "The VPN username"},
            {name_key: vpn_users_add_key, desc_key: "Additional VPN usernames"},
            {name_key: "VPN_CLIENT_NAME", desc_key: "The first VPN client, renamed from default 'vpnclient'"},
            {name_key: "VPN_DNS_SRV1", desc_key: "Alternative DNS servers #1"},
            {name_key: "VPN_DNS_SRV2", desc_key: "Alternative DNS servers #2"},
        ]:
            if os.getenv(p[name_key]):
                paths_props: list[str] = [self.stack_name, p[name_key]]
                factory.ssm_string_parameter(
                    self,
                    [p[name_key]],
                    p[desc_key],
                    factory.get_path(paths_props, lead=True),
                    os.environ[p[name_key]],
                ).grant_read(self.role)
                if p[name_key] == vpn_user_key:
                    username: str = os.getenv(p[name_key])
                    factory.secrets_manager_secret(
                        self,
                        [factory.VPN_, factory.USER_, factory.PASSWORD_],
                        f"The VPN user password secret for: {username}",
                        factory.get_path(paths_props + [username]),
                        secret_string_template={factory.USERNAME_: username},
                    ).grant_read(self.role)
                if p[name_key] == vpn_users_add_key:
                    for vpn_addl_user in os.getenv(p[name_key]).split(factory.SEP_SPACE_):
                        factory.secrets_manager_secret(
                            self,
                            [factory.VPN_, factory.ADDL_, factory.USER_, factory.PASSWORD_, vpn_addl_user],
                            f"The VPN additional user password secret for: {vpn_addl_user}",
                            factory.get_path(paths_props + [vpn_addl_user]),
                            secret_string_template={factory.USERNAME_: vpn_addl_user},
                        ).grant_read(self.role)

        # Logs log group for the IPsec VPN server
        self.log_group: logs.LogGroup = factory.logs_log_group(
            self,
            [factory.EC2_],
            factory.get_path(
                [factory.log_groups[factory.EC2_], factory.INSTANCE_, factory.get_attr_project_name_comp(self)]
            ),
        )
        self.log_group.grant_write(self.role)
