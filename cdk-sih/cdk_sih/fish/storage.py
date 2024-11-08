from cdk_sih.generic.storage import CdkStorageStack


class CdkFishStorageStack(CdkStorageStack):
    def __init__(self, **kwargs) -> None:
        # pylint: disable=useless-parent-delegation
        super().__init__(**kwargs)
