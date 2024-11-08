from aws_cdk import Stack, aws_cloudtrail as cloudtrail, aws_iam as iam, aws_s3 as s3

from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkCloudTrailTrailsStack(Stack):
    def __init__(
        self,
        factory: CdkConstructsFactory,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_kms_key_stack(self, no_trim=True)

        setattr(self, factory.DEPLOY_ENV_PROD_, True)

        # Allow CloudTrail to use the KMS key to deliver logs
        factory.get_attr_kms_key_stack(self).add_to_resource_policy(
            statement=iam.PolicyStatement(
                actions=[
                    factory.join_sep_colon([factory.KMS_, i])
                    for i in [factory.join_sep_empty(["GenerateDataKey", factory.SEP_ASTERISK_]), "Decrypt"]
                ],
                resources=factory.ALL_RESOURCES,
                principals=[factory.iam_service_principal(factory.CT_)],
            )
        )

        main_trail_name_props: list[str] = [
            factory.AWS_,
            factory.CT_,
            factory.LOGS_,
            factory.organisation.lower(),
        ]
        if factory.aws_profile is not None:
            main_trail_name_props.append(factory.aws_profile.lower())
        main_trail_name_props.append(factory.MAIN_)

        main_trail_s3_bucket: s3.Bucket = factory.s3_bucket(
            self,
            factory.join_sep_score(main_trail_name_props),
            bucket_key_enabled=True,
            lifecycle_rules=True,
        )
        self.main_trail = cloudtrail.Trail(
            scope=self,
            id=factory.get_construct_id(self, main_trail_name_props, "Trail"),
            bucket=main_trail_s3_bucket,
            cloud_watch_log_group=factory.logs_log_group(
                self,
                main_trail_name_props,
                factory.get_path([factory.log_groups[factory.CT_], factory.join_sep_score(main_trail_name_props)]),
            ),
            cloud_watch_logs_retention=factory.logs_retention_days(self),
            enable_file_validation=True,
            encryption_key=factory.get_attr_kms_key_stack(self),
            include_global_service_events=True,
            is_multi_region_trail=True,
            # TODO: (NEXT) Consider enabling is_organization_trail (requires additional S3 bucket policy config):
            #  https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-s3-bucket-policy-for-cloudtrail.html#org-trail-bucket-policy
            is_organization_trail=False,
            management_events=cloudtrail.ReadWriteType.ALL,
            s3_key_prefix=self.stack_name,
            send_to_cloud_watch_logs=True,
            sns_topic=factory.sns_topic(
                self, main_trail_name_props
            ),  # TODO: (NEXT) Add SNS topic subscriptions, as needed
            trail_name=factory.join_sep_score(main_trail_name_props),
        )
        self.main_trail.log_all_lambda_data_events()
        self.main_trail.log_all_s3_data_events()
