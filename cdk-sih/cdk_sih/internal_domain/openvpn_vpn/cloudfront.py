from aws_cdk import Stack, aws_wafv2 as waf

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.openvpn_vpn.base import CdkOpenvpnVpnBaseStack


class CdkOpenvpnVpnCloudFrontStack(Stack):
    def __init__(
        self,
        base_stack: CdkOpenvpnVpnBaseStack,
        component: str,
        factory: CdkConstructsFactory,
        project_name: str,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_project_name_comp(self, project_name, component)

        setattr(self, factory.DEPLOY_ENV_INTERNAL_, False)
        setattr(self, factory.NO_PERMITTED_USER_AGENTS_, True)

        self.fqdn: str = factory.join_sep_dot(
            [getattr(base_stack, factory.COMP_SUBDOMAIN_), getattr(base_stack, factory.HOSTED_ZONE_NAME_)]
        )

        factory.cfn_output_acm_cert(
            self, factory.acm_certificate(self, [factory.ACM_], self.fqdn, getattr(base_stack, factory.HOSTED_ZONE_))
        )

        # ---------- WAFv2 ----------

        # CloudFront Web Application Firewall (WAF)

        cloudfront_waf_web_acl_: waf.CfnWebACL = factory.cloudfront_waf_web_acl_default(
            self,
            factory.cloudfront_waf_regex_pattern_set(
                self,
                f"CloudFront WAF Regex Pattern Set for the {base_stack.server_description}.",
                regex_short_list=True,
            ).attr_arn,
            None,
            factory.cloudfront_waf_ip_set_ipv4(
                self,
                [factory.BLOCK_, factory.IPV4_, factory.SET_],
                [
                    factory.get_path([i, str(32)]) if factory.SEP_FW_ not in i else i
                    for i in factory.CLOUDFRONT_WAF_BLOCK_IPS_V4
                ],
                f"Blocked IPv4 addresses for the {base_stack.server_description}.",
            ),
            f"CloudFront WAF Web ACL for the {base_stack.server_description}.",
            aws_managed_rules_common_rule_set_excluded_rules=["SizeRestrictions_BODY"],
        )

        factory.cloudfront_waf_web_acl_logging_configuration_default(self, cloudfront_waf_web_acl_)

        factory.cfn_output_cf_waf_web_acl(self, cloudfront_waf_web_acl_, desc_insert=base_stack.server_description)
