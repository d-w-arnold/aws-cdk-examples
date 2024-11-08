from aws_cdk import Stack, aws_efs as efs

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.pypi.base import CdkPypiBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkPypiStorageStack(Stack):
    def __init__(
        self,
        base_stack: CdkPypiBaseStack,
        component: str,
        factory: CdkConstructsFactory,
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_kms_key_stack(self, alt_stack=base_stack)

        # EFS file system to store packages
        self.efs_file_system: efs.FileSystem = factory.efs_file_system(self, base_stack.ec2_sg)
