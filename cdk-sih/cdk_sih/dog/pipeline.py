from typing import Union

from aws_cdk import aws_ecs as ecs
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.dog.em.main import CdkDogEmStack
from cdk_sih.dog.gw import CdkDogGwStack
from cdk_sih.generic.pipeline import CdkPipelineStack


class CdkDogPipelineStack(CdkPipelineStack):
    def __init__(
        self,
        factory: CdkConstructsFactory,
        gw_stack: Union[CdkDogGwStack, CdkDogEmStack],
        custom_val: str = None,
        **kwargs,
    ) -> None:
        self.ecs_container_name: str = gw_stack.ecs_container_name
        self.ecs_service: ecs.FargateService = gw_stack.ecs_service
        if custom_val is not None:
            setattr(self, factory.PRODUCT_CUSTOM_, custom_val)

        super().__init__(
            factory=factory,
            **kwargs,
        )
