from cdk_sih.generic.database import CdkDatabaseStack


class CdkCatDatabaseStack(CdkDatabaseStack):
    def __init__(self, **kwargs) -> None:
        super().__init__(inc_proxy=True, **kwargs)
