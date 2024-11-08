from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codestarnotifications as codestar_notifications,
    aws_ec2 as ec2,
    aws_sns as sns,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.pypi.base import CdkPypiBaseStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkPipelineStack(Stack):
    def __init__(
        self,
        base_stack: Stack,
        component: str,
        deploy_env: str,
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        project_name_comp_list: list[str],
        pypi_base_stack: CdkPypiBaseStack,
        vpc_stack: CdkVpcSihStack,
        bitbucket_workspace: str = None,
        pipeline_base: bool = None,
        pypi_package: bool = False,
        repo: str = None,
        tag_deploy: bool = None,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        if not hasattr(self, factory.PROJECT_NAME_COMP_):
            factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(self, base_stack, deploy_env, env_meta, no_subdomain=True)

        factory.set_attrs_codepipeline_stage_action_names(self)
        factory.set_attrs_codestar_connection(self, bitbucket_workspace)
        factory.set_attrs_kms_key_stack(self)

        self.build_output: codepipeline.Artifact = None
        self.tag_deploy: bool = env_meta[factory.TAG_DEPLOY_] if tag_deploy is None else tag_deploy

        if not (bool(deploy_env in factory.DEV_STAG_PROD_LIST) if pipeline_base is None else pipeline_base):
            project_name_comp_list = [i for i in list(project_name_comp_list) if factory.BASE_ not in i]

        self.codepipeline_pipelines: dict[str, codepipeline.Pipeline] = factory.codepipeline_pipelines_map(
            self,
            project_name_comp_list,
            repo_name_list=factory.get_repo_name_list(self, project_name_comp_list, repo) if repo else None,
            pypi_server_access=True,
            version_meta_param_name=(
                param_name
                if (param_name := getattr(self, factory.VERSION_META_PARAM_NAME_, None))
                else getattr(base_stack, factory.VERSION_META_PARAM_NAME_)
            ),
            vpc_props=(factory.get_attr_vpc(self), [pypi_base_stack.ec2_sg], ec2.SubnetType.PRIVATE_WITH_EGRESS),
            pypi_package=pypi_package,
        )

        self.sns_topics: dict[str, sns.Topic] = {}
        self.codestar_notifications_notification_rules: list[codestar_notifications.NotificationRule] = []
        for p in project_name_comp_list:
            if factory.BASE_ not in p:
                self.sns_topics[p] = factory.sns_topic_codestar_notifications_sns(self, p)
            self.codestar_notifications_notification_rules.append(
                factory.codestar_notifications_notification_rule(self, p)
            )
