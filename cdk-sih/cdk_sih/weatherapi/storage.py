from aws_cdk import (
    Duration,
    Size,
    Stack,
    aws_events as events,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
)

from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkWeatherapiStorageStack(Stack):
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

        # Cron: "At minute (m) past every (h)th hour."
        event_hour: str = str(3)  # (h)
        event_minute: str = str(4)  # (m)

        # ---------- Secrets Manager ----------

        # WeatherAPI Storage API keys and passwords
        lambda_func_secret_props: list[str] = [factory.LAMBDA_, factory.FUNCTION_, factory.SECRET_]
        self.lambda_func_secret: secretsmanager.ISecret = secretsmanager.Secret.from_secret_attributes(
            scope=self,
            id=factory.get_construct_id(self, lambda_func_secret_props, "ISecret"),
            secret_complete_arn=factory.format_arn_custom(
                self,
                service=factory.SECRETSMANAGER_,
                resource=factory.SECRET_,
                resource_name=factory.get_path(
                    [
                        factory.get_attr_project_name_comp(self),
                        factory.join_sep_score(lambda_func_secret_props + ["mee7QH"]),
                    ]
                ),
            ),  # Manually created AWS Secrets Manager secret
        )

        # ---------- Lambda ----------

        weatherapi_: str = factory.join_sep_empty([factory.WEATHER_, factory.API_])
        function_download_name: str = factory.join_sep_empty(
            [
                factory.DOWNLOAD_.capitalize(),
                getattr(self, factory.WORD_MAP_PROJECT_NAME_),
                getattr(self, factory.WORD_MAP_COMPONENT_),
            ]
        )

        function_download_role: iam.Role = factory.iam_role_lambda(
            self,
            function_download_name,
            managed_policies=factory.lambda_managed_policies_vpc_list()
            + [iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="AmazonS3FullAccess")],
        )
        self.lambda_func_secret.grant_read(function_download_role)

        factory.lambda_function(
            self,
            function_download_name,
            factory.get_path([weatherapi_, function_download_name]),
            f"Lambda function for {factory.get_attr_word_map_project_name_comp(self, inc_deploy_env=False)}.",
            {
                "ACCOUNT_OWNER_ID": factory.get_attr_env_account(self),
                "BUCKET_NAME_DEST_PREFIX": factory.join_sep_score([factory.INNOVAULT_, factory.ARCHIVE_]),
                "WEATHERAPI_KEY_SECRET": self.lambda_func_secret.secret_full_arn,
            },
            function_download_role,
            ephemeral_storage_size=Size.mebibytes(2048),
            layers=[
                factory.lambda_layer_version_base(self, function_download_name),
                factory.lambda_layer_version(
                    self,
                    [function_download_name, weatherapi_, factory.PY_, factory.LAYER_],
                    factory.get_path([weatherapi_, factory.get_file_name_zip([factory.PY_, factory.LAYER_])]),
                    "Lambda layer that contains: weatherapi py modules.",
                ),
            ],
            memory_size=1024,
            timeout=Duration.minutes(15),
            events_rules=[
                (
                    factory.events_rule(
                        self,
                        [function_download_name, event_hour, "hours"],
                        f"Trigger Lambda function {function_download_name} "
                        f"every {event_hour} hours, at minute {event_minute} past the hour.",
                        events.Schedule.cron(
                            minute=event_minute,
                            hour=factory.get_path([factory.SEP_ASTERISK_, event_hour]),
                        ),
                    ),
                    {},  # Payload
                ),
            ],
        )
