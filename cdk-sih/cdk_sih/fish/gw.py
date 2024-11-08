import json

from aws_cdk import (
    aws_ecs as ecs,
    aws_secretsmanager as secretsmanager,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.fish.base import CdkFishBaseStack
from cdk_sih.fish.cache import CdkFishCacheStack
from cdk_sih.fish.database import CdkFishDatabaseStack
from cdk_sih.generic.gw import CdkGwStack
from cdk_sih.mail.ms import CdkMailMsStack


class CdkFishGwStack(CdkGwStack):
    def __init__(
        self,
        base_stack: CdkFishBaseStack,
        cache_stack: CdkFishCacheStack,
        database_stack: CdkFishDatabaseStack,
        deploy_env: str,
        factory: CdkConstructsFactory,
        mail_ms_stack: CdkMailMsStack,
        **kwargs,
    ) -> None:
        super().__init__(
            base_stack=base_stack,
            deploy_env=deploy_env,
            factory=factory,
            **kwargs,
        )

        # ---------- ECS ----------

        mail_ms_stack.ses_lambda_func.grant_invoke(self.ecs_exec_role)

        ecs_container_environment: dict[str, str] = {
            "ADDITIONAL_ALLOWED_ORIGINS": self.get_additional_allowed_origins(
                factory.get_additional_allowed_origins_deploy_envs(deploy_env),
                dev_ports=[2000, 5173, 5174],
                staging_ports=[2000, 5173, 5174],
            ),
            "APP_NAME": self.get_app_name(self.admin),
            "BASE_URL": getattr(self, factory.URL_PRIVATE_),
            "BACKGROUND_DEBUG_LEVEL": str(int(json.loads(self.debug))),
            "BACKGROUND_URL": f"{factory.HTTPS_}www.google.com/search?q=",
            "DB_ENGINE_OPTIONS": json.dumps(self.get_sqlalchemy_database_engine_options()),
            "DB_URL": self.get_sqlalchemy_database_uri(database_stack, deploy_env, secret_db_pw=False),
            "DEBUG": self.debug,
            "FIREBASE_ACCOUNT_INFO": base_stack.firebase_account_info_param.string_value,
            "FIREBASE_NOTIFY_API_URL": f"{factory.HTTPS_}fcm.googleapis.com/v1/projects/fish/messages:send",
            "GW_AUTOIOD": self.auto_iod,
            "INTERNAL_NAME": self.internal_name,
            "MAIL_HOST": self.mail_host,
            "MAIL_PORT": self.mail_port,
            "MAIL_USER": getattr(base_stack, factory.MAIL_USER_),
            "MAIL_USERNAME": getattr(base_stack, factory.MAIL_USER_),
            "OPENAPI_OFF": self.openapi_off,
            "PASSLIB_SCHEMES": self.passlib_schemes,
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
            "SES_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "SES_LAMBDA_FUNCTION_NAME": mail_ms_stack.ses_lambda_func.function_name,
            "SES_REPLY_TO": json.dumps([getattr(base_stack, factory.MAIL_USER_SUPPORT_)]),
            "SES_SUPPORT_MAIL_USERNAME": getattr(base_stack, factory.MAIL_USER_SUPPORT_),
            "STATUS_ROUTE": self.status_route,
            "TOKEN_ALGORITHM": self.token_algorithm,
            "TOKEN_DURATION_MINS": self.token_duration_mins,
            "TOKEN_REFRESH_DURATION_MINS": self.token_refresh_duration_mins,
            "UVICORN_HOST": self.local_host,
            "UVICORN_LOG_LEVEL": self.log_level,
            "UVICORN_PORT": str(getattr(self, factory.ALB_PORT_)),
            "UVICORN_WORKERS": self.workers,
            "WEB_PORTAL_URL": self.url_portal,
        }

        ecs_container_secret: secretsmanager.ISecret = getattr(base_stack, factory.ECS_CONTAINER_SECRET_)
        weatherapi_key: ecs.Secret = ecs.Secret.from_secrets_manager(
            secret=ecs_container_secret, field="WEATHERAPI_KEY"
        )
        ecs_container_secrets: dict[str, ecs.Secret] = {
            "BACKGROUND_API_KEY": ecs.Secret.from_secrets_manager(
                secret=ecs_container_secret, field="BACKGROUND_API_KEY"
            ),
            "MAIL_PASSWORD": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="MAIL_PASSWORD"),
            "RECAPTCHA_SECRET": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="RECAPTCHA_SECRET"),
            "FIREBASE_ACCOUNT_INFO_PRIVATE_KEY": ecs.Secret.from_secrets_manager(
                secret=ecs_container_secret, field="FIREBASE_ACCOUNT_INFO_PRIVATE_KEY"
            ),
            "REDIS_PASSWORD": factory.ecs_secret_from_secrets_manager_redis_password(
                self, cache_stack.ec_redis_auth_secret
            ),
            "WEATHERAPI_API_KEY": weatherapi_key,
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
