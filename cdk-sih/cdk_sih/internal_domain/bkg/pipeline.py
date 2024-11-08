from typing import Union

from aws_cdk import aws_ecs as ecs
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.pipeline import CdkPipelineStack
from cdk_sih.internal_domain.bkg.ms import CdkBkgMsStack


class CdkBkgPipelineStack(CdkPipelineStack):
    def __init__(
        self,
        factory: CdkConstructsFactory,
        ms_stack: CdkBkgMsStack,
        **kwargs,
    ) -> None:
        self.ecs_container_name: Union[str, dict[str, str]] = ms_stack.ecs_container_names
        self.ecs_service: ecs.FargateService = ms_stack.ecs_service

        super().__init__(
            bitbucket_workspace=factory.BITBUCKET_WORKSPACE_SIH_INFR_INN,
            factory=factory,
            **kwargs,
        )
