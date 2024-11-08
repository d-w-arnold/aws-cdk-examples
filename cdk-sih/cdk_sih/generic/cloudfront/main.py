from aws_cdk import Stack, aws_wafv2 as waf

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.generic.cloudfront.base import CdkCloudFrontBaseStack


class CdkCloudFrontStack(Stack):
    def __init__(
        self,
        base_stack: Stack,
        cloudfront_base_stack: CdkCloudFrontBaseStack,
        component: str,
        deploy_env: str,
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        component_alt: str = None,
        wordpress: bool = False,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta)

        self.fqdn: str = None
        if subdomain := getattr(self, factory.SUBDOMAIN_, None):
            if component_alt:
                subdomain = factory.join_sep_dot([component_alt, subdomain])
            self.fqdn = factory.join_sep_dot([subdomain, getattr(base_stack, factory.HOSTED_ZONE_NAME_)])

        factory.cfn_output_acm_cert(
            self,
            factory.acm_certificate(
                self,
                [factory.ACM_],
                self.fqdn,
                getattr(base_stack, factory.HOSTED_ZONE_),
                alternative_names=[factory.join_sep_dot([i, self.fqdn]) for i in factory.region_meta_multi_region],
            ),
        )

        excluded_rules: list[str] = cloudfront_base_stack.aws_managed_rules_common_rule_set_excluded_rules

        aws_managed_rules_word_press_rule_set_: str = "AWSManagedRulesWordPressRuleSet"
        aws_aws_managed_rules_word_press_rule_set_: str = factory.join_sep_score(
            [factory.AWS_.upper(), aws_managed_rules_word_press_rule_set_]
        )
        cloudfront_waf_web_acl_: waf.CfnWebACL = factory.cloudfront_waf_web_acl_default(
            self,
            cloudfront_base_stack.cloudfront_waf_regex_pattern_set.attr_arn,
            cloudfront_base_stack.cloudfront_waf_allow_ip_set,
            cloudfront_base_stack.cloudfront_waf_block_ip_set,
            f"CloudFront WAF Web ACL for {factory.get_attr_word_map_project_name_comp(self)}.",
            additional_rules=(
                [
                    # https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-use-case.html#aws-managed-rule-groups-use-case-wordpress-app
                    waf.CfnWebACL.RuleProperty(
                        name=aws_aws_managed_rules_word_press_rule_set_,
                        priority=10,
                        statement=waf.CfnWebACL.StatementProperty(
                            managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                                name=aws_managed_rules_word_press_rule_set_,
                                vendor_name=factory.AWS_.upper(),
                                excluded_rules=[waf.CfnWebACL.ExcludedRuleProperty(name=i) for i in excluded_rules],
                            ),
                        ),
                        override_action=waf.CfnWebACL.OverrideActionProperty(none={}),
                        visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=True,
                            metric_name=aws_aws_managed_rules_word_press_rule_set_,
                            sampled_requests_enabled=True,
                        ),
                    )
                ]
                if wordpress
                else None
            ),
            aws_managed_rules_common_rule_set_excluded_rules=excluded_rules,
        )

        factory.cloudfront_waf_web_acl_logging_configuration_default(self, cloudfront_waf_web_acl_)

        factory.cfn_output_cf_waf_web_acl(self, cloudfront_waf_web_acl_)
