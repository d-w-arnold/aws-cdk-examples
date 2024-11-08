from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as events,
    aws_events_targets as targets,
    aws_kms as kms,
    aws_s3 as s3,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.lion.base import CdkLionBaseStack
from cdk_sih.internal_domain.lion.events import CdkLionEventsStack


class CdkLionStorageStack(Stack):
    def __init__(
        self,
        base_stack: CdkLionBaseStack,
        component: str,
        deploy_env: str,
        env_meta: dict,
        event_bus_regions: set[str],
        events_stack: CdkLionEventsStack,
        factory: CdkConstructsFactory,
        project_name: str,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta)

        self.s3_param_data_bucket_name: str = factory.join_sep_score(
            [project_name, factory.PARAM_, factory.DATA_, deploy_env]
        )
        s3_bucket_name_props: list[str] = [self.s3_param_data_bucket_name, factory.S3_]
        s3_kms_key: kms.Key = factory.kms_key_encryption(
            self,
            s3_bucket_name_props,
            factory.join_sep_space(
                [
                    getattr(self, factory.WORD_MAP_PROJECT_NAME_),
                    factory.PARAM_.capitalize(),
                    factory.DATA_.capitalize(),
                    factory.S3_.upper(),
                    factory.BUCKET_,
                ]
            ),
        )

        factory.set_attrs_kms_key_stack(self, existing_key=s3_kms_key)

        # ---------- S3 ----------

        self.s3_cdk_stack_name: str = factory.get_cdk_stack_name_short(self.stack_name).lower()
        self.s3_checksum_algorithm: str = (
            factory.SHA256_  # https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html
        )
        self.s3_encryption_context_key: str = factory.join_sep_empty(
            [i.capitalize() for i in [factory.CDK_, factory.STACK_, factory.NAME_]]
        )

        self.s3_param_data_bucket: s3.Bucket = s3.Bucket(
            scope=self,
            id=factory.get_construct_id(self, s3_bucket_name_props, "Bucket"),
            access_control=s3.BucketAccessControl.PRIVATE,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_key_enabled=True,
            bucket_name=self.s3_param_data_bucket_name,
            # cors=[],  # Default: - No CORS configuration.
            encryption=s3.BucketEncryption.KMS,
            encryption_key=factory.get_attr_kms_key_stack(self),
            enforce_ssl=True,  # Default: false
            event_bridge_enabled=False,
            # intelligent_tiering_configurations=,  # Default: No Intelligent Tiering Configurations.
            # inventories=[]  # Default: - No inventory configuration,
            lifecycle_rules=factory.s3_bucket_lifecycle_rules_delete_objects_days(
                self, self.s3_param_data_bucket_name, 2
            ),
            # metrics=[],  # Default: - No metrics configuration.
            # notifications_handler_role=,  # Default: - a new role will be created.  # TODO: (OPTIONAL) Add notifications_handler_role
            object_ownership=s3.ObjectOwnership.OBJECT_WRITER,
            public_read_access=False,
            removal_policy=RemovalPolicy.DESTROY,
            # TODO: (OPTIONAL) Define S3 server access logs prefix/bucket
            # server_access_logs_bucket=,  # Default: - If “serverAccessLogsPrefix” undefined - access logs disabled, otherwise - log to current bucket.
            # server_access_logs_prefix=,  # Default: - No log file prefix
            transfer_acceleration=False,
            versioned=False,
        )

        self.s3_param_data_bucket.enable_event_bridge_notification()

        s3_param_data_bucket_name_s3_bucket: str = factory.join_sep_score(
            [self.s3_param_data_bucket_name, factory.S3_, factory.BUCKET_]
        )
        s3_param_data_bucket_rule: events.Rule = events.Rule(
            scope=self,
            id=factory.get_construct_id(self, [s3_param_data_bucket_name_s3_bucket], "Rule"),
            enabled=True,
            # event_bus=,  # Default: - The default event bus.
            # schedule=,  # Default: - None.
            # targets=[],  # Default: - No targets.
            # cross_stack_scope=,  # Default: - none (the main scope will be used, even for cross-stack Events)
            description="Send S3 object creation events to regional Event buses, in order to "
            "trigger all Extractor Lambda function(s) in that region.",
            event_pattern=factory.events_event_pattern_s3_object_created(self.s3_param_data_bucket.bucket_arn),
            rule_name=factory.get_construct_name(self, [s3_param_data_bucket_name_s3_bucket], underscore=True),
        )

        custom_events_props: list[str] = [factory.CUSTOM_, factory.EVENTS_]
        cdk_custom_outputs: dict = factory.file_json_load_cdk_custom_outputs()
        for event_bus_region in event_bus_regions:
            s3_param_data_bucket_rule.add_target(
                target=targets.EventBus(
                    event_bus=events.EventBus.from_event_bus_arn(
                        scope=self,
                        id=factory.get_construct_id(self, custom_events_props + [event_bus_region], "IEventBus"),
                        event_bus_arn=cdk_custom_outputs[factory.get_attr_env_region(self)][events_stack.stack_name][
                            factory.join_sep_empty(
                                [factory.CDK_STACK_PREFIX]
                                + factory.get_attr_project_name_comp_props(self)
                                + [deploy_env]
                                + custom_events_props
                                + [factory.EVENT_, factory.BUS_, factory.ARN_, factory.CFN_OUTPUT_TYPE]
                            )
                        ],
                    ),
                    # dead_letter_queue=,  # Default: - no dead-letter queue  # TODO: (OPTIONAL) Add an SQS queue to be used as DLQ ?
                    # role=,  # Default: a new role is created.
                )
            )

        s3_param_data_bucket_rule.add_target(
            target=targets.CloudWatchLogGroup(
                log_group=factory.logs_log_group(
                    self,
                    [self.s3_param_data_bucket_name] + custom_events_props,
                    factory.get_path(
                        [
                            factory.log_groups[factory.EVENTS_],
                            self.s3_param_data_bucket_name,
                            factory.join_sep_score(custom_events_props),
                        ]
                    ),
                ),
                # log_event=,  # Default: - the entire EventBridge event
                # dead_letter_queue=,  # Default: - no dead-letter queue  # TODO: (OPTIONAL) Add an SQS queue to be used as DLQ ?
                max_event_age=Duration.hours(24),
                retry_attempts=185,
            )
        )
