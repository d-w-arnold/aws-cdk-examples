from aws_cdk import Stack, aws_efs as efs

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.dog.base import CdkDogBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkDogFsStack(Stack):
    def __init__(
        self,
        base_stack: CdkDogBaseStack,
        component: str,
        deploy_env: str,
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta)

        factory.set_attrs_kms_key_stack(self)

        # ---------- EFS ----------

        self.efs_file_system: efs.FileSystem = factory.efs_file_system(self, getattr(base_stack, factory.ECS_SG_))

        factory.cfn_output_efs_file_system_id(
            self, self.efs_file_system, "WordPress to share file assets between nodes in the cluster"
        )
