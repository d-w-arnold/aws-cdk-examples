from cdk_sih.generic.cache import CdkCacheStack


class CdkBirdCacheStack(CdkCacheStack):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
