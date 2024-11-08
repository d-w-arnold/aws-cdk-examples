from aws_cdk import (
    Duration,
    Stack,
    aws_amazonmq as amazonmq,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    aws_elasticloadbalancingv2_targets as elasticloadbalancing_targets,
    aws_ssm as ssm,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.bkg.base import CdkBkgBaseStack
from cdk_sih.internal_domain.bkg.broker import CdkBkgBrokerStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkBkgMqStack(Stack):
    def __init__(
        self,
        base_stack: CdkBkgBaseStack,
        broker_stack: CdkBkgBrokerStack,
        component: str,
        component_alt: str,
        deploy_env: str,
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta)

        factory.set_attrs_kms_key_stack(self)

        self.price_class: cloudfront.PriceClass = factory.get_cloudfront_dist_price_class(self, default=True)

        self.fqdn: str = None
        if subdomain := getattr(self, factory.SUBDOMAIN_, None):
            subdomain = factory.join_sep_dot([component_alt, subdomain])
            self.fqdn = factory.join_sep_dot([subdomain, getattr(base_stack, factory.HOSTED_ZONE_NAME_)])

        # ---------- EC2 NLB & CloudFront ----------

        # Network Load Balancer (NLB) for Bkg Amazon MQ RabbitMQ Web Console
        nlb: elasticloadbalancing.NetworkLoadBalancer = elasticloadbalancing.NetworkLoadBalancer(
            scope=self,
            id=factory.get_construct_id(self, [factory.NLB_], "NetworkLoadBalancer"),
            cross_zone_enabled=False,
            vpc=factory.get_attr_vpc(self),
            deletion_protection=True,
            internet_facing=True,
            load_balancer_name=factory.get_construct_name_short(self, [factory.NLB_]),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        # Amazon MQ RabbitMQ broker Private IPs
        #  (NB. parameter created in AWS Systems Manager Parameter Store using:
        #  https://bitbucket.org/foobar-products-development/aws-scripts/src/main/aws-amazonmq-broker/aws-amazonmq-broker-web.py)

        mq_rabbitmq_broker: amazonmq.CfnBroker = broker_stack.mq_rabbitmq_broker

        nlb.node.add_dependency(mq_rabbitmq_broker)
        private_ips: dict[str, str] = {
            az: ssm.StringParameter.value_from_lookup(
                scope=self,
                parameter_name=factory.get_path(
                    [
                        mq_rabbitmq_broker.broker_name,
                        factory.join_sep_empty(
                            [i.capitalize() for i in [factory.PRIVATE_, factory.IP_, factory.ADDRESS_]]
                        ),
                        az,
                    ],
                    lead=True,
                ),
            )
            for az in factory.get_attr_vpc(self).availability_zones
        }

        # CloudFront Distribution
        cf_origin_path: str = factory.SEP_FW_
        factory.cloudfront_distribution(
            self,
            nlb,
            getattr(base_stack, factory.HOSTED_ZONE_),
            subdomain,
            cf_origin_path,
        )

        factory.set_attrs_url(self, cf_origin_path)
        factory.cfn_output_url(self)

        certificate: acm.Certificate = factory.acm_certificate(
            self,
            [factory.NLB_, factory.LISTENER_],
            self.fqdn,
            getattr(base_stack, factory.HOSTED_ZONE_),
        )

        for p in [factory.HTTPS_PORT, base_stack.mq_rabbitmq_port]:
            nlb_target_group: elasticloadbalancing.NetworkTargetGroup = elasticloadbalancing.NetworkTargetGroup(
                scope=self,
                id=factory.get_construct_id(self, [factory.NLB_, str(p), factory.TG_], "NetworkTargetGroup"),
                port=p,
                connection_termination=False,
                # preserve_client_ip=,
                # Default: False if the target group type is IP address and the
                #  target group protocol is TCP or TLS. Otherwise, True.
                protocol=elasticloadbalancing.Protocol.TLS,
                proxy_protocol_v2=False,
                # targets=[],
                deregistration_delay=Duration.seconds(120),
                health_check=elasticloadbalancing.HealthCheck(
                    # enabled=,  # Default: - Determined automatically.
                    # healthy_grpc_codes="12",  # Health check matcher cannot be set for both 'HTTP' and 'GRPC' codes at the same time.
                    healthy_http_codes=str(200),
                    healthy_threshold_count=2,  # Default: 3 for NLBs
                    interval=Duration.seconds(10),
                    path=cf_origin_path,
                    port=str(factory.HTTPS_PORT),  # Default: 'traffic-port'
                    protocol=elasticloadbalancing.Protocol.HTTPS,
                    timeout=Duration.seconds(10),
                    unhealthy_threshold_count=2,
                ),
                target_group_name=factory.get_construct_name_short(self, [factory.NLB_, str(p), factory.TG_]),
                target_type=elasticloadbalancing.TargetType.IP,
                vpc=factory.get_attr_vpc(self),
            )
            for az, private_ip in private_ips.items():
                # NB. The NLB target group targets will be marked as UNHEALTHY, unless the Amazon MQ RabbitMQ broker
                #  is status RUNNING prior to deploying this CDK stack
                nlb_target_group.add_target(
                    elasticloadbalancing_targets.IpTarget(
                        ip_address=private_ip,
                        port=p,
                        availability_zone=az,
                    )
                )
            nlb.add_listener(
                id=factory.get_construct_id(self, [factory.NLB_, str(p)], "NetworkListener"),
                port=p,
                # alpn_policy=,  # Application-Layer Protocol Negotiation (ALPN) is a TLS extension. Default: - None
                certificates=[certificate],
                # default_action=,  # Cannot be specified together with default_target_groups. Default: - None.
                # default_target_groups=,  # Cannot be specified together with default_action. Default: - None.
                protocol=elasticloadbalancing.Protocol.TLS,
                # ssl_policy=elasticloadbalancing.SslPolicy.RECOMMENDED,
                # Default: - Current predefined security policy.
            ).add_action(
                _id=factory.get_construct_id(self, [factory.NLB_, str(p), factory.LISTENER_], "NetworkListenerAction"),
                action=elasticloadbalancing.NetworkListenerAction.forward(
                    target_groups=[nlb_target_group],
                    # stickiness_duration=,  # Target group stickiness cannot be configured on NLBs
                ),
            )
