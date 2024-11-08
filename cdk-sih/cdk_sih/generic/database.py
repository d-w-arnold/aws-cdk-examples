import json

from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_rds as rds,
    aws_ssm as ssm,
)
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkDatabaseStack(Stack):
    def __init__(
        self,
        base_stack: Stack,
        component: str,
        database_meta: dict,
        db_server_name: str,
        db_server_preview_demo: dict[str, str],
        deploy_env_24_7_set: set[str],
        deploy_env_weekend_set: set[str],
        factory: CdkConstructsFactory,
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        customisations: list[str] = None,
        engine_version: rds.MysqlEngineVersion = None,
        inc_proxy: bool = False,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        self.factory: CdkConstructsFactory = factory

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component, is_custom=bool(customisations))
        factory.set_attrs_deploy_env(
            self,
            base_stack,
            db_server_name,
            database_meta,
            deploy_env_24_7_set=deploy_env_24_7_set,
            deploy_env_weekend_set=deploy_env_weekend_set,
            is_db_server=True,
        )

        factory.set_attrs_from_alt_stack(self, base_stack, factory.DB_PORT_)
        factory.set_attrs_from_alt_stack(self, base_stack, factory.DB_SERVER_LAMBDA_SG_)
        factory.set_attrs_from_alt_stack(self, base_stack, factory.DB_SERVER_SG_)
        factory.set_attrs_kms_key_stack(self)
        factory.set_attrs_schedule_windows(self, factory.RDS_)

        self.database_meta: dict = database_meta

        self.db_admin_username: str = factory.ADMIN_

        project_name_comp_props: list[str] = factory.get_attr_project_name_comp_props(self)

        db_api_user_username_suffix: str = factory.API_
        db_api_user_username: str = factory.join_sep_score(project_name_comp_props + [db_api_user_username_suffix])

        self.rds_mysql_props: list[str] = [factory.RDS_, factory.MYSQL_]

        self.db_admin_creds_secret: rds.DatabaseSecret = factory.rds_database_secret(
            self,
            [self.db_admin_username],
            self.db_admin_username,
            rotation_schedule=self.db_admin_username,
        )
        self.db_api_user_creds_secret: rds.DatabaseSecret = factory.rds_database_secret(
            self,
            [db_api_user_username_suffix, factory.USER_],
            db_api_user_username,
        )

        setattr(
            self,
            factory.DB_API_USER_PW_,
            self.db_api_user_creds_secret.secret_value_from_json(factory.PASSWORD_).to_string(),
        )
        setattr(
            self,
            factory.DB_API_USER_USERNAME_,
            factory.join_sep_score(project_name_comp_props + [db_api_user_username_suffix]),
        )

        db_server: rds.DatabaseInstance = factory.rds_database_instance(
            self,
            factory.join_sep_score(
                project_name_comp_props
                + [
                    db_server_name.replace(factory.SEP_UNDER_, factory.SEP_SCORE_),
                    factory.RDS_,
                    factory.MYSQL_,
                ]
            ),
            engine_version=engine_version,
        )

        db_schemas: dict[str, str] = {}
        project_names_comps: list[str] = []
        if p := factory.get_attr_project_name_comp(self):
            project_names_comps: list[str] = (
                [p.replace(factory.CUSTOM_, j, 1) for j in customisations] if customisations else [p]
            )
        for i in project_names_comps:
            for deploy_env in database_meta[factory.DEPLOY_ENV_LIST_]:
                db_schemas[deploy_env] = factory.join_sep_under(
                    factory.get_attr_project_name_comp_props(self, project_name_comp=i) + [deploy_env]
                )
                factory.ssm_string_parameter(
                    self,
                    self.rds_mysql_props,
                    factory.AWS_PRIVATE_DESCRIPTION_,
                    factory.get_path(
                        [
                            factory.AWS_PRIVATE_PARAMETER_PREFIX_,
                            factory.join_sep_score(self.rds_mysql_props),
                            factory.join_sep_score([i, deploy_env]),
                        ]
                    ),
                    json.dumps(
                        {
                            factory.TARGETHOST_: db_server.instance_endpoint.hostname,
                            factory.DESTPORT_: db_server.instance_endpoint.port,
                        }
                    ),
                    project_name_comp=i,
                    deploy_env=deploy_env,
                    data_type=ssm.ParameterDataType.TEXT,
                    tier=ssm.ParameterTier.STANDARD,
                )

        db_port: int = getattr(self, factory.DB_PORT_)

        if inc_proxy:
            db_proxy_sg_list: list[int] = [getattr(self, factory.DB_SERVER_SG_)]
            db_proxy_max_connections_percent: int = int(100 / len(db_schemas))
            db_proxies: dict[str, rds.DatabaseProxy] = {}
            db_proxy_secrets_list: list[rds.DatabaseSecret] = [self.db_api_user_creds_secret]
            db_proxy_role: iam.Role = factory.iam_role(
                self,
                self.rds_mysql_props + [factory.DATABASE_, factory.PROXY_],
                factory.iam_service_principal(factory.RDS_),
                "RDS role that the RDS proxy uses to access secrets in AWS Secrets Manager.",
            )
            for i in db_proxy_secrets_list:
                i.grant_read(grantee=db_proxy_role)

            for deploy_env in database_meta[factory.DEPLOY_ENV_LIST_]:
                db_proxy: rds.DatabaseProxy = rds.DatabaseProxy(
                    scope=self,
                    id=self.get_construct_id(self.rds_mysql_props, "DatabaseProxy", deploy_env=deploy_env),
                    proxy_target=rds.ProxyTarget.from_instance(
                        instance=rds.DatabaseInstance.from_database_instance_attributes(
                            scope=self,
                            id=self.get_construct_id(self.rds_mysql_props, "IDatabaseInstance", deploy_env=deploy_env),
                            instance_endpoint_address=db_server.db_instance_endpoint_address,
                            instance_identifier=db_server.instance_identifier,
                            port=db_port,
                            security_groups=db_proxy_sg_list,
                            engine=factory.rds_database_instance_engine(version=engine_version),
                        )
                    ),
                    secrets=db_proxy_secrets_list,
                    vpc=factory.get_attr_vpc(self),
                    borrow_timeout=Duration.seconds(30),  # Default: Duration.seconds(120)
                    client_password_auth_type=rds.ClientPasswordAuthType.MYSQL_NATIVE_PASSWORD,
                    db_proxy_name=factory.join_sep_score(project_name_comp_props + [deploy_env] + self.rds_mysql_props),
                    debug_logging=getattr(self, factory.DEPLOY_ENV_TYPE_INTERNAL_),
                    iam_auth=False,
                    idle_client_timeout=Duration.minutes(1),  # Default: Duration.minutes(30)
                    # init_query=,   # TODO: (NEXT) Default: - no initialization query
                    max_connections_percent=db_proxy_max_connections_percent,
                    max_idle_connections_percent=(
                        20
                        if getattr(self, factory.DEPLOY_ENV_TYPE_INTERNAL_)
                        else min([db_proxy_max_connections_percent, 40])
                    ),
                    require_tls=True,
                    role=db_proxy_role,
                    security_groups=db_proxy_sg_list,
                    # session_pinning_filters=[],  # TODO: (OPTIONAL) Default: - no session pinning filters
                    vpc_subnets=ec2.SubnetSelection(one_per_az=True, subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                )
                factory.ssm_string_parameter(
                    self,
                    self.rds_mysql_props + [factory.PROXY_],
                    factory.AWS_PRIVATE_DESCRIPTION_,
                    factory.get_path(
                        [
                            factory.AWS_PRIVATE_PARAMETER_PREFIX_,
                            factory.join_sep_score(self.rds_mysql_props),
                            factory.PROXY_,
                            factory.join_sep_score(project_name_comp_props + [deploy_env]),
                        ]
                    ),
                    json.dumps(
                        {
                            factory.TARGETHOST_: db_proxy.endpoint,
                            factory.DESTPORT_: db_port,
                        }
                    ),
                    deploy_env=deploy_env,
                    data_type=ssm.ParameterDataType.TEXT,
                    tier=ssm.ParameterTier.STANDARD,
                )
                db_proxies[deploy_env] = db_proxy

            setattr(self, factory.DB_PROXIES_, db_proxies)

        setattr(self, factory.DB_SERVER_, db_server)

        rds_init_lambda_func_name: str = factory.join_sep_score(
            [factory.join_sep_empty([factory.RDS_.upper(), factory.INIT_.capitalize()])]
            + project_name_comp_props
            + [
                db_server_name.upper().replace(factory.SEP_UNDER_, factory.SEP_SCORE_),
            ]
        )
        rds_init_s3_bucket_project_name: str = factory.join_sep_empty(project_name_comp_props).lower()
        rds_init_s3_bucket_prefixes: list[str] = (
            [rds_init_s3_bucket_project_name.replace(factory.CUSTOM_, i, 1) for i in customisations]
            if customisations
            else [rds_init_s3_bucket_project_name]
        )

        rds_init_lambda_func: lambda_.Function = factory.lambda_function(
            self,
            rds_init_lambda_func_name,
            factory.get_path(self.rds_mysql_props + [factory.INIT_]),
            f"Initialise RDS MySQL database server for {factory.get_attr_word_map_project_name_comp(self)}.",
            {
                **{
                    "ACCOUNT_OWNER_ID": factory.get_attr_env_account(self),
                    "ADMIN_SECRET": self.db_admin_creds_secret.secret_arn,
                    "USER_SECRET": self.db_api_user_creds_secret.secret_arn,
                    "DB_PORT": str(db_port),
                    "DB_SCHEMAS": factory.join_sep_comma(db_schemas.values()),
                    "PROJECT_NAME": rds_init_s3_bucket_project_name,
                },
                **({"PREVIEW_DEMO": json.dumps(db_server_preview_demo)} if db_server_preview_demo else {}),
            },
            factory.iam_role_lambda(
                self,
                rds_init_lambda_func_name,
                managed_policies=factory.lambda_managed_policies_vpc_list(),
                custom_policies=[
                    factory.iam_policy_statement_s3_get_objects(self, s3_bucket_prefixes=rds_init_s3_bucket_prefixes),
                    factory.iam_policy_statement_s3_list_buckets(self, s3_bucket_prefixes=rds_init_s3_bucket_prefixes),
                ],
            ),
            vpc_props=(
                factory.get_attr_vpc(self),
                [getattr(self, factory.DB_SERVER_LAMBDA_SG_)],
                ec2.SubnetType.PRIVATE_WITH_EGRESS,
            ),
            layers=[
                factory.lambda_layer_version_base(self, rds_init_lambda_func_name),
                factory.lambda_layer_version_mysql(self, rds_init_lambda_func_name),
            ],
            params_and_secrets_ext=True,
            timeout=Duration.seconds(10),
        )

        setattr(self, factory.DB_SCHEMAS_, db_schemas)

        self.db_admin_creds_secret.grant_read(grantee=rds_init_lambda_func)
        self.db_api_user_creds_secret.grant_read(grantee=rds_init_lambda_func)

    def get_construct_id(
        self,
        construct_id_props: list[str],
        construct_type: str,
        project_name_comp: str = None,
        deploy_env: str = None,
        global_: bool = False,
        lambda_layer: bool = False,
    ) -> str:
        return self.factory.get_construct_id_default(
            self,
            construct_id_props,
            construct_type,
            project_name_comp=project_name_comp,
            deploy_env=(
                deploy_env
                if deploy_env
                else (
                    self.factory.join_sep_score([i[:4] for i in d.split(self.factory.SEP_UNDER_)])
                    if (d := getattr(self, self.factory.DEPLOY_ENV_)) and self.factory.SEP_UNDER_ in d
                    else d
                )
            ),
            global_=global_,
            lambda_layer=lambda_layer,
        )
