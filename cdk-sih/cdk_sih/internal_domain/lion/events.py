from aws_cdk import CfnOutput, Stack, aws_events as events

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.lion.base import CdkLionBaseStack


class CdkLionEventsStack(Stack):
    def __init__(
        self,
        base_stack: CdkLionBaseStack,
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

        # ---------- Events ----------

        custom_events_props: list[str] = [factory.CUSTOM_, factory.EVENTS_]
        event_bus: events.EventBus = events.EventBus(
            scope=self,
            id=factory.get_construct_id(self, custom_events_props, "EventBus"),
            event_bus_name=factory.get_construct_name(self, custom_events_props, underscore=True),
        )

        # Publish the EventBridge Event Bus ARN as CloudFormation output, to be used as a ref for an
        #  S3 Bucket EventBridge Target.
        CfnOutput(
            scope=self,
            id=factory.get_construct_id(
                self, custom_events_props + [factory.EVENT_, factory.BUS_, factory.ARN_], factory.CFN_OUTPUT_TYPE
            ),
            description=f"The EventBridge Event Bus ARN for {factory.get_attr_word_map_project_name_comp(self)}. "
            f"For example, arn:aws:events::111122223333:event-bus/*.",
            value=event_bus.event_bus_arn,
        )
