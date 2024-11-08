from aws_cdk import Stack, aws_ecr as ecr

from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkDogSpainBaseStack(Stack):
    def __init__(
        self,
        component: str,
        elastic_ip_parameter_names: dict[str, str],
        factory: CdkConstructsFactory,
        custom_val: str,
        project_name: str,
        project_name_comp_list: list[str],
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        setattr(self, factory.PRODUCT_CUSTOM_, custom_val)

        factory.set_attrs_project_name_comp(self, project_name, component)

        factory.set_attrs_deploy_env_preview_demo_meta(self, None)
        factory.set_attrs_elastic_ips_meta(self, elastic_ip_parameter_names)
        factory.set_attrs_kms_key_stack(self)

        # ---------- ECR ----------

        self.repos: dict[str, ecr.Repository] = {p: factory.ecr_repository(self, p) for p in project_name_comp_list}

        # ---------- SSM ----------

        # Version meta
        factory.ssm_string_parameter_version_meta(self)

        # ---------- Secrets Manager ----------

        # E-Commerce API key secrets
        factory.secrets_manager_secret_api_keys_e_commerce(self)

        # Secret key secrets
        factory.secrets_manager_secret_secret_keys_secret(self)
