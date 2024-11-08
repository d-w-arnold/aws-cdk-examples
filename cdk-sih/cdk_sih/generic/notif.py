from aws_cdk import (
    CfnOutput,
    Stack,
    aws_iam as iam,
    aws_sns as sns,
)

from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkNotifStack(Stack):
    def __init__(
        self,
        base_stack: Stack,
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

        factory.set_attrs_kms_key_stack(self)

        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self)

        sns_mob_push_props: list[str] = [factory.SNS_, factory.MOB_, factory.PUSH_]
        self.sns_topic_: sns.Topic = factory.sns_topic(
            self,
            sns_mob_push_props,
            subscriptions_=[
                factory.sns_subscriptions_lambda_function(
                    self,
                    sns_mob_push_props,
                    factory.lambda_function_sns(
                        self,
                        factory.join_sep_empty(
                            [
                                i.capitalize()
                                for i in factory.get_construct_name_short(self, sns_mob_push_props).split(
                                    factory.SEP_SCORE_
                                )
                            ]
                        ),
                        security_groups=[getattr(base_stack, factory.ECS_SG_)],
                    ).function_arn,
                )
            ],
        )

        # Publish the SNS topic ARN, for capturing SNS (Mobile push notifications) event notifications,
        #  as CloudFormation output, to be used as a ref by the script:
        #  https://bitbucket.org/foobar-products-development/aws-scripts/src/main/aws-create/aws-create-sns-mob-push.py)
        sns_mob_push_topic_arn_cfn_output_id: str = factory.get_construct_id(
            self, sns_mob_push_props + [factory.TOPIC_], factory.CFN_OUTPUT_TYPE
        )
        CfnOutput(
            scope=self,
            id=sns_mob_push_topic_arn_cfn_output_id,
            description=f"The {word_map_project_name_comp} SNS (Mobile push notifications) "
            f"topic ARN as CloudFormation output. For example, arn:aws:sns:eu-west-2:123456789123:*",
            value=self.sns_topic_.topic_arn,
            export_name=sns_mob_push_topic_arn_cfn_output_id,
        )

        role: iam.Role = factory.iam_role(
            self,
            sns_mob_push_props,
            factory.iam_service_principal(factory.SNS_),
            f"SNS (Mobile push notifications) execution role to give write access "
            f"to CloudWatch Logs for {word_map_project_name_comp}.",
            custom_policies=[
                iam.PolicyStatement(
                    actions=[
                        factory.join_sep_colon([factory.LOGS_, i])
                        for i in [
                            "CreateLogGroup",
                            "CreateLogStream",
                            "PutLogEvents",
                            "PutMetricFilter",
                            "PutRetentionPolicy",
                        ]
                    ],
                    resources=factory.ALL_RESOURCES,
                ),
            ],
        )

        # Publish the IAM role ARN, used to give SNS (Mobile push notifications) write access to use CloudWatch Logs
        #  as CloudFormation output, to be used as a ref by the script:
        #  https://bitbucket.org/foobar-products-development/aws-scripts/src/main/aws-create/aws-create-sns-mob-push.py)
        sns_mob_push_role_arn_cfn_output_id: str = factory.get_construct_id(
            self, sns_mob_push_props + [factory.ROLE_], factory.CFN_OUTPUT_TYPE
        )
        CfnOutput(
            scope=self,
            id=sns_mob_push_role_arn_cfn_output_id,
            description=f"The {word_map_project_name_comp} SNS (Mobile push notifications) "
            f"IAM role ARN as CloudFormation output. For example, arn:aws:sns:eu-west-2:123456789123:*",
            value=role.role_arn,
            export_name=sns_mob_push_role_arn_cfn_output_id,
        )
