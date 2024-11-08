import os

from aws_cdk import Stack, aws_ec2 as ec2
from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkOpenvpnVpnBaseStack(Stack):
    def __init__(
        self,
        component: str,
        elastic_ip_parameter_names: dict[str, str],
        factory: CdkConstructsFactory,
        project_name: str,
        vpc: ec2.Vpc = None,  # Default: Uses the default VPC
        vpc_name: str = None,  # Default: Specifies the default VPC name
        **kwargs,
    ) -> None:
        if vpc_name is None:
            vpc_name = factory.DEFAULT_

        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc: ec2.IVpc = vpc if vpc else factory.ec2_vpc_default(self, vpc_name)
        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_elastic_ips_meta(self, elastic_ip_parameter_names, inc_cfn_output=False)
        factory.set_attrs_ports_default(self, alb_port=factory.HTTPS_PORT)
        factory.set_attrs_kms_key_stack(self)

        factory.load_dotenv_vpn(self)

        setattr(self, factory.VPC_, vpc)
        setattr(self, factory.VPC_NAME_, vpc_name)

        self.nlb_port: int = 1194
        self.server_description: str = (
            f"Foobar{f' {profile}' if (profile := factory.aws_profile) else factory.SEP_EMPTY_} OpenVPN Access Server"
        )

        trans_layer_protocol_port_mapping: dict[str, list[int]] = {
            factory.TCP_: [getattr(self, factory.ALB_PORT_), 943, 945],
            factory.UDP_: [self.nlb_port],
        }

        # ---------- Route 53 ----------

        factory.set_attrs_hosted_zone(
            self,
            comp_subdomain_custom=factory.get_attr_project_name_comp_props(self, project_name_comp=project_name)[0],
        )

        # ---------- OpenVPN Server - EC2 ----------

        self.alb_sg: ec2.SecurityGroup = factory.ec2_security_group(
            self,
            [factory.ALB_],
            factory.join_sep_space([self.server_description, factory.ALB_.upper()]),
        )
        self.ec2_sg: ec2.SecurityGroup = factory.ec2_security_group(self, [factory.EC2_], self.server_description)

        # Allowed TCP/UDP ports -> ALB
        for trans_layer_protocol, port_list in trans_layer_protocol_port_mapping.items():
            if trans_layer_protocol in {factory.TCP_, factory.UDP_}:
                for p in port_list:
                    self.alb_sg.add_ingress_rule(
                        peer=ec2.Peer.any_ipv4(),
                        connection=ec2.Port.tcp(p) if trans_layer_protocol == factory.TCP_ else ec2.Port.udp(p),
                        description=f"Allow {trans_layer_protocol.upper()} port {p} traffic.",
                    )

        # ALB -> (All TCP/UDP ports) -> OpenVPN Server EC2 instance
        self.ec2_sg.connections.allow_from(
            other=self.alb_sg,
            port_range=ec2.Port.all_tcp(),
            description=f"Allow {factory.ALB_.upper()} traffic on all TCP ports.",
        )
        self.ec2_sg.connections.allow_from(
            other=self.alb_sg,
            port_range=ec2.Port.all_udp(),
            description=f"Allow {factory.ALB_.upper()} traffic on all UDP ports.",
        )

        if os.environ.get("EC2_SSH_ALLOWED"):
            # [Elastic IPs] -> (SSH) -> EC2 instances
            for _, meta in getattr(self, factory.ELASTIC_IP_META_).items():
                self.ec2_sg.add_ingress_rule(
                    peer=ec2.Peer.ipv4(cidr_ip=factory.get_path([meta[0], str(32)])),
                    connection=ec2.Port.tcp(factory.SSH_PORT),
                    description=factory.get_ec2_security_group_rule_description(
                        f"{meta[1]} public IP", factory.SSH_PORT
                    ),
                )

        # [VPC traffic] -> (Each TCP/UDP port) -> EC2 instances
        for trans_layer_protocol in [factory.TCP_, factory.UDP_]:
            for p in trans_layer_protocol_port_mapping[trans_layer_protocol]:
                is_tcp: bool = bool(trans_layer_protocol == factory.TCP_)
                self.ec2_sg.add_ingress_rule(
                    peer=ec2.Peer.ipv4(cidr_ip=vpc.vpc_cidr_block) if is_tcp else ec2.Peer.any_ipv4(),
                    connection=ec2.Port.tcp(p) if is_tcp else ec2.Port.udp(p),
                    description=(
                        factory.get_ec2_security_group_rule_description(f"VPC ({vpc_name}) traffic", p)
                        if is_tcp
                        else f"Allow {trans_layer_protocol.upper()} port {p} traffic."
                    ),
                )

        # [VPC traffic] -> (SSH port) -> EC2 instances
        self.ec2_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(cidr_ip=vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(factory.SSH_PORT),
            description=factory.get_ec2_security_group_rule_description(f"VPC ({vpc_name}) traffic", factory.SSH_PORT),
        )
