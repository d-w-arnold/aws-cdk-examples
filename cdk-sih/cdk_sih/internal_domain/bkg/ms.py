import json
from typing import Optional

from aws_cdk import (
    Fn,
    Stack,
    aws_cloudfront as cloudfront,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.bkg.base import CdkBkgBaseStack
from cdk_sih.internal_domain.bkg.broker import CdkBkgBrokerStack
from cdk_sih.internal_domain.bkg.cache import CdkBkgCacheStack
from cdk_sih.internal_domain.bkg.database import CdkBkgDatabaseStack
from cdk_sih.internal_domain.bkg.storage import CdkBkgStorageStack
from cdk_sih.internal_domain.lion.ms import CdkLionMsStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkBkgMsStack(Stack):
    def __init__(
        self,
        base_stack: CdkBkgBaseStack,
        broker_stack: CdkBkgBrokerStack,
        cache_stack: CdkBkgCacheStack,
        component: str,
        database_stack: CdkBkgDatabaseStack,
        deploy_env: str,
        deploy_env_24_7_set: set[str],
        deploy_env_weekend_set: set[str],
        ecs_container_service_access: dict[str, str],
        ecs_container_service_access_task_subscriptions: dict[str, list[str]],
        lion_ms_stack: CdkLionMsStack,
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        project_name_comp_subs: dict[str, tuple[str, int, bool, Optional[float]]],
        ses_lambda_func: lambda_.Function,
        storage_stack: CdkBkgStorageStack,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        env_meta[factory.ECS_SERVICE_MAX_] = max(env_meta[factory.ECS_SERVICE_MAX_], 5)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(
            self,
            base_stack,
            deploy_env,
            env_meta,
            allow_24_7_disabling=True,
            deploy_env_24_7_set=deploy_env_24_7_set,
            deploy_env_weekend_set=deploy_env_weekend_set,
        )

        factory.set_attrs_from_alt_stack(self, base_stack, factory.ALB_PORT_)
        factory.set_attrs_from_alt_stack(self, base_stack, factory.ECS_SG_)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_schedule_windows(self, factory.ECS_)

        for i in [
            factory.STORAGE_S3_BUCKET_NAME_,
            factory.STORAGE_S3_CDK_STACK_NAME_,
            factory.STORAGE_S3_CHECKSUM_ALGORITHM_,
            factory.STORAGE_S3_ENCRYPTION_CONTEXT_KEY_,
            factory.STORAGE_S3_KMS_KEY_,
        ]:
            factory.set_attrs_from_alt_stack(self, storage_stack, i)

        self.env_meta: dict = env_meta
        self.price_class: cloudfront.PriceClass = factory.get_cloudfront_dist_price_class(self)
        self.storage_stack: CdkBkgStorageStack = storage_stack

        self.status_route: str = "3SJ6G7aSpi4S"

        self.fqdn: str = None
        self.fqdn_private: str = None
        if subdomain := getattr(self, factory.SUBDOMAIN_, None):
            hosted_zone_name: str = getattr(base_stack, factory.HOSTED_ZONE_NAME_)
            self.fqdn = factory.join_sep_dot([subdomain, hosted_zone_name])
            self.fqdn_private = factory.join_sep_dot([subdomain, factory.get_attr_env_region(self), hosted_zone_name])

        project_name_comp_props: list[str] = factory.get_attr_project_name_comp_props(self)
        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self)

        # ---------- EC2 ALB & CloudFront ----------

        # Application Load Balancer (ALB) for Bkg Mirco-service
        alb: elasticloadbalancing.ApplicationLoadBalancer = factory.elasticloadbalancing_application_load_balancer(
            self, getattr(base_stack, factory.ALB_SG_)
        )

        # CloudFront Distribution
        cf_origin_path: str = factory.SEP_FW_
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

        factory.set_attrs_url(self, cf_origin_path)
        factory.cfn_output_url(self)

        # Target group for Bkg Mirco-service ALB - to make resources containers discoverable by the ALB
        alb_target_group: elasticloadbalancing.ApplicationTargetGroup = (
            factory.elasticloadbalancing_application_target_group(
                self,
                elasticloadbalancing.TargetType.IP,
                health_check_path=factory.elasticloadbalancing_application_target_group_health_check_path_status_route(
                    self, cf_origin_path
                ),
            )
        )

        # Add listener to ALB - only allow HTTPS connections
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
            [alb_target_group],
            [(cf_origin_custom_header, cf_origin_custom_header_secret)],
        )

        # ---------- ECS ----------

        s3_cdk_stack_name: str = factory.get_cdk_stack_name_short(self.stack_name).lower()
        ecs_exec_role: iam.Role = factory.iam_role_ecs_task(
            self,
            f"Role used by {word_map_project_name_comp} ECS task definitions.",
            managed_policies=factory.ecs_task_managed_policies_list(),
            custom_policies=factory.iam_policy_statement_ecs_access_to_sns(self)
            + [
                factory.iam_policy_statement_ecs_exec(),
                factory.iam_policy_statement_kmy_key_decrypt(self),
                factory.iam_policy_statement_secretsmanager_get_secret_value(self),
                factory.iam_policy_statement_service_role_for_ecs(self),
                factory.iam_policy_statement_ssm_get_parameter(self),
            ]
            + factory.iam_policy_statement_ecs_access_to_dynamodb(database_stack.dydb_table.table_arn)
            + factory.iam_policy_statement_ecs_access_to_s3(
                self,
                s3_cdk_stack_name,
                [s3_cdk_stack_name, getattr(self, factory.STORAGE_S3_CDK_STACK_NAME_)],
            ),
        )

        ecs_task_role: iam.Role = ecs_exec_role

        ses_lambda_func.grant_invoke(ecs_exec_role)

        # ECS task definition
        ecs_task_definition_container_memory_mib: int = 16384
        ecs_task_definition_container_cpu_units: int = int(ecs_task_definition_container_memory_mib / 2)
        ecs_task_definition: ecs.TaskDefinition = factory.ecs_fargate_service_task_definition(
            self,
            str(ecs_task_definition_container_cpu_units),
            str(ecs_task_definition_container_memory_mib),
            ecs_exec_role,
            ecs_task_role,
        )

        self.ecs_container_names: dict[str, str] = {}

        ecs_container_secret: secretsmanager.ISecret = getattr(base_stack, factory.ECS_CONTAINER_SECRET_)
        weatherapi_key: ecs.Secret = ecs.Secret.from_secrets_manager(
            secret=ecs_container_secret, field="WEATHERAPI_KEY"
        )
        ecs_container_service_access_secret: secretsmanager.ISecret = getattr(
            base_stack, factory.ECS_CONTAINER_SERVICE_ACCESS_SECRET_
        )
        ecs_container_secrets_base: dict[str, ecs.Secret] = {
            "LIONAPI_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="LIONAPI_API_KEY"),
            "MAIL_PASSWORD": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="MAIL_PASSWORD"),
            "WEATHERAPI_API_KEY": weatherapi_key,
            "WEATHERBIT_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="WEATHERBIT_KEY"),
            "BROKER_PASSWORD": factory.ecs_secret_from_secrets_manager(
                self, broker_stack.mq_rabbitmq_pw_secret.secret_name, broker_stack.mq_rabbitmq_pw_secret.secret_full_arn
            ),
            "REDIS_PASSWORD": factory.ecs_secret_from_secrets_manager_redis_password(
                self, cache_stack.ec_redis_auth_secret
            ),
            "SERVICE_ACCESS_SECRET": factory.ecs_secret_from_secrets_manager(
                self,
                ecs_container_service_access_secret.secret_name,
                ecs_container_service_access_secret.secret_full_arn,
                full_content=True,
            ),
        }

        factory.set_attrs_url_private(self, cf_origin_path)
        factory.cfn_output_url_private(self)
        self.base_url: str = factory.get_url_for_ms_from_cdk_stack(self)

        for comp_sub, (
            word_map_comp_sub,
            comp_sub_port,
            api_container,
            cpu_unit_weighting,
        ) in project_name_comp_subs.items():
            project_name_comp_sub: str = factory.join_sep_score(project_name_comp_props + [comp_sub])

            ecs_task_container_log_group: logs.LogGroup = factory.logs_log_group_ecs_task_container(
                self, project_name_comp=project_name_comp_sub
            )

            is_internal: bool = getattr(self, factory.DEPLOY_ENV_INTERNAL_)
            mq_rabbitmq_broker_attr_amqp_endpoints: list[str] = broker_stack.mq_rabbitmq_broker.attr_amqp_endpoints
            ecs_container_environment: dict[str, str] = {
                "APP_NAME": factory.join_sep_space([word_map_project_name_comp, word_map_comp_sub]),
                "INTERNAL_NAME": factory.join_sep_score([project_name_comp_sub, deploy_env]),
                "BASE_URL": self.base_url,
                "BROKER_DETAILS": factory.join_sep_comma(
                    [
                        Fn.select(i, mq_rabbitmq_broker_attr_amqp_endpoints)
                        for i in range(0, len(mq_rabbitmq_broker_attr_amqp_endpoints))
                    ]
                ),
                "BROKER_QUEUE": factory.get_attr_project_name_comp(self),
                "BROKER_USER": broker_stack.mq_rabbitmq_user,
                "DEBUG": json.dumps(is_internal),
                "DYNAMODB_CDK_STACK_REGION": factory.get_attr_env_region(self),
                "DYNAMODB_KMS_KEY": factory.get_attr_kms_key_stack(database_stack).key_arn,
                "DYNAMODB_PARTITION_KEY": database_stack.dydb_partition_key,
                "DYNAMODB_SORT_KEY": database_stack.dydb_sort_key,
                "DYNAMODB_TABLE_NAME": database_stack.dydb_table_name,
                "DYNAMODB_TTL": database_stack.dydb_time_to_live_attribute,
                "LIONAPI_BASE_URL": factory.get_url_for_ms_from_cdk_stack(self, lion_ms_stack),
                "LOKY_MAX_CPU_COUNT": str(1),
                "MAIL_HOST": "smtp.office365.com",  # TODO: (IMPORTANT) Remove when AWS SES replaces mail sending
                "MAIL_PORT": str(587),  # TODO: (IMPORTANT) Remove when AWS SES replaces mail sending
                "MAIL_USER": getattr(base_stack, factory.MAIL_USER_),
                "REDIS_HOST": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_address,
                "REDIS_HOST_READER": cache_stack.ec_redis_cluster_rep_group.attr_reader_end_point_address,
                "REDIS_PORT": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_port,
                "REDIS_SSL": json.dumps(True),
                "S3_BUCKET_NAME": getattr(self, factory.STORAGE_S3_BUCKET_NAME_),
                "S3_CDK_STACK_ACCOUNT_ID": factory.get_attr_env_account(self),
                "S3_CDK_STACK_NAME": s3_cdk_stack_name,
                "S3_CDK_STACK_REGION": factory.get_attr_env_region(self),
                "S3_CHECKSUM_ALGORITHM": getattr(self, factory.STORAGE_S3_CHECKSUM_ALGORITHM_),
                "S3_ENCRYPTION_CONTEXT_KEY": getattr(self, factory.STORAGE_S3_ENCRYPTION_CONTEXT_KEY_),
                "S3_KMS_KEY": getattr(self, factory.STORAGE_S3_KMS_KEY_).key_arn,
                "S3_TAGS": json.dumps(factory.get_s3_bucket_tags(self), default=str),
                "SERVICE_ACCESS": json.dumps(
                    {
                        k: {
                            "MAIL_USER": v,
                            "TASK_SUBSCRIPTIONS": dict(ecs_container_service_access_task_subscriptions).get(k, []),
                        }
                        for k, v in ecs_container_service_access.items()
                    }
                ),
                "SES_CDK_STACK_REGION": factory.get_attr_env_region(self),
                "SES_LAMBDA_FUNCTION_NAME": ses_lambda_func.function_name,
                "SES_REPLY_TO": json.dumps([getattr(base_stack, factory.MAIL_USER_SUPPORT_)]),
                "SES_SUPPORT_MAIL_USERNAME": getattr(base_stack, factory.MAIL_USER_SUPPORT_),
                "SNS_CDK_STACK_REGION": factory.get_attr_env_region(self),
                "SNS_PLATFORM_APPLICATION_ARN": factory.format_arn_custom(
                    self,
                    service=factory.SNS_,
                    resource=factory.APP_,
                    resource_name=factory.get_path([factory.GCM_.upper(), factory.SEP_EMPTY_]),
                ),
            }
            ecs_container_secrets: dict[str, ecs.Secret] = dict(ecs_container_secrets_base)

            if api_container:
                self.ecs_task_container_log_group = ecs_task_container_log_group
                ecs_container_environment = {
                    **ecs_container_environment,
                    **{
                        "APP_NAME_API": factory.join_sep_space(
                            [
                                factory.get_attr_word_map_project_name_comp(self, inc_deploy_env=False),
                                word_map_comp_sub,
                                factory.SERVER_.capitalize(),
                            ]
                        ),
                        "INTERNAL_NAME_API": factory.join_sep_score(project_name_comp_props + [comp_sub, deploy_env]),
                        "OPENAPI_OFF": json.dumps(bool(not is_internal)),
                        "PASSLIB_SCHEMES": factory.PASSLIB_SCHEMES,
                        "STATUS_ROUTE": self.status_route,
                        "TOKEN_ALGORITHM": factory.TOKEN_ALGORITHM,
                        "TOKEN_DURATION_MINS": str(30),
                        "UVICORN_HOST": factory.WILDCARD_ADDRESS,
                        "UVICORN_LOG_LEVEL": "debug" if is_internal else factory.INFO_,
                        "UVICORN_PORT": str(getattr(self, factory.ALB_PORT_)),
                        "UVICORN_WORKERS": str(4),
                    },
                }
                for k, v in {
                    factory.join_sep_under([factory.SECRET_, factory.KEY_]).upper(): factory.SECRET_KEY_SECRET_,
                    factory.join_sep_under([factory.TOKEN_, factory.KEY_]).upper(): factory.TOKEN_KEY_SECRET_,
                }.items():
                    if is_internal:
                        ecs_container_environment[k] = factory.join_sep_under([deploy_env.upper(), k])
                    else:
                        ecs_container_secrets[k] = factory.get_ecs_secret_from_secrets_manager(self, base_stack, v)
                ecs_container_api_keys_secret: secretsmanager.ISecret = getattr(
                    base_stack, factory.ECS_CONTAINER_API_KEYS_SECRET_
                )
                ecs_container_secrets["API_KEYS"] = factory.ecs_secret_from_secrets_manager(
                    self,
                    ecs_container_api_keys_secret.secret_name,
                    ecs_container_api_keys_secret.secret_full_arn,
                    full_content=True,
                )
            elif not api_container:
                ecs_container_environment["MPLCONFIGDIR"] = "/tmp/"

            self.ecs_container_names[comp_sub] = factory.get_ecs_container_name(
                self, project_name_comp=project_name_comp_sub
            )

            factory.ecs_fargate_service_task_definition_add_container(
                self,
                ecs_task_definition,
                ecs.RepositoryImage.from_ecr_repository(
                    repository=base_stack.repos[project_name_comp_sub], tag=deploy_env
                ),
                self.ecs_container_names[comp_sub],
                comp_sub_port,
                ecs_task_definition_container_memory_mib,
                ecs_task_container_log_group,
                ecs_container_environment,
                ecs_container_secrets,
                project_name_comp=project_name_comp_sub,
                cpu=(
                    int(ecs_task_definition_container_cpu_units * cpu_unit_weighting)
                    if cpu_unit_weighting is not None
                    else None
                ),
                shared=len(project_name_comp_subs) - 1,
            )

        # The ECS Service used for deploying tasks
        self.ecs_service: ecs.FargateService = factory.ecs_fargate_service(
            self,
            ecs_task_definition,
            self.fqdn_private,
            self.ecs_task_container_log_group,
            custom_filter_patterns={"ugex": '?"UNEXPECTED GATEWAY EXCEPTION"'},
            target_group=alb_target_group,
        )
