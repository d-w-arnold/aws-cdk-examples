from aws_cdk import CfnOutput, Stack, aws_ec2 as ec2, aws_ssm as ssm

from cdk_sih.client_vpn.endpoint import CdkClientVpnEndpointStack
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkBastionHostLinuxStack(Stack):
    def __init__(
        self,
        client_vpn_endpoint_stack: CdkClientVpnEndpointStack,
        factory: CdkConstructsFactory,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        self.factory: CdkConstructsFactory = factory
        self.vpc_stack: CdkVpcSihStack = vpc_stack

        bastion_host_linux_props: list[str] = [factory.BASTION_, factory.HOST_, factory.LINUX_]
        self.bastion_host_linux_: str = factory.join_sep_empty(i.capitalize() for i in bastion_host_linux_props)
        self.private_ip_address_props: list[str] = [factory.PRIVATE_, factory.IP_, factory.ADDRESS_]

        # ---------- EC2 ----------

        # For each VPC with a private subnet(s), create a Bastion Host Linux-based EC2 instance in each AZ
        self.bastion_hosts: dict[str, dict[str, ec2.BastionHostLinux]] = {}
        for vpc_name, vpc in self.vpc_stack.vpcs.items():
            setattr(self, factory.VPC_, vpc)
            setattr(self, factory.VPC_NAME_, vpc_name)

            sg: ec2.SecurityGroup = factory.ec2_security_group(
                self, bastion_host_linux_props, "Bastion Host Linux-based EC2 instance"
            )
            sg.add_ingress_rule(
                peer=ec2.Peer.any_ipv4(), connection=ec2.Port.icmp_ping(), description="Allow ping from anywhere."
            )
            if hasattr(client_vpn_endpoint_stack, factory.CLIENT_VPN_ENDPOINT_PRIVATE_SG_):
                sg.connections.allow_from(
                    other=getattr(client_vpn_endpoint_stack, factory.CLIENT_VPN_ENDPOINT_PRIVATE_SG_),
                    port_range=ec2.Port.tcp(factory.SSH_PORT),
                    description=factory.get_ec2_security_group_rule_description(
                        "Client VPN Endpoint PRIVATE", factory.SSH_PORT
                    ),
                )

            self.bastion_hosts[vpc_name] = {
                az: self.ec2_bastion_host_linux(vpc, az, sg, factory.ssh_key) for az in vpc.availability_zones
            }

    def ec2_bastion_host_linux(
        self, vpc: ec2.Vpc, az: str, sg: ec2.SecurityGroup, ssh_key: str
    ) -> ec2.BastionHostLinux:
        bastion_host: ec2.BastionHostLinux = ec2.BastionHostLinux(
            scope=self,
            id=self.factory.get_construct_id(self, [self.factory.PRIVATE_, az], self.bastion_host_linux_),
            vpc=vpc,
            # availability_zone=,  # Default: - Random zone.
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=8,  # Gibibytes (GiB)
                        encrypted=False,
                        # kms_key=,  # Default: - If encrypted is true, the default aws/ebs KMS key will be used.
                        delete_on_termination=True,
                        # iops=,  # Default: - none, required for EbsDeviceVolumeType.IO1
                        volume_type=ec2.EbsDeviceVolumeType.GP2,
                    ),
                    mapping_enabled=True,
                )
            ],  # Default: - Uses the block device mapping of the AMI
            # init=,  # Default: - no CloudFormation init
            # init_options=,  # Default: - default options
            instance_name=self.factory.join_sep_score(
                [self.bastion_host_linux_, self.factory.PRIVATE_, az, getattr(self, self.factory.VPC_NAME_)]
            ),
            instance_type=self.factory.ec2_instance_type_t3_micro(),
            # machine_image=,  # Default: - An Amazon Linux 2 image which is kept up-to-date automatically (the instance may be replaced on every deployment) and already has SSM Agent installed.
            require_imdsv2=False,
            security_group=sg,
            subnet_selection=ec2.SubnetSelection(
                availability_zones=[az], one_per_az=True, subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        )
        # Update EC2 instance name
        bastion_host.instance.instance.add_property_override("KeyName", ssh_key)
        # Update the BastionHostLinux user data
        bastion_host.instance.add_user_data("yum update -y")
        # Set aws-private AWS SSM Parameter Store parameter containing the Bastion Host instance ID
        self.factory.ssm_string_parameter(
            self,
            [self.factory.PRIVATE_, az],
            self.factory.AWS_PRIVATE_DESCRIPTION_,
            self.factory.get_path(
                [
                    self.factory.AWS_PRIVATE_PARAMETER_PREFIX_,
                    self.bastion_host_linux_,
                    self.factory.join_sep_score([self.factory.PRIVATE_, az]),
                ]
            ),
            bastion_host.instance_id,
            data_type=ssm.ParameterDataType.TEXT,
            tier=ssm.ParameterTier.STANDARD,
        )
        # Publish the bastion Host private IP address as CloudFormation output, to be used in project base stacks
        #  in allowing inbound rules on certain security groups.
        CfnOutput(
            scope=self,
            id=self.factory.get_construct_id(self, [az] + self.private_ip_address_props, self.factory.CFN_OUTPUT_TYPE),
            description=f"The Bastion Host ({az}) private IP address. For example, 10.0.1.96.",
            value=bastion_host.instance_private_ip,
        )
        return bastion_host

    def get_bastion_host_private_ips(self, vpc_name: str = None) -> list[str]:
        if vpc_name is None:
            vpc_name = self.vpc_stack.vpc_01_sih_
        return [
            v
            for k, v in self.factory.file_json_load_cdk_custom_outputs()[self.stack_name].items()
            if (self.factory.join_sep_empty(self.private_ip_address_props) in k)
            and (vpc_name.replace(self.factory.SEP_SCORE_, self.factory.SEP_EMPTY_) in k)
        ]
