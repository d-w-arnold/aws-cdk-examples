from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_ecs as ecs,
    aws_efs as efs,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    aws_iam as iam,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.dog.base import CdkDogBaseStack
from cdk_sih.dog.database import CdkDogDatabaseStack
from cdk_sih.dog.em.fs import CdkDogFsStack
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkDogEmStack(Stack):
    def __init__(
        self,
        base_stack: CdkDogBaseStack,
        component: str,
        custom_subdomain: str,
        database_stack: CdkDogDatabaseStack,
        deploy_env: str,
        deploy_env_24_7_set: set[str],
        deploy_env_weekend_set: set[str],
        env_meta: dict,
        factory: CdkConstructsFactory,
        fs_stack: CdkDogFsStack,
        project_name: str,
        url_gw: str,
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
            deploy_env_24_7_set=deploy_env_24_7_set,
            deploy_env_weekend_set=deploy_env_weekend_set,
            custom_subdomain=custom_subdomain,
        )

        factory.set_attrs_from_alt_stack(self, base_stack, factory.ECS_SG_)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_schedule_windows(self, factory.ECS_)

        setattr(self, factory.ALB_PORT_, factory.HTTP_PORT)

        self.env_meta: dict = env_meta
        self.price_class: cloudfront.PriceClass = factory.get_cloudfront_dist_price_class(self, default=True)

        self.fqdn: str = None
        self.fqdn_private: str = None
        if subdomain := getattr(self, factory.SUBDOMAIN_, None):
            hosted_zone_name: str = getattr(base_stack, factory.HOSTED_ZONE_NAME_)
            self.fqdn = factory.join_sep_dot([subdomain, hosted_zone_name])
            self.fqdn_private = factory.join_sep_dot([subdomain, factory.get_attr_env_region(self), hosted_zone_name])

        # ---------- EFS ----------

        is_prod: bool = getattr(self, factory.DEPLOY_ENV_PROD_)
        efs_file_system_access_point_id: str = str(1002 if is_prod else 1001)
        efs_file_system_access_point: efs.AccessPoint = fs_stack.efs_file_system.add_access_point(
            id=factory.get_construct_id(self, [factory.EFS_], "AccessPoint"),
            # As the path does not exist in a new EFS file system,
            #  the EFS will create the directory with the following create_acl
            create_acl=efs.Acl(
                owner_uid=efs_file_system_access_point_id,
                owner_gid=efs_file_system_access_point_id,
                permissions=str(750),
            ),
            path=factory.get_path([deploy_env], lead=True),
            posix_user=efs.PosixUser(uid=efs_file_system_access_point_id, gid=efs_file_system_access_point_id),
        )

        # ---------- EC2 ALB & CloudFront ----------

        # Application Load Balancer (ALB) for E-Commerce
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

        # Target group for E-Commerce ALB - to make resources containers discoverable by the ALB
        alb_target_group: elasticloadbalancing.ApplicationTargetGroup = (
            factory.elasticloadbalancing_application_target_group(
                self,
                elasticloadbalancing.TargetType.IP,
                healthy_http_codes=factory.join_sep_score([str(i) for i in [200, 399]]),
                health_check_path=factory.elasticloadbalancing_application_target_group_health_check_path(
                    cf_origin_path
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

        ecs_container_environment: dict[str, str] = {
            "GW_URL": url_gw,
            "WORDPRESS_DB_HOST": getattr(database_stack, factory.DB_SERVER_).instance_endpoint.hostname,
            "WORDPRESS_DB_NAME": getattr(database_stack, factory.DB_SCHEMAS_)[deploy_env],
            "WORDPRESS_DB_USER": database_stack.db_admin_username,
            "WORDPRESS_TABLE_PREFIX": factory.join_sep_empty(
                [
                    factory.join_sep_under(factory.get_attr_project_name_comp_props(self)),
                    factory.SEP_UNDER_,
                ]
            ),
        }
        if not is_prod:
            ecs_container_environment["WORDPRESS_DEBUG"] = str(1)

        ecs_container_secrets: dict[str, ecs.Secret] = {
            "WORDPRESS_DB_PASSWORD": factory.ecs_secret_from_secrets_manager(
                self,
                database_stack.db_admin_creds_secret.secret_name,
                database_stack.db_admin_creds_secret.secret_full_arn,
            ),
        }

        ecs_task_container_log_group: logs.LogGroup = factory.logs_log_group_ecs_task_container(self)

        self.ecs_container_name: str = factory.get_ecs_container_name(self)

        factory.ecs_fargate_service_task_definition_add_container(
            self,
            ecs_task_definition,
            # ecs.ContainerImage.from_registry(name="public.ecr.aws/docker/library/wordpress:latest"),
            ecs.RepositoryImage.from_ecr_repository(repository=base_stack.repo_ecomm, tag=deploy_env),
            self.ecs_container_name,
            getattr(self, factory.ALB_PORT_),
            ecs_task_definition_container_memory_mib,
            ecs_task_container_log_group,
            ecs_container_environment,
            ecs_container_secrets,
        )

        ecs_task_definition_ecs_volume_name: str = factory.get_construct_name_short(
            self, [factory.ECS_, factory.VOLUME_, factory.EFS_], length=64
        )
        ecs_task_definition.add_volume(
            name=ecs_task_definition_ecs_volume_name,
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=fs_stack.efs_file_system.file_system_id,
                authorization_config=ecs.AuthorizationConfig(
                    access_point_id=efs_file_system_access_point.access_point_id,
                    iam="DISABLED",  # Valid values: [ENABLED|DISABLED]
                ),
                root_directory=factory.SEP_FW_,  # The root directory value will be relative to the directory set for the access point
                transit_encryption="ENABLED",
                # transit_encryption_port=,  # Default: Port selection strategy that the Amazon EFS mount helper uses.
            ),
        )
        ecs_task_definition.default_container.add_mount_points(
            ecs.MountPoint(
                container_path="/var/www/html", read_only=False, source_volume=ecs_task_definition_ecs_volume_name
            )
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
