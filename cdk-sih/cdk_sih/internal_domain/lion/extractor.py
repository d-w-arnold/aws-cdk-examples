import json

from aws_cdk import (
    Duration,
    Size,
    Stack,
    aws_codebuild as codebuild,
    aws_ec2 as ec2,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_ssm as ssm,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.lion.base import CdkLionBaseStack
from cdk_sih.internal_domain.lion.cache import CdkLionCacheStack
from cdk_sih.internal_domain.lion.events import CdkLionEventsStack
from cdk_sih.internal_domain.lion.processor import CdkLionProcessorStack
from cdk_sih.internal_domain.lion.storage import CdkLionStorageStack
from cdk_sih.internal_domain.pypi.package.base import CdkPypiPackageBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkLionExtractorStack(Stack):
    def __init__(
        self,
        base_stack: CdkLionBaseStack,
        cache_regions: dict[str, list[str]],
        cache_stack: CdkLionCacheStack,
        component: str,
        deploy_env: str,
        lion_global_region: str,
        env_meta: dict,
        events_stack: CdkLionEventsStack,
        factory: CdkConstructsFactory,
        project_name: str,
        pypi_package_base_stack: CdkPypiPackageBaseStack,
        storage_stack: CdkLionStorageStack,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        self.add_dependency(events_stack)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta)

        factory.set_attrs_codestar_connection(self, factory.BITBUCKET_WORKSPACE_SIH_INFR_INN)
        factory.set_attrs_kms_key_stack(self)

        project_name_comp: str = factory.get_attr_project_name_comp(self)
        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self, inc_comp=False)

        component_alt: str = base_stack.extractor_
        word_map_component_alt: str = factory.lookup_word_map(component_alt)

        is_prod: bool = getattr(self, factory.DEPLOY_ENV_PROD_)
        security_groups: list[ec2.SecurityGroup] = [base_stack.ec_redis_extractor_lambda_sg]

        project_name_comp_props: list[str] = factory.get_attr_project_name_comp_props(self)

        # ---------- SSM ----------

        # LION Micro-service Cache regions meta(s)
        #  (NB. each parameter manually created in AWS Systems Manager Parameter Store)

        cache_regions_meta_props: list[str] = [factory.CACHE_, factory.REGIONS_, factory.META_]
        cache_regions_meta_params: dict[str, ssm.IStringParameter] = {
            i: ssm.StringParameter.from_string_parameter_name(
                scope=self,
                id=factory.get_construct_id(self, cache_regions_meta_props + [i.lower()], "IStringParameter"),
                string_parameter_name=factory.get_path(
                    [project_name_comp, factory.join_sep_score(cache_regions_meta_props), i],
                    lead=True,
                ),
            )
            for i in list(cache_regions.keys())
        }

        # LION Micro-service extractor FILENAMES_INFO meta
        #  (NB. each parameter manually created in AWS Systems Manager Parameter Store)

        filenames_info_props: list[str] = [factory.FILENAMES_, factory.INFO_]
        filenames_info_: str = factory.join_sep_under([i.upper() for i in filenames_info_props])
        filenames_info_param: ssm.IStringParameter = ssm.StringParameter.from_string_parameter_name(
            scope=self,
            id=factory.get_construct_id(self, filenames_info_props, "IStringParameter"),
            string_parameter_name=factory.get_path([project_name_comp, component_alt, filenames_info_], lead=True),
        )

        # ---------- Lambda ----------

        pypi_package_name: str = base_stack.pypi_package_name
        pypi_package_s3_bucket_name: str = base_stack.pypi_package_s3_bucket_name

        custom_policies_pypi_package_s3_bucket_read: list[iam.PolicyStatement] = [
            factory.iam_policy_statement_s3_get_objects(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
            factory.iam_policy_statement_s3_list_buckets(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
            factory.iam_policy_statement_s3_put_objects(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
        ]
        custom_policies_codebuild_project: list[iam.PolicyStatement] = [
            factory.iam_policy_statement_s3_put_objects(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
            iam.PolicyStatement(
                actions=[
                    factory.join_sep_colon([factory.CODEBUILD_, i])
                    for i in [
                        "BatchPutTestCases",
                        "CreateReport",
                        "CreateReportGroup",
                        "UpdateReport",
                    ]
                ]
                + [
                    factory.join_sep_colon([factory.LOGS_, i])
                    for i in [
                        "CreateLogGroup",
                        "CreateLogStream",
                        "PutLogEvents",
                    ]
                ],
                resources=factory.ALL_RESOURCES,
            ),
        ]

        extractor_rule: events.Rule = events.Rule(
            scope=self,
            id=factory.get_construct_id(self, [component_alt], "Rule"),
            enabled=True,
            # event_bus=,  # Default: - The default event bus.
            # schedule=,  # Default: - None.
            # targets=[],  # Default: - No targets.
            # cross_stack_scope=,  # Default: - none (the main scope will be used, even for cross-stack Events)
            description="Trigger all Extractor Lambda function(s), based on events from the S3 Param Data bucket.",
            event_pattern=factory.events_event_pattern_s3_object_created(storage_stack.s3_param_data_bucket.bucket_arn),
            rule_name=factory.get_construct_name(self, [component_alt], underscore=True),
        )

        pypi_package_s3_bucket_obj_key: str = factory.get_path(
            [
                factory.LAYERS_,
                component_alt,
                deploy_env,
                factory.get_file_name_zip([factory.PY_, factory.LAYER_]),
            ]
        )

        lambda_func_names: list[str] = []
        lambda_func_arns: list[str] = []
        for cache_region_code, lambda_func_name in {
            i: factory.get_lambda_func_name(self, [word_map_component_alt, i.capitalize()])
            for i in cache_regions_meta_params.keys()
        }.items():
            lambda_func_role: iam.Role = factory.iam_role_lambda(
                self,
                lambda_func_name,
                managed_policies=factory.lambda_managed_policies_vpc_list(),
                custom_policies=custom_policies_pypi_package_s3_bucket_read
                + [
                    factory.iam_policy_statement_kmy_key_decrypt(self),
                    factory.iam_policy_statement_secretsmanager_get_secret_value(
                        self, secret_full_arn=cache_stack.ec_redis_auth_secret.secret_full_arn
                    ),
                ],
            )
            factory.get_attr_kms_key_stack(storage_stack).grant_encrypt_decrypt(lambda_func_role)
            storage_stack.s3_param_data_bucket.grant_read_write(lambda_func_role)

            cache_square_source_names: list[str] = cache_regions[cache_region_code]
            lambda_func: lambda_.Function = factory.lambda_function(
                self,
                lambda_func_name,
                factory.get_path(
                    [
                        project_name,
                        component_alt,
                        factory.join_sep_empty(
                            [word_map_component_alt, factory.EXTRACT_.capitalize()]
                            + [i.capitalize() for i in project_name_comp_props]
                        ),
                    ]
                ),
                f"{word_map_project_name_comp} {word_map_component_alt} {cache_region_code.capitalize()} Lambda function.",
                {
                    "ACCOUNT_OWNER_ID": factory.get_attr_env_account(self),
                    "LION_GLOBAL_AWS_REGION": lion_global_region,
                    "PYPI_PACKAGE_S3_BUCKET_NAME": pypi_package_s3_bucket_name,
                    "PYPI_PACKAGE_S3_BUCKET_BRANCH": factory.MAIN_ if is_prod else factory.DEV_,
                    "CACHE_SQUARE_CODE": cache_region_code,
                    "CACHE_SQUARE_SOURCE_NAMES": json.dumps(cache_square_source_names),
                    "CACHE_SQUARE_META": cache_regions_meta_params[cache_region_code].string_value,
                    "REDIS_HOST": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_address,
                    "REDIS_PORT": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_port,
                    "REDIS_SSL": json.dumps(True),
                    "REDIS_PW_SECRET": cache_stack.ec_redis_auth_secret.secret_full_arn,
                    "REDIS_DECODE_RESPONSES": json.dumps(True),
                    filenames_info_: filenames_info_param.string_value,
                },
                lambda_func_role,
                vpc_props=(factory.get_attr_vpc(self), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
                layers=[factory.lambda_layer_version_base(self, lambda_func_name)],
                params_and_secrets_ext=True,
                timeout=Duration.seconds(60 * 15),
                ephemeral_storage_size=Size.mebibytes(
                    1024 if CdkLionProcessorStack.HIMAWARI9_ in cache_square_source_names else 512
                ),
                memory_size=2048 if CdkLionProcessorStack.HIMAWARI9_ in cache_square_source_names else 768,  # in MiB
            )
            lambda_func_names.append(lambda_func.function_name)
            lambda_func_arns.append(lambda_func.function_arn)

            extractor_rule.add_target(
                target=targets.LambdaFunction(
                    handler=lambda_func,
                    # event=,  # Default: the entire EventBridge event
                    # dead_letter_queue=,  # Default: - no dead-letter queue  # TODO: (OPTIONAL) Add an SQS queue to be used as DLQ ?
                    max_event_age=Duration.hours(24),
                    retry_attempts=185,
                )
            )

        custom_events_: str = factory.join_sep_score([factory.CUSTOM_, factory.EVENTS_])
        extractor_rule.add_target(
            target=targets.CloudWatchLogGroup(
                log_group=factory.logs_log_group(
                    self,
                    [component_alt, custom_events_],
                    factory.get_path(
                        [
                            factory.log_groups[factory.EVENTS_],
                            factory.join_sep_score(project_name_comp_props + [deploy_env, component_alt]),
                            custom_events_,
                        ]
                    ),
                ),
                # log_event=,  # Default: - the entire EventBridge event
                # dead_letter_queue=,  # Default: - no dead-letter queue  # TODO: (OPTIONAL) Add an SQS queue to be used as DLQ ?
                max_event_age=Duration.hours(24),
                retry_attempts=185,
            )
        )

        layer_: str = factory.LAYER_.capitalize()
        lambda_func_layer_description: str = (
            f"{word_map_project_name_comp} {word_map_component_alt} {layer_} Lambda function."
        )
        lambda_func_layer_name: str = factory.get_lambda_func_name(self, [word_map_component_alt, layer_])

        lambda_func_layer_role: iam.Role = factory.iam_role_lambda(
            self,
            lambda_func_layer_name,
            managed_policies=factory.lambda_managed_policies_vpc_list(),
            custom_policies=custom_policies_pypi_package_s3_bucket_read
            + [
                iam.PolicyStatement(
                    actions=[
                        factory.join_sep_colon([factory.LAMBDA_, i])
                        for i in [
                            "GetFunctionConfiguration",
                            "GetLayerVersion",
                            "PublishLayerVersion",
                            "UpdateFunctionConfiguration",
                        ]
                    ],
                    resources=[factory.format_arn_custom(self, service=factory.LAMBDA_, resource=factory.LAYER_)]
                    + lambda_func_arns
                    + [factory.get_params_and_secrets_ext_arn()],
                ),
            ],
        )
        factory.get_attr_kms_key_stack(self).grant_encrypt_decrypt(lambda_func_layer_role)

        lambda_func_layer: lambda_.Function = factory.lambda_function(
            self,
            lambda_func_layer_name,
            factory.get_path(
                [
                    project_name,
                    component_alt,
                    factory.get_lambda_func_name(self, [word_map_component_alt, layer_], code_path=True),
                ]
            ),
            lambda_func_layer_description,
            {
                "BUCKET_NAME": pypi_package_s3_bucket_name,
                "BUCKET_OBJ_KEY": pypi_package_s3_bucket_obj_key,
                "LAMBDA_FUNCTION_EXTRACT": json.dumps(lambda_func_names),
                "LAMBDA_LAYER_NAME": factory.join_sep_score(
                    [lambda_func_layer_name, pypi_package_name, factory.PY_, factory.LAYER_]
                ),
                "LAMBDA_LAYER_DESC": f"Lambda layer that contains: {pypi_package_name} py modules.",
                "LAMBDA_LAYER_RUNTIMES": factory.lambda_runtime_python_3_9(str_=True),
                "LAMBDA_LAYER_ARCHITECTURES": factory.lambda_architecture_x86_64(str_=True),
            },
            lambda_func_layer_role,
            vpc_props=(factory.get_attr_vpc(self), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
            timeout=Duration.seconds(60),
        )

        project_role: iam.Role = factory.iam_role_codebuild(
            self, factory.join_sep_score(project_name_comp_props + [deploy_env, component_alt]), pypi_server_access=True
        )
        lambda_func_layer.grant_invoke(project_role)
        for policy_statement in custom_policies_codebuild_project:
            project_role.add_to_policy(statement=policy_statement)

        codebuild.Project(
            scope=self,
            id=factory.get_construct_id(
                self,
                [component_alt, factory.CODEBUILD_],
                "Project",
            ),
            build_spec=factory.file_yaml_safe_load_codebuild_buildspec(
                factory.get_buildspec_path(self, factory.join_sep_score([project_name, factory.LAYER_]))
            ),
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER),
            check_secrets_in_plain_text_env_variables=True,
            description=f"CodeBuild project for {word_map_project_name_comp}, "
            f"to generate latest {word_map_component_alt} package Lambda layer.",
            environment=factory.codebuild_build_environment(project_name_comp, base_ignore=True),
            environment_variables={
                k: codebuild.BuildEnvironmentVariable(value=v)
                for k, v in {
                    "AWS_ACCOUNT_ID": factory.get_attr_env_account(self),
                    "AWS_DEFAULT_REGION": factory.get_attr_env_region(self),
                    "PYPI_PACKAGE_NAME": pypi_package_name,
                    "BUCKET_NAME": pypi_package_s3_bucket_name,
                    "BUCKET_OBJ_KEY": pypi_package_s3_bucket_obj_key,
                    "LAMBDA_LAYER_FUNCTION": lambda_func_layer.function_name,
                    "SIH_LION_EXTRAS": f"[{factory.CACHE_}]",
                    "SIH_LION_VERSION_META_PARAMETER": pypi_package_base_stack.version_meta_param_names[
                        pypi_package_name
                    ],
                }.items()
                if v
            },
            grant_report_group_permissions=False,
            logging=codebuild.LoggingOptions(
                cloud_watch=codebuild.CloudWatchLoggingOptions(
                    log_group=factory.logs_log_group(
                        self,
                        [component_alt, factory.CODEBUILD_, factory.PROJECT_],
                        factory.get_path(
                            [
                                factory.log_groups[factory.CODEBUILD_],
                                factory.join_sep_score(project_name_comp_props + [deploy_env, component_alt]),
                            ]
                        ),
                    )
                )
            ),
            project_name=factory.join_sep_score(project_name_comp_props + [deploy_env, component_alt]),
            queued_timeout=Duration.hours(8),
            role=project_role,
            security_groups=security_groups,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            timeout=Duration.minutes(30),
            vpc=factory.get_attr_vpc(self),
        )
