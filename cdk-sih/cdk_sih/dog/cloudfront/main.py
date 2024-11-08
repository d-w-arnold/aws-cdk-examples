from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.cloudfront.main import CdkCloudFrontStack


class CdkDogCloudFrontStack(CdkCloudFrontStack):
    def __init__(
        self,
        factory: CdkConstructsFactory,
        custom_val: str = None,
        wordpress: bool = False,
        **kwargs,
    ) -> None:
        if custom_val is not None:
            setattr(self, factory.PRODUCT_CUSTOM_, custom_val)

        super().__init__(
            factory=factory,
            wordpress=wordpress,
            **kwargs,
        )
