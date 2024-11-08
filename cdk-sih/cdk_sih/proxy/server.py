from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)

from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkProxyServerStack(Stack):
    def __init__(
        self,
        component: str,
        elastic_ip: ec2.CfnEIP,
        elastic_ip_parameter_names: dict[str, str],
        factory: CdkConstructsFactory,
        project_name: str,
        ec2_ssh_allowed: str = True,
        vpc: ec2.Vpc = None,  # Default: Uses the default VPC
        vpc_name: str = None,  # Default: Specifies the default VPC name
        **kwargs,
    ) -> None:
        if vpc_name is None:
            vpc_name = factory.DEFAULT_

        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc: ec2.IVpc = vpc if vpc else factory.ec2_vpc_default(self, vpc_name)
        setattr(self, factory.VPC_, vpc)
        setattr(self, factory.VPC_NAME_, vpc_name)
        factory.set_attrs_project_name_comp(self, project_name, component, inc_cfn_output=True)

        factory.set_attrs_elastic_ips_meta(self, elastic_ip_parameter_names, inc_cfn_output=False)
        factory.set_attrs_kms_key_stack(self)

        self.schedule_window: dict[str, dict[str, int]] = factory.schedules.window_proxy

        project_name_comp_props: list[str] = factory.get_attr_project_name_comp_props(self)

        server_port: int = 8888

        # IAM Role for Proxy server EC2 instance
        role: iam.Role = factory.iam_role_ec2(
            self,
            f"Role for EC2 instance {factory.join_sep_score(project_name_comp_props + [vpc_name, factory.PUBLIC_])}",
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
            ],
        )

        # Create a secret in AWS Secrets Manager for the Tinyproxy BasicAuth password
        basic_auth_props: list[str] = [factory.BASIC_, factory.AUTH_]
        factory.secrets_manager_secret(
            self,
            basic_auth_props,
            "The Tinyproxy BasicAuth password secret.",
            factory.get_path(
                [
                    self.stack_name,
                    factory.join_sep_score(project_name_comp_props + basic_auth_props),
                ]
            ),
            exclude_punctuation=True,
            exclude_characters=False,
            password_length=32,
        ).grant_read(role)

        # Get Tinyproxy configuration
        tinyproxy_port_option: str = factory.PORT_.capitalize()
        tinyproxy_basic_auth_option: str = factory.join_sep_empty([i.capitalize() for i in basic_auth_props])
        tinyproxy_conf_props: list[str] = [factory.TINYPROXY_, factory.CONF_]
        with open(
            factory.get_path(
                [
                    factory.sub_paths[factory.EC2_],
                    factory.join_sep_under(project_name_comp_props),
                    factory.join_sep_dot(tinyproxy_conf_props),
                ]
            ),
            "r",
            encoding=factory.ENCODING,
        ) as f:
            tinyproxy_config: list[str] = [i for i in f.readlines() if i[0] not in ["\n", "#"]]
            to_update: set = {tinyproxy_port_option, tinyproxy_basic_auth_option}
            for i, s in enumerate(tinyproxy_config):
                if not to_update:
                    break
                if s.startswith(tinyproxy_port_option):
                    tinyproxy_config[i] = s.replace(f"<{factory.PORT_}>", str(server_port), 1)
                    to_update.remove(tinyproxy_port_option)
                if s.startswith(tinyproxy_basic_auth_option):
                    tinyproxy_config[i] = s.replace(
                        f"<{factory.USER_}>", factory.join_sep_under([project_name, factory.organisation_abbrev]), 1
                    )
                    to_update.remove(tinyproxy_basic_auth_option)

        # Create a parameter in AWS SSM Parameter Store containing the Tinyproxy configuration
        factory.ssm_string_list_parameter(
            self,
            tinyproxy_conf_props,
            "The Tinyproxy configuration options to set on the Proxy server EC2 instance.",
            factory.get_path([self.stack_name, factory.join_sep_score(tinyproxy_conf_props)], lead=True),
            tinyproxy_config,
        ).grant_read(role)

        ec2_sg: ec2.SecurityGroup = factory.ec2_security_group(
            self,
            [factory.EC2_],
            "Allow access to Proxy server EC2 instance.",
            ingress_rules=[
                (
                    ec2.Peer.any_ipv4(),
                    ec2.Port.tcp(server_port),
                    f"Allow Tinyproxy on port {server_port}.",
                )
            ],
            full_description=True,
        )

        if ec2_ssh_allowed:
            # [Elastic IPs] -> (SSH) -> EC2 instances
            for _, meta in getattr(self, factory.ELASTIC_IP_META_).items():
                ec2_sg.add_ingress_rule(
                    peer=ec2.Peer.ipv4(cidr_ip=factory.get_path([meta[0], str(32)])),
                    connection=ec2.Port.tcp(factory.SSH_PORT),
                    description=factory.get_ec2_security_group_rule_description(
                        f"{meta[1]} public IP", factory.SSH_PORT
                    ),
                )

        factory.autoscaling_auto_scaling_group_default(
            self,
            role,
            ec2_sg,
            factory.lambda_function_sns_asg(self, use_vpc=False),
            instance_type=factory.ec2_instance_type_t3_large(),
            machine_image=factory.ec2_machine_image_ubuntu_22_04(),
        )

        self.public_ipv4_parameter_name: str = factory.get_path(
            [self.stack_name, factory.join_sep_score([factory.PUBLIC_, factory.IPV4_])], lead=True
        )

        factory.cfn_output_ec2_instance_eip_allocation_id(self, elastic_ip)
        factory.cfn_output_ec2_instance_public_ipv4_parameter_name(self, self.public_ipv4_parameter_name)
        factory.cfn_output_ec2_instance_vpc_name(self)
