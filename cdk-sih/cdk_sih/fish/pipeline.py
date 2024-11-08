from aws_cdk import aws_ecs as ecs
from cdk_sih.fish.gw import CdkFishGwStack
from cdk_sih.generic.pipeline import CdkPipelineStack


class CdkFishPipelineStack(CdkPipelineStack):
    def __init__(self, gw_stack: CdkFishGwStack, **kwargs) -> None:
        self.ecs_container_name: str = gw_stack.ecs_container_name
        self.ecs_service: ecs.FargateService = gw_stack.ecs_service

        super().__init__(**kwargs)
