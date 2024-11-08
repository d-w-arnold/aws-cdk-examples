import json

from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    aws_iam as iam,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.internal_domain.lion.base import CdkLionBaseStack
from cdk_sih.internal_domain.lion.cache import CdkLionCacheStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkLionMsStack(Stack):
    def __init__(
        self,
        base_stack: CdkLionBaseStack,
        cache_regions: list[str],
        cache_stack: CdkLionCacheStack,
        component: str,
        deploy_env: str,
        deploy_env_24_7_set: set[str],
        deploy_env_weekend_set: set[str],
        env_meta: dict,
        factory: CdkConstructsFactory,
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)
        factory.set_attrs_deploy_env(
            self,
            base_stack,
            deploy_env,
            env_meta,
            allow_24_7_disabling=True,
            deploy_env_24_7_set=deploy_env_24_7_set,
            deploy_env_weekend_set=deploy_env_weekend_set,
        )

        factory.set_attrs_from_alt_stack(self, base_stack, factory.ALB_PORT_)
        factory.set_attrs_from_alt_stack(self, base_stack, factory.ECS_SG_)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_schedule_windows(self, factory.ECS_)

        self.env_meta: dict = env_meta
        self.price_class: cloudfront.PriceClass = factory.get_cloudfront_dist_price_class(self)

        self.status_route: str = "zda67QppK76D"

        self.fqdn: str = None
        self.fqdn_private: str = None
        if subdomain := getattr(self, factory.SUBDOMAIN_, None):
            hosted_zone_name: str = getattr(base_stack, factory.HOSTED_ZONE_NAME_)
            self.fqdn = factory.join_sep_dot([subdomain, hosted_zone_name])
            self.fqdn_private = factory.join_sep_dot([subdomain, factory.get_attr_env_region(self), hosted_zone_name])

        project_name_comp: str = factory.get_attr_project_name_comp(self)

        # ---------- SSM ----------

        # LION Micro-service Cache regions meta(s)
        #  (NB. each parameter manually created in AWS Systems Manager Parameter Store)

        cache_regions_meta_props: list[str] = [factory.CACHE_, factory.REGIONS_, factory.META_]
        cache_regions_meta_params: dict[str, ssm.IStringParameter] = {
            i: ssm.StringParameter.from_string_parameter_name(
                scope=self,
                id=factory.get_construct_id(self, cache_regions_meta_props + [i.lower()], "IStringParameter"),
                string_parameter_name=factory.get_path(
                    [project_name_comp, factory.join_sep_score(cache_regions_meta_props), i],
                    lead=True,
                ),
            )
            for i in cache_regions
        }

        # ---------- EC2 ALB & CloudFront ----------

        # Application Load Balancer (ALB) for LION Mirco-service
        alb: elasticloadbalancing.ApplicationLoadBalancer = factory.elasticloadbalancing_application_load_balancer(
            self, getattr(base_stack, factory.ALB_SG_)
        )

        # CloudFront Distribution
        cf_origin_path: str = factory.SEP_FW_
        cf_origin_custom_header: str = factory.X_CUSTOM_HEADER_
        cf_origin_custom_header_secret: secretsmanager.Secret = factory.secrets_manager_secret_cf_origin_custom_header(
            self, cf_origin_custom_header
        )
        factory.cloudfront_distribution(
            self,
            alb,
            getattr(base_stack, factory.HOSTED_ZONE_),
            subdomain,
            cf_origin_path,
            origin_custom_headers=[(cf_origin_custom_header, cf_origin_custom_header_secret)],
        )

        factory.set_attrs_url(self, cf_origin_path)
        factory.cfn_output_url(self)

        # Target group for LION Mirco-service ALB - to make resources containers discoverable by the ALB
        alb_target_group: elasticloadbalancing.ApplicationTargetGroup = (
            factory.elasticloadbalancing_application_target_group(
                self,
                elasticloadbalancing.TargetType.IP,
                health_check_path=factory.elasticloadbalancing_application_target_group_health_check_path_status_route(
                    self, cf_origin_path
                ),
            )
        )

        # Add listener to ALB - only allow HTTPS connections
        factory.elasticloadbalancing_application_listener(
            self,
            alb,
            [
                factory.acm_certificate(
                    self,
                    [factory.ALB_, factory.LISTENER_],
                    self.fqdn,
                    getattr(base_stack, factory.HOSTED_ZONE_),
                )
            ],
            [alb_target_group],
            [(cf_origin_custom_header, cf_origin_custom_header_secret)],
        )

        # ---------- ECS ----------

        ecs_exec_role: iam.Role = factory.iam_role_ecs_task(
            self,
            f"Role used by {factory.get_attr_word_map_project_name_comp(self)} ECS task definitions.",
            managed_policies=factory.ecs_task_managed_policies_list(),
            custom_policies=[
                factory.iam_policy_statement_ecs_exec(),
                factory.iam_policy_statement_kmy_key_decrypt(self),
                factory.iam_policy_statement_secretsmanager_get_secret_value(self),
                factory.iam_policy_statement_service_role_for_ecs(self),
                factory.iam_policy_statement_ssm_get_parameter(self),
            ],
        )

        ecs_task_role: iam.Role = ecs_exec_role

        # ECS task definition
        ecs_task_definition_container_memory_mib: int = 4096
        ecs_task_definition: ecs.TaskDefinition = factory.ecs_fargate_service_task_definition(
            self,
            str(int(ecs_task_definition_container_memory_mib / 2)),
            str(ecs_task_definition_container_memory_mib),
            ecs_exec_role,
            ecs_task_role,
        )

        cache_regions: list[str] = [f'"{k}": {v.string_value}' for k, v in cache_regions_meta_params.items()]
        is_internal: bool = getattr(self, factory.DEPLOY_ENV_INTERNAL_)
        alb_port: int = getattr(self, factory.ALB_PORT_)
        ecs_container_environment: dict[str, str] = {
            "NAME": factory.join_sep_space(
                [factory.get_attr_word_map_project_name_comp(self, inc_deploy_env=False), factory.API_.upper()]
            ),
            "INTERNAL_NAME": factory.join_sep_score(
                factory.get_attr_project_name_comp_props(self) + [factory.API_, deploy_env]
            ),
            "PASSLIB_SCHEMES": factory.PASSLIB_SCHEMES,
            "OPENAPI_OFF": json.dumps(bool(not is_internal)),
            "DEBUG": json.dumps(is_internal),
            "CACHE_SQUARES_META": f"{{{factory.join_sep_comma(cache_regions)}}}",  # Nick H. was very helpful here ^_^
            "CACHE_UNIQUE_CLIENTS": json.dumps(False),
            "REDIS_HOST": cache_stack.ec_redis_cluster_rep_group.attr_reader_end_point_address,
            "REDIS_PORT": cache_stack.ec_redis_cluster_rep_group.attr_reader_end_point_port,
            "REDIS_SSL": json.dumps(True),
            "STATUS_ROUTE": self.status_route,
            "UVICORN_PORT": str(alb_port),
            "UVICORN_HOST": factory.WILDCARD_ADDRESS,
            "UVICORN_WORKERS": str(4),
            "UVICORN_LOG_LEVEL": factory.DEBUG_ if is_internal else factory.INFO_,
        }

        ecs_container_secrets: dict[str, ecs.Secret] = {
            "REDIS_PASSWORD": factory.ecs_secret_from_secrets_manager_redis_password(
                self, cache_stack.ec_redis_auth_secret
            ),
        }
        for k, v in {
            factory.join_sep_under([factory.SECRET_, factory.KEY_]).upper(): factory.SECRET_KEY_SECRET_
        }.items():
            if is_internal:
                ecs_container_environment[k] = factory.join_sep_under([deploy_env.upper(), k])
            else:
                ecs_container_secrets[k] = factory.get_ecs_secret_from_secrets_manager(self, base_stack, v)
        ecs_container_api_keys_secret: secretsmanager.ISecret = getattr(
            base_stack, factory.ECS_CONTAINER_API_KEYS_SECRET_
        )
        ecs_container_secrets["API_KEYS"] = factory.ecs_secret_from_secrets_manager(
            self,
            ecs_container_api_keys_secret.secret_name,
            ecs_container_api_keys_secret.secret_full_arn,
            full_content=True,
        )

        ecs_task_container_log_group: logs.LogGroup = factory.logs_log_group_ecs_task_container(self)

        self.ecs_container_name: str = factory.get_ecs_container_name(self)

        factory.ecs_fargate_service_task_definition_add_container(
            self,
            ecs_task_definition,
            ecs.RepositoryImage.from_ecr_repository(repository=base_stack.repos[project_name_comp], tag=deploy_env),
            self.ecs_container_name,
            alb_port,
            ecs_task_definition_container_memory_mib,
            ecs_task_container_log_group,
            ecs_container_environment,
            ecs_container_secrets,
        )

        # The ECS Service used for deploying tasks
        self.ecs_service: ecs.FargateService = factory.ecs_fargate_service(
            self,
            ecs_task_definition,
            self.fqdn_private,
            ecs_task_container_log_group,
            http_error_code=500,
            target_group=alb_target_group,
        )

        factory.set_attrs_url_private(self, cf_origin_path)
        factory.cfn_output_url_private(self)
