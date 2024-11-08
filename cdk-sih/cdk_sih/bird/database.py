from cdk_sih.generic.database import CdkDatabaseStack


class CdkBirdDatabaseStack(CdkDatabaseStack):
    def __init__(self, **kwargs) -> None:
        super().__init__(inc_proxy=True, **kwargs)
