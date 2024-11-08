from cdk_sih.generic.cache import CdkCacheStack


class CdkFishCacheStack(CdkCacheStack):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
