from aws_cdk import RemovalPolicy, Stack, aws_dynamodb as dynamodb, aws_kms as kms

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.bkg.base import CdkBkgBaseStack


class CdkBkgDatabaseStack(Stack):
    def __init__(
        self,
        base_stack: CdkBkgBaseStack,
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

        dydb_table_name: str = factory.get_construct_name_short(self, [factory.DYDB_, factory.TABLE_])
        dydb_kms_key: kms.Key = factory.kms_key_encryption(
            self,
            [dydb_table_name],
            factory.join_sep_space([factory.get_attr_word_map_project_name_comp(self), "DynamoDB"]),
        )

        factory.set_attrs_kms_key_stack(self, existing_key=dydb_kms_key)

        # ---------- DynamoDB ----------

        self.dydb_table_name: str = dydb_table_name
        self.dydb_partition_key: str = factory.join_sep_under([factory.DOMAIN_, factory.NAME_])
        self.dydb_sort_key: str = factory.join_sep_under([factory.URL_, factory.REGISTERED_])
        self.dydb_time_to_live_attribute: str = factory.join_sep_under([factory.EXPIRE_, factory.AT_])

        self.dydb_table: dynamodb.TableV2 = dynamodb.TableV2(
            self,
            factory.get_construct_id(self, [factory.DYDB_], "TableV2"),
            partition_key=dynamodb.Attribute(name=self.dydb_partition_key, type=dynamodb.AttributeType.STRING),
            billing=dynamodb.Billing.on_demand(),
            # dynamo_stream=,
            encryption=dynamodb.TableEncryptionV2.customer_managed_key(table_key=factory.get_attr_kms_key_stack(self)),
            # global_secondary_indexes=,
            # local_secondary_indexes=,
            removal_policy=RemovalPolicy.DESTROY,
            # replicas=,
            sort_key=dynamodb.Attribute(name=self.dydb_sort_key, type=dynamodb.AttributeType.STRING),
            table_name=self.dydb_table_name,
            time_to_live_attribute=self.dydb_time_to_live_attribute,
            contributor_insights=False,
            deletion_protection=True,
            # kinesis_stream=,
            # TODO: (OPTIONAL) Future consideration, to have point_in_time_recovery enabled for DynamoDB tables:
            #   https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery.html
            point_in_time_recovery=False,
            table_class=dynamodb.TableClass.STANDARD_INFREQUENT_ACCESS,
        )
