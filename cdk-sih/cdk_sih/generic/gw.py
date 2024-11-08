import json

from aws_cdk import (
    Resource,
    Stack,
    aws_cloudfront as cloudfront,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    aws_iam as iam,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.database import CdkDatabaseStack
from cdk_sih.generic.notif import CdkNotifStack
from cdk_sih.generic.storage import CdkStorageStack
from cdk_sih.internal_domain.bkg.ms import CdkBkgMsStack
from cdk_sih.internal_domain.bkg.storage import CdkBkgStorageStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkGwStack(Stack):
    def __init__(
        self,
        base_stack: Stack,
        component: str,
        deploy_env: str,
        deploy_env_24_7_set: set[str],
        deploy_env_weekend_set: set[str],
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        storage_stack: CdkStorageStack,
        vpc_stack: CdkVpcSihStack,
        admin: bool = False,
        ecs_task_definition_container_memory_mib: int = None,
        multi_region: str = None,
        notif_stack: CdkNotifStack = None,
        storage_bkg_stack: CdkBkgStorageStack = None,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        self.factory: CdkConstructsFactory = factory

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(
            self,
            base_stack,
            deploy_env,
            env_meta,
            deploy_env_24_7_set=deploy_env_24_7_set,
            deploy_env_weekend_set=deploy_env_weekend_set,
        )

        factory.set_attrs_from_alt_stack(self, base_stack, factory.ALB_PORT_)
        factory.set_attrs_from_alt_stack(self, base_stack, factory.ECS_SG_)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_schedule_windows(self, factory.ECS_)

        self.word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self)

        self.fqdn: str = None
        self.fqdn_private: str = None
        if subdomain := getattr(self, factory.SUBDOMAIN_, None):
            hosted_zone_name: str = getattr(base_stack, factory.HOSTED_ZONE_NAME_)
            self.fqdn = factory.join_sep_dot([subdomain, hosted_zone_name])
            self.fqdn_private = factory.join_sep_dot([subdomain, factory.get_attr_env_region(self), hosted_zone_name])

        self.admin: bool = admin
        self.env_meta: dict = env_meta
        self.price_class: cloudfront.PriceClass = factory.get_cloudfront_dist_price_class(self)

        cf_origin_path: str = factory.SEP_FW_
        factory.set_attrs_url(self, cf_origin_path)
        factory.set_attrs_url_private(self, cf_origin_path)

        if storage_stack:
            for i in [
                factory.STORAGE_S3_BUCKET_NAME_,
                factory.STORAGE_S3_CDK_STACK_NAME_,
                factory.STORAGE_S3_CHECKSUM_ALGORITHM_,
                factory.STORAGE_S3_ENCRYPTION_CONTEXT_KEY_,
                factory.STORAGE_S3_KMS_KEY_,
            ]:
                factory.set_attrs_from_alt_stack(self, storage_stack, i)

        s3_bucket_prefixes_read_only: list[str] = []
        self.inc_bkg_custom_filter_patterns: bool = False
        if storage_bkg_stack:
            self.inc_bkg_custom_filter_patterns = True
            for k, v in {
                factory.STORAGE_S3_BUCKET_NAME_: factory.STORAGE_S3_BKG_BUCKET_NAME_,
                factory.STORAGE_S3_CDK_STACK_NAME_: factory.STORAGE_S3_BKG_CDK_STACK_NAME_,
                factory.STORAGE_S3_CHECKSUM_ALGORITHM_: factory.STORAGE_S3_BKG_CHECKSUM_ALGORITHM_,
                factory.STORAGE_S3_ENCRYPTION_CONTEXT_KEY_: factory.STORAGE_S3_BKG_ENCRYPTION_CONTEXT_KEY_,
                factory.STORAGE_S3_KMS_KEY_: factory.STORAGE_S3_BKG_KMS_KEY_,
            }.items():
                factory.set_attrs_from_alt_stack(self, storage_bkg_stack, k, new_attr_name=v)
            s3_bucket_prefixes_read_only.append(getattr(self, factory.STORAGE_S3_BKG_CDK_STACK_NAME_))

        self.is_dev: bool = bool(factory.DEV_ == deploy_env)
        self.is_internal: bool = getattr(self, factory.DEPLOY_ENV_INTERNAL_)
        self.is_staging: bool = bool(factory.STAGING_ == deploy_env)
        is_debug: bool = bool(not getattr(self, factory.DEPLOY_ENV_PROD_))

        self.auto_iod: str = json.dumps(True)
        self.debug: str = json.dumps(is_debug)
        self.ecs_task_definition_container_memory_mib: int = (
            ecs_task_definition_container_memory_mib if ecs_task_definition_container_memory_mib else 4096
        )
        self.internal_name: str = factory.join_sep_score(factory.get_attr_project_name_comp_props(self) + [deploy_env])
        self.local_host: str = factory.WILDCARD_ADDRESS
        self.log_level: str = factory.DEBUG_ if is_debug else factory.INFO_
        self.mail_host: str = "smtp.office365.com"  # TODO: (IMPORTANT) Remove when AWS SES replaces mail sending
        self.mail_port: str = str(587)  # TODO: (IMPORTANT) Remove when AWS SES replaces mail sending
        self.openapi_off: str = json.dumps(bool(not self.is_internal))
        self.passlib_schemes: str = factory.PASSLIB_SCHEMES
        self.redis_ssl: str = json.dumps(True)
        self.s3_cdk_stack_name: str = factory.get_cdk_stack_name_short(self.stack_name).lower()
        self.s3_handler_: str = factory.join_sep_empty([factory.S3_.upper(), factory.HANDLER_.capitalize()])
        self.status_route: str = "3SJ6G7aSpi4S"
        self.token_algorithm: str = factory.TOKEN_ALGORITHM
        self.token_duration_mins: str = str(30)
        self.token_refresh_duration_mins: str = str(2880)
        self.url_portal: str = self.get_url_portal(self.fqdn, multi_region)
        self.workers: str = str(4)

        self.ecomm_api_key: str = factory.join_sep_under([factory.ECOMM_, factory.API_, factory.KEY_]).upper()
        self.secret_key: str = factory.join_sep_under([factory.SECRET_, factory.KEY_]).upper()
        self.token_key: str = factory.join_sep_under([factory.TOKEN_, factory.KEY_]).upper()

        alb: elasticloadbalancing.ApplicationLoadBalancer = factory.elasticloadbalancing_application_load_balancer(
            self, getattr(base_stack, factory.ALB_SG_)
        )

        cf_origin_custom_header: str = factory.X_CUSTOM_HEADER_
        cf_origin_custom_header_secret: secretsmanager.Secret = factory.secrets_manager_secret_cf_origin_custom_header(
            self, cf_origin_custom_header
        )

        factory.cloudfront_distribution(
            self,
            alb,
            getattr(base_stack, factory.HOSTED_ZONE_),
            subdomain,
            cf_origin_path,
            origin_custom_headers=[(cf_origin_custom_header, cf_origin_custom_header_secret)],
        )

        self.alb_target_group: elasticloadbalancing.ApplicationTargetGroup = (
            factory.elasticloadbalancing_application_target_group(
                self,
                elasticloadbalancing.TargetType.IP,
                health_check_path=factory.elasticloadbalancing_application_target_group_health_check_path_status_route(
                    self, cf_origin_path
                ),
            )
        )

        factory.elasticloadbalancing_application_listener(
            self,
            alb,
            [
                factory.acm_certificate(
                    self,
                    [factory.ALB_, factory.LISTENER_],
                    self.fqdn,
                    getattr(base_stack, factory.HOSTED_ZONE_),
                )
            ],
            [self.alb_target_group],
            [(cf_origin_custom_header, cf_origin_custom_header_secret)],
        )

        factory.cfn_output_url(self)
        factory.cfn_output_url_private(self)

        ecs_exec_role_custom_policies: list[iam.PolicyStatement] = [
            factory.iam_policy_statement_ecs_exec(),
            factory.iam_policy_statement_kmy_key_decrypt(self),
            factory.iam_policy_statement_secretsmanager_get_secret_value(self),
            factory.iam_policy_statement_service_role_for_ecs(self),
            factory.iam_policy_statement_ssm_get_parameter(self),
        ]
        if storage_stack:
            ecs_exec_role_custom_policies = (
                ecs_exec_role_custom_policies
                + factory.iam_policy_statement_ecs_access_to_s3(
                    self,
                    self.s3_cdk_stack_name,
                    [self.s3_cdk_stack_name, getattr(self, factory.STORAGE_S3_CDK_STACK_NAME_)],
                    s3_bucket_prefixes_read_only=s3_bucket_prefixes_read_only,
                )
            )
        if notif_stack:
            self.add_dependency(notif_stack)
            sns_mob_push_props: list[str] = [factory.SNS_, factory.MOB_, factory.PUSH_]
            self.sns_mob_push_param: ssm.IStringParameter = ssm.StringParameter.from_string_parameter_name(
                scope=self,
                id=factory.get_construct_id(self, sns_mob_push_props, "IStringParameter"),
                string_parameter_name=factory.get_path(
                    [factory.join_sep_score(sns_mob_push_props), factory.get_attr_project_name_comp(self), deploy_env],
                    lead=True,
                ),
            )
            self.sns_platform_application_arn: str = self.sns_mob_push_param.string_value
            ecs_exec_role_custom_policies = (
                ecs_exec_role_custom_policies + factory.iam_policy_statement_ecs_access_to_sns(self)
            )

        self.ecs_exec_role: iam.Role = factory.iam_role_ecs_task(
            self,
            f"Role used by {self.word_map_project_name_comp} ECS task definitions.",
            managed_policies=factory.ecs_task_managed_policies_list(),
            custom_policies=ecs_exec_role_custom_policies,
        )
        self.ecs_task_role: iam.Role = self.ecs_exec_role

        ecs_task_definition_container_cpu_units: int = int(self.ecs_task_definition_container_memory_mib / 2)
        self.ecs_task_definition: ecs.TaskDefinition = factory.ecs_fargate_service_task_definition(
            self,
            str(ecs_task_definition_container_cpu_units),
            str(self.ecs_task_definition_container_memory_mib),
            self.ecs_exec_role,
            self.ecs_task_role,
        )
        self.ecs_task_definition_container_cpu_cores: str = str(int(ecs_task_definition_container_cpu_units / 1024))

        self.ecs_task_container_log_group: logs.LogGroup = factory.logs_log_group_ecs_task_container(self)

        self.ecs_container_name: str = factory.get_ecs_container_name(self)

    def get_additional_allowed_origins(
        self, additional_allowed_origins_deploy_envs: list[str], dev_ports: list[int], staging_ports: list[int]
    ) -> str:
        allowed_origins: list[str] = []
        if self.is_internal:
            for i in additional_allowed_origins_deploy_envs:
                allowed_origins += [self.url_portal.replace(self.factory.get_attr_deploy_env(self), i, 1)]
            additional_allowed_origins_localhost_ports: list[int] = []
            if self.is_dev:
                additional_allowed_origins_localhost_ports += dev_ports
            elif self.is_staging:
                additional_allowed_origins_localhost_ports += staging_ports
            for host in self.factory.LOCAL_HOST_LIST:
                allowed_origins += [
                    self.factory.join_sep_empty([self.factory.HTTP_, self.factory.join_sep_colon([host, str(p)])])
                    for p in additional_allowed_origins_localhost_ports
                ]
        return json.dumps(allowed_origins, default=str)

    def get_app_name(self, admin: bool) -> str:
        return self.factory.join_sep_space(
            [
                self.word_map_project_name_comp,
                (self.factory.ADMIN_ if admin else self.factory.CLIENT_).capitalize(),
                self.factory.SERVER_.capitalize(),
            ]
        )

    def get_ecs_service(
        self,
        project_repo: ecr.Repository,
        ecs_container_environment: dict[str, str],
        ecs_container_secrets: dict[str, ecs.Secret],
        http_error_code: int = None,
        dependant_constructs: list[Resource] = None,
    ):
        self.factory.ecs_fargate_service_task_definition_add_container(
            self,
            self.ecs_task_definition,
            ecs.RepositoryImage.from_ecr_repository(
                repository=project_repo, tag=self.factory.get_attr_deploy_env(self)
            ),
            self.ecs_container_name,
            getattr(self, self.factory.ALB_PORT_),
            self.ecs_task_definition_container_memory_mib,
            self.ecs_task_container_log_group,
            ecs_container_environment,
            ecs_container_secrets,
        )
        return self.factory.ecs_fargate_service(
            self,
            self.ecs_task_definition,
            self.fqdn_private,
            self.ecs_task_container_log_group,
            custom_filter_patterns={"btf": '?"BKG TASK FAILURE"'} if self.inc_bkg_custom_filter_patterns else None,
            dependant_constructs=dependant_constructs,
            target_group=self.alb_target_group,
            admin=self.admin,
            **{k: v for k, v in {"http_error_code": http_error_code}.items() if http_error_code},
        )

    @staticmethod
    def get_sqlalchemy_database_engine_options(pool_size: int = 10, max_overflow: int = 30) -> dict:
        return {
            "pool_pre_ping": True,
            "pool_size": pool_size,
            "pool_recycle": 7200,
            "connect_args": {"connect_timeout": 20},
            "max_overflow": max_overflow,
        }

    def get_sqlalchemy_database_options(self, database_stack: CdkDatabaseStack, deploy_env: str) -> str:
        return json.dumps(
            {
                self.factory.join_sep_dot(["sqlalchemy", k]): v
                for k, v in {
                    **{
                        self.factory.URL_: self.get_sqlalchemy_database_uri(
                            database_stack, deploy_env, secret_db_pw=False
                        )
                    },
                    **self.get_sqlalchemy_database_engine_options(),
                }.items()
            }
        )

    def get_sqlalchemy_database_uri(
        self, database_stack: CdkDatabaseStack, deploy_env: str, secret_db_pw: bool = True
    ) -> str:
        db_username: str = getattr(database_stack, self.factory.DB_API_USER_USERNAME_)
        db_pw: str = getattr(database_stack, self.factory.DB_API_USER_PW_)
        db_hostname: str = (
            db_proxies[deploy_env].endpoint
            if (db_proxies := getattr(database_stack, self.factory.DB_PROXIES_, None))
            else getattr(database_stack, self.factory.DB_SERVER_).instance_endpoint.hostname
        )
        db_schema_name: str = getattr(database_stack, self.factory.DB_SCHEMAS_)[deploy_env]
        return self.factory.join_sep_empty(
            [
                "mysql+mysqlconnector",
                self.factory.SEP_COLON_FW_FW_,
                self.factory.join_sep_colon([db_username, "{password}" if secret_db_pw else db_pw]),
                self.factory.SEP_AT_SIGN_,
                self.factory.join_sep_colon([db_hostname, str(getattr(database_stack, self.factory.DB_PORT_))]),
                self.factory.SEP_FW_,
                db_schema_name,
            ]
        )

    @staticmethod
    def get_url_background(self_obj, bkg_ms_stack: CdkBkgMsStack) -> str:
        self_obj.add_dependency(bkg_ms_stack)
        return bkg_ms_stack.base_url

    def get_url_portal(self, fqdn: str, multi_region: str) -> str:
        new_fqdn: str = fqdn.split(sep=self.factory.SEP_DOT_, maxsplit=(2 if multi_region else 1))[-1]
        return self.factory.join_sep_empty(
            [self.factory.HTTPS_, self.factory.join_sep_dot([self.factory.PORTAL_, new_fqdn])]
        )
