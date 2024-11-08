from aws_cdk import Stack, aws_ssm as ssm

from cdk_sih.constructs.factory import CdkConstructsFactory


class CdkPypiPackageBaseStack(Stack):
    def __init__(
        self,
        factory: CdkConstructsFactory,
        project_name: str,
        pypi_package_list: list[str],
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        # ---------- SSM ----------

        # Version meta(s)
        self.version_meta_param_names: dict[str, str] = {}
        for pypi_package in pypi_package_list:
            version_meta_param_name: str = factory.get_path(
                [project_name, pypi_package, factory.VERSION_, factory.META_], lead=True
            )
            ssm.StringParameter.from_string_parameter_name(
                scope=self,
                id=factory.get_construct_id(self, [pypi_package, factory.VERSION_, factory.META_], "IStringParameter"),
                string_parameter_name=version_meta_param_name,
            )
            self.version_meta_param_names[pypi_package] = version_meta_param_name
