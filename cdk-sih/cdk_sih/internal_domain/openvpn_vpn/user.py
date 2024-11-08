from aws_cdk import Stack, aws_secretsmanager as secretsmanager

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.openvpn_vpn.base import CdkOpenvpnVpnBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkOpenvpnVpnUserStack(Stack):
    def __init__(
        self,
        base_stack: CdkOpenvpnVpnBaseStack,
        component: str,
        factory: CdkConstructsFactory,
        project_name: str,
        vpc_default: bool,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self, default=vpc_default)
        factory.set_attrs_project_name_comp(self, project_name, component)

        # Create a secret in AWS Secrets Manager for the OpenVPN User password
        vpn_user_props: list[str] = [factory.VPN_, factory.USER_]
        self.user_password_len: int = 32
        self.user_password_secret: secretsmanager.Secret = factory.secrets_manager_secret(
            self,
            vpn_user_props + [factory.PASSWORD_],
            "The OpenVPN VPN user password secret.",
            factory.get_path(
                [
                    self.stack_name,
                    factory.join_sep_under([i.upper() for i in vpn_user_props]),
                    self.user_password_len,
                ]
            ),
            encryption_key=factory.get_attr_kms_key_stack(base_stack),
            secret_string_template={
                factory.USERNAME_: factory.join_sep_score([factory.organisation_abbrev, factory.ANDROID_])
            },
            password_length=self.user_password_len,
        )
