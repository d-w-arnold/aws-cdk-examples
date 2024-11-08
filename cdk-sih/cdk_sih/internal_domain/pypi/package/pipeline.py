from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.pipeline import CdkPipelineStack
from cdk_sih.internal_domain.pypi.package.base import CdkPypiPackageBaseStack


class CdkPypiPackagePipelineStack(CdkPipelineStack):
    def __init__(
        self,
        base_stack: CdkPypiPackageBaseStack,
        branch: str,
        factory: CdkConstructsFactory,
        project_name: str,
        **kwargs,
    ) -> None:
        setattr(self, factory.DEPLOY_ENV_DEV_, bool(branch == factory.DEV_))
        setattr(self, factory.PROJECT_NAME_COMP_, project_name)
        setattr(self, factory.VERSION_META_PARAM_NAME_, base_stack.version_meta_param_names[project_name])

        super().__init__(
            base_stack=base_stack,
            bitbucket_workspace=factory.BITBUCKET_WORKSPACE_SIH_INFR_INN,
            component=None,
            deploy_env=branch,
            env_meta=None,
            factory=factory,
            pipeline_base=False,
            project_name=None,
            project_name_comp_list=[project_name],
            pypi_package=True,
            tag_deploy=False,
            **kwargs,
        )
