from aws_cdk import CfnOutput, Stack, aws_ec2 as ec2, aws_iam as iam

from cdk_sih.client_vpn.endpoint import CdkClientVpnEndpointStack
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkPypiBaseStack(Stack):
    def __init__(
        self,
        bastion_host_private_ips: list[str],
        client_vpn_endpoint_stack: CdkClientVpnEndpointStack,
        component: str,
        elastic_ip_parameter_names: dict[str, str],
        factory: CdkConstructsFactory,
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        ec2_ssh_allowed: bool = True,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_client_vpn_endpoint_sg(self, client_vpn_endpoint_stack)
        factory.set_attrs_elastic_ips_meta(self, elastic_ip_parameter_names, inc_cfn_output=False)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_ports_default(self, alb_port=8080)

        self.bastion_host_private_ips: list[str] = bastion_host_private_ips

        self.server_description: str = (
            f"Foobar{f' {profile}' if (profile := factory.aws_profile) else factory.SEP_EMPTY_} Private PyPi server"
        )

        # Publish the Elastic IP public IPv4 addresses as CloudFormation output, to be used as a ref for an
        #  WAF Web ACL during CloudFront Distribution creation.
        for elastic_ip_str, meta in getattr(self, factory.ELASTIC_IP_META_).items():
            CfnOutput(
                scope=self,
                id=factory.get_construct_id(self, [elastic_ip_str], factory.CFN_OUTPUT_TYPE),
                description=f"The {meta[1]} public IPv4 address for the {self.server_description}. For example, 123.4.5.67.",
                value=meta[0],
            )

        # IAM Role for PyPi server EC2 instance
        server_stack_name: str = self.stack_name.replace(factory.BASE_.capitalize(), factory.SERVER_.capitalize(), 1)
        self.role: iam.Role = factory.iam_role_ec2(
            self,
            f"Role for EC2 instance {factory.join_sep_score(factory.get_attr_project_name_comp_props(self) + [factory.get_attr_vpc_name(self), factory.PRIVATE_])}",
            custom_policies=[
                factory.iam_policy_statement_cloudformation_stack_all(
                    self, resource_name=factory.get_path([server_stack_name, factory.SEP_ASTERISK_])
                ),
                factory.iam_policy_statement_kms_key_encrypt_decrypt(
                    self, resources=[factory.get_attr_kms_key_stack(self).key_arn]
                ),
                factory.iam_policy_statement_ssm_put_parameter(self),
                iam.PolicyStatement(
                    actions=[
                        factory.join_sep_colon([factory.EC2_, i])
                        for i in [
                            "AssociateAddress",
                            "CreateTags",
                            "DescribeAddresses",
                            "DescribeVolumes",
                            "DescribeVpcs",
                        ]
                    ],
                    resources=factory.ALL_RESOURCES,
                ),
            ],
        )

        # Create a secret in AWS Secrets Manager to store the PyPi server: port, username and password details
        self.secret_name: str = factory.get_path(
            [
                self.stack_name,
                factory.join_sep_under([i.upper() for i in [project_name, factory.SERVER_, factory.SECRET_]]),
            ]
        )
        self.username: str = factory.join_sep_under([project_name, factory.organisation_abbrev])
        factory.secrets_manager_secret(
            self,
            [],
            f"The {self.server_description} secret.",
            self.secret_name,
            secret_string_template={
                factory.PORT_: getattr(self, factory.ALB_PORT_),
                factory.USERNAME_: self.username,
            },
            password_length=32,
        ).grant_read(self.role)

        # ---------- Route 53 ----------

        factory.set_attrs_hosted_zone(self)

        # ---------- EC2 ----------

        self.alb_sg: ec2.SecurityGroup = factory.ec2_security_group(
            self,
            [factory.ALB_],
            factory.join_sep_space([self.server_description, factory.ALB_.upper()]),
        )
        self.ec2_sg: ec2.SecurityGroup = factory.ec2_security_group(self, [factory.EC2_], self.server_description)

        # HTTPS -> ALB
        self.alb_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(factory.HTTPS_PORT), description="Allow HTTPS traffic."
        )

        # ALB -> (All TCP ports) -> PyPi server EC2 instance
        self.ec2_sg.connections.allow_from(
            other=self.alb_sg,
            port_range=ec2.Port.all_tcp(),
            description=f"Allow {factory.ALB_.upper()} traffic on all TCP ports.",
        )

        if ec2_ssh_allowed:
            # [Bastion Hosts, Client VPN, Elastic IPs] -> (SSH) -> EC2 instances
            factory.ec2_security_group_add_support_infra(self, self.ec2_sg)
