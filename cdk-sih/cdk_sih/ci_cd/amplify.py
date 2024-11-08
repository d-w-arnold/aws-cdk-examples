import json

from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_ssm as ssm,
)
from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkAmplifyCiCdStack(Stack):
    def __init__(
        self,
        factory: CdkConstructsFactory,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_kms_key_stack(self, no_trim=True)

        function_name: str = factory.join_sep_empty(
            i.capitalize() for i in [factory.AMPLIFY_, factory.MS_, factory.TEAMS_, factory.NOTIFICATION_]
        )

        # ---------- IAM ----------

        lambda_role: iam.Role = factory.iam_role_lambda(
            self,
            function_name,
            managed_policies=factory.lambda_managed_policies_list(),
            custom_policies=[
                iam.PolicyStatement(
                    actions=[
                        factory.join_sep_colon([factory.AMPLIFY_, i]) for i in ["GetJobs", "ListApps", "ListJobs"]
                    ],
                    resources=[self.format_arn(service=factory.AMPLIFY_, resource=factory.SEP_ASTERISK_)],
                )
            ],
        )

        # ---------- SSM ----------

        # A mapping of all MS Teams Webhook URLS - used by AmplifyMsTeamsNotification Lambda function
        webhook_url_mappings_props: list[str] = [factory.WEBHOOK_, factory.URL_, factory.MAPPINGS_]
        webhook_url_mappings_param: ssm.StringParameter = factory.ssm_string_parameter(
            self,
            webhook_url_mappings_props,
            "A mapping of all MS Teams Webhook URLs for Amplify Notifications.",
            factory.get_path([self.stack_name, factory.join_sep_score(webhook_url_mappings_props)], lead=True),
            json.dumps(factory.lookup_ms_teams(factory.WEBHOOK_URL_AMPLIFY_)),
            data_type=ssm.ParameterDataType.TEXT,
            tier=ssm.ParameterTier.STANDARD,
        )
        webhook_url_mappings_param.grant_read(lambda_role)

        # ---------- Lambda ----------

        self.lambda_function: lambda_.Function = factory.lambda_function(
            self,
            function_name,
            factory.get_path([factory.AMPLIFY_, function_name]),
            "Send Amplify notifications to MS Teams Webhook URL.",
            {"MAPPING_PARAMETER": webhook_url_mappings_param.parameter_name},
            lambda_role,
            params_and_secrets_ext=True,
            timeout=Duration.seconds(10),
        )
        factory.lambda_function_add_permission_invoke_by_sns(self, self.lambda_function, function_name)
