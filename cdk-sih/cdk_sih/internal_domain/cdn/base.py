from aws_cdk import (
    Stack,
)

from cdk_sih.constructs.factory import (
    CdkConstructsFactory,
)


class CdkCdnBaseStack(Stack):
    def __init__(
        self,
        component: str,
        factory: CdkConstructsFactory,
        project_name: str,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_project_name_comp(self, project_name, component)

        # ---------- Route 53 ----------

        factory.set_attrs_hosted_zone(self)
