from cdk_sih.generic.notif import CdkNotifStack


class CdkCatNotifStack(CdkNotifStack):
    def __init__(self, **kwargs) -> None:
        # pylint: disable=useless-parent-delegation
        super().__init__(**kwargs)
