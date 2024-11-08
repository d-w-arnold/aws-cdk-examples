from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.cache import CdkCacheStack


class CdkLionCacheStack(CdkCacheStack):
    def __init__(self, env_meta: dict, factory: CdkConstructsFactory, **kwargs) -> None:

        super().__init__(
            env_meta=env_meta,
            factory=factory,
            ec_redis_auto_scaling_custom=False,
            ec_redis_instance_type_custom=factory.M6G_LARGE_,
            **kwargs
        )
