from netaddr import IPNetwork

from aws_cdk import Stack, Tags, aws_ec2 as ec2, aws_iam as iam
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkClientVpnEndpointStack(Stack):
    def __init__(
        self,
        client_vpn_endpoint_internet: bool,
        client_vpn_endpoint_server_certificate_id: str,
        factory: CdkConstructsFactory,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)

        client_vpn_endpoint_props: list[str] = [factory.CLIENT_, factory.VPN_, factory.ENDPOINT_]
        client_vpn_endpoint_azure_ad_props: list[str] = client_vpn_endpoint_props + [factory.AZURE_, factory.AD_]

        saml_provider: iam.SamlProvider = iam.SamlProvider(
            scope=self,
            id=factory.get_construct_id(self, client_vpn_endpoint_azure_ad_props, "SamlProvider"),
            metadata_document=iam.SamlMetadataDocument.from_file(
                path=factory.get_path(
                    [
                        factory.sub_paths[factory.EC2_],
                        factory.join_sep_under(client_vpn_endpoint_props),
                        factory.join_sep_dot(
                            [
                                factory.join_sep_score(
                                    [
                                        factory.AWS_,
                                        factory.CLIENT_,
                                        factory.VPN_,
                                        factory.SAML_,
                                        factory.FEDERATION_,
                                        factory.METADATA_,
                                    ]
                                ),
                                factory.XML_,
                            ]
                        ),
                    ]
                )
            ),
            name=factory.join_sep_score(client_vpn_endpoint_azure_ad_props),
        )
        associated_subnets: list[ec2.ISubnet] = factory.get_attr_vpc(self).private_subnets

        ip_network: IPNetwork = IPNetwork(
            factory.get_path(
                [
                    str(IPNetwork(factory.get_attr_vpc_cidr(self)).next()).rsplit(sep=factory.SEP_FW_, maxsplit=1)[0],
                    str(22),
                ]
            )
        )

        for i in [factory.INTERNET_, factory.PRIVATE_]:
            ip_network = ip_network.next()

            if i == factory.INTERNET_ and not client_vpn_endpoint_internet:
                continue

            desc: str = f"Client VPN Endpoint {i.upper()}"
            sg: ec2.SecurityGroup = factory.ec2_security_group(self, client_vpn_endpoint_props + [i], desc)
            is_private: bool = bool(i == factory.PRIVATE_)

            # https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/what-is.html#what-is-components
            client_vpn_endpoint: ec2.ClientVpnEndpoint = ec2.ClientVpnEndpoint(
                scope=self,
                id=factory.get_construct_id(self, [i], "ClientVpnEndpoint"),
                vpc=factory.get_attr_vpc(self),
                cidr=str(ip_network),
                server_certificate_arn=factory.format_arn_custom(
                    self,
                    service=factory.ACM_,
                    resource=factory.CERTIFICATE_,
                    resource_name=client_vpn_endpoint_server_certificate_id,
                ),
                authorize_all_users_to_vpc_cidr=False,
                # client_certificate_arn=,  # Default: - use user-based authentication
                # client_connection_handler=,  # Lambda function used for connection auth. Default: - no connection handler
                client_login_banner=f"""
                *** AWS Client VPN - {factory.organisation.upper()} ({i.upper()}) ***

                Welcome! Hello, world.

                A VPN session has been successfully established.

                AWS Account:\t{factory.get_attr_env_account(self)}
                AWS Region:\t{factory.get_attr_env_region(self)} ({factory.region_tz})
                AWS VPC:\t\t{factory.get_attr_vpc_name(self)}

                Sign in to the AWS console:

                https://{factory.get_attr_env_account(self)}.signin.aws.amazon.com/console
                """,
                description=f"The {desc} for `{factory.get_attr_vpc_name(self)}`.",
                # dns_servers=,  # Default: - use the DNS address configured on the device
                logging=True,
                log_group=factory.logs_log_group(
                    self,
                    client_vpn_endpoint_props + [i],
                    factory.get_path(
                        [
                            factory.log_groups[factory.VPC_],
                            factory.get_attr_vpc_name(self),
                            factory.join_sep_score(client_vpn_endpoint_props + [i]),
                        ]
                    ),
                ),
                # log_stream=,  # Default: - a new stream is created
                port=ec2.VpnPort.HTTPS,
                security_groups=[sg],
                self_service_portal=True,
                session_timeout=ec2.ClientVpnSessionTimeout.EIGHT_HOURS,
                split_tunnel=is_private,
                transport_protocol=ec2.TransportProtocol.UDP,
                user_based_authentication=ec2.ClientVpnUserBasedAuthentication.federated(saml_provider=saml_provider),
                vpc_subnets={factory.SUBNETS_: associated_subnets},
            )
            Tags.of(client_vpn_endpoint).add(
                factory.NAME_.capitalize(),
                factory.join_sep_score([factory.get_attr_vpc_name(self)] + client_vpn_endpoint_props + [i]),
            )

            client_vpn_endpoint.add_authorization_rule(
                id=factory.get_construct_id(self, client_vpn_endpoint_props + [i], "ClientVpnAuthorizationRule"),
                cidr=factory.get_attr_vpc_cidr(self) if is_private else factory.CIDR_ALL,
                # group_id=,  # Default: - authorize all groups
                description=f"A {desc} authorization rule for `{factory.get_attr_vpc_name(self)}`.",
            )

            if is_private:
                client_vpn_endpoint.add_route(
                    id=factory.get_construct_id(
                        self,
                        client_vpn_endpoint_props + [i, factory.CLIENT_, factory.TO_, factory.CLIENT_, factory.ACCESS_],
                        "ClientVpnRoute",
                    ),
                    cidr=str(ip_network),
                    target=ec2.ClientVpnRouteTarget.local(),
                    description=f"A {desc} route for Client-to-client access.",
                )
                sg.add_ingress_rule(
                    peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(22), description="Allow SSH traffic."
                )
                setattr(self, factory.CLIENT_VPN_ENDPOINT_PRIVATE_SG_, sg)
            else:
                for n, s in enumerate(associated_subnets):
                    client_vpn_endpoint.add_route(
                        id=factory.get_construct_id(
                            self,
                            client_vpn_endpoint_props + [i, factory.ALL_, factory.TRAFFIC_, n],
                            "ClientVpnRoute",
                        ),
                        cidr=factory.CIDR_ALL,
                        target=ec2.ClientVpnRouteTarget.subnet(subnet=s),
                        description=f"A {desc} route for all traffic: `{s.availability_zone}`.",
                    )
