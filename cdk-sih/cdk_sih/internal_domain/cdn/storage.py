from aws_cdk import (
    Stack,
    aws_s3 as s3,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.cdn.base import CdkCdnBaseStack


class CdkCdnStorageStack(Stack):
    def __init__(
        self,
        base_stack: CdkCdnBaseStack,
        component: str,
        deploy_env: str,
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta)

        self.s3_bucket_: s3.Bucket = factory.s3_bucket(
            self, factory.join_sep_empty([project_name, component, deploy_env])
        )
