from aws_cdk import aws_ecs as ecs
from cdk_sih.cow.gw import CdkCowGwStack
from cdk_sih.generic.pipeline import CdkPipelineStack


class CdkCowPipelineStack(CdkPipelineStack):
    def __init__(self, gw_stack: CdkCowGwStack, **kwargs) -> None:
        self.ecs_container_name: str = gw_stack.ecs_container_name
        self.ecs_service: ecs.FargateService = gw_stack.ecs_service

        super().__init__(**kwargs)
