from cdk_sih.generic.storage import CdkStorageStack


class CdkBkgStorageStack(CdkStorageStack):
    def __init__(self, **kwargs) -> None:
        self.lifecycle_rules_delete: dict[str, int] = {"tmp/": 31}

        super().__init__(**kwargs)
