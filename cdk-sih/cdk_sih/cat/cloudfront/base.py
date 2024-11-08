from cdk_sih.generic.cloudfront.base import CdkCloudFrontBaseStack


class CdkCatCloudFrontBaseStack(CdkCloudFrontBaseStack):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.aws_managed_rules_common_rule_set_excluded_rules: list[str] = ["SizeRestrictions_BODY"]
