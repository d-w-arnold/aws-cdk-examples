from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.cache import CdkCacheStack


class CdkDogCacheStack(CdkCacheStack):
    def __init__(self, factory: CdkConstructsFactory, custom_val: str = None, **kwargs) -> None:
        if custom_val is not None:
            setattr(self, factory.PRODUCT_CUSTOM_, custom_val)

        super().__init__(
            factory=factory,
            **kwargs,
        )
