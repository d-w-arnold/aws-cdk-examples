from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_route53 as route53,
    aws_ses as ses,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    custom_resources,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkMailBaseStack(Stack):
    def __init__(
        self,
        component: str,
        factory: CdkConstructsFactory,
        mail_users_hosted_zones: dict[str, route53.HostedZone],
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        self.factory: CdkConstructsFactory = factory

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_kms_key_stack(self)

        project_name_comp_props: list[str] = factory.get_attr_project_name_comp_props(self)
        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self, inc_deploy_env=False)

        bounce_: str = "bounce"
        complaint_: str = "complaint"

        dmarc_policy_mode: str = (
            "quarantine"  # https://aws.amazon.com/blogs/messaging-and-targeting/email-authenctication-dmarc-policy/
        )

        # ---------- EC2 ----------

        ses_lambda_sg_description: str = f"{factory.SES_.upper()} Lambda function"
        self.ses_lambda_sg: ec2.SecurityGroup = factory.ec2_security_group(
            self,
            [factory.SES_, factory.LAMBDA_],
            factory.join_sep_space([word_map_project_name_comp, ses_lambda_sg_description]),
        )
        # [VPC traffic] -> (All TCP ports) -> SES Lambda function
        self.ses_lambda_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(cidr_ip=factory.get_attr_vpc_cidr(self)),
            connection=ec2.Port.all_tcp(),
            description=factory.get_ec2_security_group_rule_description(
                f"VPC ({factory.get_attr_vpc_name(self)}) traffic"
            ),
        )

        # ---------- SES ----------

        security_groups: list[ec2.SecurityGroup] = [self.ses_lambda_sg]

        rep_met_props: list[str] = [factory.REP_, factory.MET_]
        sns_topic_rep_met: sns.Topic = factory.sns_topic(
            self,
            rep_met_props,
            subscriptions_=[
                factory.sns_subscriptions_email_subscription(),
                subscriptions.LambdaSubscription(
                    fn=factory.lambda_function_cloudwatch(
                        self,
                        factory.join_sep_score(project_name_comp_props + rep_met_props),
                        code_path_prefix=project_name,
                        custom_policies=[
                            iam.PolicyStatement(
                                actions=[
                                    factory.join_sep_colon([factory.SES_, i])
                                    for i in ["UpdateConfigurationSetSendingEnabled"]
                                ],
                                resources=factory.ALL_RESOURCES,
                            )
                        ],
                        security_groups=security_groups,
                    )
                ),
            ],
        )

        event_dest_props: list[str] = [factory.EVENT_, factory.DEST_]
        sns_topic_event_dest: sns.Topic = factory.sns_topic(
            self,
            event_dest_props,
            subscriptions_=[
                subscriptions.LambdaSubscription(
                    fn=factory.lambda_function_sns(
                        self,
                        factory.join_sep_score(project_name_comp_props + event_dest_props),
                        code_path_prefix=project_name,
                        security_groups=security_groups,
                    )
                )
            ],
        )

        rep_met_thresholds: dict[str, int] = {
            bounce_: 0.04,
            complaint_: 0.0008,
        }  # https://docs.aws.amazon.com/ses/latest/dg/reputationdashboard-cloudwatch-alarm.html

        verified_domains: dict[str, ses.EmailIdentity] = {}
        verified_domain_config_sets: dict[str, ses.ConfigurationSet] = {}
        self.verified_mail_users: dict[str, ses.EmailIdentity] = {}
        self.mail_users_config_set_names: dict[str, str] = {}
        for mail_user, hosted_zone in mail_users_hosted_zones.items():
            domain_name: str = mail_user.split(sep=factory.SEP_AT_SIGN_, maxsplit=1)[1]
            if domain_name not in verified_domains:
                san_domain_name_domain_props: list[str] = [self.sanitise(domain_name), factory.DOMAIN_]
                configuration_set_name: str = factory.get_construct_name_short(
                    self, san_domain_name_domain_props + [factory.CONFIG_, factory.SET_], length=64
                )
                verified_domain_config_sets[domain_name] = ses.ConfigurationSet(
                    scope=self,
                    id=factory.get_construct_id(self, san_domain_name_domain_props, "ConfigurationSet"),
                    configuration_set_name=configuration_set_name,
                    # custom_tracking_redirect_domain=,  # Default: - use the default awstrack.me domain
                    # dedicated_ip_pool=,  # TODO: (OPTIONAL) Default: - do not use a dedicated IP pool
                    reputation_metrics=True,
                    sending_enabled=True,
                    suppression_reasons=ses.SuppressionReasons.BOUNCES_AND_COMPLAINTS,
                    # TODO: (OPTIONAL) ses.ConfigurationSetTlsPolicy.REQUIRE - so messages
                    #  are only delivered if a TLS connection can be established.
                    tls_policy=ses.ConfigurationSetTlsPolicy.OPTIONAL,
                )
                verified_domain_config_sets[domain_name].add_event_destination(
                    id=factory.get_construct_id(self, san_domain_name_domain_props, "ConfigurationSetEventDestination"),
                    destination=ses.EventDestination.sns_topic(topic=sns_topic_event_dest),
                    configuration_set_event_destination_name=factory.get_construct_name_short(
                        self, san_domain_name_domain_props + event_dest_props, length=64
                    ),
                    enabled=True,
                    events=[
                        # ses.EmailSendingEvent.SEND,
                        ses.EmailSendingEvent.RENDERING_FAILURE,
                        ses.EmailSendingEvent.REJECT,
                        # ses.EmailSendingEvent.DELIVERY,
                        ses.EmailSendingEvent.BOUNCE,
                        ses.EmailSendingEvent.COMPLAINT,
                        ses.EmailSendingEvent.DELIVERY_DELAY,
                        ses.EmailSendingEvent.SUBSCRIPTION,
                        # ses.EmailSendingEvent.OPEN,
                        # ses.EmailSendingEvent.CLICK,
                    ],
                )
                mail_from_subdomain: str = factory.join_sep_dot([factory.SES_, project_name])
                verified_domains[domain_name] = ses.EmailIdentity(
                    scope=self,
                    id=factory.get_construct_id(self, san_domain_name_domain_props, "EmailIdentity"),
                    identity=ses.Identity.public_hosted_zone(hosted_zone=hosted_zone),
                    configuration_set=verified_domain_config_sets[domain_name],
                    dkim_identity=ses.DkimIdentity.easy_dkim(
                        signing_key_length=ses.EasyDkimSigningKeyLength.RSA_2048_BIT
                    ),
                    dkim_signing=True,
                    feedback_forwarding=True,
                    mail_from_behavior_on_mx_failure=ses.MailFromBehaviorOnMxFailure.REJECT_MESSAGE,
                    # Default: ses.MailFromBehaviorOnMxFailure.USE_DEFAULT_VALUE
                    mail_from_domain=factory.join_sep_dot(
                        [mail_from_subdomain, domain_name]
                    ),  # Default: - use amazonses.com
                )
                route53.TxtRecord(
                    scope=self,
                    id=factory.get_construct_id(self, san_domain_name_domain_props + [factory.ROUTE_53_], "TxtRecord"),
                    values=[f"v=DMARC1;p={dmarc_policy_mode};rua=mailto:{factory.email_notification_recipient}"],
                    zone=hosted_zone,
                    comment=f"A TXT-Record for {word_map_project_name_comp}, " f"for DMARC: {factory.HTTPS_}dmarc.org/",
                    delete_existing=False,
                    # geo_location=,
                    record_name=f"_dmarc.{mail_from_subdomain}",
                    # set_identifier=,  # can only be set when either 'weight' or 'geo_location' is defined
                    ttl=Duration.minutes(30),  # 1800 seconds
                    # weight=,
                )
                for i in [bounce_, complaint_]:
                    metric_name: str = factory.join_sep_dot(
                        [
                            factory.REPUTATION_.capitalize(),
                            factory.join_sep_empty([j.capitalize() for j in [i, factory.RATE_]]),
                        ]
                    )
                    factory.cloudwatch_alarm(
                        self,
                        san_domain_name_domain_props + [i] + rep_met_props,
                        cloudwatch.Metric(
                            metric_name=metric_name,
                            namespace=factory.join_sep_fw([i.upper() for i in [factory.AWS_, factory.SES_]]),
                            dimensions_map={
                                factory.join_sep_colon(
                                    [factory.SES_, factory.join_sep_score([factory.CONFIGURATION_, factory.SET_])]
                                ): configuration_set_name
                            },
                            label=metric_name,
                            period=Duration.minutes(5),
                            statistic="Average",
                            # unit=,  # Default: - All metric datums in the given metric stream
                        ),
                        f"Reputation '{i.capitalize()} rate' metric alarm for `{configuration_set_name}` config set.",
                        cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                        cloudwatch.TreatMissingData.IGNORE,
                        threshold=rep_met_thresholds[i],
                        evaluation_periods=3,
                        datapoints_to_alarm=1,
                    ).add_alarm_action(cloudwatch_actions.SnsAction(sns_topic_rep_met))
            san_mail_user_: str = self.sanitise(mail_user)
            config_set: ses.ConfigurationSet = verified_domain_config_sets[domain_name]
            self.verified_mail_users[mail_user] = ses.EmailIdentity(
                scope=self,
                id=factory.get_construct_id(self, [san_mail_user_], "EmailIdentity"),
                identity=ses.Identity.email(email=mail_user),
                configuration_set=config_set,
            )
            self.verified_mail_users[mail_user].node.add_dependency(verified_domains[domain_name])
            self.mail_users_config_set_names[mail_user] = config_set.configuration_set_name
            custom_resource: custom_resources.AwsCustomResource = custom_resources.AwsCustomResource(
                scope=self,
                id=factory.get_construct_id(self, [san_mail_user_], "AwsCustomResource"),
                policy=custom_resources.AwsCustomResourcePolicy.from_statements(
                    statements=[
                        iam.PolicyStatement(
                            actions=[factory.join_sep_colon([factory.SES_, "VerifyEmailIdentity"])],
                            resources=factory.ALL_RESOURCES,
                        )
                    ]
                ),
                on_create=custom_resources.AwsSdkCall(
                    action="verifyEmailIdentity",
                    service=factory.SES_.upper(),
                    parameters={"EmailAddress": mail_user},
                    physical_resource_id=custom_resources.PhysicalResourceId.of(
                        id=factory.join_sep_score([self.stack_name, "AwsSdkCall", san_mail_user_])
                    ),
                ),
                removal_policy=RemovalPolicy.DESTROY,
            )
            custom_resource.node.add_dependency(self.verified_mail_users[mail_user])

        self.mail_users_verified_mail_users_arns: dict[str, str] = {
            k: factory.format_arn_custom(
                self, service=factory.SES_, resource=factory.IDENTITY_, resource_name=v.email_identity_name
            )
            for k, v in self.verified_mail_users.items()
        }

    def sanitise(self, str_: str) -> str:
        return self.factory.join_sep_empty(i if i.isalnum() else self.factory.SEP_SCORE_ for i in str_)
