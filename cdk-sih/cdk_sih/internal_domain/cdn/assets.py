from aws_cdk import (
    Stack,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
)

from cdk_sih.constructs.factory import (
    CdkConstructsFactory,
)
from cdk_sih.internal_domain.cdn.base import CdkCdnBaseStack
from cdk_sih.internal_domain.cdn.storage import CdkCdnStorageStack


class CdkCdnAssetsStack(Stack):
    def __init__(
        self,
        base_stack: CdkCdnBaseStack,
        component: str,
        deploy_env: str,
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        storage_stack: CdkCdnStorageStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta)

        factory.set_attrs_kms_key_stack(self)

        self.price_class: cloudfront.PriceClass = factory.get_cloudfront_dist_price_class(self)

        self.fqdn: str = None
        if subdomain := getattr(self, factory.SUBDOMAIN_, None):
            self.fqdn = factory.join_sep_dot([subdomain, getattr(base_stack, factory.HOSTED_ZONE_NAME_)])

        enable_ipv6: bool = True

        # ---------- CloudFront ----------

        # Allow CloudFront to use the KMS key to deliver logs
        factory.get_attr_kms_key_stack(self).add_to_resource_policy(
            statement=iam.PolicyStatement(
                actions=[
                    factory.join_sep_colon([factory.KMS_, i])
                    for i in ["Decrypt", factory.join_sep_empty(["GenerateDataKey", factory.SEP_ASTERISK_])]
                ],
                resources=factory.ALL_RESOURCES,
                principals=[factory.iam_service_principal(factory.join_sep_dot([factory.DELIVERY_, factory.LOGS_]))],
            )
        )

        cf_stack_outputs: dict[str, str] = factory.get_cloudfront_stack_outputs(
            self.stack_name,
            getattr(self, factory.COMPONENT_).capitalize(),
            True,
        )

        name_props: list[str] = [factory.CF_]
        name_dist_props: list[str] = name_props + [factory.DIST_]
        cdk_stack_name_short: str = factory.get_cdk_stack_name_short(self.stack_name).lower()
        log_bucket_name_prefix_props: list[str] = [cdk_stack_name_short]
        if factory.aws_profile is not None:
            log_bucket_name_prefix_props.append(factory.aws_profile)

        cf_origin_path: str = factory.SEP_FW_
        cf_dist: cloudfront.Distribution = cloudfront.Distribution(
            scope=self,
            id=factory.get_construct_id(self, name_props, "Distribution"),
            default_behavior=cloudfront.BehaviorOptions(
                # TODO: (NEXT) Consider using: S3BucketOrigin.with_origin_access_control(...)
                #  NB. This would create a cyclic reference between: CdkCdnStorageStack <-> CdkCdnAssetsStack
                origin=origins.S3BucketOrigin.with_origin_access_identity(
                    bucket=storage_stack.s3_bucket_,
                    origin_path=cf_origin_path,
                )
            ),
            certificate=acm.Certificate.from_certificate_arn(
                scope=self,
                id=factory.get_construct_id(self, name_dist_props, "ICertificate"),
                certificate_arn=cf_stack_outputs[factory.cfn_output_acm_cert_construct_id(self, is_key=True)],
            ),
            comment=f"CloudFront distribution for {factory.get_attr_word_map_project_name_comp(self)}, origin pointing to an S3 bucket.",
            # default_root_object=,  # The request goes to the origin’s root (e.g., example.com/) if unset. Default: - no default root object
            domain_names=[self.fqdn],
            enabled=True,
            enable_ipv6=enable_ipv6,
            enable_logging=True,
            # geo_restriction=cloudfront.GeoRestriction.allowlist("UK", "GB"),
            # TODO: (OPTIONAL) Dynamically update geo_restriction list per AWS region deployed to, see: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/GeoRestriction.html#aws_cdk.aws_cloudfront.GeoRestriction
            http_version=cloudfront.HttpVersion.HTTP2,
            log_bucket=factory.s3_bucket(
                self,
                factory.join_sep_score(log_bucket_name_prefix_props + name_dist_props),
                bucket_key_enabled=True,
                lifecycle_rules=True,
            ),
            log_file_prefix=factory.get_path([cdk_stack_name_short, factory.SEP_EMPTY_]),
            log_includes_cookies=False,
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            price_class=self.price_class,
            web_acl_id=cf_stack_outputs[factory.cfn_output_cf_waf_web_acl_construct_id(self, is_key=True)],
        )
        factory.set_attrs_route53_record_cloudfront_distribution(
            self,
            cf_dist,
            getattr(base_stack, factory.HOSTED_ZONE_),
            subdomain,
            enable_ipv6=enable_ipv6,
        )

        factory.set_attrs_url(self, cf_origin_path)
        factory.cfn_output_url(self)
