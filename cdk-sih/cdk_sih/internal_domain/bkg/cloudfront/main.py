from cdk_sih.generic.cloudfront.main import CdkCloudFrontStack


class CdkBkgCloudFrontStack(CdkCloudFrontStack):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
