from aws_cdk import Stack, aws_kms as kms, aws_s3 as s3

from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkStorageStack(Stack):
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

        s3_bucket_name_prefix: str = factory.get_cdk_stack_name_short(self.stack_name).lower()
        s3_bucket_name: str = factory.get_s3_bucket_name(self, s3_bucket_name_prefix)
        s3_kms_key: kms.Key = factory.kms_key_encryption(
            self,
            [s3_bucket_name, factory.S3_],
            factory.join_sep_space(
                [factory.get_attr_word_map_project_name_comp(self), factory.S3_.upper(), factory.BUCKET_]
            ),
        )

        factory.set_attrs_kms_key_stack(self, existing_key=s3_kms_key)

        self.s3_bucket_: s3.Bucket = factory.s3_bucket(
            self,
            s3_bucket_name_prefix,
            bucket_key_enabled=True,
            encryption_key=s3_kms_key,
        )

        setattr(self, factory.STORAGE_S3_BUCKET_NAME_, s3_bucket_name)
        setattr(self, factory.STORAGE_S3_CDK_STACK_NAME_, s3_bucket_name_prefix)
        setattr(
            self, factory.STORAGE_S3_CHECKSUM_ALGORITHM_, factory.SHA256_
        )  # https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html
        setattr(
            self,
            factory.STORAGE_S3_ENCRYPTION_CONTEXT_KEY_,
            factory.join_sep_empty([i.capitalize() for i in [factory.CDK_, factory.STACK_, factory.NAME_]]),
        )
        setattr(self, factory.STORAGE_S3_KMS_KEY_, s3_kms_key)
