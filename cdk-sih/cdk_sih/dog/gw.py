import json
from typing import Optional, Union

from aws_cdk import (
    Duration,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_secretsmanager as secretsmanager,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.gw import CdkGwStack
from cdk_sih.internal_domain.bkg.ms import CdkBkgMsStack
from cdk_sih.internal_domain.lion.ms import CdkLionMsStack
from cdk_sih.mail.ms import CdkMailMsStack
from cdk_sih.pdf.ms import CdkPdfMsStack
from cdk_sih.dog.base import CdkDogBaseStack
from cdk_sih.dog.cache import CdkDogCacheStack
from cdk_sih.dog.database import CdkDogDatabaseStack
from cdk_sih.dog.spain.base import CdkDogSpainBaseStack


class CdkDogGwStack(CdkGwStack):
    def __init__(
        self,
        base_stack: CdkDogBaseStack,
        bkg_ms_stack: CdkBkgMsStack,
        cache_stack: CdkDogCacheStack,
        database_stack: CdkDogDatabaseStack,
        deploy_env: str,
        lion_ms_stack: CdkLionMsStack,
        factory: CdkConstructsFactory,
        mail_ms_stack: CdkMailMsStack,
        pdf_ms_stack: CdkPdfMsStack,
        base_stack_alt: Optional[CdkDogSpainBaseStack] = None,
        custom_val: str = None,
        **kwargs,
    ) -> None:
        if custom_val is not None:
            setattr(self, factory.PRODUCT_CUSTOM_, custom_val)

        super().__init__(
            base_stack=base_stack,
            deploy_env=deploy_env,
            factory=factory,
            **kwargs,
        )

        base_stack_focus: Union[CdkDogBaseStack, CdkDogSpainBaseStack] = (
            base_stack_alt if base_stack_alt else base_stack
        )

        # ---------- S3 ----------

        s3_bucket_tags: str = json.dumps(factory.get_s3_bucket_tags(self), default=str)

        s3_lambda_func_name: str = factory.get_lambda_func_name(self, [self.s3_handler_])
        s3_lambda_func_security_groups: list[ec2.SecurityGroup] = [getattr(base_stack, factory.S3_LAMBDA_SG_)]
        s3_lambda_func: lambda_.Function = factory.lambda_function(
            self,
            s3_lambda_func_name,
            factory.get_path(
                [
                    factory.get_attr_project_name(self, no_custom=True),
                    factory.get_lambda_func_name(self, [self.s3_handler_], code_path=True),
                ]
            ),
            f"{self.s3_handler_} Lambda function for {factory.get_attr_word_map_project_name_comp(self)}.",
            {
                "ACCOUNT_OWNER_ID": factory.get_attr_env_account(self),
                "CHECKSUM_ALGORITHM": getattr(self, factory.STORAGE_S3_CHECKSUM_ALGORITHM_),
                "KMS_MASTER_KEY_ID": getattr(self, factory.STORAGE_S3_KMS_KEY_).key_arn,
                "TAGS": s3_bucket_tags,
            },
            factory.iam_role_lambda(
                self,
                s3_lambda_func_name,
                managed_policies=factory.lambda_managed_policies_vpc_list(),
                custom_policies=[
                    factory.iam_policy_statement_s3_delete_objects(self, s3_bucket_prefixes=[self.s3_cdk_stack_name]),
                    factory.iam_policy_statement_s3_list_buckets(self, s3_bucket_prefixes=[self.s3_cdk_stack_name]),
                    iam.PolicyStatement(
                        actions=[
                            factory.join_sep_colon([factory.S3_, i])
                            for i in [
                                "CreateBucket",
                                "DeleteBucket",
                                "PutBucketAcl",
                                "PutBucketObjectLockConfiguration",
                                "PutBucketOwnershipControls",
                                "PutBucketPolicy",
                                "PutBucketPublicAccessBlock",
                                "PutBucketTagging",
                                "PutBucketVersioning",
                                "PutEncryptionConfiguration",
                            ]
                        ],
                        resources=[
                            factory.format_arn_custom(
                                self,
                                service=factory.S3_,
                                resource=factory.join_sep_empty([self.s3_cdk_stack_name, factory.SEP_ASTERISK_]),
                            )
                        ],
                    ),
                ],
            ),
            vpc_props=(factory.get_attr_vpc(self), s3_lambda_func_security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
            timeout=Duration.seconds(5),
        )

        # ---------- ECS ----------

        s3_lambda_func.grant_invoke(self.ecs_exec_role)
        mail_ms_stack.ses_lambda_func.grant_invoke(self.ecs_exec_role)
        pdf_ms_stack.pdf_lambda_func.grant_invoke(self.ecs_exec_role)

        ecs_container_environment: dict[str, str] = {
            "ADDITIONAL_ALLOWED_ORIGINS": self.get_additional_allowed_origins(
                factory.get_additional_allowed_origins_deploy_envs(deploy_env), dev_ports=[2000], staging_ports=[2000]
            ),
            "APP_NAME": self.get_app_name(self.admin),
            "BACKGROUND_URL": self.get_url_background(self, bkg_ms_stack),
            "BASE_URL": getattr(self, factory.URL_PRIVATE_),
            "DB_ENGINE_OPTIONS": json.dumps(self.get_sqlalchemy_database_engine_options()),
            "DB_URL": self.get_sqlalchemy_database_uri(database_stack, deploy_env, secret_db_pw=False),
            "DEBUG": self.debug,
            "LIONAPI_BASE_URL": factory.get_url_for_ms_from_cdk_stack(self, lion_ms_stack),
            "FIREBASE_ACCOUNT_INFO": base_stack.firebase_account_info_param.string_value,
            "INTERNAL_NAME": self.internal_name,
            "MAIL_USERNAME": getattr(base_stack, factory.MAIL_USER_),
            "PDF_CDK_STACK_ACCOUNT_ID": factory.get_attr_env_account(self),
            "PDF_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "PDF_LAMBDA_FUNCTION_NAME": pdf_ms_stack.pdf_lambda_func.function_name,
            "PORTAL_BASE_URL": self.url_portal,
            "REDIS_HOST": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_address,
            "REDIS_HOST_READER": cache_stack.ec_redis_cluster_rep_group.attr_reader_end_point_address,
            "REDIS_PORT": cache_stack.ec_redis_cluster_rep_group.attr_primary_end_point_port,
            "REDIS_SSL": self.redis_ssl,
            "S3_BUCKET_NAME": getattr(self, factory.STORAGE_S3_BUCKET_NAME_),
            "S3_CDK_STACK_ACCOUNT_ID": factory.get_attr_env_account(self),
            "S3_CDK_STACK_NAME": self.s3_cdk_stack_name,
            "S3_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "S3_CHECKSUM_ALGORITHM": getattr(self, factory.STORAGE_S3_CHECKSUM_ALGORITHM_),
            "S3_ENCRYPTION_CONTEXT_KEY": getattr(self, factory.STORAGE_S3_ENCRYPTION_CONTEXT_KEY_),
            "S3_KMS_KEY": getattr(self, factory.STORAGE_S3_KMS_KEY_).key_arn,
            "S3_LAMBDA_FUNCTION_NAME": s3_lambda_func.function_name,
            "S3_TAGS": s3_bucket_tags,
            "SES_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "SES_LAMBDA_FUNCTION_NAME": mail_ms_stack.ses_lambda_func.function_name,
            "SES_REPLY_TO": json.dumps([getattr(base_stack, factory.MAIL_USER_SUPPORT_)]),
            "SES_SUPPORT_MAIL_USERNAME": getattr(base_stack, factory.MAIL_USER_SUPPORT_),
            "SNS_CDK_STACK_REGION": factory.get_attr_env_region(self),
            "SNS_PLATFORM_APPLICATION_ARN": self.sns_platform_application_arn,
            "STATUS_ROUTE": self.status_route,
            "UVICORN_HOST": self.local_host,
            "UVICORN_LOG_LEVEL": self.log_level,
            "UVICORN_PORT": str(getattr(self, factory.ALB_PORT_)),
            "UVICORN_WORKERS": self.workers,
        }

        ecs_container_secret: secretsmanager.ISecret = getattr(base_stack, factory.ECS_CONTAINER_SECRET_)
        ecs_container_api_keys_secret: secretsmanager.ISecret = getattr(
            base_stack, factory.ECS_CONTAINER_API_KEYS_SECRET_
        )
        ecs_container_secrets: dict[str, ecs.Secret] = {
            "BACKGROUND_API_KEY": ecs.Secret.from_secrets_manager(
                secret=ecs_container_secret, field="BACKGROUND_API_KEY"
            ),
            "LIONAPI_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="LIONAPI_API_KEY"),
            "FIREBASE_ACCOUNT_INFO_PRIVATE_KEY": ecs.Secret.from_secrets_manager(
                secret=ecs_container_secret, field="FIREBASE_ACCOUNT_INFO_PRIVATE_KEY"
            ),
            "REDIS_PASSWORD": factory.ecs_secret_from_secrets_manager_redis_password(
                self, cache_stack.ec_redis_auth_secret
            ),
            "WEATHERAPI_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="WEATHERAPI_KEY"),
            "WEATHERBIT_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="WEATHERBIT_KEY"),
            "WORDNIK_API_KEY": ecs.Secret.from_secrets_manager(secret=ecs_container_secret, field="WORDNIK_API_KEY"),
        }
        if ecs_container_api_keys_secret:
            ecs_container_api_keys_secret: secretsmanager.ISecret = secretsmanager.Secret.from_secret_complete_arn(
                scope=self,
                id=factory.get_construct_id(self, [ecs_container_api_keys_secret.secret_name], "ISecret"),
                secret_complete_arn=ecs_container_api_keys_secret.secret_full_arn,
            )
            ecs_container_secrets["SERVICE_ACCESS_KEY_HASH"] = ecs.Secret.from_secrets_manager(
                secret=ecs_container_api_keys_secret, field=deploy_env
            )
        for k, v in {
            "AUTH_ECOMMERCE_API_KEY": factory.E_COMMERCE_API_KEY_SECRET_,
            "SECURITY_SECRET_KEY": factory.SECRET_KEY_SECRET_,
        }.items():
            if self.is_internal:
                ecs_container_environment[k] = factory.join_sep_under([deploy_env.upper(), k])
            else:
                ecs_container_secrets[k] = factory.get_ecs_secret_from_secrets_manager(self, base_stack_focus, v)

        self.ecs_service: ecs.FargateService = self.get_ecs_service(
            base_stack_focus.repos[factory.get_attr_project_name_comp(self)],
            ecs_container_environment,
            ecs_container_secrets,
            http_error_code=500,
            dependant_constructs=[s3_lambda_func],
        )
