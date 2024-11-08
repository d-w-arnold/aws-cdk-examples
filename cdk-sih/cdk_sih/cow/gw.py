import json

from aws_cdk import (
    aws_ecs as ecs,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.cow.base import CdkCowBaseStack
from cdk_sih.cow.cache import CdkCowCacheStack
from cdk_sih.cow.database import CdkCowDatabaseStack
from cdk_sih.generic.gw import CdkGwStack


class CdkCowGwStack(CdkGwStack):
    def __init__(
        self,
        base_stack: CdkCowBaseStack,
        cache_stack: CdkCowCacheStack,
        database_stack: CdkCowDatabaseStack,
        deploy_env: str,
        factory: CdkConstructsFactory,
        **kwargs,
    ) -> None:
        super().__init__(
            base_stack=base_stack,
            deploy_env=deploy_env,
            factory=factory,
            storage_stack=None,
            **kwargs,
        )

        # ---------- ECS ----------

        ecs_container_environment: dict[str, str] = {
            "ADDITIONAL_ALLOWED_ORIGINS": self.get_additional_allowed_origins(
                factory.get_additional_allowed_origins_deploy_envs(deploy_env),
                dev_ports=[3000, 4173, 5173],
                staging_ports=[5174, 5175],
            ),
            "APP_NAME": self.get_app_name(self.admin),
            "BASE_URL": getattr(self, factory.URL_PRIVATE_),
            "DB_ENGINE_OPTIONS": json.dumps(self.get_sqlalchemy_database_engine_options()),
            "DB_URL": self.get_sqlalchemy_database_uri(database_stack, deploy_env, secret_db_pw=False),
            "DEBUG": json.dumps(True),  # Local dev against Sih-Preview deploy env
            "GW_AUTOIOD": self.auto_iod,
            "INTERNAL_NAME": self.internal_name,
            "OPENAPI_OFF": json.dumps(False),  # Local dev against Sih-Preview deploy env
            "PASSLIB_SCHEMES": self.passlib_schemes,
            "REDIS_HOST": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_address,
            "REDIS_HOST_READER": cache_stack.ec_redis_cluster_rep_group.attr_reader_end_point_address,
            "REDIS_PORT": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_port,
            "REDIS_SSL": self.redis_ssl,
            "STATUS_ROUTE": self.status_route,
            "TOKEN_ALGORITHM": self.token_algorithm,
            "UVICORN_HOST": self.local_host,
            "UVICORN_LOG_LEVEL": "debug",  # Local dev against Sih-Preview deploy env
            "UVICORN_PORT": str(getattr(self, factory.ALB_PORT_)),
            "UVICORN_WORKERS": self.workers,
            "VERSION": deploy_env,
            "WEB_PORTAL_URL": self.url_portal,
            # "TOKEN_DURATION_MINS": self.token_duration_mins,  # (?) Using default value in Gw app
            # "TOKEN_REFRESH_DURATION_MINS": self.token_refresh_duration_mins,  # (?) Using default value in Gw app
        }

        ecs_container_secrets: dict[str, ecs.Secret] = {
            "REDIS_PASSWORD": factory.ecs_secret_from_secrets_manager_redis_password(
                self, cache_stack.ec_redis_auth_secret
            ),
        }
        for k, v in {self.token_key: factory.TOKEN_KEY_SECRET_}.items():
            if self.is_internal:
                ecs_container_environment[k] = factory.join_sep_under([deploy_env.upper(), k])
            else:
                ecs_container_secrets[k] = factory.get_ecs_secret_from_secrets_manager(self, base_stack, v)

        self.ecs_service: ecs.FargateService = self.get_ecs_service(
            base_stack.repos[factory.get_attr_project_name_comp(self)],
            ecs_container_environment,
            ecs_container_secrets,
        )
