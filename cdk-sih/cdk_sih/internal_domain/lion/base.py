from aws_cdk import (
    Duration,
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codestarnotifications as codestar_notifications,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_s3 as s3,
    aws_sns as sns,
)

from cdk_sih.client_vpn.endpoint import CdkClientVpnEndpointStack
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkLionBaseStack(Stack):
    def __init__(
        self,
        bastion_host_private_ips: list[str],
        client_vpn_endpoint_stack: CdkClientVpnEndpointStack,
        component: str,
        elastic_ip_parameter_names: dict[str, str],
        factory: CdkConstructsFactory,
        project_name: str,
        project_name_comp_list: list[str],
        pypi_package_name: str,
        vpc_stack: CdkVpcSihStack,
        disable_24_7_: bool = False,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_client_vpn_endpoint_sg(self, client_vpn_endpoint_stack)
        factory.set_attrs_codepipeline_stage_action_names(self)
        factory.set_attrs_codestar_connection(self, factory.BITBUCKET_WORKSPACE_SIH_INFR_INN)
        factory.set_attrs_disable_24_7_(self, disable_24_7_)
        factory.set_attrs_elastic_ips_meta(self, elastic_ip_parameter_names)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_ports_default(self, alb_port=8000)

        self.bastion_host_private_ips: list[str] = bastion_host_private_ips
        self.pypi_package_name: str = pypi_package_name

        self.pypi_package_s3_bucket_name: str = factory.get_s3_bucket_name(
            self, pypi_package_name.replace(factory.SEP_SCORE_, factory.SEP_EMPTY_)
        )

        self.collector_: str = "collector"
        self.extractor_: str = "extractor"
        self.processor_: str = "processor"
        self.processor_step_available: str = "available"
        self.processor_step_latest: str = "latest"
        self.processor_step_process: str = "process"
        self.producer_: str = "producer"

        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self, inc_deploy_env=False)

        # ---------- Route 53 ----------

        factory.set_attrs_hosted_zone(self)

        # ---------- ECR ----------

        self.repos: dict[str, ecr.Repository] = {p: factory.ecr_repository(self, p) for p in project_name_comp_list}
        self.repo_collector: ecr.Repository = factory.ecr_repository(
            self, factory.join_sep_score([project_name, self.collector_])
        )
        self.repos_processor: dict[str, ecr.Repository] = {
            i: factory.ecr_repository(self, factory.join_sep_score([project_name, self.processor_, i]))
            for i in [self.processor_step_latest, self.processor_step_available, self.processor_step_process]
        }

        # ---------- EC2 ----------

        # pylint: disable=no-member
        factory.ec2_security_group_all(
            self,
            all_vpc_traffic=(
                [getattr(self, factory.ALB_PORT_)],
                factory.get_attr_vpc_cidr(self),
                factory.get_attr_vpc_name(self),
            ),
            ec_redis=True,
        )

        collector_lambda_sg_description: str = f"{factory.lookup_word_map(self.collector_)} Lambda functions"
        processor_lambda_sg_description: str = f"{factory.lookup_word_map(self.processor_)} Lambda functions"
        ec_redis_extractor_lambda_sg_description: str = (
            f"{getattr(self, factory.EC_REDIS_SG_DESCRIPTION_)} "
            f"{factory.lookup_word_map(self.extractor_)} Lambda functions"
        )
        self.collector_lambda_sg: ec2.SecurityGroup = factory.ec2_security_group(
            self,
            [self.collector_, factory.LAMBDA_],
            factory.join_sep_space([word_map_project_name_comp, collector_lambda_sg_description]),
        )
        self.processor_lambda_sg: ec2.SecurityGroup = factory.ec2_security_group(
            self,
            [self.processor_, factory.LAMBDA_],
            factory.join_sep_space([word_map_project_name_comp, processor_lambda_sg_description]),
        )
        self.ec_redis_extractor_lambda_sg: ec2.SecurityGroup = factory.ec2_security_group(
            self,
            [factory.ELASTICACHE_, factory.REDIS_, factory.CLUSTER_, self.extractor_, factory.LAMBDA_],
            factory.join_sep_space([word_map_project_name_comp, ec_redis_extractor_lambda_sg_description]),
        )
        # HTTPS -> S3 Param Data Collector/Processor Lambda functions
        self.collector_lambda_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(factory.HTTPS_PORT), description="Allow HTTPS traffic."
        )
        self.processor_lambda_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(factory.HTTPS_PORT), description="Allow HTTPS traffic."
        )
        # ElastiCache Redis cluster <-- (Redis Port) --> ElastiCache Redis cluster Extractor Lambda functions
        factory.ec2_security_group_connections_allow_from_bi_direct(
            getattr(self, factory.EC_REDIS_SG_),
            self.ec_redis_extractor_lambda_sg,
            getattr(self, factory.REDIS_PORT_),
            factory.join_sep_space(
                [
                    word_map_project_name_comp,
                    getattr(self, factory.EC_REDIS_SG_DESCRIPTION_),
                    factory.TCT_,
                    ec_redis_extractor_lambda_sg_description,
                ]
            ),
        )

        # ---------- SSM ----------

        # MS Teams CI-CD Channel Webhook URL
        factory.ssm_string_parameter_webhook_url(self)

        # Version meta
        factory.ssm_string_parameter_version_meta(self)

        # ---------- Secrets Manager ----------

        # ECS container API_KEYS secret
        factory.secrets_manager_secret_ecs_container(self, "mcxpkG", attr_name=factory.ECS_CONTAINER_API_KEYS_SECRET_)

        # Secret key secret
        factory.secrets_manager_secret_secret_keys_secret(self, singleton=True)

        # ---------- S3 Sat Data ----------

        s3_sat_data_bucket_name: str = factory.join_sep_score([project_name, factory.SAT_, factory.DATA_])
        self.s3_sat_data_bucket: s3.IBucket = s3.Bucket.from_bucket_name(
            scope=self,
            id=factory.get_construct_id(self, [s3_sat_data_bucket_name, factory.S3_], "IBucket"),
            bucket_name=s3_sat_data_bucket_name,
        )

        # ---------- CodePipeline ----------

        self.lion_producer: str = factory.join_sep_score([project_name, self.producer_])

        self.image_tag: str = factory.LATEST_

        self.codepipeline_source_repo: str = "aws-lambda"  # Git repo name, as shown in Bitbucket
        self.codepipeline_source_branch: str = "main"  # TODO: (OPTIONAL) Change branch for testing purposes

        lion_producer_base_name: str = None
        codepipeline_pipeline_project_names: dict[str, str] = {
            step_name: factory.join_sep_score([self.lion_producer, step_name])
            for step_name in [factory.BASE_, factory.BIN_]
        }
        self.codepipeline_pipelines: dict[str, codepipeline.Pipeline] = {}
        for step_name, p in codepipeline_pipeline_project_names.items():
            factory.ecr_repository(self, p)

            buildspec_path: str = factory.get_path(
                [
                    factory.sub_paths[factory.CODEPIPELINE_],
                    self.lion_producer.replace(factory.SEP_SCORE_, factory.SEP_FW_, 1),
                    step_name,
                    factory.get_file_name_yml([factory.BUILDSPEC_]),
                ]
            )

            project_role: iam.Role = factory.iam_role_codebuild(self, p)
            pipeline_role: iam.Role = factory.iam_role_codepipeline(self, p)

            is_base_step: bool = bool(step_name == factory.BASE_)
            is_bin_step: bool = bool(step_name == factory.BIN_)

            if is_base_step:
                lion_producer_base_name = p
                ecr_public_perms: iam.PolicyStatement = iam.PolicyStatement(
                    actions=[
                        factory.join_sep_colon(
                            [factory.join_sep_score([factory.ECR_, factory.PUBLIC_]), "GetAuthorizationToken"]
                        ),
                        factory.join_sep_colon([factory.STS_, "GetServiceBearerToken"]),
                    ],
                    resources=factory.ALL_RESOURCES,
                )
                project_role.add_to_policy(ecr_public_perms)
                pipeline_role.add_to_policy(ecr_public_perms)

            self.codepipeline_pipelines[p] = factory.codepipeline_pipeline(
                self,
                p,
                codebuild.Project(
                    scope=self,
                    id=factory.get_construct_id(
                        self,
                        [self.producer_, step_name, factory.CODEBUILD_],
                        "Project",
                        project_name_comp=self.lion_producer,
                    ),
                    build_spec=factory.file_yaml_safe_load_codebuild_buildspec(buildspec_path),
                    cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER),
                    check_secrets_in_plain_text_env_variables=True,
                    description=f"CodeBuild project for {getattr(self, factory.WORD_MAP_PROJECT_NAME_)}, "
                    f"to generate latest {self.producer_.capitalize()} {step_name.capitalize()} Docker image.",
                    environment=factory.codebuild_build_environment(
                        factory.get_attr_project_name_comp(self), base_ignore=True
                    ),
                    environment_variables={
                        k: codebuild.BuildEnvironmentVariable(value=v)
                        for k, v in {
                            k_: v_
                            for k_, v_ in {
                                "AWS_ACCOUNT_ID": factory.get_attr_env_account(self),
                                "AWS_DEFAULT_REGION": factory.get_attr_env_region(self),
                                "ORGANISATION": factory.organisation,
                                "PROJECT_NAME": p,
                                "IMAGE_TAG": self.image_tag,
                                "BASE_PROJECT_NAME": (
                                    "public.ecr.aws/lambda/python" if is_base_step else lion_producer_base_name
                                ),
                                "BASE_IMAGE_TAG": factory.PYTHON_VERSION if is_base_step else self.image_tag,
                                "CMAKE_VERSION": str(3.27) if is_base_step else None,
                                "CMAKE_PATCH": str(7) if is_base_step else None,
                                "AEC_VER": str(1.1) if is_bin_step else None,
                                "AEC_PAT": str(2) if is_bin_step else None,
                                "ECC_VER": str(2.32) if is_bin_step else None,
                                "ECC_PAT": str(1) if is_bin_step else None,
                            }.items()
                            if v_
                        }.items()
                        if v
                    },
                    grant_report_group_permissions=False,
                    logging=codebuild.LoggingOptions(
                        cloud_watch=codebuild.CloudWatchLoggingOptions(
                            log_group=factory.logs_log_group(
                                self,
                                [self.producer_, step_name, factory.CODEBUILD_, factory.PROJECT_],
                                factory.get_path([factory.log_groups[factory.CODEBUILD_], p]),
                                project_name_comp=self.lion_producer,
                            )
                        )
                    ),
                    project_name=p,
                    queued_timeout=Duration.hours(8),
                    role=project_role,
                    security_groups=[
                        getattr(self, factory.ECS_SG_)
                    ],  # TODO: (OPTIONAL) Add an additional/new Security Group instead
                    subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                    timeout=Duration.minutes(30),
                    vpc=factory.get_attr_vpc(self),
                ),
                pipeline_role,
                repo=pypi_package_name,
                branch=factory.MAIN_,
                trigger_on_push=False,
                deploy=False,
            )

        self.sns_topics: dict[str, sns.Topic] = {}
        self.codestar_notifications_notification_rules: list[codestar_notifications.NotificationRule] = []
        for _, p in codepipeline_pipeline_project_names.items():
            self.sns_topics[p] = factory.sns_topic_codestar_notifications_sns(self, p)
            self.codestar_notifications_notification_rules.append(
                factory.codestar_notifications_notification_rule(self, p, base_ignore=True)
            )
