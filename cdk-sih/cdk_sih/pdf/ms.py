import json

from aws_cdk import (
    Duration,
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codestarnotifications as codestar_notifications,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_sns as sns,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.pdf.base import CdkPdfBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkPdfMsStack(Stack):
    def __init__(
        self,
        base_stack: CdkPdfBaseStack,
        component: str,
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
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta, no_subdomain=True)

        factory.set_attrs_codepipeline_stage_action_names(self)
        factory.set_attrs_codestar_connection(self, factory.BITBUCKET_WORKSPACE_SIH_INFR_INN)
        factory.set_attrs_kms_key_stack(self)

        project_name_comp: str = factory.get_attr_project_name_comp(self)
        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self)

        s3_handler_: str = factory.join_sep_empty([factory.S3_.upper(), factory.HANDLER_.capitalize()])
        security_groups: list[ec2.SecurityGroup] = [base_stack.s3_lambda_sg]

        # ---------- CodePipeline ----------

        update_: str = factory.UPDATE_.capitalize()
        lambda_func_update_description: str = f"{word_map_project_name_comp} {update_} Lambda function."
        lambda_func_update_name: str = factory.get_lambda_func_name(self, [update_])

        lambda_func_update_role: iam.Role = factory.iam_role_lambda(
            self,
            lambda_func_update_name,
            managed_policies=factory.lambda_managed_policies_vpc_list(),
        )
        factory.get_attr_kms_key_stack(self).grant(
            lambda_func_update_role, factory.join_sep_colon([factory.KMS_, "CreateGrant"])
        )
        factory.get_attr_kms_key_stack(self).grant_encrypt_decrypt(lambda_func_update_role)

        lambda_func_update: lambda_.Function = factory.lambda_function(
            self,
            lambda_func_update_name,
            factory.get_path([project_name, factory.get_lambda_func_name(self, [update_], code_path=True)]),
            lambda_func_update_description,
            {},
            lambda_func_update_role,
            vpc_props=(factory.get_attr_vpc(self), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
            timeout=Duration.seconds(60),
        )

        project_role: iam.Role = factory.iam_role_codebuild(self, project_name_comp)
        lambda_func_update.grant_invoke(project_role)

        s3_lambda_func_name: str = factory.get_lambda_func_name(self, [s3_handler_])

        codepipeline_pipeline_project_names: list[str] = [project_name_comp]
        self.codepipeline_pipelines: dict[str, codepipeline.Pipeline] = {
            p_deploy_env: factory.codepipeline_pipeline(
                self,
                p,
                codebuild.Project(
                    scope=self,
                    id=factory.get_construct_id(
                        self,
                        [factory.CODEBUILD_],
                        "Project",
                    ),
                    build_spec=factory.file_yaml_safe_load_codebuild_buildspec(
                        factory.get_buildspec_path(self, project_name_comp)
                    ),
                    cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER),
                    check_secrets_in_plain_text_env_variables=True,
                    description=f"CodeBuild project for {word_map_project_name_comp}, "
                    f"to generate latest {s3_handler_} Docker image.",
                    environment=factory.codebuild_build_environment(project_name_comp, base_ignore=True),
                    environment_variables={
                        k: codebuild.BuildEnvironmentVariable(value=v)
                        for k, v in {
                            "AWS_ACCOUNT_ID": factory.get_attr_env_account(self),
                            "AWS_DEFAULT_REGION": factory.get_attr_env_region(self),
                            "ORGANISATION": factory.organisation,
                            "PROJECT_NAME": p,
                            "IMAGE_TAG": deploy_env,
                            "BASE_PROJECT_NAME": "lambda-libreoffice-base",
                            "BASE_IMAGE_TAG": "7.6-node18-x86_64",
                            "LAMBDA_FUNC_SOURCE": factory.get_path(
                                [
                                    project_name,
                                    factory.join_sep_empty(
                                        [s3_handler_]
                                        + [i.capitalize() for i in factory.get_attr_project_name_comp_props(self)]
                                    ),
                                ]
                            ),
                            "S3HANDLER_UPDATE_FUNCTION": lambda_func_update.function_name,
                            "LAMBDA_FUNC_NAMES": json.dumps([s3_lambda_func_name]),
                        }.items()
                        if v
                    },
                    grant_report_group_permissions=False,
                    logging=codebuild.LoggingOptions(
                        cloud_watch=codebuild.CloudWatchLoggingOptions(
                            log_group=factory.logs_log_group(
                                self,
                                [factory.CODEBUILD_, factory.PROJECT_],
                                factory.get_path([factory.log_groups[factory.CODEBUILD_], p_deploy_env]),
                            )
                        )
                    ),
                    project_name=p_deploy_env,
                    queued_timeout=Duration.hours(8),
                    role=project_role,
                    security_groups=security_groups,
                    subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                    timeout=Duration.minutes(30),
                    vpc=factory.get_attr_vpc(self),
                ),
                factory.iam_role_codepipeline(self, project_name_comp),
                repo=base_stack.codepipeline_source_repo,
                branch=base_stack.codepipeline_source_branch,
                trigger_on_push=False,
                deploy=False,
            )
            for p in codepipeline_pipeline_project_names
            if (p_deploy_env := factory.join_sep_score([p, deploy_env]))
        }

        self.sns_topics: dict[str, sns.Topic] = {}
        self.codestar_notifications_notification_rules: list[codestar_notifications.NotificationRule] = []
        for p in codepipeline_pipeline_project_names:
            self.sns_topics[p] = factory.sns_topic_codestar_notifications_sns(self, p)
            self.codestar_notifications_notification_rules.append(
                factory.codestar_notifications_notification_rule(self, p)
            )

        # ---------- Lambda ----------

        self.pdf_lambda_func: lambda_.DockerImageFunction = factory.lambda_docker_image_function(
            self,
            s3_lambda_func_name,
            base_stack.repo,
            f"{word_map_project_name_comp} {s3_handler_} Lambda function.",
            {
                "HOME": "/tmp",  # Is also set in the base Dockerfile
                # TODO: (NEXT) Consider updating Lambda function to set AWS S3 tags for the s3.upload(),
                #  based on the 'dest_bucket' set in the event payload.
                # "TAGS": json.dumps(factory.get_s3_bucket_tags(self), default=str),
            },
            factory.iam_role_lambda(
                self,
                s3_lambda_func_name,
                managed_policies=factory.lambda_managed_policies_vpc_list(),
                custom_policies=[
                    factory.iam_policy_statement_s3_get_objects(self, s3_bucket_prefixes=[factory.SEP_EMPTY_]),
                    factory.iam_policy_statement_s3_list_buckets(self, s3_bucket_prefixes=[factory.SEP_EMPTY_]),
                    factory.iam_policy_statement_s3_put_objects(self, s3_bucket_prefixes=[factory.SEP_EMPTY_]),
                    factory.iam_policy_statement_kms_key_encrypt_decrypt(self),
                ],
            ),
            vpc_props=(factory.get_attr_vpc(self), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
            timeout=Duration.seconds(60),
            memory_size=3072,  # in MiB
        )

        lambda_func_update_role.add_to_policy(
            statement=factory.iam_policy_statement_lambda_update_function_code(
                lambda_func_arns=[self.pdf_lambda_func.function_arn]
            )
        )
