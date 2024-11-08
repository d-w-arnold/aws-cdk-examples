import json

from aws_cdk import (
    aws_ecs as ecs,
    aws_secretsmanager as secretsmanager,
)
from cdk_sih.cat.base import CdkCatBaseStack
from cdk_sih.cat.cache import CdkCatCacheStack
from cdk_sih.cat.database import CdkCatDatabaseStack
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.gw import CdkGwStack
from cdk_sih.internal_domain.bkg.ms import CdkBkgMsStack
from cdk_sih.internal_domain.lion.ms import CdkLionMsStack
from cdk_sih.mail.ms import CdkMailMsStack
from cdk_sih.pdf.ms import CdkPdfMsStack


class CdkCatGwStack(CdkGwStack):
    def __init__(
        self,
        base_stack: CdkCatBaseStack,
        bkg_ms_stack: CdkBkgMsStack,
        cache_stack: CdkCatCacheStack,
        database_stack: CdkCatDatabaseStack,
        deploy_env: str,
        lion_ms_stack: CdkLionMsStack,
        factory: CdkConstructsFactory,
        mail_ms_stack: CdkMailMsStack,
        pdf_ms_stack: CdkPdfMsStack,
        **kwargs,
    ) -> None:
        super().__init__(
            base_stack=base_stack,
            deploy_env=deploy_env,
            factory=factory,
            ecs_task_definition_container_memory_mib=8192,
            storage_bkg_stack=bkg_ms_stack.storage_stack,
            **kwargs,
        )

        # ---------- ECS ----------

        mail_ms_stack.ses_lambda_func.grant_invoke(self.ecs_exec_role)
        pdf_ms_stack.pdf_lambda_func.grant_invoke(self.ecs_exec_role)

        ecs_container_environment: dict[str, str] = {
            "ADDITIONAL_ALLOWED_ORIGINS": self.get_additional_allowed_origins(
                factory.get_additional_allowed_origins_deploy_envs(deploy_env),
                dev_ports=[3000, 4173, 5173],
                staging_ports=[5174, 5175],
            ),
            "APP_NAME": self.get_app_name(self.admin),
            "BACKGROUND_URL": self.get_url_background(self, bkg_ms_stack),
            "BASE_URL": getattr(self, factory.URL_PRIVATE_),
            "CPU_CORES": self.ecs_task_definition_container_cpu_cores,
            "DB_ENGINE_OPTIONS": json.dumps(
                self.get_sqlalchemy_database_engine_options(pool_size=80, max_overflow=100)
            ),
            "DB_URL": self.get_sqlalchemy_database_uri(database_stack, deploy_env),
            "DEBUG": self.debug,
            "LIONAPI_BASE_URL": factory.get_url_for_ms_from_cdk_stack(self, lion_ms_stack),
            "FIREBASE_ACCOUNT_INFO": base_stack.firebase_account_info_param.string_value,
            "INTERNAL_NAME": self.internal_name,
            "LOKALISE_PROJECT_ID": "????????",
            "LOKALISE_USERNAME": "lokalise@foobar.co.uk",
            "MAIL_USERNAME": getattr(base_stack, factory.MAIL_USER_),
            "OPENAPI_OFF": self.openapi_off,
            "PASSLIB_SCHEMES": self.passlib_schemes,
            "PDF_CDK_STACK_ACCOUNT_ID": factory.get_attr_env_account(self),
            "PDF_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "PDF_LAMBDA_FUNCTION_NAME": pdf_ms_stack.pdf_lambda_func.function_name,
            "PORTAL_BASE_URL": self.url_portal,
            "REDIS_HOST": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_address,
            "REDIS_HOST_READER": cache_stack.ec_redis_cluster_rep_group.attr_reader_end_point_address,
            "REDIS_PORT": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_port,
            "REDIS_SSL": self.redis_ssl,
            "S3_BUCKET_NAME": getattr(self, factory.STORAGE_S3_BUCKET_NAME_),
            "S3_CDK_STACK_ACCOUNT_ID": factory.get_attr_env_account(self),
            "S3_CDK_STACK_NAME": self.s3_cdk_stack_name,
            "S3_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "S3_CHECKSUM_ALGORITHM": getattr(self, factory.STORAGE_S3_CHECKSUM_ALGORITHM_),
            "S3_ENCRYPTION_CONTEXT_KEY": getattr(self, factory.STORAGE_S3_ENCRYPTION_CONTEXT_KEY_),
            "S3_KMS_KEY": getattr(self, factory.STORAGE_S3_KMS_KEY_).key_arn,
            "S3_TAGS": json.dumps(factory.get_s3_bucket_tags(self), default=str),
            "S3_BKG_BUCKET_NAME": getattr(self, factory.STORAGE_S3_BKG_BUCKET_NAME_),
            "S3_BKG_CDK_STACK_ACCOUNT_ID": factory.get_attr_env_account(self),
            "S3_BKG_CDK_STACK_NAME": self.s3_cdk_stack_name,
            "S3_BKG_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "S3_BKG_CHECKSUM_ALGORITHM": getattr(self, factory.STORAGE_S3_BKG_CHECKSUM_ALGORITHM_),
            "S3_BKG_ENCRYPTION_CONTEXT_KEY": getattr(self, factory.STORAGE_S3_BKG_ENCRYPTION_CONTEXT_KEY_),
            "S3_BKG_KMS_KEY": getattr(self, factory.STORAGE_S3_BKG_KMS_KEY_).key_arn,
            "S3_BKG_TAGS": json.dumps(factory.get_s3_bucket_tags(bkg_ms_stack), default=str),
            "SES_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "SES_LAMBDA_FUNCTION_NAME": mail_ms_stack.ses_lambda_func.function_name,
            "SES_REPLY_TO": json.dumps([getattr(base_stack, factory.MAIL_USER_SUPPORT_)]),
            "SES_SUPPORT_MAIL_USERNAME": getattr(base_stack, factory.MAIL_USER_SUPPORT_),
            "SNS_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "SNS_PLATFORM_APPLICATION_ARN": self.sns_platform_application_arn,
            "STATUS_ROUTE": self.status_route,
            "SUNBURN_RISK_NOTIFICATIONS": json.dumps(True),
            "TOKEN_ALGORITHM": self.token_algorithm,
            "TOKEN_DURATION_MINS": str(115200),
            "TOKEN_REFRESH_DURATION_MINS": str(144000),
            "UVICORN_HOST": self.local_host,
            "UVICORN_LOG_LEVEL": self.log_level,
            "UVICORN_PORT": str(getattr(self, factory.ALB_PORT_)),
            "UVICORN_WORKERS": self.workers,
        }
        if getattr(self, factory.DEPLOY_ENV_NOT_24_7_):
            ecs_container_environment["DAILY_TASK_SLOT_LOCAL_START"] = str(14)
            ecs_container_environment["DAILY_TASK_TIME_SLOT_PERIOD"] = str(4)
        if not self.is_internal:
            ecs_container_environment["ARCHIVE_DELETION"] = json.dumps(False)
            ecs_container_environment["ARCHIVE_ENABLED"] = json.dumps(False)

        ecs_container_secret: secretsmanager.ISecret = getattr(base_stack, factory.ECS_CONTAINER_SECRET_)
        ecs_container_secrets: dict[str, ecs.Secret] = {
            "BACKGROUND_API_KEY": ecs.Secret.from_secrets_manager(
                secret=ecs_container_secret, field="BACKGROUND_API_KEY"
            ),
            "DB_PASSWORD": factory.ecs_secret_from_secrets_manager_db_password(
                self, database_stack.db_api_user_creds_secret
            ),
            "LIONAPI_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="LIONAPI_API_KEY"),
            "FIREBASE_ACCOUNT_INFO_PRIVATE_KEY": ecs.Secret.from_secrets_manager(
                secret=ecs_container_secret, field="FIREBASE_ACCOUNT_INFO_PRIVATE_KEY"
            ),
            "LOKALISE_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="LOKALISE_API_KEY"),
            "RECAPTCHA_SECRET": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="RECAPTCHA_SECRET"),
            "REDIS_PASSWORD": factory.ecs_secret_from_secrets_manager_redis_password(
                self, cache_stack.ec_redis_auth_secret
            ),
            "WEATHERAPI_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="WEATHERAPI_KEY"),
            "WORDNIK_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="WORDNIK_API_KEY"),
        }
        for k, v in {
            self.ecomm_api_key: factory.E_COMMERCE_API_KEY_SECRET_,
            self.secret_key: factory.SECRET_KEY_SECRET_,
            self.token_key: factory.TOKEN_KEY_SECRET_,
        }.items():
            if self.is_internal:
                ecs_container_environment[k] = factory.join_sep_under([deploy_env.upper(), k])
            else:
                ecs_container_secrets[k] = factory.get_ecs_secret_from_secrets_manager(self, base_stack, v)

        self.ecs_service: ecs.FargateService = self.get_ecs_service(
            base_stack.repos[factory.get_attr_project_name_comp(self)],
            ecs_container_environment,
            ecs_container_secrets,
        )
