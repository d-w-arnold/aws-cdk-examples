from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_sns as sns,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkLambdaRdsInstanceAutoStack(Stack):
    def __init__(
        self,
        factory: CdkConstructsFactory,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)

        factory.set_attrs_kms_key_stack(self, no_trim=True)

        security_groups: list[ec2.SecurityGroup] = [
            factory.ec2_security_group(
                self,
                [factory.RDS_, factory.INSTANCE_, factory.LAMBDA_],
                f"Security group for {factory.RDS_.upper()} database {factory.INSTANCE_} {factory.AUTO_} {factory.START_}/{factory.STOP_} Lambda functions.",
                full_description=True,
            )
        ]

        func_name_base_props: list[str] = [
            factory.RDS_.upper(),
            factory.INSTANCE_.capitalize(),
            factory.AUTO_.capitalize(),
        ]
        lambda_func_cloudwatch_custom: lambda_.Function = factory.lambda_function_cloudwatch(
            self,
            factory.join_sep_empty(func_name_base_props),
            security_groups=security_groups,
        )
        resource_arn: str = factory.format_arn_custom(self, service=factory.RDS_, resource=factory.DB_)
        for i in [factory.START_, factory.STOP_]:
            func_name: str = factory.join_sep_empty(func_name_base_props + [i.capitalize()])
            topic: sns.Topic = factory.sns_topic(self, [func_name])

            role: iam.Role = factory.iam_role_lambda(
                self,
                func_name,
                managed_policies=factory.lambda_managed_policies_vpc_list(),
                custom_policies=[
                    iam.PolicyStatement(
                        actions=[factory.join_sep_colon([factory.RDS_, "DescribeDBInstances"])],
                        resources=[resource_arn],
                    ),
                    iam.PolicyStatement(
                        actions=[
                            factory.join_sep_colon(
                                [factory.RDS_, ("StopDBInstance" if i == factory.STOP_ else "StartDBInstance")]
                            )
                        ],
                        resources=[resource_arn],
                    ),
                ],
            )
            topic.grant_publish(role)

            tag_key: str = factory.join_sep_score([factory.AUTO_, i])
            factory.lambda_function(
                self,
                func_name,
                factory.get_path([factory.RDS_, func_name]),
                f"{factory.AUTO_.capitalize()} {i} {factory.RDS_.upper()} database instances based on `{tag_key}` tag.",
                {
                    k: v
                    for k, v in {
                        "SNS_TOPIC": topic.topic_arn,
                        "TAG_KEY": tag_key,
                        "TAG_VALUES": factory.TAG_VAL_AUTO_ON,
                        "WEBHOOK_URL": factory.get_ms_teams_aws_notifications_webhook_url(
                            self, factory.WEBHOOK_URL_LAMBDA_
                        ),
                        # "SEP": sep if sep else None,
                    }.items()
                    if v
                },
                role,
                vpc_props=(factory.get_attr_vpc(self), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
                timeout=Duration.seconds(10),
                events_rules=factory.lambda_function_events_rules_cron(
                    self,
                    func_name,
                    factory.END_ if i == factory.STOP_ else i,
                    [
                        ([func_name], factory.schedules.window_ec_rds_week_days, {}),
                        (
                            [func_name, factory.BACKUP_],
                            factory.schedules.window_rds_mysql_daily_backup_week_days,
                            {},
                        ),
                        (
                            [func_name, factory.WEEKEND_],
                            factory.schedules.window_ec_rds_weekend,
                            {factory.WEEKEND_: True},
                        ),
                        (
                            [func_name, factory.WEEKEND_, factory.BACKUP_],
                            factory.schedules.window_rds_mysql_daily_backup_weekend,
                            {factory.WEEKEND_: True},
                        ),
                    ],
                ),
                lambda_function_cloudwatch_custom=lambda_func_cloudwatch_custom,
            )
