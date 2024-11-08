import json
from datetime import datetime, timedelta, timezone

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Size,
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codestarnotifications as codestar_notifications,
    aws_ec2 as ec2,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_kms as kms,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_sns as sns,
    aws_ssm as ssm,
    aws_stepfunctions as stepfunctions,
    aws_stepfunctions_tasks as stepfunctions_tasks,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.lion.base import CdkLionBaseStack
from cdk_sih.internal_domain.lion.storage import CdkLionStorageStack
from cdk_sih.internal_domain.pypi.package.base import CdkPypiPackageBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkLionProcessorStack(Stack):
    _GOES_: str = "goes"
    _HIMAWARI_: str = "himawari"
    _MSG_: str = "msg"

    GOES16_: str = f"{_GOES_}16"  # East
    GOES18_: str = f"{_GOES_}18"  # West
    HIMAWARI9_: str = f"{_HIMAWARI_}9"
    MSG0DEG_: str = f"{_MSG_}0deg"
    MSGIODC_: str = f"{_MSG_}iodc"

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

        self.wait_duration: int = 30

        project_name_comp: str = factory.get_attr_project_name_comp(self)
        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self, inc_comp=False)

        cap_project_name_comp_props: list[str] = [
            i.capitalize() for i in factory.get_attr_project_name_comp_props(self)
        ]

        component_alt: str = base_stack.processor_
        word_map_component_alt: str = factory.lookup_word_map(component_alt)
        word_map_component_alt_current: str = word_map_component_alt[:-2]
        word_map_component_alt_past: str = f"{word_map_component_alt_current}ed"

        sat_data_source_families: dict[str, str] = {
            self.GOES16_: self._GOES_,
            self.GOES18_: self._GOES_,
            self.HIMAWARI9_: self._HIMAWARI_,
            self.MSG0DEG_: self._MSG_,
            self.MSGIODC_: self._MSG_,
        }

        noaa_: str = "noaa"
        noaa_public_: str = factory.join_sep_score([noaa_, factory.PUBLIC_])
        eumetsat_: str = "eumetsat"
        clm_: str = "clm"
        rad_: str = "rad"

        base_station_key: str = "base"
        sat_data_source_folder_key: str = "folder"
        sat_data_source_filter_key: str = "filter"
        sat_data_source_num_files_key: str = factory.join_sep_score(["num", "files"])
        sat_data_source_reader_key: str = "reader"

        sat_data_sources_meta: dict[str, dict] = {
            # self.GOES16_: {
            #     rad_: {
            #         sat_data_source_folder_key: "ABI-L1b-RadF",
            #         sat_data_source_filter_key: "M6C02",
            #         sat_data_source_num_files_key: 1,
            #         sat_data_source_reader_key: "abi_l1b",
            #     },
            #     clm_: {
            #         sat_data_source_folder_key: "ABI-L2-ACMF",
            #         sat_data_source_filter_key: None,
            #         sat_data_source_num_files_key: 1,
            #         sat_data_source_reader_key: "abi_l2_nc",
            #     },
            # },
            # self.GOES18_: {
            #     rad_: {
            #         sat_data_source_folder_key: "ABI-L1b-RadF",
            #         sat_data_source_filter_key: "M6C02",
            #         sat_data_source_num_files_key: 1,
            #         sat_data_source_reader_key: "abi_l1b",
            #     },
            #     clm_: {
            #         sat_data_source_folder_key: "ABI-L2-ACMF",
            #         sat_data_source_filter_key: None,
            #         sat_data_source_num_files_key: 1,
            #         sat_data_source_reader_key: "abi_l2_nc",
            #     },
            # },
            self.HIMAWARI9_: {
                rad_: {
                    sat_data_source_folder_key: "AHI-L1b-FLDK",
                    sat_data_source_filter_key: "B03",
                    sat_data_source_num_files_key: 10,
                    sat_data_source_reader_key: "ahi_hsd",
                },
                clm_: {
                    sat_data_source_folder_key: "AHI-L2-FLDK-Clouds",
                    sat_data_source_filter_key: "CMSK",
                    sat_data_source_num_files_key: 1,
                    sat_data_source_reader_key: None,
                },
            },
            self.MSG0DEG_: {
                base_station_key: True,
                rad_: {
                    sat_data_source_num_files_key: 42,
                    sat_data_source_reader_key: "seviri_l1b_hrit",
                },
                clm_: {
                    sat_data_source_num_files_key: 1,
                    sat_data_source_reader_key: None,
                },
            },
            # self.MSGIODC_: {
            #     base_station_key: True,
            #     rad_: {
            #         sat_data_source_num_files_key: 42,
            #         sat_data_source_reader_key: "seviri_l1b_hrit",
            #     },
            #     clm_: {
            #         sat_data_source_num_files_key: 1,
            #         sat_data_source_reader_key: None,
            #     },
            # },
        }

        is_prod: bool = getattr(self, factory.DEPLOY_ENV_PROD_)
        sat_data_services: list[str] = [clm_, rad_]  # The data service(s), for each data source.
        security_groups: list[ec2.SecurityGroup] = [base_stack.processor_lambda_sg]

        s3_sat_data_bucket: s3.IBucket = base_stack.s3_sat_data_bucket

        processor_step_available: str = base_stack.processor_step_available
        processor_step_latest: str = base_stack.processor_step_latest
        processor_step_process: str = base_stack.processor_step_process

        # ---------- SSM ----------

        # LION Global sat data sources SOURCE_SYSTEM_OBJS meta
        #  (NB. each parameter manually created in AWS Systems Manager Parameter Store)

        source_system_objs_props: list[str] = [factory.SOURCE_, factory.SYSTEM_, factory.OBJS_]
        source_system_objs_: str = factory.join_sep_under([i.upper() for i in source_system_objs_props])
        source_system_objs_params: dict[str, ssm.IStringParameter] = {
            k: ssm.StringParameter.from_string_parameter_name(
                scope=self,
                id=factory.get_construct_id(self, source_system_objs_props + [k], "IStringParameter"),
                string_parameter_name=factory.get_path([project_name_comp, k, source_system_objs_], lead=True),
            )
            for k, _ in sat_data_sources_meta.items()
        }

        # LION Global sat data sources FILENAMES_INFO meta
        #  (NB. each parameter manually created in AWS Systems Manager Parameter Store)

        filenames_info_props: list[str] = [factory.FILENAMES_, factory.INFO_]
        filenames_info_: str = factory.join_sep_under([i.upper() for i in filenames_info_props])
        filenames_info_params: dict[str, ssm.IStringParameter] = {
            k: ssm.StringParameter.from_string_parameter_name(
                scope=self,
                id=factory.get_construct_id(self, filenames_info_props + [k], "IStringParameter"),
                string_parameter_name=factory.get_path([project_name_comp, k, filenames_info_], lead=True),
            )
            for k, _ in sat_data_sources_meta.items()
        }

        # ---------- CodePipeline ----------

        lion_processor: str = factory.join_sep_score([project_name, component_alt])

        buildspec_path: str = factory.get_path(
            [
                factory.sub_paths[factory.CODEPIPELINE_],
                base_stack.lion_producer.replace(factory.SEP_SCORE_, factory.SEP_FW_, 1),
                factory.get_file_name_yml([factory.BUILDSPEC_]),
            ]
        )

        project_role: iam.Role = factory.iam_role_codebuild(
            self,
            factory.join_sep_score([lion_processor, deploy_env]),
            pypi_server_access=True,
            params_and_secrets_ext_arn=factory.get_params_and_secrets_ext_arn(),
        )
        pipeline_role: iam.Role = factory.iam_role_codepipeline(self, lion_processor)

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

        sat_data_source_step_func_state_machine_name: dict[str, str] = {
            i: factory.get_lambda_func_name(self, [word_map_component_alt, i.capitalize()])
            for i, _ in sat_data_sources_meta.items()
        }

        steps_comment: dict[str, str] = {
            processor_step_process: f"{word_map_component_alt_current} {getattr(self, factory.WORD_MAP_PROJECT_NAME_)} Sat Data.",
            processor_step_available: "Check All Files Available.",
            processor_step_latest: "Get Latest Start Times.",
        }
        steps_docker_image: list[str] = [processor_step_latest, processor_step_available, processor_step_process]

        step_func_state_machine_lambda_func_name: dict[str, dict[str, str]] = {}
        steps_docker_image_lambda_func_names: list[str] = []
        for _, step_func_state_machine_name in sat_data_source_step_func_state_machine_name.items():
            for s, _ in steps_comment.items():
                lambda_func_name: str = step_func_state_machine_name.replace(
                    word_map_component_alt, factory.join_sep_empty([word_map_component_alt, s.capitalize()]), 1
                )
                if step_func_state_machine_name not in step_func_state_machine_lambda_func_name:
                    step_func_state_machine_lambda_func_name[step_func_state_machine_name] = {}
                step_func_state_machine_lambda_func_name[step_func_state_machine_name][s] = lambda_func_name
                if s in steps_docker_image:
                    steps_docker_image_lambda_func_names.append(lambda_func_name)

        codepipeline_pipeline_project_names: dict[str, str] = {
            step_name: factory.join_sep_score([lion_processor, step_name]) for step_name in steps_docker_image
        }
        self.codepipeline_pipelines: dict[str, codepipeline.Pipeline] = {
            p_deploy_env: factory.codepipeline_pipeline(
                self,
                p,
                codebuild.Project(
                    scope=self,
                    id=factory.get_construct_id(
                        self,
                        [component_alt, step_name, factory.CODEBUILD_],
                        "Project",
                    ),
                    build_spec=factory.file_yaml_safe_load_codebuild_buildspec(buildspec_path),
                    cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER),
                    check_secrets_in_plain_text_env_variables=True,
                    description=f"CodeBuild project for {word_map_project_name_comp}, "
                    f"to generate latest {word_map_component_alt} {step_name.capitalize()} Docker image.",
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
                                        [word_map_component_alt, step_name.capitalize()] + cap_project_name_comp_props
                                    ),
                                ]
                            ),
                            "PRODUCER_UPDATE_FUNCTION": lambda_func_update.function_name,
                            "LAMBDA_FUNC_NAMES": json.dumps(
                                [
                                    i
                                    for i in steps_docker_image_lambda_func_names
                                    if i.startswith(
                                        factory.join_sep_empty([word_map_component_alt, step_name.capitalize()])
                                    )
                                ]
                            ),
                            "PARAMS_AND_SECRETS_EXT_ARN": factory.get_params_and_secrets_ext_arn(),
                        }.items()
                        if v
                    },
                    grant_report_group_permissions=False,
                    logging=codebuild.LoggingOptions(
                        cloud_watch=codebuild.CloudWatchLoggingOptions(
                            log_group=factory.logs_log_group(
                                self,
                                [component_alt, step_name, factory.CODEBUILD_, factory.PROJECT_],
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
            for step_name, p in codepipeline_pipeline_project_names.items()
            if (p_deploy_env := factory.join_sep_score([p, deploy_env]))
        }

        self.sns_topics: dict[str, sns.Topic] = {}
        self.codestar_notifications_notification_rules: list[codestar_notifications.NotificationRule] = []
        for _, p in codepipeline_pipeline_project_names.items():
            self.sns_topics[p] = factory.sns_topic_codestar_notifications_sns(self, p)
            self.codestar_notifications_notification_rules.append(
                factory.codestar_notifications_notification_rule(self, p)
            )

        # ---------- Step Functions ----------

        poll_rate: int = 1  # in minutes
        step_func_rate: int = 1  # in minutes
        lambda_func_timeout: int = 300  # in seconds
        step_func_state_machine_timeout: int = 30  # in minutes

        custom_policies_step_func_state_machine: list[iam.PolicyStatement] = [
            iam.PolicyStatement(
                actions=[
                    factory.join_sep_colon([factory.CODEBUILD_, i])
                    for i in [
                        "BatchGetBuilds",
                        "BatchGetReports",
                        "StartBuild",
                        "StopBuild",
                    ]
                ],
                resources=factory.ALL_RESOURCES,
            ),
            iam.PolicyStatement(
                actions=[
                    factory.join_sep_colon([factory.EVENTS_, i])
                    for i in [
                        "DescribeRule",
                        "PutRule",
                        "PutTargets",
                    ]
                ],
                resources=factory.ALL_RESOURCES,
            ),
            iam.PolicyStatement(
                actions=[
                    factory.join_sep_colon([factory.LOGS_, i])
                    for i in [
                        "CreateLogDelivery",
                        "DeleteLogDelivery",
                        "DescribeLogGroups",
                        "DescribeResourcePolicies",
                        "GetLogDelivery",
                        "ListLogDeliveries",
                        "PutLogEvents",
                        "PutResourcePolicy",
                        "UpdateLogDelivery",
                    ]
                ],
                resources=factory.ALL_RESOURCES,
            ),
        ]

        pypi_package_s3_bucket_name: str = base_stack.pypi_package_s3_bucket_name

        custom_policies_pypi_package_s3_bucket_read: list[iam.PolicyStatement] = [
            factory.iam_policy_statement_s3_get_objects(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
            factory.iam_policy_statement_s3_list_buckets(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
            factory.iam_policy_statement_s3_put_objects(self, s3_bucket_prefixes=[pypi_package_s3_bucket_name]),
        ]

        datetime_now = datetime.now(timezone.utc)

        poll_: str = factory.POLL_.capitalize()

        storage_kms_key: kms.Key = factory.get_attr_kms_key_stack(storage_stack)

        lambda_func_arns: list[str] = []
        for sat_data_source_name, n in sat_data_source_step_func_state_machine_name.items():
            self.step_func_state_machine_name = n
            sat_data_source_meta: dict = sat_data_sources_meta[sat_data_source_name]
            sat_data_org: str = (
                eumetsat_
                if base_station_key in sat_data_source_meta and sat_data_source_meta[base_station_key]
                else noaa_public_
            )

            if sat_data_org == noaa_public_:
                lambda_func_poll_description: str = (
                    f"{word_map_project_name_comp} {word_map_component_alt} {poll_} Lambda function."
                )
                lambda_func_poll_name: str = self.step_func_state_machine_name.replace(
                    word_map_component_alt, factory.join_sep_empty([word_map_component_alt, poll_]), 1
                )

                s3_public_bucket_name: str = factory.join_sep_score([noaa_, sat_data_source_name])

                lambda_func_poll_role: iam.Role = factory.iam_role_lambda(
                    self,
                    lambda_func_poll_name,
                    managed_policies=factory.lambda_managed_policies_vpc_list(),
                    custom_policies=[
                        factory.iam_policy_statement_s3_get_objects(self, s3_bucket_prefixes=[s3_public_bucket_name]),
                        factory.iam_policy_statement_s3_list_buckets(self, s3_bucket_prefixes=[s3_public_bucket_name]),
                    ],
                )
                s3_sat_data_bucket.grant_read_write(lambda_func_poll_role)

                factory.lambda_function(
                    self,
                    lambda_func_poll_name,
                    factory.get_path(
                        [
                            project_name,
                            component_alt,
                            factory.join_sep_empty([word_map_component_alt, poll_] + cap_project_name_comp_props),
                        ]
                    ),
                    lambda_func_poll_description,
                    {
                        "ACCOUNT_OWNER_ID": factory.get_attr_env_account(self),
                        "BUCKET_NAME_SOURCE": s3_public_bucket_name,
                        "BUCKET_NAME_DEST": s3_sat_data_bucket.bucket_name,
                        "SAT_DATA_ORG": sat_data_org,
                        "SOURCE_NAME": sat_data_source_name,
                        "SAT_DATA_SERVICES": json.dumps(
                            {k: v for k, v in sat_data_source_meta.items() if k != base_station_key}
                        ),
                    },
                    lambda_func_poll_role,
                    # As this Poll Lambda function is copying S3 objs from a public S3 bucket we do not own...
                    # Do NOT add the Lambda function to the VPC, to fix:
                    #  """ClientError: An error occurred (AccessDenied) when calling the UploadPartCopy operation:
                    #  VPC endpoints do not support cross-region requests"""
                    # vpc_props=(vpc, security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
                    timeout=Duration.minutes(poll_rate),
                    events_rules=factory.lambda_function_events_rules_rate(self, lambda_func_poll_name, poll_rate),
                )

            lambda_func_description: str = f"{word_map_project_name_comp} {word_map_component_alt} Lambda function."

            latest_start_time_props: list[str] = [factory.LATEST_, factory.START_, factory.TIME_]
            latest_start_time_param: ssm.StringParameter = factory.ssm_string_parameter(
                self,
                [self.step_func_state_machine_name] + latest_start_time_props,
                f"Last start time of {lambda_func_description}.",
                factory.get_path(
                    [
                        self.stack_name,
                        self.step_func_state_machine_name,
                        factory.join_sep_score(latest_start_time_props),
                    ],
                    lead=True,
                ),
                json.dumps({i: (datetime_now - timedelta(days=1)).strftime("%Y%m%d%H%M") for i in sat_data_services}),
                data_type=ssm.ParameterDataType.TEXT,
                tier=ssm.ParameterTier.STANDARD,
            )

            latest_available_props: list[str] = [factory.LATEST_, factory.AVAILABLE_]
            latest_available_param: ssm.StringParameter = factory.ssm_string_parameter(
                self,
                [self.step_func_state_machine_name] + latest_available_props,
                f"Last start time of {lambda_func_description}, for which all files are available.",
                factory.get_path(
                    [
                        self.stack_name,
                        self.step_func_state_machine_name,
                        factory.join_sep_score(latest_available_props),
                    ],
                    lead=True,
                ),
                json.dumps({i: (datetime_now - timedelta(hours=1)).strftime("%Y%m%d%H%M") for i in sat_data_services}),
                data_type=ssm.ParameterDataType.TEXT,
                tier=ssm.ParameterTier.STANDARD,
            )

            step_func_state_machine_role: iam.Role = factory.iam_role(
                self,
                [self.step_func_state_machine_name],
                factory.iam_service_principal(factory.STATES_),
                f"Step Function execution role for {self.step_func_state_machine_name}.",
            )
            for policy_statement in custom_policies_step_func_state_machine:
                step_func_state_machine_role.add_to_policy(statement=policy_statement)

            step_func_lambda_funcs: dict[str, lambda_.Function] = {}
            step_func_lambda_invokes: dict[str, stepfunctions_tasks.LambdaInvoke] = {}

            lambda_layers: list[lambda_.LayerVersion] = [
                factory.lambda_layer_version_base(self, self.step_func_state_machine_name),
            ]

            lambda_func_cloudwatch_custom: lambda_.Function = factory.lambda_function_cloudwatch(
                self, self.step_func_state_machine_name, security_groups=security_groups
            )

            environment_key: str = "environment"
            for step_name, lambda_func_name in step_func_state_machine_lambda_func_name[
                self.step_func_state_machine_name
            ].items():
                lambda_func_role: iam.Role = factory.iam_role_lambda(
                    self,
                    lambda_func_name,
                    managed_policies=factory.lambda_managed_policies_vpc_list(),
                    custom_policies=custom_policies_pypi_package_s3_bucket_read,
                )
                storage_kms_key.grant_encrypt_decrypt(lambda_func_role)
                storage_stack.s3_param_data_bucket.grant_read_write(lambda_func_role)
                s3_sat_data_bucket.grant_read_write(lambda_func_role)
                latest_start_time_param.grant_read(lambda_func_role)
                latest_start_time_param.grant_write(lambda_func_role)
                latest_available_param.grant_read(lambda_func_role)
                latest_available_param.grant_write(lambda_func_role)

                lambda_func_kwargs: dict = {
                    k: v
                    for k, v in {
                        "function_name": lambda_func_name,
                        "description": lambda_func_description,
                        environment_key: {
                            **{
                                "ACCOUNT_OWNER_ID": factory.get_attr_env_account(self),
                                "S3_SAT_DATA_BUCKET_NAME": s3_sat_data_bucket.bucket_name,
                                "PYPI_PACKAGE_S3_BUCKET_NAME": pypi_package_s3_bucket_name,
                                "PYPI_PACKAGE_S3_BUCKET_BRANCH": factory.MAIN_ if is_prod else factory.DEV_,
                                "EVENT_META_KEY": "meta",
                                "SAT_DATA_ORG": sat_data_org,
                                "DEPLOY_ENV": deploy_env,
                                "SOURCE_NAME": sat_data_source_name,
                                "SAT_DATA_SERVICES": json.dumps(
                                    {k: v for k, v in sat_data_source_meta.items() if k != base_station_key}
                                ),
                                "LATEST_START_TIME_PARAMETER": latest_start_time_param.parameter_name,
                                "LATEST_AVAILABLE_PARAMETER": latest_available_param.parameter_name,
                                "S3_PARAM_DATA_BUCKET_NAME": storage_stack.s3_param_data_bucket.bucket_name,
                                "S3_PARAM_DATA_BUCKET_OBJ_PREFIX": factory.get_path(
                                    [component_alt, sat_data_source_name]
                                ),
                                "CHECKSUM_ALGORITHM": storage_stack.s3_checksum_algorithm,
                                "KMS_MASTER_KEY_ID": storage_kms_key.key_arn,
                                "ENCRYPTION_CONTEXT_KEY": storage_stack.s3_encryption_context_key,
                                "CDK_STACK_NAME": storage_stack.s3_cdk_stack_name,
                                "TAGS": json.dumps(factory.get_s3_bucket_tags(self), default=str),
                                "SOURCE_MODULE_NAME": factory.join_sep_dot(
                                    [
                                        f"{component_alt}s",
                                        factory.join_sep_under(
                                            [sat_data_source_families[sat_data_source_name], component_alt]
                                        ),
                                    ]
                                ),
                                "SOURCE_CLASS_NAME": factory.join_sep_empty(
                                    [sat_data_source_families[sat_data_source_name].upper(), word_map_component_alt]
                                ),
                                source_system_objs_: source_system_objs_params[sat_data_source_name].string_value,
                                filenames_info_: filenames_info_params[sat_data_source_name].string_value,
                            },
                            **factory.lambda_function_kwargs_params_and_secrets(to_string=True),
                        },
                        "role": lambda_func_role,
                        "environment_encryption": factory.get_attr_kms_key_stack(self),
                        "vpc_props": (factory.get_attr_vpc(self), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
                        "timeout": Duration.seconds(
                            (60 * 15) if step_name == processor_step_process else lambda_func_timeout
                        ),
                        "ephemeral_storage_size": (
                            Size.mebibytes(9216 if sat_data_source_name == self.HIMAWARI9_ else 2560)
                            if step_name == processor_step_process
                            else None
                        ),
                        "memory_size": (
                            (10240 if sat_data_source_name == self.HIMAWARI9_ else 6144)
                            if step_name == processor_step_process
                            else (None if step_name == processor_step_latest else 512)
                        ),  # in MiB
                        "lambda_function_cloudwatch_custom": lambda_func_cloudwatch_custom,
                    }.items()
                    if v
                }
                for k, v in sat_data_source_meta.items():
                    if k != base_station_key and (reader_val := v[sat_data_source_reader_key]):
                        lambda_func_kwargs[environment_key][
                            factory.join_sep_under([k.upper(), sat_data_source_reader_key.upper()])
                        ] = reader_val

                if step_name in steps_docker_image:
                    lambda_func: lambda_.DockerImageFunction = factory.lambda_docker_image_function(
                        self,
                        project_repo=base_stack.repos_processor[step_name],
                        **lambda_func_kwargs,
                    )
                else:
                    lambda_func: lambda_.Function = factory.lambda_function(
                        self,
                        code_path=factory.get_path(
                            [
                                project_name,
                                component_alt,
                                factory.join_sep_empty(
                                    [word_map_component_alt, step_name.capitalize()] + cap_project_name_comp_props
                                ),
                            ],
                            lead=True,
                        ),
                        layers=lambda_layers,
                        **lambda_func_kwargs,
                    )
                lambda_func_arns.append(lambda_func.function_arn)
                lambda_func.grant_invoke(step_func_state_machine_role)

                step_func_lambda_funcs[step_name] = lambda_func
                step_func_lambda_invokes[step_name] = stepfunctions_tasks.LambdaInvoke(
                    scope=self,
                    id=factory.get_construct_id(self, [lambda_func_name], "LambdaInvoke")[:80],
                    lambda_function=lambda_func,
                    # client_context=,  # Up to 3583 bytes of base64-encoded data about the invoking client to pass to the function. Default: - No context
                    invocation_type=stepfunctions_tasks.LambdaInvocationType.REQUEST_RESPONSE,
                    # EVENT - Invoke the function asynchronously.
                    # payload=,  # Default: - The state input (JSON path ‘$’)
                    # payload_response_only=True,  # Cannot be used if integration_pattern, invocation_type, client_context, or qualifier are specified. It always uses the REQUEST_RESPONSE invocation_type.
                    retry_on_service_exceptions=True,
                    comment=steps_comment[step_name],
                    # heartbeat=,  # Timeout for the heartbeat. Default: - None
                    # input_path="$",  # Default: - The entire task input (JSON path ‘$’)
                    integration_pattern=stepfunctions.IntegrationPattern.REQUEST_RESPONSE,
                    output_path="$.Payload",
                    # result_path="$"  #Default: - Replaces the entire input with the result (JSON path ‘$’)
                    # result_selector={},  # Default: - None
                    task_timeout=stepfunctions.Timeout.duration(Duration.seconds(lambda_func_timeout * 3)),
                )

            process_choice: stepfunctions.Choice = factory.stepfunctions_choice_failed_succeeded(
                self,
                f"{word_map_component_alt_past} Successfully?",
                step_func_lambda_funcs[processor_step_process],
                steps_comment[processor_step_process],
                step_func_lambda_invokes[processor_step_process],
                word_map_component_alt_past,
            )

            available_choice: stepfunctions.Choice = factory.stepfunctions_choice_failed_succeeded(
                self,
                "All Files Available?",
                step_func_lambda_funcs[processor_step_available],
                steps_comment[processor_step_available],
                step_func_lambda_invokes[processor_step_available],
                word_map_component_alt_past,
                continue_=step_func_lambda_invokes[processor_step_process].next(next=process_choice),
            )

            latest_choice: stepfunctions.Choice = (
                stepfunctions.Choice(
                    scope=self,
                    id=factory.get_construct_id(
                        self, [step_func_lambda_funcs[processor_step_latest].function_name], "Choice"
                    ),
                    comment="Got Latest Start Times?",
                    # input_path="$",  # Default: $
                    # output_path="$",  # Default: $
                )
                .when(
                    condition=factory.stepfunctions_condition_string_equals(factory.STATUS_SUCCEEDED_),
                    next=step_func_lambda_invokes[processor_step_available].next(next=available_choice),
                )
                .otherwise(
                    def_=factory.stepfunctions_fail(
                        self, step_func_lambda_funcs[processor_step_latest], word_map_component_alt_current
                    )
                )
            )

            stepfunctions_state_machine = stepfunctions.StateMachine(
                self,
                factory.get_construct_id(self, [self.step_func_state_machine_name], "StateMachine"),
                definition_body=stepfunctions.DefinitionBody.from_chainable(
                    chainable=step_func_lambda_invokes[processor_step_latest].next(next=latest_choice)
                ),
                # definition_substitutions={}  # Substitutions for the definition body as a key-value map
                logs=stepfunctions.LogOptions(
                    destination=factory.logs_log_group(
                        self,
                        [self.step_func_state_machine_name],
                        factory.get_path(
                            [
                                factory.log_groups[factory.VENDEDLOGS_],
                                factory.STATES_,
                                self.step_func_state_machine_name,
                            ]
                        ),
                    ),
                    include_execution_data=True,
                    level=stepfunctions.LogLevel.ALL,
                ),
                removal_policy=RemovalPolicy.DESTROY,
                role=step_func_state_machine_role,
                state_machine_name=self.step_func_state_machine_name,
                state_machine_type=stepfunctions.StateMachineType.STANDARD,
                timeout=Duration.minutes(step_func_state_machine_timeout),
                tracing_enabled=False,
            )

            factory.events_rule(
                self,
                [self.step_func_state_machine_name],
                f"Trigger Step Functions state machine {self.step_func_state_machine_name} "
                f"every {step_func_rate} minutes.",
                events.Schedule.cron(minute=factory.get_path([factory.SEP_ASTERISK_, step_func_rate])),
            ).add_target(
                target=targets.SfnStateMachine(
                    machine=stepfunctions_state_machine,
                    # input=,  # Default: the entire EventBridge event
                    # role=,  # Default: - a new role will be created
                    # dead_letter_queue=,  # Default: - no dead-letter queue  # TODO: (OPTIONAL) Add an SQS queue to be used as DLQ ?
                    max_event_age=Duration.hours(24),
                    retry_attempts=185,
                )
            )

            archive_: str = factory.ARCHIVE_.capitalize()
            lambda_func_archive_description: str = (
                f"{word_map_project_name_comp} {word_map_component_alt} {archive_} Lambda function."
            )
            lambda_func_archive_name: str = self.step_func_state_machine_name.replace(
                word_map_component_alt, factory.join_sep_empty([word_map_component_alt, archive_]), 1
            )

            lambda_func_archive_role: iam.Role = factory.iam_role_lambda(
                self,
                lambda_func_archive_name,
                managed_policies=factory.lambda_managed_policies_vpc_list(),
                custom_policies=custom_policies_pypi_package_s3_bucket_read,
            )
            storage_kms_key.grant_encrypt_decrypt(lambda_func_archive_role)
            s3_sat_data_bucket.grant_read_write(lambda_func_archive_role)

            factory.lambda_function(
                self,
                lambda_func_archive_name,
                factory.get_path(
                    [
                        project_name,
                        component_alt,
                        factory.join_sep_empty([word_map_component_alt, archive_] + cap_project_name_comp_props),
                    ]
                ),
                lambda_func_archive_description,
                {
                    "ACCOUNT_OWNER_ID": factory.get_attr_env_account(self),
                    "BUCKET_NAME_DEST": pypi_package_s3_bucket_name,
                    "BUCKET_NAME_SOURCE": s3_sat_data_bucket.bucket_name,
                    "DEPLOY_ENV": deploy_env,
                    "SOURCE_NAME": sat_data_source_name,
                },
                lambda_func_archive_role,
                vpc_props=(factory.get_attr_vpc(self), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
                timeout=Duration.minutes(5),
                events_rules=[
                    (
                        factory.events_rule(
                            self,
                            [lambda_func_archive_name, factory.DAILY_],
                            f"Trigger Lambda function {lambda_func_archive_name} every day 6am (UTC).",
                            events.Schedule.cron(minute=str(0), hour=str(6)),
                        ),
                        {},  # Payload
                    ),
                ],
            )

        lambda_func_update_role.add_to_policy(
            statement=factory.iam_policy_statement_lambda_update_function_code(lambda_func_arns=lambda_func_arns)
        )
