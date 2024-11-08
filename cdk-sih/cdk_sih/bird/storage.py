from cdk_sih.generic.storage import CdkStorageStack


class CdkBirdStorageStack(CdkStorageStack):
    def __init__(self, **kwargs) -> None:
        self.lifecycle_rules_delete: dict[str, int] = {"insights/": 186}

        super().__init__(**kwargs)
