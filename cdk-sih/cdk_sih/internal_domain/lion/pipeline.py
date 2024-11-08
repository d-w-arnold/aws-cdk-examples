from aws_cdk import aws_ecs as ecs

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.pipeline import CdkPipelineStack
from cdk_sih.internal_domain.lion.ms import CdkLionMsStack


class CdkLionPipelineStack(CdkPipelineStack):
    def __init__(
        self,
        factory: CdkConstructsFactory,
        ms_stack: CdkLionMsStack,
        **kwargs,
    ) -> None:
        self.ecs_container_name: str = ms_stack.ecs_container_name
        self.ecs_service: ecs.FargateService = ms_stack.ecs_service

        super().__init__(
            bitbucket_workspace=factory.BITBUCKET_WORKSPACE_SIH_INFR_INN,
            factory=factory,
            **kwargs,
        )
