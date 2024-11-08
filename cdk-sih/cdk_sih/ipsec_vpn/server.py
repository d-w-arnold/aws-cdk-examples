import os

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from cdk_sih.client_vpn.endpoint import CdkClientVpnEndpointStack
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.ipsec_vpn.base import CdkIpsecVpnBaseStack
from cdk_sih.ipsec_vpn.psk import CdkIpsecVpnPskStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkIpsecVpnServerStack(Stack):
    def __init__(
        self,
        base_stack: CdkIpsecVpnBaseStack,
        client_vpn_endpoint_stack: CdkClientVpnEndpointStack,
        component: str,
        elastic_ip: ec2.CfnEIP,
        factory: CdkConstructsFactory,
        project_name: str,
        psk_stack: CdkIpsecVpnPskStack,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component, inc_cfn_output=True)

        factory.set_attrs_kms_key_stack(self, alt_stack=base_stack)

        self.schedule_window: dict[str, dict[str, int]] = factory.schedules.window_vpn

        factory.load_dotenv_vpn(self)

        ec2_sg: ec2.SecurityGroup = factory.ec2_security_group(
            self,
            [factory.EC2_],
            "Allow access to IPsec VPN server EC2 instance.",
            ingress_rules=[
                (ec2.Peer.any_ipv4(), ec2.Port.udp(port), desc)
                for port, desc in {
                    500: "For IKE, to manage encryption keys.",
                    4500: "For IPSEC NAT-Traversal mode.",
                }.items()
            ],
            full_description=True,
        )

        if os.environ.get("EC2_SSH_ALLOWED") and hasattr(
            client_vpn_endpoint_stack, factory.CLIENT_VPN_ENDPOINT_PRIVATE_SG_
        ):
            ec2_sg.connections.allow_from(
                other=getattr(client_vpn_endpoint_stack, factory.CLIENT_VPN_ENDPOINT_PRIVATE_SG_),
                port_range=ec2.Port.tcp(factory.SSH_PORT),
                description=factory.get_ec2_security_group_rule_description(
                    "Client VPN Endpoint PRIVATE", factory.SSH_PORT
                ),
            )

        factory.autoscaling_auto_scaling_group_default(
            self,
            base_stack.role,
            ec2_sg,
            factory.lambda_function_sns_asg(self, security_groups=[ec2_sg]),
            instance_type=factory.ec2_instance_type_t3_xlarge(),
            dependant_constructs=[psk_stack.psk_secret],
        )

        self.public_ipv4_parameter_name: str = factory.get_path(
            [self.stack_name, factory.join_sep_score([factory.PUBLIC_, factory.IPV4_])], lead=True
        )

        for k, v in {base_stack: factory.BASE_, psk_stack: factory.PSK_}.items():
            factory.cfn_output_dependant_stack_name(self, k, v)

        factory.cfn_output_ec2_instance_eip_allocation_id(self, elastic_ip)
        factory.cfn_output_ec2_instance_log_group_name(self, base_stack.log_group.log_group_name)
        factory.cfn_output_ec2_instance_public_ipv4_parameter_name(self, self.public_ipv4_parameter_name)
        factory.cfn_output_ec2_instance_vpc_name(self)
        factory.cfn_output_int_val(self, [factory.PSK_, factory.LEN_], psk_stack.psk_len)
