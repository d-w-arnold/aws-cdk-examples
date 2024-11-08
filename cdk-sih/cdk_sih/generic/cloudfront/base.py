from aws_cdk import Stack, aws_wafv2 as waf

from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkCloudFrontBaseStack(Stack):
    def __init__(
        self,
        base_stack: Stack,
        component: str,
        elastic_ip_str_list: list[str],
        factory: CdkConstructsFactory,
        project_name: str,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        factory.set_attrs_project_name_comp(self, project_name, component)

        word_map_project_name_comp: str = factory.get_attr_word_map_project_name_comp(self, inc_deploy_env=False)

        self.aws_managed_rules_common_rule_set_excluded_rules: list[str] = []

        self.cloudfront_waf_regex_pattern_set: waf.CfnRegexPatternSet = factory.cloudfront_waf_regex_pattern_set(
            self,
            f"CloudFront WAF Regex Pattern Set for {word_map_project_name_comp}.",
        )

        self.cloudfront_waf_allow_ip_set: waf.CfnIPSet = factory.cloudfront_waf_ip_set_ipv4(
            self,
            [factory.ALLOW_, factory.IPV4_, factory.SET_],
            factory.get_vpc_nat_gateway_ip_ranges(self)
            + factory.get_elastic_ip_ranges(
                self,
                base_stack.stack_name,
                elastic_ip_str_list,
                project_name_comp=project_name,
            ),
            f"Allowed IPv4 addresses for {word_map_project_name_comp}.",
        )

        self.cloudfront_waf_block_ip_set: waf.CfnIPSet = factory.cloudfront_waf_ip_set_ipv4(
            self,
            [factory.BLOCK_, factory.IPV4_, factory.SET_],
            [
                i if factory.SEP_FW_ in i else factory.get_path([i, str(32)])
                for i in factory.CLOUDFRONT_WAF_BLOCK_IPS_V4
            ],
            f"Blocked IPv4 addresses for {word_map_project_name_comp}.",
        )
