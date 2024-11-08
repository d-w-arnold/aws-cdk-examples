import json

from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_events as events,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ssm as ssm,
)
from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkMetofficeStorageStack(Stack):
    def __init__(
        self,
        component: str,
        factory: CdkConstructsFactory,
        project_name: str,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_kms_key_stack(self)

        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self, inc_deploy_env=False)

        lambda_function_monitoring_rate: int = 15  # minutes
        s3_bucket_daily_ingestion_threshold: int = 5  # in GiB

        # ---------- S3 ----------

        s3_bucket_name_prefix: str = factory.join_sep_score(
            [factory.organisation, factory.get_cdk_stack_name_short(self.stack_name).lower()]
        )
        s3_bucket_: s3.Bucket = factory.s3_bucket(
            self,
            s3_bucket_name_prefix,
            lifecycle_rules=True,
            server_access_logs_bucket=True,
        )

        # ---------- SSM ----------

        # S3 bucket state meta

        state_param_props: list[str] = [
            s3_bucket_name_prefix,
            factory.get_attr_env_region(self),
            factory.STATE_,
            factory.META_,
        ]
        state_param: ssm.StringParameter = factory.ssm_string_parameter(
            self,
            state_param_props,
            f"S3 bucket state meta for {word_map_project_name_comp}.",
            factory.get_path([self.stack_name, factory.join_sep_score(state_param_props)], lead=True),
            json.dumps(
                {
                    i: factory.SEP_EMPTY_
                    for i in [
                        factory.DATE_,
                        factory.join_sep_score([factory.DAILY_, factory.START_, factory.BYTE_, factory.COUNT_]),
                        factory.join_sep_score([factory.LATEST_, factory.BYTE_, factory.COUNT_]),
                    ]
                }
            ),
            # json.dumps({i: factory.SEP_EMPTY_ for i in ["date", "daily-start-byte-count", "latest-byte-count"]}),
            data_type=ssm.ParameterDataType.TEXT,
            tier=ssm.ParameterTier.STANDARD,
        )

        # ---------- IAM ----------

        metoffice_iam_props: list[str] = [project_name, factory.IAM_]
        metoffice_iam_user_props: list[str] = metoffice_iam_props + [factory.USER_]
        iam_user_group_name: str = factory.join_sep_under(
            [getattr(self, factory.WORD_MAP_PROJECT_NAME_), getattr(self, factory.WORD_MAP_COMPONENT_)]
        )
        iam_user_group: iam.Group = iam.Group(
            scope=self,
            id=factory.get_construct_id(self, metoffice_iam_user_props, "Group"),
            group_name=iam_user_group_name,
            # managed_policies=,  # Default: - No managed policies.
            # path=,  # Default: /
        )
        s3_bucket_.grant_read_write(iam_user_group)

        iam_user_name: str = project_name
        iam_user: iam.User = iam.User(
            scope=self,
            id=factory.get_construct_id(self, metoffice_iam_props, "User"),
            groups=[iam_user_group],
            # managed_policies=,  # Default: - No managed policies.
            # password=,  # Default: - User won’t be able to access the management console without a password.
            # password_reset_required=False,
            # path=,  # Default: /
            permissions_boundary=iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="AmazonS3FullAccess"
            ),  # A permissions boundary if for setting maximum IAM perms using a managed policy
            user_name=iam_user_name,
        )

        iam_user_access_key: iam.AccessKey = iam.AccessKey(
            scope=self,
            id=factory.get_construct_id(self, metoffice_iam_user_props, "AccessKey"),
            user=iam_user,
            # serial=,  # Default: - No serial value
            status=iam.AccessKeyStatus.ACTIVE,
        )

        # Publish the IAM user Access Key ID as CloudFormation output.
        CfnOutput(
            scope=self,
            id=factory.get_construct_id(
                self, metoffice_iam_user_props + [factory.ACCESS_, factory.KEY_, factory.ID_], factory.CFN_OUTPUT_TYPE
            ),
            description=f"The '{iam_user_name}' IAM user Access Key ID. For example, ABC123??????????????.",
            value=iam_user_access_key.access_key_id,
        )

        # ---------- Secrets Manager ----------

        secret_access_key_props: list[str] = [factory.SECRET_, factory.ACCESS_, factory.KEY_]
        factory.secrets_manager_secret(
            self,
            metoffice_iam_user_props + secret_access_key_props,
            f"The IAM user Secret Access Key secret for: {iam_user_name}",
            factory.get_path([self.stack_name, factory.join_sep_score(secret_access_key_props)]),
            secret_string_value=iam_user_access_key.secret_access_key,
        )

        # ---------- Lambda ----------

        archive_byte_count_: str = factory.join_sep_score([factory.ARCHIVE_, factory.BYTE_, factory.COUNT_])

        function_monitor_name: str = factory.join_sep_empty(
            [
                factory.MONITOR_.capitalize(),
                getattr(self, factory.WORD_MAP_PROJECT_NAME_),
                getattr(self, factory.WORD_MAP_COMPONENT_),
            ]
        )

        function_monitor_role: iam.Role = factory.iam_role_lambda(
            self,
            function_monitor_name,
            managed_policies=factory.lambda_managed_policies_vpc_list()
            + [iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="AmazonS3ReadOnlyAccess")],
            custom_policies=[
                iam.PolicyStatement(
                    actions=[factory.join_sep_colon([factory.IAM_, i]) for i in ["GetGroup", "RemoveUserFromGroup"]],
                    resources=[iam_user_group.group_arn],
                ),
            ],
        )
        state_param.grant_read(function_monitor_role)
        state_param.grant_write(function_monitor_role)

        # Lambda function for monitoring the Metoffice Storage
        factory.lambda_function(
            self,
            function_monitor_name,
            factory.get_path([project_name, function_monitor_name]),
            f"Lambda function for monitoring the {word_map_project_name_comp}.",
            {
                "BUCKET_NAME": s3_bucket_.bucket_name,
                "DAILY_THRESHOLD": str(s3_bucket_daily_ingestion_threshold),
                "IAM_USER": iam_user_name,
                "IAM_USER_GROUP": iam_user_group_name,
                "STATE_PARAMETER": state_param.parameter_name,
                "ARCHIVE_BYTE_COUNT": archive_byte_count_,
            },
            function_monitor_role,
            params_and_secrets_ext=True,
            timeout=Duration.seconds(30),
            events_rules=factory.lambda_function_events_rules_rate(
                self, function_monitor_name, lambda_function_monitoring_rate
            ),
        )

        # Lambda function for archiving the Metoffice Storage
        cron_start_hour: int = 8  # UTC
        cron_week_day: str = "MON"  # Monday

        function_archive_name: str = factory.join_sep_empty(
            [
                factory.ARCHIVE_.capitalize(),
                getattr(self, factory.WORD_MAP_PROJECT_NAME_),
                getattr(self, factory.WORD_MAP_COMPONENT_),
            ]
        )

        function_archive_role: iam.Role = factory.iam_role_lambda(
            self,
            function_archive_name,
            managed_policies=factory.lambda_managed_policies_vpc_list()
            + [iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="AmazonS3FullAccess")],
        )
        state_param.grant_read(function_archive_role)
        state_param.grant_write(function_archive_role)

        factory.lambda_function(
            self,
            function_archive_name,
            factory.get_path([project_name, function_archive_name]),
            f"Lambda function for archiving the {word_map_project_name_comp}.",
            {
                "ACCOUNT_OWNER_ID": factory.get_attr_env_account(self),
                "BUCKET_NAME_SOURCE": s3_bucket_.bucket_name,
                "BUCKET_NAME_DEST_PREFIX": factory.join_sep_score([factory.INNOVAULT_, factory.ARCHIVE_]),
                "STATE_PARAMETER": state_param.parameter_name,
                "ARCHIVE_BYTE_COUNT": archive_byte_count_,
            },
            function_archive_role,
            params_and_secrets_ext=True,
            timeout=Duration.minutes(10),
            events_rules=[
                (
                    factory.events_rule(
                        self,
                        [function_archive_name],
                        f"Trigger Lambda function {function_archive_name} every {cron_week_day} "
                        f"@ {cron_start_hour}:00 UTC.",
                        events.Schedule.cron(
                            week_day=cron_week_day,
                            minute=str(0),
                            hour=str(cron_start_hour),
                        ),
                    ),
                    {},  # Payload
                )
            ],
        )
