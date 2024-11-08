import json

from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_ses as ses,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.mail.base import CdkMailBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkMailMsStack(Stack):
    def __init__(
        self,
        base_stack: CdkMailBaseStack,
        component: str,
        deploy_env: str,
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        project_names_ses_email_templates: list[str],
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta, no_subdomain=True)

        factory.set_attrs_kms_key_stack(self)

        # ---------- SES ----------

        ses_handler_props: list[str] = [factory.SES_.upper(), factory.HANDLER_.capitalize()]
        ses_lambda_func_name: str = factory.get_lambda_func_name(self, ses_handler_props)

        ses_lambda_func_role: iam.Role = factory.iam_role_lambda(
            self,
            ses_lambda_func_name,
            managed_policies=factory.lambda_managed_policies_vpc_list(),
            custom_policies=[
                iam.PolicyStatement(
                    actions=[
                        factory.join_sep_colon([factory.SES_, i])
                        for i in [
                            "SendBulkEmail",
                            "SendBulkTemplatedEmail",
                            "SendEmail",
                            "SendTemplatedEmail",
                        ]
                    ],
                    resources=factory.ALL_RESOURCES,
                ),
            ],
        )

        self.ses_email_templates: dict[str, dict[str, ses.CfnTemplate]] = {}
        ses_email_template_name_prefix: str = factory.join_sep_empty(
            [
                factory.join_sep_score(factory.get_attr_project_name_comp_props(self) + [deploy_env]),
                factory.SEP_UNDER_,
            ]
        )
        project_names_ses_email_template_names: dict[str, list[str]] = {}
        for project_name_ses_email_template in project_names_ses_email_templates:
            templates: dict[str, ses.CfnTemplate] = factory.ses_templates(
                self, project_name=project_name_ses_email_template, template_name_prefix=ses_email_template_name_prefix
            )
            project_names_ses_email_template_names[project_name_ses_email_template] = [
                name for name, _ in templates.items()
            ]
            self.ses_email_templates[project_name_ses_email_template] = templates

        ses_lambda_func_security_groups: list[ec2.SecurityGroup] = [base_stack.ses_lambda_sg]

        self.ses_lambda_func: lambda_.Function = factory.lambda_function(
            self,
            ses_lambda_func_name,
            factory.get_path([project_name, factory.get_lambda_func_name(self, ses_handler_props, code_path=True)]),
            f"{factory.join_sep_empty(ses_handler_props)} Lambda function for {factory.get_attr_word_map_project_name_comp(self)}.",
            {
                "SES_CONFIG_SET_MAPPING": json.dumps(base_stack.mail_users_config_set_names, default=str),
                "SES_EMAIL_IDENTITY_ARN_MAPPING": json.dumps(
                    base_stack.mail_users_verified_mail_users_arns, default=str
                ),
                "SES_EMAIL_TEMPLATE_ARN_FORMAT": factory.format_arn_custom(
                    self, service=factory.SES_, resource=factory.TEMPLATE_
                ),
                "SES_EMAIL_TEMPLATE_MAPPING": json.dumps(project_names_ses_email_template_names, default=str),
                "SES_EMAIL_TEMPLATE_NAME_PREFIX": ses_email_template_name_prefix,
            },
            ses_lambda_func_role,
            vpc_props=(
                factory.get_attr_vpc(self),
                ses_lambda_func_security_groups,
                ec2.SubnetType.PRIVATE_WITH_EGRESS,
            ),
            timeout=Duration.seconds(5),
            async_=True,
        )
