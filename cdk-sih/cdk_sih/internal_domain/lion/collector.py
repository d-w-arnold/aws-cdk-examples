import json

from aws_cdk import (
    Duration,
    Size,
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codestarnotifications as codestar_notifications,
    aws_ec2 as ec2,
    aws_events as events,
    aws_iam as iam,
    aws_kms as kms,
    aws_lambda as lambda_,
    aws_secretsmanager as secretsmanager,
    aws_sns as sns,
    aws_ssm as ssm,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.lion.base import CdkLionBaseStack
from cdk_sih.internal_domain.lion.storage import CdkLionStorageStack
from cdk_sih.internal_domain.pypi.package.base import CdkPypiPackageBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkLionCollectorStack(Stack):
    CAMS_: str = "cams"
    METOFFICE_: str = "metoffice"

    def __init__(
        self,
        base_stack: CdkLionBaseStack,
        component: str,
        deploy_env: str,
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        pypi_package_base_stack: CdkPypiPackageBaseStack,
        storage_stack: CdkLionStorageStack,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta)

        factory.set_attrs_codepipeline_stage_action_names(self)
        factory.set_attrs_codestar_connection(self, factory.BITBUCKET_WORKSPACE_SIH_INFR_INN)
        factory.set_attrs_kms_key_stack(self)

        self.env_meta: dict = env_meta

        project_name_comp: str = factory.get_attr_project_name_comp(self)
        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self, inc_comp=False)

        component_alt: str = base_stack.collector_
        word_map_component_alt: str = factory.lookup_word_map(component_alt)

        data_sources: list[str] = [self.CAMS_]  # [self.CAMS_, self.METOFFICE_]

        security_groups: list[ec2.SecurityGroup] = [base_stack.collector_lambda_sg]

        # ---------- Secrets Manager ----------

        # LION Mirco-service ECS container API keys and passwords
        collector_secret: secretsmanager.ISecret = secretsmanager.Secret.from_secret_attributes(
            scope=self,
            id=factory.get_construct_id(self, [component_alt, factory.SECRET_], "ISecret"),
            secret_complete_arn=factory.format_arn_custom(
                self,
                service=factory.SECRETSMANAGER_,
                resource=factory.SECRET_,
                resource_name=factory.get_path(
                    [
                        project_name_comp,
                        factory.join_sep_score([component_alt, factory.SECRET_, "UFoT53"]),
                    ]
                ),
            ),  # Manually created AWS Secrets Manager secret
        )

        # ---------- SSM ----------

        # LION Global data sources ATMOS_PARAMS meta
        #  (NB. each parameter manually created in AWS Systems Manager Parameter Store)

        atmos_params_props: list[str] = [factory.ATMOS_, factory.PARAMS_]
        atmos_params_: str = factory.join_sep_under([i.upper() for i in atmos_params_props])
        atmos_params_params: dict[str, ssm.IStringParameter] = {
            i: ssm.StringParameter.from_string_parameter_name(
                scope=self,
                id=factory.get_construct_id(self, atmos_params_props + [i], "IStringParameter"),
                string_parameter_name=factory.get_path([project_name_comp, i, atmos_params_], lead=True),
            )
            for i in data_sources
        }

        # ---------- CodePipeline ----------

        lion_collector: str = factory.join_sep_score([project_name, component_alt])

        buildspec_path: str = factory.get_path(
            [
                factory.sub_paths[factory.CODEPIPELINE_],
                base_stack.lion_producer.replace(factory.SEP_SCORE_, factory.SEP_FW_, 1),
                factory.get_file_name_yml([factory.BUILDSPEC_]),
            ]
        )

        project_role: iam.Role = factory.iam_role_codebuild(
            self,
            factory.join_sep_score([lion_collector, deploy_env]),
            pypi_server_access=True,
            params_and_secrets_ext_arn=factory.get_params_and_secrets_ext_arn(),
        )
        pipeline_role: iam.Role = factory.iam_role_codepipeline(self, lion_collector)

        update_: str = factory.UPDATE_.capitalize()
        lambda_func_update_description: str = (
            f"{word_map_project_name_comp} {word_map_component_alt} {update_} Lambda function."
        )
        lambda_func_update_name: str = factory.get_lambda_func_name(self, [word_map_component_alt, update_])

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
            factory.get_path(
                [
                    project_name,
                    base_stack.producer_,
                    factory.get_lambda_func_name(self, [base_stack.producer_.capitalize(), update_], code_path=True),
                ]
            ),
            lambda_func_update_description,
            {},
            lambda_func_update_role,
            vpc_props=(factory.get_attr_vpc(self), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
            timeout=Duration.seconds(60),
        )
        lambda_func_update.grant_invoke(project_role)

        data_source_lambda_func_name: dict[str, str] = {
            i: factory.get_lambda_func_name(self, [word_map_component_alt, i.capitalize()]) for i in data_sources
        }

        codepipeline_pipeline_project_names: list[str] = [lion_collector]
        self.codepipeline_pipelines: dict[str, codepipeline.Pipeline] = {
            p_deploy_env: factory.codepipeline_pipeline(
                self,
                p,
                codebuild.Project(
                    scope=self,
                    id=factory.get_construct_id(
                        self,
                        [component_alt, factory.CODEBUILD_],
                        "Project",
                    ),
                    build_spec=factory.file_yaml_safe_load_codebuild_buildspec(buildspec_path),
                    cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER),
                    check_secrets_in_plain_text_env_variables=True,
                    description=f"CodeBuild project for {word_map_project_name_comp}, "
                    f"to generate latest {word_map_component_alt} Docker image.",
                    environment=factory.codebuild_build_environment(project_name_comp, base_ignore=True),
                    environment_variables={
                        k: codebuild.BuildEnvironmentVariable(value=v)
                        for k, v in {
                            "AWS_ACCOUNT_ID": factory.get_attr_env_account(self),
                            "AWS_DEFAULT_REGION": factory.get_attr_env_region(self),
                            "ORGANISATION": factory.organisation,
                            "PROJECT_NAME": p,
                            "IMAGE_TAG": deploy_env,
                            "BASE_PROJECT_NAME": factory.join_sep_score([base_stack.lion_producer, factory.BIN_]),
                            "BASE_IMAGE_TAG": base_stack.image_tag,
                            "SIH_LION_EXTRAS": f"[{component_alt}s]",
                            "SIH_LION_VERSION_META_PARAMETER": pypi_package_base_stack.version_meta_param_names[
                                base_stack.pypi_package_name
                            ],
                            "LAMBDA_FUNC_SOURCE": factory.get_path(
                                [
                                    project_name,
                                    component_alt,
                                    factory.join_sep_empty(
                                        [word_map_component_alt, factory.COLLECT_.capitalize()]
                                        + [i.capitalize() for i in factory.get_attr_project_name_comp_props(self)]
                                    ),
                                ]
                            ),
                            "PRODUCER_UPDATE_FUNCTION": lambda_func_update.function_name,
                            "LAMBDA_FUNC_NAMES": json.dumps(list(data_source_lambda_func_name.values())),
                            "PARAMS_AND_SECRETS_EXT_ARN": factory.get_params_and_secrets_ext_arn(),
                        }.items()
                        if v
                    },
                    grant_report_group_permissions=False,
                    logging=codebuild.LoggingOptions(
                        cloud_watch=codebuild.CloudWatchLoggingOptions(
                            log_group=factory.logs_log_group(
                                self,
                                [component_alt, factory.CODEBUILD_, factory.PROJECT_],
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
                pipeline_role,
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

        pypi_package_s3_bucket_name: str = base_stack.pypi_package_s3_bucket_name

        custom_policies_pypi_package_s3_bucket_read: list[iam.PolicyStatement] = [
            factory.iam_policy_statement_s3_get_objects(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
            factory.iam_policy_statement_s3_list_buckets(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
            factory.iam_policy_statement_s3_put_objects(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
        ]

        lion_collector_hours: list[int] = factory.schedules.get_hours(
            start_hour=10, end_hour=11
        ) + factory.schedules.get_hours(start_hour=22, end_hour=23)

        storage_kms_key: kms.Key = factory.get_attr_kms_key_stack(storage_stack)

        lambda_func_arns: list[str] = []
        for data_source_name, lambda_func_name in data_source_lambda_func_name.items():
            lambda_func_role: iam.Role = factory.iam_role_lambda(
                self,
                lambda_func_name,
                managed_policies=factory.lambda_managed_policies_vpc_list(),
                custom_policies=custom_policies_pypi_package_s3_bucket_read,
            )
            storage_kms_key.grant_encrypt_decrypt(lambda_func_role)
            storage_stack.s3_param_data_bucket.grant_read_write(lambda_func_role)
            collector_secret.grant_read(lambda_func_role)

            lambda_func: lambda_.DockerImageFunction = factory.lambda_docker_image_function(
                self,
                lambda_func_name,
                base_stack.repo_collector,
                f"{word_map_project_name_comp} {word_map_component_alt} {data_source_name.capitalize()} Lambda function.",
                {
                    **{
                        "ACCOUNT_OWNER_ID": factory.get_attr_env_account(self),
                        "COLLECTOR_SECRET": collector_secret.secret_full_arn,
                        "S3_PARAM_DATA_BUCKET_NAME": storage_stack.s3_param_data_bucket.bucket_name,
                        "S3_PARAM_DATA_BUCKET_OBJ_PREFIX": factory.get_path([component_alt, data_source_name]),
                        "CHECKSUM_ALGORITHM": storage_stack.s3_checksum_algorithm,
                        "KMS_MASTER_KEY_ID": storage_kms_key.key_arn,
                        "ENCRYPTION_CONTEXT_KEY": storage_stack.s3_encryption_context_key,
                        "CDK_STACK_NAME": storage_stack.s3_cdk_stack_name,
                        "TAGS": json.dumps(factory.get_s3_bucket_tags(self), default=str),
                        "SOURCE_NAME": data_source_name,
                        "SOURCE_MODULE_NAME": factory.join_sep_dot(
                            [f"{component_alt}s", factory.join_sep_under([data_source_name, component_alt])]
                        ),
                        "SOURCE_CLASS_NAME": factory.join_sep_empty([data_source_name.upper(), word_map_component_alt]),
                        atmos_params_: atmos_params_params[data_source_name].string_value,
                    },
                    **factory.lambda_function_kwargs_params_and_secrets(to_string=True),
                },
                lambda_func_role,
                vpc_props=(factory.get_attr_vpc(self), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
                timeout=Duration.seconds(60 * 15),
                ephemeral_storage_size=Size.mebibytes(4096),
                memory_size=512,  # in MiB
                events_rules=[
                    (
                        factory.events_rule(
                            self,
                            [lambda_func_name, i],
                            f"Trigger Lambda function {lambda_func_name} "
                            f"every day @ {i} UTC{factory.schedules.utc_offset}.",
                            events.Schedule.cron(
                                minute=str(0),
                                hour=i,
                            ),
                        ),
                        {},  # Payload
                    )
                    for i in lion_collector_hours
                ],
            )
            lambda_func_arns.append(lambda_func.function_arn)

        lambda_func_update_role.add_to_policy(
            statement=factory.iam_policy_statement_lambda_update_function_code(lambda_func_arns=lambda_func_arns)
        )
