from aws_cdk import Stack, aws_secretsmanager as secretsmanager

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.ipsec_vpn.base import CdkIpsecVpnBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkIpsecVpnPskStack(Stack):
    def __init__(
        self,
        base_stack: CdkIpsecVpnBaseStack,
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

        # Create a secret in AWS Secrets Manager for the VPN IPsec Pre-Shared Key (PSK)
        self.psk_len: int = 64
        self.psk_secret: secretsmanager.Secret = factory.secrets_manager_secret(
            self,
            [factory.PSK_],
            "The VPN IPsec Pre-Shared Key (PSK) secret.",
            factory.get_path(
                [
                    self.stack_name,
                    factory.join_sep_under([i.upper() for i in [factory.VPN_, factory.IPSEC_, factory.PSK_]]),
                    self.psk_len,
                ]
            ),
            encryption_key=factory.get_attr_kms_key_stack(base_stack),
            password_length=self.psk_len,
        )
