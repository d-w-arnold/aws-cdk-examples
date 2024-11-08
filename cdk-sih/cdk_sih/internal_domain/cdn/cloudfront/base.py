from cdk_sih.generic.cloudfront.base import CdkCloudFrontBaseStack


class CdkCdnCloudFrontBaseStack(CdkCloudFrontBaseStack):
    def __init__(self, **kwargs) -> None:
        # pylint: disable=useless-parent-delegation
        super().__init__(**kwargs)
