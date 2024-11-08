from aws_cdk import (
    Stack,
    aws_elasticache as elasticache,
    aws_secretsmanager as secretsmanager,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkCacheStack(Stack):
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
        vpc_stack: CdkVpcSihStack,
        ec_redis_auto_scaling_custom: bool = None,
        ec_redis_instance_type_custom: str = None,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

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

        factory.set_attrs_from_alt_stack(self, base_stack, factory.EC_REDIS_SG_)
        factory.set_attrs_from_alt_stack(self, base_stack, factory.REDIS_PORT_)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_schedule_windows(self, factory.ELASTICACHE_)

        self.env_meta: dict = env_meta

        self.ec_redis_props: list[str] = [factory.EC_, factory.REDIS_]

        ec_redis_auth_props: list[str] = self.ec_redis_props + [factory.AUTH_]
        self.ec_redis_auth_secret: secretsmanager.Secret = factory.secrets_manager_secret(
            self,
            ec_redis_auth_props,
            f"ElastiCache Redis AUTH secret for {factory.get_attr_word_map_project_name_comp(self)}.",
            factory.get_construct_name(self, ec_redis_auth_props),
            password_length=128,
        )

        self.ec_redis_cluster_rep_group: elasticache.CfnReplicationGroup = factory.elasticache_replication_group(
            self,
            self.ec_redis_auth_secret,
            ec_redis_auto_scaling_custom=ec_redis_auto_scaling_custom,
            ec_redis_instance_type_custom=ec_redis_instance_type_custom,
        )
