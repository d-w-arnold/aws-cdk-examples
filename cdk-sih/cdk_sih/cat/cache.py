from cdk_sih.generic.cache import CdkCacheStack


class CdkCatCacheStack(CdkCacheStack):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
