from aws_cdk import (
    Stack,
    aws_amazonmq as amazonmq,
    aws_secretsmanager as secretsmanager,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.bkg.base import CdkBkgBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkBkgBrokerStack(Stack):
    def __init__(
        self,
        base_stack: CdkBkgBaseStack,
        component: str,
        deploy_env: str,
        env_meta: dict,
        factory: CdkConstructsFactory,
        mq_rabbitmq_user_prefix: str,
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta)

        factory.set_attrs_kms_key_stack(self)

        self.mq_rabbitmq_user: str = factory.join_sep_score(
            [mq_rabbitmq_user_prefix] + factory.get_attr_project_name_comp_props(self) + [deploy_env]
        )

        mq_rabbitmq_props: list[str] = [factory.MQ_, factory.RABBITMQ_]
        mq_rabbitmq_pw_props: list[str] = mq_rabbitmq_props + [factory.PW_]
        self.mq_rabbitmq_pw_secret: secretsmanager.Secret = factory.secrets_manager_secret(
            self,
            mq_rabbitmq_pw_props,
            f"Amazon MQ RabbitMQ Password secret for {factory.get_attr_word_map_project_name_comp(self)}.",
            factory.get_construct_name(self, mq_rabbitmq_pw_props),
            secret_string_template={factory.USERNAME_: self.mq_rabbitmq_user},
            password_length=32,
        )

        # ---------- AmazonMQ ----------

        self.mq_rabbitmq_broker: amazonmq.CfnBroker = amazonmq.CfnBroker(
            scope=self,
            id=factory.get_construct_id(self, mq_rabbitmq_props, "CfnBroker"),
            auto_minor_version_upgrade=True,
            broker_name=factory.get_construct_name_short(self, mq_rabbitmq_props + [factory.BROKER_], length=50),
            deployment_mode="CLUSTER_MULTI_AZ",
            engine_type=factory.RABBITMQ_.upper(),
            # https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/rabbitmq-version-management.html
            engine_version=factory.join_sep_dot([str(i) for i in [3.11, 16]]),
            # Consider: 'mq.t3.micro' (free-tier, and does not support cluster deployment) for light-weight deploy envs
            #  https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/broker-instance-types.html#rabbitmq-broker-instance-types
            host_instance_type=factory.join_sep_dot([factory.MQ_, factory.M5_XLARGE_]),
            publicly_accessible=False,
            users=[
                amazonmq.CfnBroker.UserProperty(
                    password=self.mq_rabbitmq_pw_secret.secret_value_from_json(
                        factory.GENERATE_STRING_KEY_
                    ).to_string(),
                    username=self.mq_rabbitmq_user,
                    console_access=True,  # Does not apply to RabbitMQ brokers.
                )
            ],
            # authentication_strategy="SIMPLE",  # ['SIMPLE'|'LDAP']
            # configuration=,  # Does not apply to RabbitMQ brokers.
            # Amazon MQ for ActiveMQ offers a Cross-Region data replication (CRDR) feature:
            #  https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/crdr-for-active-mq.html
            # data_replication_mode=,  # ['NONE'|'CRDR']
            # data_replication_primary_broker_arn=,
            encryption_options=amazonmq.CfnBroker.EncryptionOptionsProperty(
                use_aws_owned_key=False, kms_key_id=factory.get_attr_kms_key_stack(self).key_id
            ),  # (?) Does not apply to RabbitMQ brokers.
            # ldap_server_metadata=,  # Does not apply to RabbitMQ brokers.
            logs=amazonmq.CfnBroker.LogListProperty(
                # audit=True,  # Does not apply to RabbitMQ brokers.
                general=True,
            ),
            maintenance_window_start_time=amazonmq.CfnBroker.MaintenanceWindowProperty(
                day_of_week="MONDAY", time_of_day="01:00", time_zone="UTC"  # Duration: 2 hours
            ),  # TODO: (OPTIONAL) Move these CfnBroker.maintenance_window_start_time props into factory.schedules
            security_groups=[getattr(base_stack, factory.MQ_RABBITMQ_SG_).security_group_id],
            storage_type="EBS",  # ['EBS'|'EFS'] - Concerning 'EFS' storage type: Does not apply to RabbitMQ brokers.
            subnet_ids=[s.subnet_id for s in factory.get_attr_vpc(self).private_subnets],
        )
