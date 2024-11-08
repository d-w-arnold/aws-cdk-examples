import re
from collections import OrderedDict

from aws_cdk import Stack, Tags, aws_ec2 as ec2, aws_ssm as ssm
from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkVpcSihStack(Stack):
    def __init__(self, factory: CdkConstructsFactory, **kwargs) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        self.factory: CdkConstructsFactory = factory

        factory.set_factory_nat_gateway_ip_ranges_parameter_name(self.stack_name)

        self.is_default_aws_profile: bool = bool(factory.aws_profile is None)

        self.subnet_type_mapping: dict[str, ec2.SubnetType] = {
            factory.PUBLIC_: ec2.SubnetType.PUBLIC,
            factory.PRIVATE_: ec2.SubnetType.PRIVATE_WITH_EGRESS,
            factory.ISOLATED_: ec2.SubnetType.PRIVATE_ISOLATED,
        }

        setattr(self, factory.VPC_NAME_, None)
        self.vpc_01_sih_: str = factory.join_sep_score([factory.VPC_, str(1).zfill(2), factory.organisation_abbrev])

        max_azs_key: str = factory.MAX_
        vpn_connections_key: str = factory.VPN_

        vpc_setup = {
            factory.CIDRS_: factory.get_region_meta_cidrs(),
            max_azs_key: 3,
            vpn_connections_key: {},
        }

        # ---------- VPCs ----------

        subnets_list: list[str] = [factory.PUBLIC_, factory.PRIVATE_]
        # if factory.aws_profile is None:
        #     subnets_list.append(self.isolated)

        self.gateway_endpoints_key: str = factory.ENDPOINT_
        self.subnets_key: str = factory.SUBNET_

        self.vpc_meta: dict[str, dict] = OrderedDict(
            {
                self.vpc_01_sih_: {
                    self.subnets_key: subnets_list,
                    self.gateway_endpoints_key: {
                        factory.join_sep_empty(
                            [factory.S3_.upper(), factory.ENDPOINT_.capitalize()]
                        ): ec2.GatewayVpcEndpointOptions(service=ec2.GatewayVpcEndpointAwsService.S3)
                    },
                },
            }
        )

        self.vpc_cidrs: dict[str, str] = {}
        self.vpcs: dict[str, ec2.Vpc] = OrderedDict()
        for i, (name, meta) in enumerate(self.vpc_meta.items()):
            if i < len(self.vpc_meta):
                self.vpc_cidrs[name] = vpc_setup.get(factory.CIDRS_)[i]
                self.vpcs[name] = self.ec2_vpc(
                    name, meta, self.vpc_cidrs[name], vpc_setup.get(max_azs_key), vpc_setup.get(vpn_connections_key)
                )

    def ec2_subnet_configuration(self, vpc_name: str, subnet_type: str) -> ec2.SubnetConfiguration:
        return ec2.SubnetConfiguration(
            cidr_mask=24,
            name=self.factory.get_construct_name(self, [vpc_name, subnet_type]),
            subnet_type=self.subnet_type_mapping[subnet_type],
            # map_public_ip_on_launch=,  # Default: true in Subnet.Public, false in Subnet.Private or Subnet.Isolated.
            reserved=False,
        )

    def ec2_vpc(
        self,
        vpc_name: str,
        vpc_meta: dict,
        cidr: str,
        max_azs: int = 3,
        vpn_connections: dict[str, ec2.VpnConnectionOptions] = None,
    ) -> ec2.Vpc:
        setattr(self, self.factory.VPC_NAME_, vpc_name)
        vpc_subnets: list[str] = vpc_meta[self.subnets_key]
        vpc: ec2.Vpc = ec2.Vpc(
            scope=self,
            id=self.factory.get_construct_id(self, [self.factory.VPC_], "Vpc"),
            enable_dns_hostnames=True,
            enable_dns_support=True,
            gateway_endpoints=vpc_meta.get(self.gateway_endpoints_key) if self.is_default_aws_profile else None,
            ip_addresses=ec2.IpAddresses.cidr(cidr_block=cidr),
            max_azs=max_azs,
            # TODO: (NEXT) Consider increasing number of NAT Gateways, to at least 2x, possibly 1x per AZ
            nat_gateways=1 if self.factory.PRIVATE_ in vpc_subnets else 0,
            subnet_configuration=[self.ec2_subnet_configuration(vpc_name, i) for i in vpc_subnets],
            vpc_name=vpc_name,
            vpn_connections=vpn_connections,
            vpn_gateway=bool(vpn_connections is not None),
        )
        # Record the VPC Internet Gateway ID in SSM, for future programmatic usages.
        igw_id_props: list[str] = [self.factory.IGW_, self.factory.ID_]
        self.factory.ssm_string_parameter(
            self,
            igw_id_props,
            f"The VPC Internet Gateway ID for `{vpc_name}`.",
            self.factory.get_path([self.stack_name, vpc_name, self.factory.join_sep_score(igw_id_props)], lead=True),
            vpc.internet_gateway_id,
            data_type=ssm.ParameterDataType.TEXT,
            tier=ssm.ParameterTier.STANDARD,
        )
        # Generate VPC endpoints.
        if self.is_default_aws_profile:
            self.factory.ec2_interface_vpc_endpoint_map(
                self,
                vpc,
                [
                    self.factory.EC2MESSAGES_,
                    self.factory.join_sep_dot([self.factory.ECR_, self.factory.API_]),
                    self.factory.join_sep_dot([self.factory.ECR_, self.factory.DKR_]),
                    self.factory.KMS_,
                    self.factory.LOGS_,
                    self.factory.S3_,
                    self.factory.SECRETSMANAGER_,
                    self.factory.SSMMESSAGES_,
                    self.factory.SSM_,
                ],
            )
        # Add logging for VPC flow logs.
        vpc.add_flow_log(
            id=self.factory.get_construct_id(self, [self.factory.CLOUDWATCH_], "FlowLog"),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(
                log_group=self.factory.logs_log_group(
                    self,
                    [self.factory.VPC_],
                    self.factory.get_path(
                        [
                            self.factory.log_groups[self.factory.VPC_],
                            vpc_name,
                            self.factory.join_sep_score([self.factory.FLOW_, self.factory.LOGS_]),
                        ]
                    ),
                ),
            ),
            traffic_type=ec2.FlowLogTrafficType.ALL,
        )
        # For each VPC's default security group, allow inbound ICMP (ping) requests from any IPv4 address.
        ec2.SecurityGroup.from_security_group_id(
            scope=self,
            id=self.factory.get_construct_id(self, [self.factory.DEFAULT_], "ISecurityGroup"),
            security_group_id=vpc.vpc_default_security_group,
        ).add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), connection=ec2.Port.icmp_ping(), description="Allow ping from anywhere."
        )
        # Update Name tags for all VPC subnets.
        for i in [vpc.public_subnets, vpc.private_subnets, vpc.isolated_subnets]:
            self.tag_subnets_name(vpc_name, i)
        return vpc

    def tag_subnets_name(self, vpc_name: str, subnets: list[ec2.ISubnet]) -> None:
        for subnet in subnets:
            Tags.of(subnet).add(
                self.factory.NAME_.capitalize(),
                self.factory.join_sep_score(
                    [
                        vpc_name,
                        re.sub(r"Subnet[0-9]", self.factory.SEP_EMPTY_, subnet.node.id),
                        subnet.availability_zone,
                    ]
                ),
            )

    def set_attrs_vpc(self, self_obj, vpc_name: str = None, default: bool = False) -> None:
        if default:
            vpc_name = self.factory.DEFAULT_
            vpc = self.factory.ec2_vpc_default(self_obj, vpc_name)
            vpc_cidr = vpc.vpc_cidr_block
            setattr(self_obj, self.factory.VPC_, vpc)
            setattr(self_obj, self.factory.VPC_CIDR_, vpc_cidr)
        else:
            if vpc_name is None:
                vpc_name = self.vpc_01_sih_
            setattr(self_obj, self.factory.VPC_, self.vpcs[vpc_name])
            setattr(self_obj, self.factory.VPC_CIDR_, self.vpc_cidrs[vpc_name])
        setattr(self_obj, self.factory.VPC_NAME_, vpc_name)
