import json
import os
import sys
from collections import OrderedDict
from enum import Enum
from typing import Optional, Union

import yaml
from aws_cdk import (
    Annotations,
    ArnFormat,
    CfnOutput,
    Duration,
    Environment,
    RemovalPolicy,
    Resource,
    SecretValue,
    Size,
    Stack,
    Tags,
    aws_applicationautoscaling as applicationautoscaling,
    aws_autoscaling as autoscaling,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codestarnotifications as codestar_notifications,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_efs as efs,
    aws_elasticache as elasticache,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_kms as kms,
    aws_lambda as lambda_,
    aws_lambda_destinations as lambda_destinations,
    aws_logs as logs,
    aws_rds as rds,
    aws_route53 as route53,
    aws_route53_targets as route53targets,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
    aws_servicediscovery as servicediscovery,
    aws_ses as ses,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_sqs as sqs,
    aws_ssm as ssm,
    aws_stepfunctions as stepfunctions,
    aws_stepfunctions_tasks as stepfunctions_tasks,
    aws_wafv2 as waf,
)
from constructs import IConstruct
from dotenv import load_dotenv
from schedules import Schedules


# Deployment environment 'EnvType' enum class
class EnvType(Enum):
    PROD = 1
    EXTERNAL = 2
    INTERNAL = 3


class CdkConstructsFactory:
    """
    CDK constructs factory class
    """

    SEP_ASTERISK_: str = "*"
    SEP_AT_SIGN_: str = "@"
    SEP_COLON_: str = ":"
    SEP_COMMA_: str = ","
    SEP_DOT_: str = "."
    SEP_EMPTY_: str = ""
    SEP_FW_: str = "/"
    SEP_SCORE_: str = "-"
    SEP_SPACE_: str = " "
    SEP_UNDER_: str = "_"

    # String representations
    ACCESS_: str = "access"
    ACCOUNT_: str = "account"
    ACL_: str = "acl"
    ACM_: str = "acm"
    ADDL_: str = "addl"
    ADDRESS_: str = "address"
    ADJUST_: str = "adjust"
    ADMIN_: str = "admin"
    AD_: str = "ad"
    AGENTS_: str = "agents"
    AGENT_: str = "agent"
    ALB_: str = "alb"
    ALGORITHM_: str = "algorithm"
    ALLOW_: str = "allow"
    ALL_: str = "all"
    AMAZONMQ_: str = "amazonmq"
    AMAZON_: str = "amazon"
    AMPLIFY_: str = "amplify"
    ANDROID_: str = "android"
    AND_: str = "and"
    API_: str = "api"
    APP_: str = "app"
    ARCHIVE_: str = "archive"
    ARN_: str = "arn"
    ASG_: str = "asg"
    ATMOS_: str = "atmos"
    AT_: str = "at"
    AUDIT_: str = "audit"
    AUTH_: str = "auth"
    AUTO_: str = "auto"
    AVAILABLE_: str = "available"
    AWS_: str = "aws"
    AZURE_: str = "azure"
    BACKUP_: str = "backup"
    BASE_: str = "base"
    BASIC_: str = "basic"
    BASTION_: str = "bastion"
    BEANSTALK_: str = "beanstalk"
    BIN_: str = "bin"
    BITBUCKET_: str = "bitbucket"
    BKG_: str = "bkg"
    BLOCK_: str = "block"
    BROKER_: str = "broker"
    BUCKET_: str = "bucket"
    BUILDSPEC_: str = "buildspec"
    BUILD_: str = "build"
    BUS_: str = "bus"
    BYTE_: str = "byte"
    CACHE_: str = "cache"
    CDK_: str = "cdk"
    CERTIFICATE_: str = "certificate"
    CERT_: str = "cert"
    CF_: str = "cloudfront"
    CHECKSUM_: str = "checksum"
    CIDRS_: str = "cidrs"
    CIDR_: str = "cidr"
    CLASS_: str = "class"
    CLIENT_: str = "client"
    CLOUDFORMATION_: str = "cloudformation"
    CLOUDWATCH_: str = "cloudwatch"
    CLOUD_: str = "cloud"
    CLUSTER_: str = "cluster"
    CODEBUILD_: str = "codebuild"
    CODEDEPLOY_: str = "codedeploy"
    CODEPIPELINE_: str = "codepipeline"
    CODESTAR_: str = "codestar"
    COLLECT_: str = "collect"
    COMMAND_: str = "command"
    COMMERCE_: str = "commerce"
    COMPANY_: str = "company"
    COMPONENT_: str = "component"
    COMP_: str = "comp"
    COM_: str = "com"
    CONFIGURATION_: str = "configuration"
    CONFIG_: str = "config"
    CONF_: str = "conf"
    CONNECTIONS_: str = "connections"
    CONTAINER_: str = "container"
    CONTEXT_: str = "context"
    COUNT_: str = "count"
    CO_: str = "co"
    CT_: str = "cloudtrail"
    CUSTOM_: str = "custom"
    DAILY_: str = "daily"
    DATABASE_: str = "database"
    DATA_: str = "data"
    DATE_: str = "date"
    DAYS_: str = "days"
    DB_: str = "db"
    DEBUG_: str = "debug"
    DEFAULT_: str = "default"
    DEFINITION_: str = "definition"
    DELETE_: str = "delete"
    DELIVERY_: str = "delivery"
    DEMO_: str = "demo"
    DEPLOYMENT_: str = "deployment"
    DEPLOY_: str = "deploy"
    DESCRIPTION_: str = "description"
    DESC_: str = "desc"
    DEST_: str = "dest"
    DETECTOR_: str = "detector"
    DEVICES_: str = "devices"
    DEVICE_: str = "device"
    DEV_: str = "dev"
    DISABLE_: str = "disable"
    DIST_: str = "dist"
    DKR_: str = "dkr"
    DNS_: str = "dns"
    DOMAIN_: str = "domain"
    DOWNLOAD_: str = "download"
    DYDB_: str = "dydb"
    DYNAMODB_: str = "dynamodb"
    EC2MESSAGES_: str = "ec2messages"
    EC2_: str = "ec2"
    ECOMM_: str = "ecomm"
    ECR_: str = "ecr"
    ECS_: str = "ecs"
    EC_: str = "ec"
    EFS_: str = "efs"
    ELASTICACHE_: str = "elasticache"
    ELASTIC_: str = "elastic"
    EMPTY_: str = "empty"
    ENABLED_: str = "enabled"
    ENCRYPTION_: str = "encryption"
    ENDPOINT_: str = "endpoint"
    END_: str = "end"
    ENGINE_: str = "engine"
    ENV_: str = "env"
    ERRORS_: str = "errors"
    ERROR_: str = "error"
    EVENTS_: str = "events"
    EVENT_: str = "event"
    EXECUTE_: str = "execute"
    EXPIRE_: str = "expire"
    EXTERNAL_: str = "external"
    EXTRACT_: str = "extract"
    EXT_: str = "ext"
    E_: str = "e"
    FEDERATION_: str = "federation"
    FILENAMES_: str = "filenames"
    FILE_: str = "file"
    FINAL_: str = "final"
    FIREBASE_: str = "firebase"
    FLOW_: str = "flow"
    FREE_: str = "free"
    FUNCTION_: str = "function"
    GATEWAY_: str = "gateway"
    GCM_: str = "gcm"
    GENERAL_: str = "general"
    GLOBAL_: str = "global"
    GROUP_: str = "group"
    HANDLER_: str = "handler"
    HEADER_: str = "header"
    HOSTED_: str = "hosted"
    HOST_: str = "host"
    IAM_: str = "iam"
    IDENTITY_: str = "identity"
    ID_: str = "id"
    IGW_: str = "igw"
    INDEX_: str = "index"
    INFO_: str = "info"
    INIT_: str = "init"
    INNOVAULT_: str = "innovault"
    INSIGHT_: str = "insight"
    INSTANCE_: str = "instance"
    INTERNAL_: str = "internal"
    INTERNET_: str = "internet"
    IPSEC_: str = "ipsec"
    IPS_: str = "ips"
    IPV4_: str = "ipv4"
    IP_: str = "ip"
    ISOLATED_: str = "isolated"
    IS_: str = "is"
    IT_: str = "it"
    KEYS_: str = "keys"
    KEY_: str = "key"
    KMS_: str = "kms"
    LAMBDA_: str = "lambda"
    LATEST_: str = "latest"
    LAYERS_: str = "layers"
    LAYER_: str = "layer"
    LEN_: str = "len"
    LIMIT_: str = "limit"
    LINUX_: str = "linux"
    LISTENER_: str = "listener"
    LIST_: str = "list"
    LOGS_: str = "logs"
    LOG_: str = "log"
    MAIL_: str = "mail"
    MAINTENANCE_: str = "maintenance"
    MAIN_: str = "main"
    MAPPINGS_: str = "mappings"
    MAP_: str = "map"
    MAX_: str = "max"
    METADATA_: str = "metadata"
    META_: str = "meta"
    MET_: str = "met"
    MILLIS_: str = "millis"
    MIN_: str = "min"
    MISC_: str = "misc"
    MOB_: str = "mob"
    MONITOR_: str = "monitor"
    MOZILLA_: str = "mozilla"
    MQ_: str = "mq"
    MS_: str = "ms"
    MULTI_: str = "multi"
    MYSQL_: str = "mysql"
    NAME_: str = "name"
    NAT_: str = "nat"
    NGW_: str = "ngw"
    NLB_: str = "nlb"
    NONE_: str = "none"
    NON_: str = "non"
    NOTIFICATIONS_: str = "notifications"
    NOTIFICATION_: str = "notification"
    NO_: str = "no"
    OBJECTS_: str = "objects"
    OBJS_: str = "objs"
    OFF_: str = "off"
    ON_: str = "on"
    ORIGIN_: str = "origin"
    OVERNIGHT_: str = "overnight"
    PARAMETER_: str = "parameter"
    PARAMS_: str = "params"
    PARAM_: str = "param"
    PASSWORD_: str = "password"
    PERFORMANCE_: str = "performance"
    PERFORM_: str = "perform"
    PERMITTED_: str = "permitted"
    PIPELINE_: str = "pipeline"
    POLICY_: str = "policy"
    POLL_: str = "poll"
    PORTAL_: str = "portal"
    PORT_: str = "port"
    POSTMAN_: str = "postman"
    PREVIEW_: str = "preview"
    PRICE_: str = "price"
    PRIVATE_: str = "private"
    PRODUCT_: str = "product"
    PROD_: str = "prod"
    PROJECT_: str = "project"
    PROXIES_: str = "proxies"
    PROXY_: str = "proxy"
    PSK_: str = "psk"
    PUBLIC_: str = "public"
    PUSH_: str = "push"
    PW_: str = "pw"
    PYTHON_: str = "python"
    PY_: str = "py"
    RABBITMQ_: str = "rabbitmq"
    RANGES_: str = "ranges"
    RATE_: str = "rate"
    RDS_: str = "rds"
    REASON_: str = "reason"
    RECORD_: str = "record"
    REDIS_: str = "redis"
    REGIONS_: str = "regions"
    REGION_: str = "region"
    REGISTERED_: str = "registered"
    REPLICAS_: str = "replicas"
    REPLICATION_: str = "replication"
    REPLY_: str = "reply"
    REPORT_: str = "report"
    REPUTATION_: str = "reputation"
    REP_: str = "rep"
    REQUESTS_: str = "requests"
    RESERVED_: str = "reserved"
    ROLE_: str = "role"
    ROT_: str = "rot"
    ROUTE_53_: str = "route53"
    RUNNING_: str = "running"
    RUNTIME_: str = "runtime"
    S3_: str = "s3"
    SAML_: str = "saml"
    SAT_: str = "sat"
    SCALING_: str = "scaling"
    SCHEDULE_: str = "schedule"
    SCHEMAS_: str = "schemas"
    SCRIPTS_: str = "scripts"
    SECRETSMANAGER_: str = "secretsmanager"
    SECRETS_: str = "secrets"
    SECRET_: str = "secret"
    SERVER_: str = "server"
    SERVICE_: str = "service"
    SES_: str = "ses"
    SET_: str = "set"
    SG_: str = "sg"
    SH_: str = "sh"
    SIMPLE_: str = "simple"
    SLOWQUERY_: str = "slowquery"
    SLOW_: str = "slow"
    SNAPSHOT_: str = "snapshot"
    SNS_: str = "sns"
    SOURCE_: str = "source"
    SPACE_: str = "space"
    SSH_: str = "ssh"
    SSMMESSAGES_: str = "ssmmessages"
    SSM_: str = "ssm"
    STACK_: str = "stack"
    STAGING_: str = "staging"
    START_: str = "start"
    STATES_: str = "states"
    STATE_: str = "state"
    STATUS_: str = "status"
    STOP_: str = "stop"
    STORAGE_: str = "storage"
    STS_: str = "sts"
    SUBDOMAIN_: str = "subdomain"
    SUBJECT_: str = "subject"
    SUBNETS_: str = "subnets"
    SUBNET_: str = "subnet"
    SUBSCRIPTIONS_: str = "subscriptions"
    SUBS_: str = "subs"
    SUPPORT_: str = "support"
    SYSTEM_: str = "system"
    TABLE_: str = "table"
    TAG_: str = "tag"
    TASKS_: str = "tasks"
    TASK_: str = "task"
    TCP_: str = "tcp"
    TEAMS_: str = "teams"
    TEMPLATE_: str = "template"
    TG_: str = "tg"
    TIMEOUT_: str = "timeout"
    TIMESTAMP_: str = "timestamp"
    TIME_: str = "time"
    TINYPROXY_: str = "tinyproxy"
    TOKEN_: str = "token"
    TOPIC_: str = "topic"
    TO_: str = "to"
    TRAFFIC_: str = "traffic"
    TXT_: str = "txt"
    TYPE_: str = "type"
    UDP_: str = "udp"
    UK_: str = "uk"
    UNSTABLE_: str = "unstable"
    UPDATE_: str = "update"
    URL_: str = "url"
    USERNAME_: str = "username"
    USER_: str = "user"
    VENDEDLOGS_: str = "vendedlogs"
    VERSION_: str = "version"
    VOLUME_: str = "volume"
    VPC_: str = "vpc"
    VPN_: str = "vpn"
    WAF_: str = "waf"
    WEATHER_: str = "weather"
    WEBHOOK_: str = "webhook"
    WEB_: str = "web"
    WEEKEND_: str = "weekend"
    WEEKLY_: str = "weekly"
    WEEK_: str = "week"
    WINDOW_: str = "window"
    WORD_: str = "word"
    WORKSPACE_: str = "workspace"
    XML_: str = "xml"
    YML_: str = "yml"
    ZIP_: str = "zip"
    ZONE_: str = "zone"

    AMAZONAWS_: str = SEP_EMPTY_.join([AMAZON_, AWS_])
    DOT_COM_: str = SEP_EMPTY_.join([SEP_DOT_, COM_])
    DOT_CO_UK_: str = SEP_EMPTY_.join([SEP_DOT_, CO_, SEP_DOT_, UK_])
    DOT_IT_: str = SEP_EMPTY_.join([SEP_DOT_, IT_])
    SEP_COLON_FW_FW_: str = SEP_EMPTY_.join([SEP_COLON_, SEP_FW_, SEP_FW_])
    HTTP_: str = SEP_EMPTY_.join(["http", SEP_COLON_FW_FW_])
    HTTPS_: str = SEP_EMPTY_.join(["https", SEP_COLON_FW_FW_])

    X_CUSTOM_HEADER_: str = SEP_SCORE_.join(["x", CUSTOM_, HEADER_])

    # CDK class attribute pointers
    _DB_API_USER_: str = SEP_UNDER_.join([DB_, API_, USER_])
    _ECS_CONTAINER_: str = SEP_UNDER_.join([ECS_, CONTAINER_])
    _END_WEEK_DAYS_: str = SEP_UNDER_.join([END_, WEEK_, DAYS_])
    _E_COMMERCE_API_KEY_: str = SEP_UNDER_.join([E_, COMMERCE_, API_, KEY_])
    _SCHEDULE_WINDOW_: str = SEP_UNDER_.join([SCHEDULE_, WINDOW_])
    _SECRET_KEY_: str = SEP_UNDER_.join([SECRET_, KEY_])
    _START_WEEK_DAYS_: str = SEP_UNDER_.join([START_, WEEK_, DAYS_])
    _STORAGE_S3: str = SEP_UNDER_.join([STORAGE_, S3_])
    _TOKEN_KEY_: str = SEP_UNDER_.join([TOKEN_, KEY_])
    _WEEKLY_MAINTENANCE_TIMESTAMP_: str = SEP_UNDER_.join([WEEKLY_, MAINTENANCE_, TIMESTAMP_])
    ALB_PORT_: str = SEP_UNDER_.join([ALB_, PORT_])
    ALB_SG_: str = SEP_UNDER_.join([ALB_, SG_])
    CLIENT_VPN_ENDPOINT_PRIVATE_SG_: str = SEP_UNDER_.join([CLIENT_, VPN_, ENDPOINT_, PRIVATE_, SG_])
    CODESTAR_CONNECTIONS_ARN_: str = SEP_UNDER_.join([CODESTAR_, CONNECTIONS_, ARN_])
    CODESTAR_CONNECTIONS_BITBUCKET_WORKSPACE_: str = SEP_UNDER_.join([CODESTAR_, CONNECTIONS_, BITBUCKET_, WORKSPACE_])
    COMP_SUBDOMAIN_: str = SEP_UNDER_.join([COMP_, SUBDOMAIN_])
    DB_API_USER_PW_: str = SEP_UNDER_.join([_DB_API_USER_, PW_])
    DB_API_USER_USERNAME_: str = SEP_UNDER_.join([_DB_API_USER_, USERNAME_])
    DB_PORT_: str = SEP_UNDER_.join([DB_, PORT_])
    DB_PROXIES_: str = SEP_UNDER_.join([DB_, PROXIES_])
    DB_SCHEMAS_: str = SEP_UNDER_.join([DB_, SCHEMAS_])
    DB_SERVER_: str = SEP_UNDER_.join([DB_, SERVER_])
    DB_SERVER_LAMBDA_SG_: str = SEP_UNDER_.join([DB_SERVER_, LAMBDA_, SG_])
    DB_SERVER_SG_: str = SEP_UNDER_.join([DB_SERVER_, SG_])
    DEPLOY_ENV_: str = SEP_UNDER_.join([DEPLOY_, ENV_])
    DEPLOY_ENV_24_7_: str = SEP_UNDER_.join([DEPLOY_ENV_, str(24), str(7)])
    DEPLOY_ENV_DEMO_: str = SEP_UNDER_.join([DEPLOY_ENV_, DEMO_])
    DEPLOY_ENV_DEV_: str = SEP_UNDER_.join([DEPLOY_ENV_, DEV_])
    DEPLOY_ENV_EXTERNAL_: str = SEP_UNDER_.join([DEPLOY_ENV_, EXTERNAL_])
    DEPLOY_ENV_INTERNAL_: str = SEP_UNDER_.join([DEPLOY_ENV_, INTERNAL_])
    DEPLOY_ENV_NOT_24_7_: str = SEP_UNDER_.join([DEPLOY_ENV_, "not", str(24), str(7)])
    DEPLOY_ENV_PREVIEW_: str = SEP_UNDER_.join([DEPLOY_ENV_, PREVIEW_])
    DEPLOY_ENV_PREVIEW_DEMO_: str = SEP_UNDER_.join([DEPLOY_ENV_, PREVIEW_, DEMO_])
    DEPLOY_ENV_PREVIEW_DEMO_META_: str = SEP_UNDER_.join([DEPLOY_ENV_, PREVIEW_, DEMO_, META_])
    DEPLOY_ENV_PROD_: str = SEP_UNDER_.join([DEPLOY_ENV_, PROD_])
    DEPLOY_ENV_TYPE_: str = SEP_UNDER_.join([DEPLOY_ENV_, TYPE_])
    DEPLOY_ENV_TYPE_INTERNAL_: str = SEP_UNDER_.join([DEPLOY_ENV_TYPE_, INTERNAL_])
    DEPLOY_ENV_WEEKEND_: str = SEP_UNDER_.join([DEPLOY_ENV_, WEEKEND_])
    DEV_STAGING_: str = SEP_UNDER_.join([DEV_, STAGING_])
    DISABLE_24_7_: str = SEP_UNDER_.join([DISABLE_, str(24), str(7)])
    ECS_CONTAINER_API_KEYS_SECRET_: str = SEP_UNDER_.join([_ECS_CONTAINER_, API_, KEYS_, SECRET_])
    ECS_CONTAINER_SECRET_: str = SEP_UNDER_.join([_ECS_CONTAINER_, SECRET_])
    ECS_CONTAINER_SERVICE_ACCESS_SECRET_: str = SEP_UNDER_.join([_ECS_CONTAINER_, SERVICE_, ACCESS_, SECRET_])
    ECS_SERVICE_CLOUD_MAP_SERVICE_NAME_: str = SEP_UNDER_.join([ECS_, SERVICE_, CLOUD_, MAP_, SERVICE_, NAME_])
    ECS_SG_: str = SEP_UNDER_.join([ECS_, SG_])
    EC_REDIS_SG_: str = SEP_UNDER_.join([EC_, REDIS_, SG_])
    EC_REDIS_SG_DESCRIPTION_: str = SEP_UNDER_.join([EC_, REDIS_, SG_, DESCRIPTION_])
    ELASTIC_IP_META_: str = SEP_UNDER_.join([ELASTIC_, IP_, META_])
    E_COMMERCE_API_KEY_SECRETS_: str = SEP_UNDER_.join([_E_COMMERCE_API_KEY_, SECRETS_])
    E_COMMERCE_API_KEY_SECRET_: str = SEP_UNDER_.join([_E_COMMERCE_API_KEY_, SECRET_])
    HOSTED_ZONE_: str = SEP_UNDER_.join([HOSTED_, ZONE_])
    HOSTED_ZONE_NAME_: str = SEP_UNDER_.join([HOSTED_ZONE_, NAME_])
    KMS_KEY_STACK_: str = SEP_UNDER_.join([KMS_, KEY_, STACK_])
    LAMBDA_SG_: str = SEP_UNDER_.join([LAMBDA_, SG_])
    MAIL_USER_: str = SEP_UNDER_.join([MAIL_, USER_])
    MAIL_USER_SUPPORT_: str = SEP_UNDER_.join([MAIL_USER_, SUPPORT_])
    MQ_RABBITMQ_SG_: str = SEP_UNDER_.join([MQ_, RABBITMQ_, SG_])
    MS_TEAMS_: str = SEP_UNDER_.join([MS_, TEAMS_])
    NAME_BUILD_: str = SEP_UNDER_.join([NAME_, BUILD_])
    NAME_DEPLOY_: str = SEP_UNDER_.join([NAME_, DEPLOY_])
    NAME_SOURCE_: str = SEP_UNDER_.join([NAME_, SOURCE_])
    NO_PERMITTED_USER_AGENTS_: str = SEP_UNDER_.join([NO_, PERMITTED_, USER_, AGENTS_])
    PIPELINE_EVENT_LAMBDA_FUNCTION_ARN_: str = SEP_UNDER_.join([PIPELINE_, EVENT_, LAMBDA_, FUNCTION_, ARN_])
    PREVIEW_DEMO_: str = SEP_UNDER_.join([PREVIEW_, DEMO_])
    PRODUCT_CUSTOM_: str = SEP_UNDER_.join([PRODUCT_, CUSTOM_])
    PROJECT_NAME_: str = SEP_UNDER_.join([PROJECT_, NAME_])
    PROJECT_NAME_BASE_: str = SEP_UNDER_.join([PROJECT_NAME_, BASE_])
    PROJECT_NAME_COMP_: str = SEP_UNDER_.join([PROJECT_NAME_, COMP_])
    PROJECT_NAME_COMP_BASE_: str = SEP_UNDER_.join([PROJECT_NAME_COMP_, BASE_])
    REDIS_PORT_: str = SEP_UNDER_.join([REDIS_, PORT_])
    ROUTE_53_AAAA_RECORD_: str = SEP_UNDER_.join([ROUTE_53_, "aaaa", RECORD_])
    ROUTE_53_A_RECORD_: str = SEP_UNDER_.join([ROUTE_53_, "a", RECORD_])
    S3_LAMBDA_SG_: str = SEP_UNDER_.join([S3_, LAMBDA_, SG_])
    SCHEDULE_WINDOW_ECS_: str = SEP_UNDER_.join([_SCHEDULE_WINDOW_, ECS_])
    SCHEDULE_WINDOW_ELASTICACHE_ALL_DAYS_: str = SEP_UNDER_.join([_SCHEDULE_WINDOW_, ELASTICACHE_, ALL_, DAYS_])
    SCHEDULE_WINDOW_ELASTICACHE_WEEKEND_: str = SEP_UNDER_.join([_SCHEDULE_WINDOW_, ELASTICACHE_, WEEKEND_])
    SCHEDULE_WINDOW_ELASTICACHE_WEEKLY_MAINTENANCE_TIMESTAMP_: str = SEP_UNDER_.join(
        [_SCHEDULE_WINDOW_, ELASTICACHE_, _WEEKLY_MAINTENANCE_TIMESTAMP_]
    )
    SCHEDULE_WINDOW_ELASTICACHE_WEEK_DAYS_: str = SEP_UNDER_.join([_SCHEDULE_WINDOW_, ELASTICACHE_, WEEK_, DAYS_])
    SCHEDULE_WINDOW_RDS_DAILY_BACKUP_TIMESTAMP_: str = SEP_UNDER_.join(
        [_SCHEDULE_WINDOW_, RDS_, DAILY_, BACKUP_, TIMESTAMP_]
    )
    SCHEDULE_WINDOW_RDS_WEEKLY_MAINTENANCE_TIMESTAMP_: str = SEP_UNDER_.join(
        [_SCHEDULE_WINDOW_, RDS_, _WEEKLY_MAINTENANCE_TIMESTAMP_]
    )
    SECRET_KEY_SECRETS_: str = SEP_UNDER_.join([_SECRET_KEY_, SECRETS_])
    SECRET_KEY_SECRET_: str = SEP_UNDER_.join([_SECRET_KEY_, SECRET_])
    STORAGE_S3_BKG_BUCKET_NAME_: str = SEP_UNDER_.join([_STORAGE_S3, BKG_, BUCKET_, NAME_])
    STORAGE_S3_BKG_CDK_STACK_NAME_: str = SEP_UNDER_.join([_STORAGE_S3, BKG_, CDK_, STACK_, NAME_])
    STORAGE_S3_BKG_CHECKSUM_ALGORITHM_: str = SEP_UNDER_.join([_STORAGE_S3, BKG_, CHECKSUM_, ALGORITHM_])
    STORAGE_S3_BKG_ENCRYPTION_CONTEXT_KEY_: str = SEP_UNDER_.join([_STORAGE_S3, BKG_, ENCRYPTION_, CONTEXT_, KEY_])
    STORAGE_S3_BKG_KMS_KEY_: str = SEP_UNDER_.join([_STORAGE_S3, BKG_, KMS_, KEY_])
    STORAGE_S3_BUCKET_NAME_: str = SEP_UNDER_.join([_STORAGE_S3, BUCKET_, NAME_])
    STORAGE_S3_CDK_STACK_NAME_: str = SEP_UNDER_.join([_STORAGE_S3, CDK_, STACK_, NAME_])
    STORAGE_S3_CHECKSUM_ALGORITHM_: str = SEP_UNDER_.join([_STORAGE_S3, CHECKSUM_, ALGORITHM_])
    STORAGE_S3_ENCRYPTION_CONTEXT_KEY_: str = SEP_UNDER_.join([_STORAGE_S3, ENCRYPTION_, CONTEXT_, KEY_])
    STORAGE_S3_KMS_KEY_: str = SEP_UNDER_.join([_STORAGE_S3, KMS_, KEY_])
    TAG_DEPLOY_: str = SEP_UNDER_.join([TAG_, DEPLOY_])
    TOKEN_KEY_SECRETS_: str = SEP_UNDER_.join([_TOKEN_KEY_, SECRETS_])
    TOKEN_KEY_SECRET_: str = SEP_UNDER_.join([_TOKEN_KEY_, SECRET_])
    URL_PRIVATE_: str = SEP_UNDER_.join([URL_, PRIVATE_])
    VERSION_META_PARAM_NAME_: str = SEP_UNDER_.join([VERSION_, META_, PARAM_, NAME_])
    VPC_CIDR_: str = SEP_UNDER_.join([VPC_, CIDR_])
    VPC_NAME_: str = SEP_UNDER_.join([VPC_, NAME_])
    VPC_NAT_GATEWAY_IP_RANGES_PARAMETER_NAME_: str = SEP_UNDER_.join(
        [VPC_, NAT_, GATEWAY_, IP_, RANGES_, PARAMETER_, NAME_]
    )
    WORD_MAP_: str = SEP_UNDER_.join([WORD_, MAP_])
    WORD_MAP_COMPONENT_: str = SEP_UNDER_.join([WORD_MAP_, COMPONENT_])
    WORD_MAP_PROJECT_NAME_: str = SEP_UNDER_.join([WORD_MAP_, PROJECT_NAME_])

    PLURAL_MAPPINGS: dict[str, str] = {
        E_COMMERCE_API_KEY_SECRET_: E_COMMERCE_API_KEY_SECRETS_,
        SECRET_KEY_SECRET_: SECRET_KEY_SECRETS_,
        TOKEN_KEY_SECRET_: TOKEN_KEY_SECRETS_,
    }

    # AWS region codes
    US_EAST_1_: str = "us-east-1"
    AF_SOUTH_1_: str = "af-south-1"
    AP_NORTHEAST_2_: str = "ap-northeast-2"
    AP_SOUTHEAST_2_: str = "ap-southeast-2"
    EU_CENTRAL_1_: str = "eu-central-1"
    EU_WEST_2_: str = "eu-west-2"
    SA_EAST_1_: str = "sa-east-1"

    # AWS region metadata
    _CF_PRICE_CLASS_: str = SEP_UNDER_.join([CF_, PRICE_, CLASS_])
    _CF_PRICE_CLASS_DEFAULT: cloudfront.PriceClass = cloudfront.PriceClass.PRICE_CLASS_100
    _MULTI_REGION_: str = SEP_UNDER_.join([MULTI_, REGION_])
    _PARAMS_AND_SECRETS_EXT_ARN_: str = SEP_UNDER_.join([PARAMS_, AND_, SECRETS_, EXT_, ARN_])
    _TIMEZONE_: str = "timezone"
    _REGION_META: OrderedDict[str, dict] = OrderedDict(
        {
            US_EAST_1_: {
                _TIMEZONE_: SEP_FW_.join(["US", "Eastern"]),
                _CF_PRICE_CLASS_: cloudfront.PriceClass.PRICE_CLASS_100,
                _MULTI_REGION_: "zxxd85bkqcajcy",
            },  # N. Virginia
            AF_SOUTH_1_: {
                _TIMEZONE_: SEP_FW_.join(["Africa", "Maputo"]),
                _CF_PRICE_CLASS_: cloudfront.PriceClass.PRICE_CLASS_200,
                _MULTI_REGION_: "rk9r4oeyrkry7b",
            },  # Cape Town
            AP_NORTHEAST_2_: {
                _TIMEZONE_: SEP_FW_.join(["Asia", "Seoul"]),
                _CF_PRICE_CLASS_: cloudfront.PriceClass.PRICE_CLASS_200,
                _MULTI_REGION_: "ykg3pn4y7e4eg5",
            },  # Seoul
            AP_SOUTHEAST_2_: {
                _TIMEZONE_: SEP_FW_.join(["Australia", "Sydney"]),
                _CF_PRICE_CLASS_: cloudfront.PriceClass.PRICE_CLASS_ALL,
                _MULTI_REGION_: "376mnqpdodhxyy",
            },  # Sydney
            EU_CENTRAL_1_: {
                _TIMEZONE_: SEP_FW_.join(["Europe", "Berlin"]),
                _CF_PRICE_CLASS_: cloudfront.PriceClass.PRICE_CLASS_100,
                _MULTI_REGION_: "tzy5agpq6gfste",
            },  # Frankfurt
            EU_WEST_2_: {
                _TIMEZONE_: SEP_FW_.join(["Europe", "London"]),
                _CF_PRICE_CLASS_: cloudfront.PriceClass.PRICE_CLASS_ALL,
                # TODO: (NEXT) When multi-region is enabled, reset to use _CF_PRICE_CLASS_DEFAULT
                _MULTI_REGION_: "m3c4s4y4jphaqh",
            },  # London
            SA_EAST_1_: {
                _TIMEZONE_: SEP_FW_.join(["America", "Sao_Paulo"]),
                _CF_PRICE_CLASS_: cloudfront.PriceClass.PRICE_CLASS_ALL,
                _MULTI_REGION_: "5axscsqj4pz4ec",
            },  # São Paulo
        }
    )

    # AWS tag keys - Required
    TAG_KEY_PRIORITY_REQUIRED: int = 300
    TAG_KEY_COMPANY_: str = COMPANY_
    TAG_KEY_COMPONENT_: str = COMPONENT_
    TAG_KEY_CUSTOM_: str = CUSTOM_
    TAG_KEY_DEPLOY_ENV_: str = SEP_SCORE_.join([DEPLOY_, ENV_])
    TAG_KEY_ENV_TYPE_: str = SEP_SCORE_.join([ENV_, TYPE_])
    TAG_KEY_PROJECT_NAME_: str = SEP_SCORE_.join([PROJECT_, NAME_])

    # AWS tag keys - Optional
    TAG_KEY_PRIORITY_OPTIONAL: int = 200
    TAG_KEY_AUTO_START_: str = SEP_SCORE_.join([AUTO_, START_])
    TAG_KEY_AUTO_STOP_: str = SEP_SCORE_.join([AUTO_, STOP_])
    TAG_KEY_AUTO_WEEKEND_: str = SEP_UNDER_.join([AUTO_, WEEKEND_])

    # AWS tag values
    TAG_VAL_AUTO_OFF: str = str(0)
    TAG_VAL_AUTO_ON: str = str(1)
    TAG_VAL_CF_: str = "CloudFront"
    TAG_VAL_CT_: str = "CloudTrail"
    TAG_VAL_INFRA_: str = "Infrastructure"
    TAG_VAL_NONE_: str = NONE_.capitalize()

    # AWS compute resource keywords
    # M5_LARGE_: str = "m5.large"
    M5_XLARGE_: str = "m5.xlarge"
    M6G_LARGE_: str = "m6g.large"
    T3_MEDIUM_: str = "t3.medium"
    T3_SMALL_: str = "t3.small"

    # Deployment environment weightings
    LIGHT_: str = "light"
    HEAVY_: str = "heavy"

    # Deployment environment - internal/external
    DEPLOY_ENVS_INTERNAL: dict[str, str] = {DEV_: LIGHT_, STAGING_: HEAVY_, PERFORM_: LIGHT_}
    DEPLOY_ENVS_EXTERNAL: dict[str, str] = {PROD_: HEAVY_}

    # Deployment environment lists
    DEV_MAIN_BRANCH_LIST: list[str] = [DEV_, MAIN_]
    DEV_STAG_LIST: list[str] = [DEV_, STAGING_]
    DEV_STAG_PROD_LIST: list[str] = [DEV_, STAGING_, PROD_]
    STAG_PROD_LIST: list[str] = [STAGING_, PROD_]
    DEPLOY_ENV_LIST_: str = SEP_UNDER_.join([DEPLOY_, ENV_, LIST_])
    RDS_INSTANCE_TYPE_: str = SEP_UNDER_.join([RDS_, INSTANCE_, TYPE_])
    RDS_INSTANCE_TYPE_DEFAULT_VALUE: str = T3_MEDIUM_
    DATABASE_SERVER_DEPLOY_ENV_MAP_BASE: dict[str, dict] = {
        DEV_STAGING_: {DEPLOY_ENV_LIST_: DEV_STAG_LIST, RDS_INSTANCE_TYPE_: RDS_INSTANCE_TYPE_DEFAULT_VALUE},
        PERFORM_: {DEPLOY_ENV_LIST_: [PERFORM_], RDS_INSTANCE_TYPE_: RDS_INSTANCE_TYPE_DEFAULT_VALUE},
        PROD_: {DEPLOY_ENV_LIST_: [PROD_], RDS_INSTANCE_TYPE_: RDS_INSTANCE_TYPE_DEFAULT_VALUE},
    }

    # AWS ElastiCache Redis metadata
    EC_REDIS_INSTANCE_TYPE_: str = SEP_UNDER_.join([EC_, REDIS_, INSTANCE_, TYPE_])
    EC_REDIS_REPLICAS_: str = SEP_UNDER_.join([EC_, REDIS_, REPLICAS_])
    EC_REDIS_META: dict[str, str] = {
        LIGHT_: {EC_REDIS_INSTANCE_TYPE_: T3_SMALL_, EC_REDIS_REPLICAS_: 1},
        HEAVY_: {EC_REDIS_INSTANCE_TYPE_: T3_MEDIUM_, EC_REDIS_REPLICAS_: 1},
    }

    # AWS (ECS) Elastic Container Service metadata
    ECS_SERVICE_MAX_: str = SEP_UNDER_.join([ECS_, SERVICE_, MAX_])
    ECS_SERVICE_MIN_: str = SEP_UNDER_.join([ECS_, SERVICE_, MIN_])
    ECS_META: dict[str, dict[str, int]] = {
        LIGHT_: {ECS_SERVICE_MIN_: 1, ECS_SERVICE_MAX_: 1},
        HEAVY_: {ECS_SERVICE_MIN_: 1, ECS_SERVICE_MAX_: 3},
    }

    # AWS CloudFront WAF (IPv4 address) block list
    CLOUDFRONT_WAF_BLOCK_IPS_V4: list[str] = []

    # Webhook URLs - MS Teams attribute pointers
    WEBHOOK_URL_: str = SEP_UNDER_.join([WEBHOOK_, URL_])
    WEBHOOK_URL_AMPLIFY_: str = SEP_UNDER_.join([WEBHOOK_URL_, AMPLIFY_])
    WEBHOOK_URL_AWS_NOTIFICATIONS_: str = SEP_UNDER_.join([WEBHOOK_URL_, AWS_, NOTIFICATIONS_])
    WEBHOOK_URL_AWS_NOTIFICATIONS_MISC_: str = SEP_UNDER_.join([WEBHOOK_URL_, AWS_, NOTIFICATIONS_, MISC_])
    WEBHOOK_URL_CLOUDWATCH_: str = SEP_UNDER_.join([WEBHOOK_URL_, CLOUDWATCH_])
    WEBHOOK_URL_CODEPIPELINE_: str = SEP_UNDER_.join([WEBHOOK_URL_, CODEPIPELINE_])
    WEBHOOK_URL_CODEPIPELINE_MISC_: str = SEP_UNDER_.join([WEBHOOK_URL_, CODEPIPELINE_, MISC_])
    WEBHOOK_URL_LAMBDA_: str = SEP_UNDER_.join([WEBHOOK_URL_, LAMBDA_])
    WEBHOOK_URL_SNS_: str = SEP_UNDER_.join([WEBHOOK_URL_, SNS_])

    # AWS Step Functions
    STATUS_FAILED_: str = "FAILED"
    STATUS_SUCCEEDED_: str = "SUCCEEDED"

    # Ports
    _DB_PORT: int = 3306
    _REDIS_PORT: int = 6379
    HTTPS_PORT: int = 443
    HTTP_PORT: int = 80
    SSH_PORT: int = 22

    # Misc. keywords
    ALL_RESOURCES: list[str] = [SEP_ASTERISK_]
    AWS_PRIVATE_DESCRIPTION_BASE_: str = "AWS resource info for"
    AWS_PRIVATE_DESCRIPTION_: str = f"{AWS_PRIVATE_DESCRIPTION_BASE_} `aws-private.sh`."
    AWS_PRIVATE_ECS_DESCRIPTION_: str = f"{AWS_PRIVATE_DESCRIPTION_BASE_} `aws-private-ecs.sh`."
    AWS_PRIVATE_PARAMETER_PREFIX_: str = SEP_EMPTY_.join([SEP_FW_, SCRIPTS_])
    BITBUCKET_WORKSPACE_SIH_INFR_INN: str = "foobar-infrastructure-innovation"
    BITBUCKET_WORKSPACE_SIH_PROD_DEV: str = "foobar-products-development"
    CDK_STACK_PREFIX: str = CDK_.capitalize()
    CDK_STACK_SUFFIX: str = STACK_.capitalize()
    CFN_OUTPUT_TYPE: str = "CfnOutput"
    CIDR_ALL: str = "0.0.0.0/0"
    CODESTAR_CONNECTION_ARNS: dict[str, str] = {
        BITBUCKET_WORKSPACE_SIH_INFR_INN: "arn:aws:codestar-connections:eu-west-2:123456789123:connection/f6bf79ce-405d-4d6e-95e5-7de76c745148",
        BITBUCKET_WORKSPACE_SIH_PROD_DEV: "arn:aws:codestar-connections:eu-west-2:123456789123:connection/d5c2c9e2-9d76-4027-8732-19acf1aafba2",
    }
    DESTPORT_: str = "destport"
    ENCODING: str = "utf-8"
    GENERATE_STRING_KEY_: str = "password"
    LAMBDA_HANDLER_PYTHON: str = "lambda_function.lambda_handler"
    LOCAL_HOST_LIST: list[str] = ["localhost", "127.0.0.1"]
    PASSLIB_SCHEMES: str = "bcrypt"
    PIPELINE_EVENTS: list[str] = [
        "codepipeline-pipeline-pipeline-execution-failed",
        "codepipeline-pipeline-pipeline-execution-canceled",
        "codepipeline-pipeline-pipeline-execution-started",
        "codepipeline-pipeline-pipeline-execution-resumed",
        "codepipeline-pipeline-pipeline-execution-succeeded",
        "codepipeline-pipeline-pipeline-execution-superseded",
        "codepipeline-pipeline-manual-approval-failed",
        "codepipeline-pipeline-manual-approval-needed",
        "codepipeline-pipeline-manual-approval-succeeded",
    ]
    PYTHON_VERSION: str = str(3.9)
    SECRET_EXCLUDE_CHARS: str = "@%*()_+=`~{}|[]\\:\";'?,./"  # Characters to exclude from generated secrets
    SHA256_: str = "SHA256"
    TARGETHOST_: str = "targethost"
    TCT_: str = "to connect to"  # Used in EC2 security group descriptions
    TOKEN_ALGORITHM: str = "HS256"
    URL_NOT_FOUND_: str = "URL not set"
    WILDCARD_ADDRESS: str = "0.0.0.0"

    def __init__(self, aws_region: str, submodule_path_relative_prefix: str = "..", **kwargs) -> None:
        # AWS region
        self.region: str = aws_region

        # CDK app - env vars
        self.aws_profile: str = None
        self.cdk_custom_outputs_path: str = None
        self.email_notification_recipient: str = None
        self.infrastructure_domain_name: str = None
        self.organisation: str = None
        self.organisation_abbrev: str = None
        self.ssh_key: str = None
        for k, v in kwargs.items():
            setattr(self, k, v)

        # AWS submodule paths
        self.sub_paths = {
            service: self.get_path(
                [submodule_path_relative_prefix, self.join_sep_score([self.AWS_, service, "examples"])]
            )
            for service in [self.AMPLIFY_, self.CODEPIPELINE_, self.EC2_, self.LAMBDA_, self.SES_]
        }

        # AWS log group paths
        self.log_groups = {
            service: self.get_path([self.AWS_, service], lead=True)
            for service in [
                self.CT_,
                self.CODEBUILD_,
                self.EC2_,
                self.ECS_,
                self.ELASTICACHE_,
                self.EVENTS_,
                self.LAMBDA_,
                self.VENDEDLOGS_,
                self.VPC_,
            ]
        }

        # Get IP address ranges of CloudFront edge servers
        # with urllib.request.urlopen(f"{self.https_}d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips") as url:
        #     data: dict = json.loads(url.read().decode())
        #     self.cloudfront_global_ips: list[str] = data["CLOUDFRONT_GLOBAL_IP_LIST"] + data["CLOUDFRONT_REGIONAL_EDGE_IP_LIST"]

        self._region_meta_cidrs()
        self._region_meta_params_and_secrets_ext_arn()
        self.region_meta_multi_region: list[str] = [meta[self._MULTI_REGION_] for _, meta in self._REGION_META.items()]

        # Schedule windows for backups and maintenance, dynamic to the local timezone of each AWS region
        self.region_tz = self._REGION_META[aws_region][self._TIMEZONE_]
        self.schedules: Schedules = Schedules(region_tz=self.region_tz)

        self.deploy_envs_meta: dict[str, dict] = self.get_deploy_envs_meta()
        self.deploy_envs_stag_prod_meta: dict[str, dict] = {
            env: self.deploy_envs_meta[env] for env in self.STAG_PROD_LIST
        }

        # Deployment environment and database server identifier mappings, and reverse mappings
        self.database_server_deploy_env_map: dict[str, dict] = self.get_database_server_deploy_env_map(
            self.deploy_envs_meta
        )
        self.database_server_deploy_env_stag_prod_map: dict[str, dict] = self._simplify_database_server_deploy_env_map(
            self.database_server_deploy_env_map, self.STAG_PROD_LIST
        )
        self.deploy_env_database_server_map: dict[str, str] = self.get_deploy_env_database_server_map(
            self.database_server_deploy_env_map
        )

    # --- Private methods ---

    def _add_tags_auto_weekend(self, stacks: list[IConstruct], include_resource_type: list[str] = None) -> None:
        for stack in stacks:
            self._add_tags_helper(stack, include_resource_type, self.TAG_KEY_AUTO_WEEKEND_)

    def _add_tags_helper(self, stack: IConstruct, include_resource_types: list[str], k: str, v: str = None) -> None:
        Tags.of(stack).add(
            key=k,
            value=self.TAG_VAL_AUTO_ON if v is None else v,
            include_resource_types=include_resource_types,
            priority=self.TAG_KEY_PRIORITY_OPTIONAL,
        )

    def _add_tags_required_helper(
        self,
        stacks: list[IConstruct],
        project_name_val: str,
        company_val: str = None,
        custom_val: str = TAG_VAL_NONE_,
        env_type_val: str = TAG_VAL_NONE_,
        component_val: str = TAG_VAL_NONE_,
        deploy_env_val: str = TAG_VAL_NONE_,
    ) -> None:
        if company_val is None:
            company_val = self.organisation
        tags: dict[str, str] = {
            self.TAG_KEY_COMPANY_: company_val,
            self.TAG_KEY_PROJECT_NAME_: project_name_val,
            self.TAG_KEY_CUSTOM_: custom_val,
            self.TAG_KEY_ENV_TYPE_: env_type_val,
            self.TAG_KEY_COMPONENT_: component_val,
            self.TAG_KEY_DEPLOY_ENV_: deploy_env_val,
        }
        if stacks is None:
            return tags
        for stack in stacks:
            for k, v in tags.items():
                Tags.of(stack).add(key=k, value=v, priority=self.TAG_KEY_PRIORITY_REQUIRED)
        return None

    def _add_tags_required_wrapper_helper(
        self,
        stack: IConstruct,
        resource_type: list[str],
    ) -> None:
        self.add_tags_auto_start_stop(stacks=[stack], include_resource_type=resource_type)
        if getattr(stack, self.DEPLOY_ENV_WEEKEND_, None):
            self._add_tags_auto_weekend(stacks=[stack], include_resource_type=resource_type)

    def _autoscaling_auto_scaling_group(
        self,
        self_obj,
        name_props: list[str],
        role: iam.Role,
        security_group: ec2.SecurityGroup,
        user_data: str,
        ssh_key: str,
        topic: sns.Topic,
        instance_type: ec2.InstanceType = None,
        machine_image: ec2.MachineImage = None,
        associate_public_ip_address: bool = True,
        start_capacity: int = 1,
        vpc_subnets_type: ec2.SubnetType = None,
        dependant_constructs: list = None,
        application_target_groups: list[elasticloadbalancing.ApplicationTargetGroup] = None,
        network_target_groups: list[elasticloadbalancing.NetworkTargetGroup] = None,
        max_instance_lifetime: int = 14,
        require_imdsv2: bool = True,
    ) -> autoscaling.AutoScalingGroup:
        """
        Generate an AutoScaling auto-scaling group.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param role: The role that will be associated with the instance profile assigned to this auto-scaling group.
        :param security_group: Security group to launch the instances in.
        :param user_data: A custom EC2 user data to apply to instance within the auto-scaling group.
        :param ssh_key: Name of SSH keypair to grant access to instance within the auto-scaling group.
        :param topic: The SNS topic to send notifications to whenever the auto-scaling group scales.
        :param instance_type: An optional type of instance to launch (i.e. t2.micro or t3.nano). Default: t3.nano.
        :param machine_image: If specified, use a custom ec2.MachineImage to launch. Default: Amazon Linux 2 AMI.
        :param associate_public_ip_address: Whether instances in the auto-scaling group should have public IP addresses associated with them.
        :param start_capacity: An optional capacity for the auto-scaling group to up-scale to.
        :param vpc_subnets_type: An optional selection all subnets of the given type.
        :param dependant_constructs: A list of CDK constructs which are dependencies of the CDK construct being generated.
        :param application_target_groups: An optional list of ALB target groups to attach the Autoscaling auto-scaling group to.
        :param network_target_groups: An optional list of NLB target groups to attach the Autoscaling auto-scaling group to.
        :param max_instance_lifetime: The maximum amount of time that an instance can be in service.
        :param require_imdsv2: True if IMDSv2 should be required on launched instances.
        :return: The AutoScaling auto-scaling group.
        """
        instance_type_chosen: ec2.InstanceType = instance_type if instance_type else self.ec2_instance_type_t3_micro()
        machine_image_chosen: ec2.MachineImage = (
            machine_image if machine_image else self._ec2_machine_image_amazon_linux_2()
        )
        user_data_chosen: ec2.UserData = ec2.UserData.custom(user_data)
        launch_template: ec2.LaunchTemplate = ec2.LaunchTemplate(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "LaunchTemplate"),
            # block_devices=,  Default: - Uses the block device mapping of the AMI
            # cpu_credits=,  # Default: - No credit type is specified in the Launch Template.
            detailed_monitoring=False,
            # disable_api_termination=,  # Default: - The API termination setting is not specified in the Launch Template.
            # ebs_optimized=,  # Default: - EBS optimization is not specified in the launch template.
            # hibernation_configured=,  # Default: - Hibernation configuration is not specified in the launch template; defaulting to false.
            http_endpoint=True,
            http_protocol_ipv6=True,
            http_put_response_hop_limit=1,
            http_tokens=(
                ec2.LaunchTemplateHttpTokens.REQUIRED if require_imdsv2 else ec2.LaunchTemplateHttpTokens.OPTIONAL
            ),
            # instance_initiated_shutdown_behavior=,  # Default: - Shutdown behavior is not specified in the launch template; defaults to STOP.
            instance_metadata_tags=True,  # Default: false
            instance_type=instance_type_chosen,
            key_pair=ec2.KeyPair.from_key_pair_attributes(
                scope=self_obj,
                id=self.get_construct_id(self_obj, name_props, "IKeyPair"),
                key_pair_name=ssh_key,
                type=ec2.KeyPairType.RSA,
            ),
            launch_template_name=self.get_construct_name(self_obj, name_props),
            machine_image=machine_image_chosen,
            # nitro_enclave_enabled=,  # Default: - Enablement of Nitro enclaves is not specified in the launch template; defaulting to false.
            require_imdsv2=require_imdsv2,
            role=role,
            security_group=security_group,
            # spot_options=,  # Default: - Instance launched with this template will not be spot instances.  # TODO: (OPTIONAL) Consider Spot Instances for ASG usage
            user_data=user_data_chosen,
        )
        launch_template.apply_removal_policy(policy=RemovalPolicy.DESTROY)
        auto_scaling_group: autoscaling.AutoScalingGroup = autoscaling.AutoScalingGroup(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "AutoScalingGroup"),
            vpc=self.get_attr_vpc(self_obj),
            # init=,  # Default: - no CloudFormation init
            # init_options=,  # Default: - default options
            # instance_type=instance_type_chosen,  # launch_template and mixed_instances_policy must not be specified when this property is specified
            launch_template=launch_template,  # Default: - Do not provide any launch template
            # machine_image=machine_image_chosen,  # launch_template and mixed_instances_policy must not be specified when this property is specified
            # mixed_instances_policy=,  # Default: - Do not provide any MixedInstancesPolicy
            require_imdsv2=False,  # NB. Setting to 'require_imdsv2' value causes TypeError: https://github.com/aws/aws-cdk/issues/27586
            # role=role,  # launch_template and mixed_instances_policy must not be specified when this property is specified
            # security_group=security_group,  # launch_template and mixed_instances_policy must not be specified when this property is specified
            # user_data=user_data_chosen,  # launch_template and mixed_instances_policy must not be specified when this property is specified
            allow_all_outbound=True,
            # associate_public_ip_address=associate_public_ip_address,  # Default: - Use subnet setting.  # launch_template and mixed_instances_policy must not be specified when this property is specified
            auto_scaling_group_name=self.get_construct_name(self_obj, name_props),
            # block_devices=,  Default: - Uses the block device mapping of the AMI  # launch_template and mixed_instances_policy must not be specified when this property is specified
            capacity_rebalance=False,
            cooldown=Duration.minutes(5),
            # default_instance_warmup=,  # Default: None
            desired_capacity=start_capacity,
            group_metrics=[autoscaling.GroupMetrics.all()],
            # health_check=,  # Default: - HealthCheck.ec2 with no grace period
            ignore_unmodified_size_properties=True,
            # instance_monitoring=,  # Default: - Monitoring.DETAILED (metrics every minute vs. [BASIC] metrics every 5 minutes.)  # launch_template and mixed_instances_policy must not be specified when this property is specified
            # key_name=ssh_key,  # launch_template and mixed_instances_policy must not be specified when this property is specified
            max_capacity=start_capacity,
            max_instance_lifetime=Duration.days(max_instance_lifetime),
            min_capacity=0,
            new_instances_protected_from_scale_in=False,
            notifications=[autoscaling.NotificationConfiguration(topic=topic)],
            # signals=,  # Default: - Do not wait for signals
            # spot_price=,  # Default: none  # launch_template and mixed_instances_policy must not be specified when this property is specified
            ssm_session_permissions=False,
            # termination_policies=[]  # Default: - TerminationPolicy.DEFAULT
            # update_policy=,  # Default: - UpdatePolicy.rollingUpdate() if using init, UpdatePolicy.none() otherwise
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=(
                    ec2.SubnetType.PUBLIC
                    if associate_public_ip_address
                    else (vpc_subnets_type if vpc_subnets_type else ec2.SubnetType.PUBLIC)
                )
            ),
        )
        Annotations.of(auto_scaling_group).acknowledge_warning("@aws-cdk/aws-autoscaling:desiredCapacitySet")
        if dependant_constructs:
            for i in dependant_constructs:
                auto_scaling_group.node.add_dependency(i)
        self._autoscaling_auto_scaling_group_auto_scaling(self_obj, auto_scaling_group, name_props, start_capacity)
        if application_target_groups:
            for target_group in application_target_groups:
                auto_scaling_group.attach_to_application_target_group(target_group)
        if network_target_groups:
            for target_group in network_target_groups:
                auto_scaling_group.attach_to_network_target_group(target_group)
        return auto_scaling_group

    def _autoscaling_auto_scaling_group_auto_scaling(
        self, self_obj, auto_scaling_group: autoscaling.AutoScalingGroup, name_props: list[str], start_capacity: int
    ) -> None:
        """
        Generate an Autoscaling auto-scaling group auto-scaling config.

        :param self_obj: The CDK stack class object.
        :param auto_scaling_group: The Autoscaling auto-scaling group.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param start_capacity: The capacity for the auto-scaling group to up-scale to.
        """
        props: dict = self_obj.schedule_window
        auto_scaling_group.scale_on_schedule(
            id=self.get_construct_id(self_obj, name_props + [self.START_], "ScheduledAction"),
            schedule=autoscaling.Schedule.cron(
                minute=str(0),
                hour=str(props[self.START_]),
                week_day=props[self._START_WEEK_DAYS_],
            ),
            desired_capacity=start_capacity,
            max_capacity=start_capacity,
            min_capacity=start_capacity,
        )
        auto_scaling_group.scale_on_schedule(
            id=self.get_construct_id(self_obj, name_props + [self.STOP_], "ScheduledAction"),
            schedule=autoscaling.Schedule.cron(
                minute=str(0),
                hour=str(props[self.END_]),
                week_day=props[self._END_WEEK_DAYS_],
            ),
            desired_capacity=0,
            max_capacity=0,
            min_capacity=0,
        )

    def _cfn_output_project_name_comp(self, self_obj) -> None:
        """
        Generate an CfnOutput value for this stack.

        The project name and component.

        To be used during the EC2 user data of an EC2 instance (possibly being initialised by an ASG).

        :param self_obj: The CDK stack class object.
        """
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [], self.CFN_OUTPUT_TYPE),
            description="The project name and component. For example, ipsec-vpn-server.",
            value=self.get_attr_project_name_comp(self_obj),
        )

    def _cloudfront_waf_web_acl_logging_configuration(
        self, self_obj, web_acl: waf.CfnWebACL, log_group: logs.LogGroup
    ) -> waf.CfnLoggingConfiguration:
        """
        Generate a CloudFront WAF web ACL logging configuration.

        :param self_obj: The CDK stack class object.
        :param web_acl: The CloudFront WAF web ACL.
        :param log_group: The log group to associate with the CloudFront WAF web ACL.
        :return: The CloudFront WAF web ACL logging configuration.
        """
        logging_configuration: waf.CfnLoggingConfiguration = waf.CfnLoggingConfiguration(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [self.CF_, self.WAF_], "CfnLoggingConfiguration"),
            log_destination_configs=[
                self.format_arn_custom(
                    self_obj,
                    service=self.LOGS_,
                    resource=self.join_sep_score([self.LOG_, self.GROUP_]),
                    resource_name=log_group.log_group_name,
                )
            ],
            resource_arn=web_acl.attr_arn,
        )
        logging_configuration.node.add_dependency(web_acl)
        logging_configuration.node.add_dependency(log_group)
        return logging_configuration

    @staticmethod
    def _cloudfront_waf_web_acl_rule_property_allow_block_ip(
        rule_name: str,
        priority: int,
        action: waf.CfnWebACL.RuleActionProperty,
        metric_name: str,
        waf_ip_set: waf.CfnIPSet,
    ) -> waf.CfnWebACL.RuleProperty:
        """
        Generate a CloudFront WAF web ACL rule property, for either allowing or blocking IPs.

        :param rule_name: The name of the rule.
        :param priority: The priority in which AWS WAF evaluates each request against WAF rules.
        :param action: The action that AWS WAF should take on a web request when it matches the rule's statement.
        :param metric_name: A name of the CloudWatch metric.
        :param waf_ip_set: A WAF ip set used to detect web requests coming from particular IP addresses or CIDR ranges.
        :return: The CloudFront WAF web ACL rule property, for either allowing or blocking IPs.
        """
        return waf.CfnWebACL.RuleProperty(
            name=rule_name,
            priority=priority,
            action=action,
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True,
                cloud_watch_metrics_enabled=True,
                metric_name=metric_name,
            ),
            statement=waf.CfnWebACL.StatementProperty(
                ip_set_reference_statement=waf.CfnWebACL.IPSetReferenceStatementProperty(arn=waf_ip_set.attr_arn)
            ),
        )

    @staticmethod
    def _cloudwatch_metric(
        metric_filter: logs.MetricFilter, metric_name: str, statistic: str, period: Duration = None
    ) -> cloudwatch.Metric:
        """
        Generate a CloudWatch metric.

        :param metric_filter: A filter that extracts information from CloudWatch logs and emits to CloudWatch metrics.
        :param metric_name: A name of the CloudWatch metric.
        :param statistic: What function to use for aggregating.
        :param period: An optional period over which the specified statistic is applied. Default: 5 minutes.
        :return: The CloudWatch metric.
        """
        return metric_filter.metric(
            label=metric_name,
            period=period if period else Duration.minutes(5),
            statistic=statistic,
        )

    def _codebuild_custom_policies_list(self, self_obj, project_name_comp: str) -> list[iam.PolicyStatement]:
        """
        Generate a list of CodeBuild service custom policies.

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :return: The list of CodeBuild service custom policies.
        """
        codepipeline_region: str = self.join_sep_score([self.CODEPIPELINE_, self.get_attr_env_region(self_obj)])
        return [
            self.iam_policy_statement_kmy_key_decrypt(self_obj),
            self.iam_policy_statement_s3_get_objects(
                self_obj, s3_bucket_prefixes=[self.join_sep_empty([codepipeline_region, self.SEP_SCORE_])]
            ),
            self.iam_policy_statement_secretsmanager_get_secret_value(self_obj),
            self.iam_policy_statement_ssm_get_parameter(self_obj),
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.CODEBUILD_, i])
                    for i in [
                        "BatchPutCodeCoverages",
                        "BatchPutTestCases",
                        "CreateReport",
                        "CreateReportGroup",
                        "UpdateReport",
                    ]
                ],
                resources=[
                    self.format_arn_custom(
                        self_obj,
                        service=self.CODEBUILD_,
                        resource=self.join_sep_score([self.REPORT_, self.GROUP_]),
                        resource_name=self.join_sep_score([project_name_comp, self.SEP_ASTERISK_]),
                    )
                ],
            ),
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.join_sep_score([self.CODESTAR_, self.CONNECTIONS_]), "UseConnection"])
                ],
                resources=[getattr(self_obj, self.CODESTAR_CONNECTIONS_ARN_)],
            ),
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.ECR_, i])
                    for i in [
                        "BatchCheckLayerAvailability",
                        "BatchGetImage",
                        "CompleteLayerUpload",
                        "DescribeImages",
                        "GetAuthorizationToken",
                        "GetDownloadUrlForLayer",
                        "InitiateLayerUpload",
                        "PutImage",
                        "UploadLayerPart",
                    ]
                ],
                resources=self.ALL_RESOURCES,
            ),
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.LOGS_, i]) for i in ["CreateLogGroup", "CreateLogStream", "PutLogEvents"]
                ],
                resources=[
                    self.format_arn_custom(
                        self_obj,
                        service=self.LOGS_,
                        resource=self.join_sep_score([self.LOG_, self.GROUP_]),
                        resource_name=self.get_path([self.log_groups[self.CODEBUILD_], i]),
                    )
                    for i in [
                        project_name_comp,
                        self.join_sep_colon([project_name_comp, self.SEP_ASTERISK_]),
                    ]
                ],
            ),
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.S3_, i])
                    for i in [
                        "PutObject",
                        "GetBucketAcl",
                        "GetBucketLocation",
                    ]
                ],
                resources=[
                    self.format_arn_custom(
                        self_obj,
                        service=self.S3_,
                        resource=self.join_sep_score([codepipeline_region, self.SEP_ASTERISK_]),
                    )
                ],
            ),
        ]

    def _codebuild_custom_policies_list_params_and_secrets_ext(self, arn: str) -> list[iam.PolicyStatement]:
        """
        Generate a list of CodeBuild service custom policies.

        :param arn: The ARN of the AWS Parameters and Secrets Lambda Extension.
        :return: The list of CodeBuild service custom policies.
        """
        return [iam.PolicyStatement(actions=[self.join_sep_colon([self.LAMBDA_, "GetLayerVersion"])], resources=[arn])]

    def _codebuild_custom_policies_list_pypi(self, self_obj, project_name_comp: str) -> list[iam.PolicyStatement]:
        """
        Generate a list of CodeBuild service custom policies.

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :return: The list of CodeBuild service custom policies.
        """
        aws_scripts_s3_bucket_name: str = self.get_s3_bucket_name(
            self_obj, self.join_sep_empty([self.AWS_, self.SCRIPTS_])
        )
        return self._codebuild_custom_policies_list(self_obj, project_name_comp) + [
            iam.PolicyStatement(
                actions=[self.join_sep_colon([self.CLOUDFORMATION_, "DescribeStacks"])],
                resources=[self.format_arn_custom(self_obj, service=self.CLOUDFORMATION_, resource=self.STACK_)],
            ),
            iam.PolicyStatement(
                actions=[self.join_sep_colon([self.EC2_, "DescribeInstances"])],
                resources=self.ALL_RESOURCES,
            ),
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.S3_, self.join_sep_empty([i, self.SEP_ASTERISK_])])
                    for i in [
                        "GetBucket",
                        "GetObject",
                        "List",
                    ]
                ],
                resources=[
                    self.format_arn_custom(self_obj, service=self.S3_, resource=r)
                    for r in [
                        aws_scripts_s3_bucket_name,
                        self.get_path([aws_scripts_s3_bucket_name, self.SEP_ASTERISK_]),
                    ]
                ],
            ),
        ]

    def _codebuild_project_pipeline(
        self,
        self_obj,
        project_name_comp: str,
        buildspec_path: str,
        description: str,
        role: iam.Role,
        version_meta_param_name: str = None,
        vpc_props: tuple[ec2.Vpc, list[ec2.SecurityGroup], ec2.SubnetType] = None,
        pypi_package: bool = False,
    ) -> codebuild.Project:
        """
        Generate a CodeBuild project, for use by a CodePipeline pipeline.

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :param buildspec_path: The relative system file path to a buildspec.yml file.
        :param description: A description of the CDK construct.
        :param role: The service Role to assume while running the build.
        :param version_meta_param_name: An optional name of an SSM parameter where version meta is stored.
        :param vpc_props: The VPC network to place CodeBuild network interfaces, a list of security groups to associate
            with the CodeBuild's network interfaces, and the type of subnets to select.
        :param pypi_package: True if the CodeBuild project will be used to build a PyPi package.
        :return: The CodeBuild project, for use by a CodePipeline pipeline.
        """
        # Check whether a deployment pipeline stage will also feature in the pipeline
        deploy_stage_inc: bool = self.BASE_ not in project_name_comp
        # Create a deployment tag parameter, if needed
        ssm_deploy_tag: ssm.IStringParameter = None
        is_deploy_tag: bool = False
        if not pypi_package:
            if self.BASE_ in project_name_comp or getattr(self_obj, self.TAG_DEPLOY_, None):
                is_deploy_tag = True
                ssm_deploy_tag = ssm.StringParameter.from_string_parameter_name(
                    scope=self_obj,
                    id=self.get_construct_id(
                        self_obj, [self.DEPLOY_, self.TAG_], "IStringParameter", project_name_comp=project_name_comp
                    ),
                    string_parameter_name=self.get_path(
                        [self.TAG_, project_name_comp, self.get_attr_deploy_env(self_obj)], lead=True
                    ),
                )
        pipeline_name: str = self.join_sep_score([project_name_comp, self.get_attr_deploy_env(self_obj)])

        # Create Lambda function to use to retrieve version meta, if needed
        version_meta_func_name: str = None
        if version_meta_param_name:
            version_meta_: str = self.join_sep_empty([i.capitalize() for i in [self.VERSION_, self.META_]])
            version_meta_func_name = self.get_lambda_func_name(
                self_obj, [version_meta_], project_name_comp=project_name_comp
            )
            version_meta_param: ssm.IStringParameter = ssm.StringParameter.from_string_parameter_name(
                scope=self_obj,
                id=self.get_construct_id(self_obj, [version_meta_func_name], "IStringParameter"),
                string_parameter_name=version_meta_param_name,
            )

            version_meta_function_role: iam.Role = self.iam_role_lambda(
                self_obj,
                version_meta_func_name,
                managed_policies=self.lambda_managed_policies_vpc_list(),
            )
            version_meta_param.grant_read(version_meta_function_role)
            version_meta_param.grant_write(version_meta_function_role)

            version_meta_function: lambda_.Function = self.lambda_function(
                self_obj,
                version_meta_func_name,
                self.get_path([self.VERSION_, version_meta_]),
                f"{version_meta_} Lambda function for `{pipeline_name}`.",
                {
                    "DEPLOY_ENV": self.get_attr_deploy_env(self_obj),
                    "DEPLOY_TAG": json.dumps(is_deploy_tag),
                    "VERSION_META_PARAMETER": version_meta_param_name,
                },
                version_meta_function_role,
                vpc_props=vpc_props,
                params_and_secrets_ext=True,
                timeout=Duration.seconds(5),
            )
            version_meta_function.grant_invoke(role)

        bitbucket_username: str = None
        bitbucket_app_password: secretsmanager.ISecret = None
        if bitbucket_workspace_required := (
            self.BASE_ not in project_name_comp and hasattr(self_obj, self.CODESTAR_CONNECTIONS_BITBUCKET_WORKSPACE_)
        ):
            # Bitbucket's user: pipelines@foobar.co.uk
            # pipelines_: str = "pipelines"
            # bitbucket_username = self.join_sep_empty([pipelines_, self.default_demo_preview])
            # bitbucket_app_password = secretsmanager.Secret.from_secret_attributes(
            #     scope=self_obj,
            #     id=self.get_construct_id(
            #         self_obj, [self.BITBUCKET_, pipelines_, self.APP_, self.PASSWORD_, self.SECRET_], "ISecret"
            #     ),
            #     secret_complete_arn=self.format_arn_custom(
            #         self_obj,
            #         service=self.SECRETSMANAGER_,
            #         resource=self.SECRET_,
            #         resource_name=self.join_sep_fw(
            #             [self.BITBUCKET_, pipelines_, self.join_sep_score([self.APP_, self.PASSWORD_, "m2pvtM"])]
            #         ),
            #     ),  # Manually created AWS Secrets Manager secret, and replicated across all AWS regions
            # )

            # Bitbucket's user: atlassian@foobar.co.uk
            atlassian_ = "atlassian"
            bitbucket_username = self.join_sep_under([atlassian_, self.organisation])
            bitbucket_app_password = secretsmanager.Secret.from_secret_attributes(
                scope=self_obj,
                id=self.get_construct_id(
                    self_obj, [self.BITBUCKET_, atlassian_, self.APP_, self.PASSWORD_, self.SECRET_], "ISecret"
                ),
                secret_complete_arn=self.format_arn_custom(
                    self_obj,
                    service=self.SECRETSMANAGER_,
                    resource=self.SECRET_,
                    resource_name=self.join_sep_fw(
                        [self.BITBUCKET_, atlassian_, self.join_sep_score([self.APP_, self.PASSWORD_, "A1B9CY"])]
                    ),
                ),  # Manually created AWS Secrets Manager secret, and replicated across all AWS regions
            )

        environment_variables = {
            **{
                k: codebuild.BuildEnvironmentVariable(type=codebuild.BuildEnvironmentVariableType.PLAINTEXT, value=v)
                for k, v in {
                    "AWS_ACCOUNT_ID": self.get_attr_env_account(self_obj),
                    "AWS_DEFAULT_REGION": self.get_attr_env_region(self_obj),
                    "ORGANISATION": self.organisation if not pypi_package else None,
                    "PROJECT_NAME": project_name_comp,
                    "IMAGE_TAG": (
                        self._get_cdk_stack_image_tag(self_obj, project_name_comp) if not pypi_package else None
                    ),
                    "ENV_TYPE": (
                        None
                        if pypi_package or deploy_stage_inc
                        else (self.INTERNAL_ if getattr(self_obj, self.DEPLOY_ENV_INTERNAL_) else self.EXTERNAL_)
                    ),
                    "BASE_REPO_NAME": "amazon-linux-python3" if not pypi_package and not deploy_stage_inc else None,
                    "BASE_REPO_TAG": self.LATEST_ if not pypi_package and not deploy_stage_inc else None,
                    "BASE_IMAGE_TAG": (
                        self._get_cdk_stack_branch_tag(self_obj)
                        if not pypi_package and deploy_stage_inc
                        else (None if deploy_stage_inc else self.PYTHON_VERSION)
                    ),
                    "BASE_PROJECT_NAME": None if deploy_stage_inc else "public.ecr.aws/compose-x/python",
                    "VERSION_META_FUNCTION": version_meta_func_name if version_meta_func_name else None,
                    "DEPLOY_TAG_PARAM": (
                        ssm_deploy_tag.parameter_name
                        if not pypi_package and hasattr(ssm_deploy_tag, "parameter_name")
                        else None
                    ),
                    # TODO: (OPTIONAL) Use instead: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codebuild/BuildEnvironmentVariableType.html#aws_cdk.aws_codebuild.BuildEnvironmentVariableType.PARAMETER_STORE
                    "BITBUCKET_USERNAME": bitbucket_username if bitbucket_workspace_required else None,
                    "BITBUCKET_DOMAIN": "bitbucket.org" if bitbucket_workspace_required else None,
                    "BITBUCKET_WORKSPACE": (
                        getattr(self_obj, self.CODESTAR_CONNECTIONS_BITBUCKET_WORKSPACE_)
                        if bitbucket_workspace_required
                        else None
                    ),
                }.items()
                if v
            },
            **{
                k: codebuild.BuildEnvironmentVariable(
                    type=codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER, value=v
                )
                for k, v in {
                    "BITBUCKET_APP_PASSWORD": (
                        bitbucket_app_password.secret_arn if bitbucket_workspace_required else None
                    )
                }.items()
                if v
            },
        }

        if not pypi_package and deploy_stage_inc:
            container_name_: str = self.join_sep_under([self.CONTAINER_, self.NAME_]).upper()
            comp_: str = self.COMP_.upper()
            container_name_meta: dict[str, str] = {}

            if isinstance(self_obj.ecs_container_name, str):
                container_name_meta = {container_name_: self_obj.ecs_container_name}
            else:
                for i in [container_name_, comp_]:
                    for k, v in dict(self_obj.ecs_container_name).items():
                        container_name_meta[self.join_sep_under([i, k.upper()])] = v if i != comp_ else k
            for k, v in container_name_meta.items():
                environment_variables[k] = codebuild.BuildEnvironmentVariable(
                    type=codebuild.BuildEnvironmentVariableType.PLAINTEXT, value=v
                )

        return codebuild.Project(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [self.CODEBUILD_], "Project", project_name_comp=project_name_comp),
            build_spec=self.file_yaml_safe_load_codebuild_buildspec(buildspec_path),
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER),
            check_secrets_in_plain_text_env_variables=True,
            description=description,
            environment=self.codebuild_build_environment(project_name_comp),
            environment_variables=environment_variables,
            grant_report_group_permissions=False,
            logging=codebuild.LoggingOptions(
                cloud_watch=codebuild.CloudWatchLoggingOptions(
                    log_group=self.logs_log_group(
                        self_obj,
                        [self.CODEBUILD_, self.PROJECT_],
                        self.get_path([self.log_groups[self.CODEBUILD_], pipeline_name]),
                        project_name_comp=project_name_comp,
                    )
                )
            ),
            project_name=pipeline_name,
            queued_timeout=Duration.hours(8),
            role=role,
            security_groups=vpc_props[1] if vpc_props else None,
            subnet_selection=ec2.SubnetSelection(subnet_type=vpc_props[2]) if vpc_props else None,
            timeout=Duration.hours(1),
            vpc=vpc_props[0] if vpc_props else None,
        )

    def _codepipeline_actions_action(
        self,
        self_obj,
        stage_name: str,
        action_name: str,
        project_name_comp: str,
        pipeline_artifacts: dict[str, codepipeline.Artifact],
        run_order: int,
        project: codebuild.Project = None,
        repo: str = None,
        branch: str = None,
        trigger_on_push: bool = None,
    ) -> Union[
        codepipeline_actions.CodeStarConnectionsSourceAction,
        codepipeline_actions.CodeBuildAction,
        codepipeline_actions.EcsDeployAction,
    ]:
        """
        Generate a CodePipeline actions action.

        :param self_obj: The CDK stack class object.
        :param stage_name: The name of the pipeline stage.
        :param action_name: The name to give the action within the pipeline stage.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :param pipeline_artifacts: The pipeline artifacts to be used as input for any action in a pipeline stage.
        :param run_order: The run order in which multiple actions in the same pipeline stage execute.
        :param project: The CodeBuild project to be used for a pipeline build stage.
        :param repo: An optional git repo name, different from the default project_name_comp.
        :param branch: An optional git repo branch, different from the default project_name_comp.
        :param trigger_on_push: True if desire pipeline automatically starting when a new commit is made on the configured repository and branch.
        :return: The CodePipeline actions action.
        """
        artifact_name_suffix: str = self.join_sep_score(["Artifact", project_name_comp])
        if d := getattr(self_obj, self.DEPLOY_ENV_, None):
            artifact_name_suffix = self.join_sep_score([artifact_name_suffix, d])
        source_artifact_name: str = self.join_sep_empty([self_obj.name_source, artifact_name_suffix])
        variables_namespace: str = self.join_sep_empty([action_name, "Variables"])
        action: Union[
            codepipeline_actions.CodeStarConnectionsSourceAction,
            codepipeline_actions.CodeBuildAction,
            codepipeline_actions.EcsDeployAction,
        ] = None
        if stage_name == self_obj.name_source:
            action = codepipeline_actions.CodeStarConnectionsSourceAction(
                connection_arn=getattr(self_obj, self.CODESTAR_CONNECTIONS_ARN_),
                output=codepipeline.Artifact(artifact_name=source_artifact_name),
                owner=getattr(self_obj, self.CODESTAR_CONNECTIONS_BITBUCKET_WORKSPACE_),
                repo=repo if repo else project_name_comp,
                branch=branch if branch else self._get_cdk_stack_branch_tag(self_obj),
                code_build_clone_output=True,
                trigger_on_push=(
                    trigger_on_push
                    if trigger_on_push is not None
                    else (
                        getattr(self_obj, self.DEPLOY_ENV_INTERNAL_) if self.BASE_ not in project_name_comp else False
                    )
                ),
                action_name=action_name,
                run_order=run_order,
                variables_namespace=variables_namespace,
            )
        elif stage_name == self_obj.name_build and project:
            self_obj.build_output = codepipeline.Artifact(
                artifact_name=self.join_sep_empty([self_obj.name_build, artifact_name_suffix])
            )
            action = codepipeline_actions.CodeBuildAction(
                action_name=action_name,
                check_secrets_in_plain_text_env_variables=True,
                input=pipeline_artifacts[source_artifact_name],
                outputs=[self_obj.build_output],
                project=project,
                run_order=run_order,
                type=codepipeline_actions.CodeBuildActionType.BUILD,
                variables_namespace=variables_namespace,
            )
        elif stage_name == self_obj.name_deploy:
            action = codepipeline_actions.EcsDeployAction(
                service=self_obj.ecs_service,
                deployment_timeout=Duration.minutes(20),
                image_file=self_obj.build_output.at_path(file_name="imagedefinitions.json"),
                action_name=action_name,
                run_order=run_order,
                variables_namespace=variables_namespace,
            )
        if action and stage_name != self_obj.name_deploy:
            action_artifact: codepipeline.Artifact = action.action_properties.outputs[0]
            pipeline_artifacts[action_artifact.artifact_name] = action_artifact
        return action

    def _codepipeline_custom_policies_list(self) -> list[iam.PolicyStatement]:
        """
        Generate a list of CodePipeline service custom policies.

        :return: The list of CodePipeline service custom policies.
        """
        return [
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.CODEBUILD_, i])
                    for i in [
                        "BatchGetBuildBatches",
                        "BatchGetBuilds",
                        "StartBuild",
                        "StartBuildBatch",
                    ]
                ],
                resources=self.ALL_RESOURCES,
            ),
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.CODEDEPLOY_, i])
                    for i in [
                        "CreateDeployment",
                        "GetApplication",
                        "GetApplicationRevision",
                        "GetDeployment",
                        "GetDeploymentConfig",
                        "RegisterApplicationRevision",
                    ]
                ],
                resources=self.ALL_RESOURCES,
            ),
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.ECR_, i])
                    for i in [
                        "BatchCheckLayerAvailability",
                        "BatchGetImage",
                        "CompleteLayerUpload",
                        "DescribeImages",
                        "GetAuthorizationToken",
                        "GetDownloadUrlForLayer",
                        "InitiateLayerUpload",
                        "PutImage",
                        "UploadLayerPart",
                    ]
                ],
                resources=self.ALL_RESOURCES,
            ),
            iam.PolicyStatement(
                actions=[self.join_sep_colon([self.IAM_, "PassRole"])],
                conditions={
                    "StringEqualsIfExists": {
                        self.join_sep_colon([self.IAM_, "PassedToService"]): [
                            self._get_aws_service(i)
                            for i in [
                                self.CLOUDFORMATION_,
                                self.CODEBUILD_,
                                self.ECR_,
                                self.ECS_,
                                self.join_sep_under([self.ELASTIC_, self.BEANSTALK_]),
                            ]
                        ]
                    }
                },
                resources=self.ALL_RESOURCES,
            ),
            iam.PolicyStatement(
                actions=[self.join_sep_colon([self.LAMBDA_, i]) for i in ["InvokeFunction", "ListFunctions"]],
                resources=self.ALL_RESOURCES,
            ),
        ]

    def _codepipeline_stage_props(
        self,
        self_obj,
        stage_name: str,
        project_name_comp: str,
        pipeline_artifacts: dict[str, codepipeline.Artifact],
        actions: list[str],
        project: codebuild.Project = None,
        repo: str = None,
        branch: str = None,
        trigger_on_push: bool = None,
    ) -> codepipeline.StageProps:
        """
        Generate a CodePipeline stage properties.

        :param self_obj: The CDK stack class object.
        :param stage_name: The pipeline stage name.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :param pipeline_artifacts: The pipeline artifacts to be used as input for any action in a pipeline stage.
        :param actions: List of the physical, human-readable names of actions for a pipeline stage.
        :param project: The CodeBuild project to be used for a pipeline build stage.
        :param repo: An optional git repo name, different from the default project_name_comp.
        :param branch: An optional git repo branch, different from the default project_name_comp.
        :param trigger_on_push: True if desire pipeline automatically starting when a new commit is made on the configured repository and branch.
        :return: The CodePipeline stage properties.
        """
        if stage_name in {self_obj.name_source, self_obj.name_build, self_obj.name_deploy}:
            return codepipeline.StageProps(
                stage_name=stage_name,
                actions=[
                    action
                    for c, v in enumerate(actions)
                    if (
                        action := self._codepipeline_actions_action(
                            self_obj,
                            stage_name,
                            v,
                            project_name_comp,
                            pipeline_artifacts,
                            run_order=c + 1,
                            project=project,
                            repo=repo,
                            branch=branch,
                            trigger_on_push=trigger_on_push,
                        )
                    )
                ],
            )
        sys.exit(f"## Stage name '{stage_name}' not valid.")

    def _ec2_elastic_ips_meta(
        self, self_obj, elastic_ip_parameter_names: dict[str, str], inc_cfn_output: bool
    ) -> dict[str, tuple[str, str]]:
        """
        Get all EC2 Elastic IP meta, based on Elastic IP parameter names, stored in AWS SSM Paramter Store.

        :param self_obj: The CDK stack class object.
        :param elastic_ip_parameter_names: A mapping Elastic IP to parameter name.
        :param inc_cfn_output: If true, create CfnOutput constructs for each Elastic IP public IPv4 address.
        :return: The EC2 Elastic IP meta.
        """
        return {
            eip: self._ec2_elastic_ips_meta_helper(self_obj, eip, parameter_name, inc_cfn_output)
            for eip, parameter_name in elastic_ip_parameter_names.items()
        }

    def _ec2_elastic_ips_meta_helper(
        self, self_obj, eip: str, parameter_name: str, inc_cfn_output: bool
    ) -> tuple[str, str]:
        meta: tuple[str, str] = (
            ssm.StringParameter.value_for_string_parameter(scope=self_obj, parameter_name=parameter_name),
            self.join_sep_empty([j.capitalize() for j in eip.split(self.SEP_SCORE_)]),
        )
        if inc_cfn_output:
            # Publish the Elastic IP public IPv4 address as CloudFormation output, to be used as a ref for an
            #  WAF Web ACL during CloudFront Distribution creation.
            CfnOutput(
                scope=self_obj,
                id=self.get_construct_id(
                    self_obj, [eip], self.CFN_OUTPUT_TYPE, project_name_comp=self.get_attr_project_name(self_obj)
                ),
                description=f"The {meta[1]} public IPv4 address for {getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)}. For example, 123.4.5.67.",
                value=meta[0],
            )
        return meta

    @staticmethod
    def _ec2_machine_image_amazon_linux_2() -> ec2.AmazonLinuxImage:
        """
        Generate an Amazon Linux 2 machine image (AMI).

        :return: The Amazon Linux 2 machine image.
        """
        return ec2.AmazonLinuxImage(
            cached_in_context=False,
            cpu_type=ec2.AmazonLinuxCpuType.X86_64,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            # kernel=,  # Default: -
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            # user_data=,  # Default: - Empty UserData for Linux machines
            virtualization=ec2.AmazonLinuxVirt.HVM,
        )

    def _ecs_fargate_service_auto_scaling(
        self,
        self_obj,
        name_props: list[str],
        ecs_service: ecs.FargateService,
        admin: bool,
        target_utilization_percent: int = 75,
    ) -> None:
        """
        Generate an ECS fargate service auto-scaling config.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param ecs_service: The ECS fargate service.
        :param admin: Whether the ECS service is for admin only.
        :param target_utilization_percent: The target value for memory/CPU utilization across all tasks in the service.
        """
        ecs_fargate_scalable_target: ecs.ScalableTaskCount = ecs_service.auto_scale_task_count(
            max_capacity=self_obj.env_meta[self.ECS_SERVICE_MAX_], min_capacity=0
        )
        if not admin and self_obj.env_meta[self.ECS_SERVICE_MAX_] > 1:
            ecs_fargate_scalable_target.scale_on_memory_utilization(
                id=self.get_construct_id(self_obj, name_props, "ScaleMemory"),
                target_utilization_percent=target_utilization_percent,
            )
            ecs_fargate_scalable_target.scale_on_cpu_utilization(
                id=self.get_construct_id(self_obj, name_props, "ScaleCpu"),
                target_utilization_percent=target_utilization_percent,
            )
        if getattr(self_obj, self.DEPLOY_ENV_NOT_24_7_):
            schedule_window_ecs: dict = getattr(self_obj, self.SCHEDULE_WINDOW_ECS_)
            ecs_fargate_scalable_target.scale_on_schedule(
                id=self.get_construct_id(self_obj, name_props + [self.ON_], "ScaleSchedule"),
                schedule=applicationautoscaling.Schedule.cron(
                    minute=str(0),
                    hour=str(schedule_window_ecs[self.START_]),
                    week_day=schedule_window_ecs[self._START_WEEK_DAYS_],
                ),
                max_capacity=(
                    self_obj.env_meta[self.ECS_SERVICE_MIN_] if admin else self_obj.env_meta[self.ECS_SERVICE_MAX_]
                ),
                min_capacity=self_obj.env_meta[self.ECS_SERVICE_MIN_],
            )
            ecs_fargate_scalable_target.scale_on_schedule(
                id=self.get_construct_id(self_obj, name_props + [self.OFF_], "ScaleSchedule"),
                schedule=applicationautoscaling.Schedule.cron(
                    minute=str(0),
                    hour=str(schedule_window_ecs[self.END_]),
                    week_day=schedule_window_ecs[self._END_WEEK_DAYS_],
                ),
                max_capacity=0,
                min_capacity=0,
            )

    def _elasticache_log_delivery_config(
        self, self_obj, name_props: list[str], log_group_name: str, log_type: str
    ) -> elasticache.CfnReplicationGroup.LogDeliveryConfigurationRequestProperty:
        """
        Generate an ElastiCache replication group log delivery configuration request property.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param log_group_name: The name of the Log group.
        :param log_type: Either ``slow-log`` or ``engine-log``.
        :return: The ElastiCache replication group log delivery configuration request property.
        """
        self.logs_log_group(self_obj, self_obj.ec_redis_props + name_props, log_group_name)
        return elasticache.CfnReplicationGroup.LogDeliveryConfigurationRequestProperty(
            destination_details=elasticache.CfnReplicationGroup.DestinationDetailsProperty(
                cloud_watch_logs_details=elasticache.CfnReplicationGroup.CloudWatchLogsDestinationDetailsProperty(
                    log_group=log_group_name
                )
            ),
            destination_type=self.join_sep_score([self.CLOUDWATCH_, self.LOGS_]),
            log_format="json",
            log_type=log_type,
        )

    @staticmethod
    def _elasticache_log_delivery_config_to_json(
        log_delivery_config: elasticache.CfnReplicationGroup.LogDeliveryConfigurationRequestProperty,
    ) -> dict:
        """
        Generate an ElastiCache replication group log delivery configuration request property (as JSON).

        :param log_delivery_config: ElastiCache replication group log delivery configuration request property.
        :return: The ElastiCache replication group log delivery configuration request property (as JSON).
        """
        return {
            "destination_details": {
                "cloud_watch_logs_details": {
                    "log_group": log_delivery_config.destination_details.cloud_watch_logs_details.log_group
                }
            },
            "destination_type": log_delivery_config.destination_type,
            "log_format": log_delivery_config.log_format,
            "log_type": log_delivery_config.log_type,
        }

    def _elasticache_replication_group_auto_scaling(
        self,
        self_obj,
        name_props: list[str],
        replication_group: elasticache.CfnReplicationGroup,
        replication_group_props: list[str],
        num_node_groups: int,
    ) -> None:
        """
        Generate an ElastiCache replication group auto-scaling config.

        IMPORTANT: Cluster mode enabled only.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param replication_group: The ElastiCache replication group.
        :param replication_group_props: Specific property details to include in the CDK construct ID.
        :param num_node_groups: The maximum number of node groups (shards) for
            this ElastiCache (cluster mode enabled) replication group.
        """
        if not getattr(self_obj, self.DEPLOY_ENV_PROD_):
            name_rep_group_props: list[str] = name_props + replication_group_props
            ec_scalable_target: applicationautoscaling.ScalableTarget = applicationautoscaling.ScalableTarget(
                scope=self_obj,
                id=self.get_construct_id(self_obj, name_rep_group_props, "ScalableTarget"),
                max_capacity=num_node_groups,
                min_capacity=1,
                resource_id=self.get_path(
                    [self.join_sep_score(replication_group_props), replication_group.replication_group_id]
                ),
                scalable_dimension=self.join_sep_under(
                    [self.ELASTICACHE_, self.join_sep_score(replication_group_props), "NodeGroups"]
                ),
                service_namespace=applicationautoscaling.ServiceNamespace.ELASTICACHE,
            )
            ec_scalable_target.node.add_dependency(replication_group)
            schedule_window_ec_redis: dict[str, dict[str, int]] = (
                getattr(self_obj, self.SCHEDULE_WINDOW_ELASTICACHE_ALL_DAYS_)
                if getattr(self_obj, self.SCHEDULE_WINDOW_ELASTICACHE_WEEKEND_) is not None
                else getattr(self_obj, self.SCHEDULE_WINDOW_ELASTICACHE_WEEK_DAYS_)
            )
            ec_scalable_target.scale_on_schedule(
                id=self.get_construct_id(self_obj, name_rep_group_props + [self.ON_], "ScaleSchedule"),
                schedule=applicationautoscaling.Schedule.cron(
                    minute=str(0),
                    hour=str(schedule_window_ec_redis[self.START_]),
                    week_day=schedule_window_ec_redis[self._START_WEEK_DAYS_],
                ),
                max_capacity=num_node_groups,
                min_capacity=1,
            )
            ec_scalable_target.scale_on_schedule(
                id=self.get_construct_id(self_obj, name_rep_group_props + [self.OFF_], "ScaleSchedule"),
                schedule=applicationautoscaling.Schedule.cron(
                    minute=str(0),
                    hour=str(schedule_window_ec_redis[self.END_]),
                    week_day=schedule_window_ec_redis[self._END_WEEK_DAYS_],
                ),
                max_capacity=1,
                min_capacity=1,
            )

    def _elasticache_replication_group_auto_scaling_custom(
        self,
        self_obj,
        name_props: list[str],
        replication_group: elasticache.CfnReplicationGroup,
        replication_group_kwargs: dict[str, str],
        replication_group_kms_key: kms.Key,
        auth_token_key: str,
        auth_token_secret: secretsmanager.Secret,
        security_groups: list[ec2.SecurityGroup],
    ) -> None:
        """
        Generate an ElastiCache replication group auto-scaling custom config.

        Using Lambda function to snapshot and delete an ElastiCache replication group,
        so it can be re-created later using the same snapshot.

        IMPORTANT: Cluster mode DISABLED only.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param replication_group: The ElastiCache replication group.
        :param replication_group_kwargs: The ElastiCache replication group (sanitised) kwargs, used in creation by CDK.
        :param replication_group_kms_key: The ElastiCache replication group KMS key.
        :param auth_token_key: The key in the ElastiCache replication group (sanitised) kwargs,
          which needs updating (at Lambda function runtime) with the actual Redis AUTH token value.
        :param auth_token_secret: The secret storing the password used to access a password protected server.
        :param security_groups: A list of security groups to associate with the Lambda's network interfaces.
        """
        global_rep_group_: str = self.join_sep_empty([self.GLOBAL_, self.REPLICATION_, self.GROUP_])
        ec2_actions: list[str] = [
            self.join_sep_colon([self.EC2_, i])
            for i in [
                "CreateNetworkInterface",
                "CreateTags",
                "DeleteNetworkInterface",
                "DescribeNetworkInterfaces",
                "DescribeSubnets",
                "DescribeVpcs",
            ]
        ]
        elasticache_actions: list[str] = [
            self.join_sep_colon([self.ELASTICACHE_, i])
            for i in [
                "AddTagsToResource",
                "DescribeSnapshots",
                "ListTagsForResource",
            ]
        ]
        elasticache_resource_types: list[str] = [
            "cluster",
            "parametergroup",
            "replicationgroup",
            "securitygroup",
            "snapshot",
            "subnetgroup",
            "usergroup",
        ]
        iam_policy_statement_kmy_all = iam.PolicyStatement(
            actions=[
                self.join_sep_colon([self.KMS_, self.SEP_ASTERISK_])
            ],  # TODO: (NEXT) Confirm exactly what KMS service actions are needed for this IAM policy
            resources=[replication_group_kms_key.key_arn],
        )

        func_name_base_props: list[str] = [i.capitalize() for i in name_props] + [self.AUTO_.capitalize()]
        lambda_func_cloudwatch_custom: lambda_.Function = self.lambda_function_cloudwatch(
            self_obj,
            self.get_lambda_func_name(self_obj, [self.join_sep_empty(func_name_base_props)]),
            security_groups=security_groups,
        )
        for i in [self.START_, self.STOP_]:
            is_start: bool = bool(i == self.START_)
            is_stop: bool = bool(i == self.STOP_)

            lambda_func_name_path: str = self.join_sep_empty(func_name_base_props + [i.capitalize()])
            lambda_func_name: str = self.get_lambda_func_name(self_obj, [lambda_func_name_path])
            lambda_func_topic: sns.Topic = self.sns_topic(
                self_obj, [self.join_sep_empty([self.SUBS_.capitalize(), lambda_func_name])]
            )
            lambda_func_role: iam.Role = self.iam_role_lambda(
                self_obj,
                lambda_func_name,
                managed_policies=self.lambda_managed_policies_vpc_list(),
                custom_policies=(
                    [
                        iam_policy_statement_kmy_all,
                        iam.PolicyStatement(
                            actions=[self.join_sep_colon([self.ELASTICACHE_, "DeleteReplicationGroup"])]
                            + elasticache_actions,
                            resources=[
                                self.format_arn_custom(self_obj, service=self.ELASTICACHE_, resource=r)
                                for r in [self.join_sep_score([self.RESERVED_, self.INSTANCE_]), self.USER_]
                                + elasticache_resource_types
                            ],
                        ),
                        iam.PolicyStatement(
                            actions=[self.join_sep_colon([self.ELASTICACHE_, "CreateSnapshot"])],
                            resources=self.ALL_RESOURCES,
                        ),
                        iam.PolicyStatement(
                            actions=[
                                self.join_sep_colon([self.S3_, i])
                                for i in [
                                    "DeleteObject",
                                    "GetBucketAcl",
                                    "PutObject",
                                ]
                            ]
                            + ec2_actions,
                            resources=self.ALL_RESOURCES,
                        ),
                    ]
                    if is_stop
                    else [
                        iam_policy_statement_kmy_all,
                        iam.PolicyStatement(
                            actions=[
                                self.join_sep_colon([self.ELASTICACHE_, i])
                                for i in [
                                    "CreateReplicationGroup",
                                    "DeleteSnapshot",
                                ]
                            ]
                            + elasticache_actions,
                            resources=[
                                self.format_arn_custom(
                                    self_obj,
                                    service=self.ELASTICACHE_,
                                    resource=r,
                                    **({self.REGION_: self.SEP_EMPTY_} if r == global_rep_group_ else {}),
                                )
                                for r in [global_rep_group_] + elasticache_resource_types
                            ],
                        ),
                        iam.PolicyStatement(
                            actions=[
                                self.join_sep_colon([self.LOGS_, i])
                                for i in [
                                    "CreateLogDelivery",
                                    "DeleteLogDelivery",
                                    "GetLogDelivery",
                                    "ListLogDeliveries",
                                    "UpdateLogDelivery",
                                ]
                            ]
                            + [self.join_sep_colon([self.S3_, "GetObject"])]
                            + ec2_actions,
                            resources=self.ALL_RESOURCES,
                        ),
                    ]
                ),
            )
            lambda_func_topic.grant_publish(lambda_func_role)
            if is_start:
                auth_token_secret.grant_read(lambda_func_role)

            self.lambda_function(
                self_obj,
                lambda_func_name,
                self.get_path([self.ELASTICACHE_, lambda_func_name_path]),
                self.join_sep_space([self.AUTO_.capitalize(), i, replication_group.replication_group_description]),
                {
                    k: v
                    for k, v in {
                        "EC_REP_GROUP_ARN": (
                            self.format_arn_custom(
                                self_obj,
                                service=self.ELASTICACHE_,
                                resource=self.join_sep_empty([self.REPLICATION_, self.GROUP_]),
                                resource_name=replication_group.replication_group_id,
                            )
                            if is_stop
                            else None
                        ),
                        "EC_REP_GROUP_FINAL_SNAPSHOT_ID": self.join_sep_score(
                            [replication_group.replication_group_id, self.FINAL_, self.SNAPSHOT_]
                        ),
                        "EC_REP_GROUP_ID": replication_group.replication_group_id if is_stop else None,
                        "EC_REP_GROUP_KWARGS": json.dumps(replication_group_kwargs) if is_start else None,
                        "REDIS_PW_KEY": auth_token_key if is_start else None,
                        "REDIS_PW_SECRET": auth_token_secret.secret_full_arn if is_start else None,
                        "SNS_TOPIC": lambda_func_topic.topic_arn,
                        "TAG_KEY": self.join_sep_score([self.AUTO_, i]),
                        "TAG_VALUES": self.TAG_VAL_AUTO_ON,
                        "WEBHOOK_URL": self.get_ms_teams_aws_notifications_webhook_url(
                            self_obj, self.WEBHOOK_URL_LAMBDA_
                        ),
                    }.items()
                    if v
                },
                lambda_func_role,
                vpc_props=(self.get_attr_vpc(self_obj), security_groups, ec2.SubnetType.PRIVATE_WITH_EGRESS),
                params_and_secrets_ext=is_start,
                timeout=Duration.seconds(10),
                events_rules=self.lambda_function_events_rules_cron(
                    self_obj,
                    lambda_func_name,
                    self.END_ if is_stop else i,
                    [
                        t
                        for t in [
                            ([lambda_func_name], getattr(self_obj, self.SCHEDULE_WINDOW_ELASTICACHE_WEEK_DAYS_), {}),
                            (
                                (
                                    [lambda_func_name, self.WEEKEND_],
                                    getattr(self_obj, self.SCHEDULE_WINDOW_ELASTICACHE_WEEKEND_),
                                    {self.WEEKEND_: True},
                                )
                                if getattr(self_obj, self.SCHEDULE_WINDOW_ELASTICACHE_WEEKEND_) is not None
                                else None
                            ),
                        ]
                        if t
                    ],
                ),
                lambda_function_cloudwatch_custom=lambda_func_cloudwatch_custom,
            )

    def _elasticache_replication_group_sanitise_kwargs(
        self,
        replication_group_kwargs: dict[str, str],
        auth_token_key: str,
        log_delivery_configurations_key: str,
    ) -> dict[str, str]:
        """
        Generate an ElastiCache replication group (sanitised) kwargs, for an auto-scaling custom config.

        :param replication_group_kwargs: The ElastiCache replication group kwargs, to be sanitised.
        :param auth_token_key: The key in the ElastiCache replication group kwargs,
          which needs updating (at Lambda function runtime) with the actual Redis AUTH token value.
        :param log_delivery_configurations_key: The key in the ElastiCache replication group kwargs,
          containing log delivery configurations.
        :return: The ElastiCache replication group (sanitised) kwargs.
        """
        kwargs_sanitised: dict[str, str] = {}
        for k, v in replication_group_kwargs.items():
            if k == auth_token_key:
                kwargs_sanitised[k] = self.EMPTY_
            elif k == log_delivery_configurations_key:
                kwargs_sanitised[k] = json.dumps(
                    [self._elasticache_log_delivery_config_to_json(i) for i in v], default=str
                )
            else:
                kwargs_sanitised[k] = v if isinstance(v, str) else json.dumps(v, default=str)
        return kwargs_sanitised

    def _elasticache_subnet_group(self, self_obj, description: str) -> elasticache.CfnSubnetGroup:
        """
        Generate an ElastiCache subnet group.

        :param self_obj: The CDK stack class object.
        :param description: A description of the CDK construct.
        :return: The ElastiCache subnet group.
        """
        return

    @staticmethod
    def _elasticloadbalancing_listener_condition_http_header(
        header_name: str, secret: secretsmanager.Secret
    ) -> elasticloadbalancing.ListenerCondition:
        """
        Generate an ElasticLoadBalancing listener condition, specifically for an HTTP header.

        :param header_name: The HTTP header name.
        :param secret: The secret storing the HTTP header value(s).
        :return: The ElasticLoadBalancing listener condition, specifically for an HTTP header.
        """
        return elasticloadbalancing.ListenerCondition.http_header(
            name=header_name,
            values=[secret.secret_value_from_json(header_name).to_string()],
        )

    def _file_json_load(self, path: str) -> dict:
        with open(path, "r", encoding=self.ENCODING) as f:
            return json.load(f)

    def _file_read(self, path: str) -> str:
        with open(path, "r", encoding=self.ENCODING) as f:
            return f.read()

    def _file_read_ec2_user_data(self, self_obj) -> str:
        return self._file_read(
            self.get_path(
                [
                    self.sub_paths[self.EC2_],
                    self.join_sep_under(self.get_attr_project_name_comp_props(self_obj)),
                    self.join_sep_dot([self.join_sep_score([self.USER_, self.DATA_]), self.SH_]),
                ]
            )
        )

    def _generate_url(self, self_obj, origin_path: str) -> str:
        return self.join_sep_empty([self.HTTPS_, self_obj.fqdn, origin_path])

    def _generate_url_private(self, self_obj, origin_path: str) -> str:
        return self.join_sep_empty(
            [
                self.HTTP_,
                getattr(self_obj, self.ECS_SERVICE_CLOUD_MAP_SERVICE_NAME_),
                self.SEP_DOT_,
                self_obj.fqdn_private,
                self.SEP_COLON_,
                str(getattr(self_obj, self.ALB_PORT_)),
                origin_path,
            ]
        )

    def _get_aws_service(self, service: str) -> str:
        return self.join_sep_dot([service, self.join_sep_empty([self.AMAZONAWS_, self.DOT_COM_])])

    def _get_cdk_stack_branch_tag(self, self_obj) -> str:
        """
        Generate a CDK stack branch tag.

        :param self_obj: The CDK stack class object.
        :return: The CDK stack branch tag.
        """
        return (
            self.PROD_
            if getattr(self_obj, self.DEPLOY_ENV_PROD_, None) or getattr(self_obj, self.DEPLOY_ENV_DEMO_, None)
            else (self.MAIN_ if self.get_attr_deploy_env(self_obj) != self.DEV_ else self.DEV_)
        )

    def _get_cdk_stack_image_tag(self, self_obj, project_name_comp: str) -> str:
        """
        Generate a CDK stack image tag.

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :return: The CDK stack image tag.
        """
        return (
            self.PROD_
            if getattr(self_obj, self.DEPLOY_ENV_PROD_)
            else (
                self.MAIN_
                if self.BASE_ in project_name_comp and self.get_attr_deploy_env(self_obj) != self.DEV_
                else self.get_attr_deploy_env(self_obj)
            )
        )

    def _get_factory_pipeline_event_lambda_function_arn(self) -> str:
        return getattr(self, self.PIPELINE_EVENT_LAMBDA_FUNCTION_ARN_)

    def _get_file_name_base(self, name_props: list[str], file_ext: str) -> str:
        return self.join_sep_dot([self.join_sep_under(name_props), file_ext])

    def _get_ms_teams_codepipeline_webhook_url(self, self_obj) -> str:
        project_name: str = self.get_attr_project_name(self_obj)
        urls: dict = self.lookup_ms_teams(self.WEBHOOK_URL_CODEPIPELINE_)
        if project_name in urls:
            return urls[project_name]
        return self.lookup_ms_teams(self.WEBHOOK_URL_CODEPIPELINE_MISC_)

    def _get_subdomain(
        self, self_obj, comp_subdomain: str, custom_val: str = None, project_subdomain: bool = False
    ) -> str:
        """
        Generate a subdomain, based on provided attributes.

        :param self_obj: The CDK stack class object.
        :param comp_subdomain: The subdomain for the project component (e.g. 'gw', 'portal', etc.).
        :param custom_val: An optional, is not None if the project is a customisation.
        :param project_subdomain: An optional, true if the comp_subdomain is actually a project subdomain instead.
        :return: The subdomain.
        """
        if d := self.get_attr_deploy_env(self_obj):
            if getattr(self_obj, self.DEPLOY_ENV_DEMO_, None):
                prefix: str = self.organisation_abbrev if d.startswith(self.organisation_abbrev) else d
                url_deploy_env: str = self.join_sep_score([prefix, self.DEMO_])
            elif getattr(self_obj, self.DEPLOY_ENV_PREVIEW_, None):
                prefix: str = self.organisation_abbrev if d.startswith(self.organisation_abbrev) else d
                url_deploy_env: str = self.join_sep_score([prefix, self.PREVIEW_])
            else:
                url_deploy_env: str = d
            if getattr(self_obj, self.DEPLOY_ENV_PROD_):
                subdomain: str = comp_subdomain
            else:
                props: list[str] = [comp_subdomain, url_deploy_env]
                subdomain: str = self.join_sep_dot(reversed(props) if project_subdomain else props)
            return self.join_sep_dot([subdomain, custom_val]) if custom_val else subdomain
        return None

    def _join_sep_at_sign(self, props: list[str]) -> str:
        return self.SEP_AT_SIGN_.join(props)

    def _kms_key(
        self,
        self_obj,
        name_props: list[str],
        description: str,
        no_trim: bool = False,
        enable_key_rotation: bool = False,
    ) -> kms.Key:
        """
        Generate a KMS key.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param description: A description of the CDK construct.
        :param no_trim: True if name length doesn't need to be <=64 chars.
        :param enable_key_rotation: Indicates whether AWS KMS rotates the KMS key.
        :return: The KMS key.
        """
        name_props.append(self.KMS_)
        return kms.Key(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "Key"),
            alias=self.get_construct_name(self_obj, name_props, no_trim=no_trim),
            description=f"{description} KMS customer-managed key (CMK).",
            # enabled=True,
            enable_key_rotation=enable_key_rotation,
            # key_spec=kms.KeySpec.SYMMETRIC_DEFAULT,
            # key_usage=kms.KeyUsage.ENCRYPT_DECRYPT,
            pending_window=Duration.days(7),
            # policy=,  # Default: - A policy doc with perms for the account root to administer the key will be created.
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _lambda_function_kwargs(
        self,
        self_obj,
        function_name: str,
        description: str,
        environment: dict[str, str],
        role: iam.Role,
        environment_encryption: kms.Key,
        ephemeral_storage_size: Size,
        filesystem: lambda_.FileSystem,
        vpc_props: tuple[ec2.Vpc, list[ec2.SecurityGroup], ec2.SubnetType],
        memory_size: int,
        params_and_secrets_ext: bool,
        log_group: logs.LogGroup,
        timeout: Duration,
        reserved_concurrent_executions: int,
        retry_attempts: int,
        async_: bool,
        layers: list[lambda_.LayerVersion] = None,
        docker_image: bool = False,
    ) -> dict:
        """
        Generate a Lambda function kwargs dict.

        :param self_obj: The CDK stack class object.
        :param function_name: A name for the Lambda function.
        :param description: A description of the CDK construct.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda function.
        :param role: Lambda execution role. The role that will be assumed by the Lambda function upon execution.
        :param environment_encryption: The KMS key to use for environment encryption, and optionally
            for DLQ encryption, if ``async_`` is enabled.
        :param ephemeral_storage_size: The size of the function’s `/tmp` directory in MiB. Default: 512 MiB.
        :param filesystem: An optional filesystem configuration for the Lambda function.
        :param vpc_props: The VPC network to place Lambda network interfaces, a list of security groups to associate
            with the Lambda's network interfaces, and the type of subnets to select.
        :param memory_size: The amount of memory, in MiB, that is allocated to your Lambda function. Lambda uses this
            value to proportionally allocate the amount of CPU power. Default: 128 MiB.
        :param params_and_secrets_ext: True if the Lambda function is use AWS Parameters and Secrets Extension.
        :param log_group: The log group to associate with the Lambda function.
        :param timeout: The execution time (in seconds) after which Lambda terminates the Lambda function.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function.
            Default: - No specific limit - account limit.
        :param retry_attempts: An optional maximum number of times to retry when the function returns an error.
        :param async_: True if the Lambda function is to be used with asynchronous invocation:
            https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html. Default: False.
        :param layers: A list of layers to add to the Lambda function's execution environment.
        :param docker_image: True if generating a Lambda Docker image function.
        :return: The Lambda function kwargs dict.
        """
        return {
            k: v
            for k, v in {
                # Commented out 'allow_all_outbound' after https://github.com/aws/aws-cdk/releases/tag/v2.93.0, to fix:
                #  "RuntimeError: Configure 'allowAllOutbound' directly on the supplied SecurityGroups."
                # "allow_all_outbound": True if vpc_props else None,  # Cannot configure without configuring a VPC.
                "allow_public_subnet": bool(vpc_props and vpc_props[2] == ec2.SubnetType.PUBLIC),
                "architecture": self.lambda_architecture_x86_64(),
                # TODO: (OPTIONAL) Look into Code Signing for Lambda functions: https://docs.aws.amazon.com/lambda/latest/dg/configuration-codesigning.html
                # "code_signing_config": ,  # Default: - Not Sign the Code
                # "current_version_options": ,  # Default: - default options as described in lambda_.VersionOptions
                "dead_letter_topic": (
                    self.sns_topic(
                        self_obj,
                        [self.join_sep_empty([function_name, "Dlq"])],
                        subscriptions_=[self.sns_subscriptions_email_subscription()],
                    )
                    if async_
                    else None
                ),
                "description": description,
                "environment": environment,
                "environment_encryption": (
                    environment_encryption if environment_encryption else self.get_attr_kms_key_stack(self_obj)
                ),
                "ephemeral_storage_size": ephemeral_storage_size,
                # "events": [],
                "filesystem": filesystem,
                "function_name": function_name,
                # "initial_policy": ,
                # TODO: (OPTIONAL) Look into Lambda Insights for Lambda functions: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Lambda-Insights.html
                # "insights_version": ,  # Default: - No Lambda Insights
                "layers": (
                    (layers if layers else [self.lambda_layer_version_base(self_obj, function_name)])
                    if not docker_image
                    else None
                ),
                "logging_format": lambda_.LoggingFormat.TEXT,
                "log_group": (
                    self.logs_log_group(
                        self_obj,
                        [function_name],
                        self.get_path([self.log_groups[self.LAMBDA_], function_name], lead=True),
                    )
                    if log_group is None
                    else log_group
                ),
                "memory_size": memory_size,
                "params_and_secrets": (
                    lambda_.ParamsAndSecretsLayerVersion.from_version(
                        version=lambda_.ParamsAndSecretsVersions.V1_0_103,
                        **self.lambda_function_kwargs_params_and_secrets(
                            reserved_concurrent_executions=reserved_concurrent_executions
                        ),
                    )
                    if params_and_secrets_ext
                    else None
                ),
                # "profiling": ,
                # "profiling_group": ,
                "reserved_concurrent_executions": reserved_concurrent_executions,
                "role": role,
                "security_groups": vpc_props[1] if vpc_props else None,
                "timeout": timeout,
                "tracing": lambda_.Tracing.DISABLED,  # TODO: (OPTIONAL) Enable AWS X-Ray Tracing for Lambda functions.
                "vpc": vpc_props[0] if vpc_props else None,
                "vpc_subnets": ec2.SubnetSelection(subnet_type=vpc_props[2]) if vpc_props else None,
                "max_event_age": Duration.hours(6),
                "on_failure": (
                    lambda_destinations.SnsDestination(
                        topic=self.sns_topic(
                            self_obj,
                            [self.join_sep_empty([function_name, "OnFailure"])],
                            subscriptions_=[self.sns_subscriptions_email_subscription()],
                        )
                    )
                    if async_
                    else None
                ),
                # "on_success": ,  # Default: - no destination
                "retry_attempts": retry_attempts if retry_attempts else (0 if async_ else 2),
            }.items()
            if v
        }

    @staticmethod
    def _lambda_function_metric(
        lambda_func: lambda_.Function, metric_name: str, statistic: str, period: Duration = None
    ) -> cloudwatch.Metric:
        """
        Generate a Lambda function metric.

        :param lambda_func: The Lambda function.
        :param metric_name: A name of the CloudWatch metric.
        :param statistic: What function name to use for aggregating.
        :param period: An optional period over which the specified statistic is applied. Default: 5 minutes.
        :return: The Lambda function metric.
        """
        return lambda_func.metric(
            metric_name=metric_name,
            label=metric_name,
            period=period if period else Duration.minutes(5),
            statistic=statistic,
        )

    def _lambda_function_support(
        self,
        self_obj,
        lambda_func: Union[lambda_.Function, lambda_.DockerImageFunction],
        function_name: str,
        reserved_concurrent_executions: int,
        security_groups: list[ec2.SecurityGroup],
        inc_sns_topic_errors: bool,
        events_rules: list[tuple[events.Rule, dict]],
        async_: bool,
        is_support: bool = False,
        lambda_function_cloudwatch_custom: lambda_.Function = None,
        **kwargs,
    ) -> None:
        if reserved_concurrent_executions:
            lambda_func.add_alias(
                alias_name=self.LATEST_.capitalize(),
                description=f"{function_name} latest alias, to enable {reserved_concurrent_executions} provisioned concurrent executions.",
                provisioned_concurrent_executions=reserved_concurrent_executions,
                max_event_age=Duration.hours(6),
                # on_failure=,  # Default: - no destination
                # on_success=,  # Default: - no destination
                retry_attempts=0 if async_ else 2,
            )

        metric_statistic: str = "Sum"

        function_errors_name: str = self.join_sep_empty([function_name, self.ERRORS_.capitalize()])
        cloudwatch_alarm_errors: cloudwatch.Alarm = self.cloudwatch_alarm(
            self_obj,
            [function_errors_name],
            self._lambda_function_metric(lambda_func, self.ERRORS_.capitalize(), metric_statistic),
            f"Send notifications to SNS for {function_name} function error.",
            cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            cloudwatch.TreatMissingData.NOT_BREACHING,
            threshold=0,
            alarm_name=function_errors_name,
        )

        function_errors_custom_name: str = self.join_sep_empty([function_errors_name, self.CUSTOM_.capitalize()])
        cloudwatch_alarm_errors_custom: cloudwatch.Alarm = self.cloudwatch_alarm(
            self_obj,
            [function_errors_custom_name],
            self._cloudwatch_metric(
                self._logs_metric_filter(
                    self_obj,
                    [function_name],
                    lambda_func.log_group.log_group_name,
                    lambda_func.log_group,
                    self.join_sep_fw([i.capitalize() for i in [self.LAMBDA_, self.ERRORS_]]),
                ),
                lambda_func.log_group.log_group_name,
                metric_statistic,
            ),
            f"Send notifications to SNS for {function_name} error or warning log lines.",
            cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            cloudwatch.TreatMissingData.NOT_BREACHING,
            threshold=0,
            alarm_name=function_errors_custom_name,
        )

        if inc_sns_topic_errors:
            sns_topic_errors: sns.Topic = self.sns_topic(
                self_obj,
                [function_errors_name],
                subscriptions_=[
                    (
                        subscriptions.LambdaSubscription(
                            fn=(
                                lambda_function_cloudwatch_custom
                                if lambda_function_cloudwatch_custom
                                else self.lambda_function_cloudwatch(
                                    self_obj, function_name, security_groups=security_groups, **kwargs
                                )
                            )
                        )
                        if (not is_support)
                        else self.sns_subscriptions_email_subscription()
                    )
                ],
            )
            cloudwatch_alarm_errors.add_alarm_action(cloudwatch_actions.SnsAction(sns_topic_errors))
            cloudwatch_alarm_errors_custom.add_alarm_action(cloudwatch_actions.SnsAction(sns_topic_errors))

        if events_rules:
            for event, payload in events_rules:
                event.add_target(
                    target=targets.LambdaFunction(
                        handler=lambda_func,
                        event=events.RuleTargetInput.from_object(payload) if payload else None,
                        # dead_letter_queue=,  # Default: - no dead-letter queue  # TODO: (OPTIONAL) Add an SQS queue to be used as DLQ ?
                        max_event_age=Duration.hours(24),
                        retry_attempts=185,
                    )
                )

    @staticmethod
    def _log_metric_filter_pattern_default() -> str:
        """
        Generate a Logs metric filter pattern, the default custom filter pattern used for
        filtering out error/warning log lines.

        :return: The Logs metric filter pattern.
        """
        return '?"[ERROR]" ?"[WARN]"'

    def _log_metric_filter_pattern_default_app(self, http_error_code: int) -> str:
        """
        Generate a Logs metric filter pattern, the default custom filter pattern used for
        filtering out error/warning log lines, in apps.

        :param http_error_code: The HTTP error code, which should raise an CloudWatch Alarm.
        :return: The Logs metric filter pattern.
        """
        return f'{self._log_metric_filter_pattern_default()} ?" {http_error_code} "'

    def _logs_metric_filter(
        self,
        self_obj,
        name_props: list[str],
        metric_name: str,
        log_group: logs.LogGroup,
        metric_namespace: str,
        filter_pattern: str = None,
        default_value: int = None,
        metric_value: str = None,
    ) -> logs.MetricFilter:
        """
        Generate a Logs metric filter.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param metric_name: A name of the CloudWatch metric.
        :param log_group: The log group to create the filter on.
        :param metric_namespace: The namespace of the metric to emit.
        :param filter_pattern: An optional string to use as log pattern.
        :param default_value: The value to emit if the pattern does not match a particular event.
        :param metric_value: The value to emit for the metric.
        :return: The Logs metric filter.
        """
        return logs.MetricFilter(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "MetricFilter"),
            log_group=log_group,
            filter_pattern=logs.FilterPattern.literal(
                filter_pattern if filter_pattern else self._log_metric_filter_pattern_default()
            ),
            metric_name=metric_name,
            metric_namespace=metric_namespace,
            default_value=default_value,
            # dimensions=,  # Default: - No dimensions attached to metrics.
            filter_name=metric_name,
            metric_value=metric_value,
            # unit=,  # Default: - No unit attached to metrics.
        )

    def _rds_database_instance_backup_retention(self, self_obj, default: bool = False) -> logs.RetentionDays:
        """
        Generate an RDS database instance backup retention.

        :param self_obj: The CDK stack class object.
        :param default: True if to default to the non-production RDS database instance backup retention.
        :return: The RDS database instance backup retention.
        """
        return Duration.days(30) if not default and getattr(self_obj, self.DEPLOY_ENV_PROD_) else Duration.days(14)

    def _region_meta_cidrs(self, cidr_base: int = 10, cidr_per_region: int = 5) -> None:
        """
        Populate AWS region metadata, with CIDR blocks, for each region.

        :param cidr_base: An optional base number for the first number in the CIDR block. Default: 10.
        :param cidr_per_region: The number of CIDR blocks allocated per AWS region. Default 5.
        """
        for i in [True, False]:
            for r, m in self._REGION_META.items():
                if bool(r == self.EU_WEST_2_) == i:
                    cidr_list: list[str] = [f"{cidr_base + i}.0.0.0/16" for i in range(cidr_per_region)]
                    self._REGION_META[r] = {**m, **{self.CIDRS_: cidr_list}}
                    cidr_base += cidr_per_region
                    if i:
                        break

    def _region_meta_params_and_secrets_ext_arn(self) -> None:
        """
        Populate AWS region metadata, with the AWS Parameter and Secrets Lambda extension ARN, for each region.
        """
        region_account_no: dict[str, str] = {
            self.EU_WEST_2_: "133256977650",
            self.US_EAST_1_: "177933569100",
            self.AF_SOUTH_1_: "317013901791",
            self.AP_NORTHEAST_2_: "738900069198",
            self.AP_SOUTHEAST_2_: "665172237481",
            self.EU_CENTRAL_1_: "187925254637",
            self.SA_EAST_1_: "933737806257",
        }
        for r, m in self._REGION_META.items():
            self._REGION_META[r] = {
                **m,
                **{
                    self._PARAMS_AND_SECRETS_EXT_ARN_: self.join_sep_colon(
                        [
                            self.ARN_,
                            self.AWS_,
                            self.LAMBDA_,
                            r,
                            region_account_no[r],
                            self.LAYER_,
                            "AWS-Parameters-and-Secrets-Lambda-Extension",
                            str(4),
                        ]
                    )
                },
            }

    def _route53_a_record_cloudfront_distribution(
        self,
        self_obj,
        distribution: cloudfront.Distribution,
        hosted_zone: route53.IHostedZone,
        comment: str,
        record_name: str,
        ttl: int = 300,
    ) -> route53.ARecord:
        """
        Generate a Route53 A-record, for use with a CloudFront distribution.

        :param self_obj: The CDK stack class object.
        :param distribution: The CloudFront distribution to use as an alias record target
        :param hosted_zone: The hosted zone in which to define the new record.
        :param comment: A comment to add on the record.
        :param record_name: The domain name (sub-domain) for this record.
        :param ttl: The resource record cache time to live (TTL).
        :return: The Route53 A-record, for use with a CloudFront distribution.
        """
        return route53.ARecord(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [self.ROUTE_53_], "ARecord"),
            target=route53.RecordTarget.from_alias(
                alias_target=route53targets.CloudFrontTarget(distribution=distribution)
            ),
            zone=hosted_zone,
            comment=comment,
            record_name=record_name,
            ttl=Duration.seconds(ttl),
        )

    def _route53_aaaa_record_cloudfront_distribution(
        self,
        self_obj,
        distribution: cloudfront.Distribution,
        hosted_zone: route53.IHostedZone,
        comment: str,
        record_name: str,
        ttl: int = 300,
    ) -> route53.ARecord:
        """
        Generate a Route53 AAAA-record, for use with a CloudFront distribution.

        :param self_obj: The CDK stack class object.
        :param distribution: The CloudFront distribution to use as an alias record target
        :param hosted_zone: The hosted zone in which to define the new record.
        :param comment: A comment to add on the record.
        :param record_name: The domain name (sub-domain) for this record.
        :param ttl: The resource record cache time to live (TTL).
        :return: The Route53 AAAA-record, for use with a CloudFront distribution.
        """
        return route53.AaaaRecord(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [self.ROUTE_53_], "AaaaRecord"),
            target=route53.RecordTarget.from_alias(
                alias_target=route53targets.CloudFrontTarget(distribution=distribution)
            ),
            zone=hosted_zone,
            comment=comment,
            record_name=record_name,
            ttl=Duration.seconds(ttl),
        )

    def _route53_hosted_zone(self, self_obj) -> route53.HostedZone:
        """
        Get the primary Route53 hosted zone.

        :param self_obj: The CDK stack class object.
        :return: The primary Route53 hosted zone.
        """
        return (
            self_obj.hosted_zone_com
            if getattr(self_obj, self.HOSTED_ZONE_NAME_).endswith(self.DOT_COM_)
            else self_obj.hosted_zone_co_uk
        )

    def _s3_bucket_kwargs(
        self,
        self_obj,
        bucket_name: str,
        inc_lifecycle_rules: bool,
        encryption_key: kms.Key = None,
        event_bridge_enabled: bool = False,
        notifications_handler_role: iam.Role = None,
    ) -> dict:
        """
        Generate a S3 bucket kwargs dict.

        :param self_obj: The CDK stack class object.
        :param bucket_name: The S3 bucket name.
        :param encryption_key: The KMS key to use for encryption.
        :param inc_lifecycle_rules: True if needing Amazon S3 to manage objects during their lifetime.
        :param event_bridge_enabled: True if this bucket should send notifications to Amazon EventBridge or not. Default: False
        :param notifications_handler_role: The role to be used by the notifications' handler. Default: - a new role will be created.
        :return: The S3 bucket kwargs dict.
        """
        is_encryption_key: bool = bool(encryption_key is not None)
        lifecycle_rules: list[s3.LifecycleRule] = None
        try:
            rules: dict = self_obj.lifecycle_rules_delete
            lifecycle_rules = []
            for k, v in rules.items():
                lifecycle_rules = lifecycle_rules + self.s3_bucket_lifecycle_rules_delete_objects_days(
                    self_obj, bucket_name, v, prefix=k
                )
        except AttributeError:
            if inc_lifecycle_rules:
                lifecycle_rules = self._s3_bucket_lifecycle_rules_auto_adjust_storage_class(self_obj, bucket_name)
        return {
            k: v
            for k, v in {
                "scope": self_obj,
                "id": self.get_construct_id(self_obj, [bucket_name, self.S3_], "Bucket"),
                "auto_delete_objects": True,
                "block_public_access": s3.BlockPublicAccess.BLOCK_ALL,
                "bucket_key_enabled": is_encryption_key,
                "bucket_name": bucket_name,
                # "cors": [],  # Default: - No CORS configuration.
                "encryption": s3.BucketEncryption.KMS if is_encryption_key else s3.BucketEncryption.S3_MANAGED,
                "encryption_key": encryption_key if is_encryption_key else None,
                "enforce_ssl": True,  # Default: false
                "event_bridge_enabled": event_bridge_enabled,
                # "intelligent_tiering_configurations": None,  # Default: No Intelligent Tiering Configurations.
                # "inventories": [],  # Default: - No inventory configuration.
                "lifecycle_rules": lifecycle_rules,
                # "metrics": [],  # Default: - No metrics configuration.
                "notifications_handler_role": (
                    notifications_handler_role
                    if event_bridge_enabled and notifications_handler_role is not None
                    else None
                ),  # Default: - a new role will be created.
                "object_ownership": s3.ObjectOwnership.OBJECT_WRITER,
                "public_read_access": False,
                "removal_policy": RemovalPolicy.DESTROY,
                "transfer_acceleration": False,
                "versioned": False,
            }.items()
            if v
        }

    def _s3_bucket_lifecycle_rules_auto_adjust_storage_class(
        self, self_obj, bucket_name: str
    ) -> list[s3.LifecycleRule]:
        """
        Generate a list of S3 bucket lifecycle rules, for auto adjusting S3 object storage classes.

        :param self_obj: The CDK stack class object.
        :param bucket_name: The S3 bucket name.
        :return: The list of S3 bucket lifecycle rules.
        """
        return [
            s3.LifecycleRule(
                enabled=True,
                id=self.get_construct_id(
                    self_obj,
                    [bucket_name, self.AUTO_, self.ADJUST_, self.STORAGE_, self.CLASS_],
                    "LifecycleRule",
                ),
                abort_incomplete_multipart_upload_after=Duration.days(90),
                transitions=[
                    s3.Transition(
                        storage_class=k,
                        transition_after=Duration.days(v),
                    )
                    for k, v in {
                        s3.StorageClass.INFREQUENT_ACCESS: 30,
                        s3.StorageClass.INTELLIGENT_TIERING: 60,
                        s3.StorageClass.GLACIER: 90,
                        s3.StorageClass.DEEP_ARCHIVE: 180,
                    }.items()
                ],
            )
        ]

    def _secrets_manager_secret_api_key(
        self,
        self_obj,
        name_props: list[str],
        description: str,
        password_length: int = 64,
    ) -> secretsmanager.Secret:
        """
        Generate a Secrets Manager secret, for an API key.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param description: A description of the API key.
        :param password_length: The desired length of the generated password. Default: 64 chars.
        :return: The Secrets Manager secret.
        """
        return self.secrets_manager_secret(
            self_obj,
            name_props,
            f"{description} API key secret.",
            self.get_construct_name(self_obj, name_props),
            password_length=password_length,
        )

    def _secrets_manager_secret_api_keys(
        self,
        self_obj,
        attr_name: str,
        description: str,
        singleton: bool = False,
    ) -> None:
        """
        Generate Secrets Manager secrets, for one or multiple API keys.

        :param self_obj: The CDK stack class object.
        :param attr_name: The name of the CDK stack class object to be set.
        :param description: A description of the API key.
        :param singleton: If true, only generate the one API key.
        """
        main_description: str = getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)
        if description:
            main_description = self.join_sep_space([main_description, description])
        name_props: list[str] = attr_name.split(self.SEP_UNDER_)
        setattr(self_obj, attr_name, self._secrets_manager_secret_api_key(self_obj, name_props, main_description))
        if not singleton and (preview_demo_meta := getattr(self_obj, self.DEPLOY_ENV_PREVIEW_DEMO_META_)):
            setattr(
                self_obj,
                self.PLURAL_MAPPINGS[attr_name],
                {
                    deploy_env: self._secrets_manager_secret_api_key(
                        self_obj,
                        name_props_short + [deploy_env, name_props_last],
                        self.join_sep_space([main_description, meta[1]]),
                    )
                    for deploy_env, meta in preview_demo_meta.items()
                    if (name_props_short := name_props[:-1]) and (name_props_last := name_props[-1])
                },
            )

    def _secrets_manager_secret_secret_key(
        self,
        self_obj,
        name_props: list[str],
        description: str,
        password_length: int = 64,
    ) -> secretsmanager.Secret:
        """
        Generate a Secrets Manager secret, for a Secret key.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param description: A description of the Secret key.
        :param password_length: The desired length of the generated password. Default: 64 chars.
        :return: The Secrets Manager secret.
        """
        return self.secrets_manager_secret(
            self_obj,
            name_props,
            f"{description} Secret key secret.",
            self.get_construct_name(self_obj, name_props),
            password_length=password_length,
        )

    def _secrets_manager_secret_secret_keys(
        self,
        self_obj,
        attr_name: str,
        description: str,
        singleton: bool = False,
    ) -> None:
        """
        Generate Secrets Manager secrets, for one or multiple Secret keys.

        :param self_obj: The CDK stack class object.
        :param attr_name: The name of the CDK stack class object to be set.
        :param description: A description of the Secret key.
        :param singleton: If true, only generate the one Secret key.
        """
        main_description: str = getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)
        if description:
            main_description = self.join_sep_space([main_description, description])
        name_props: list[str] = attr_name.split(self.SEP_UNDER_)
        setattr(self_obj, attr_name, self._secrets_manager_secret_secret_key(self_obj, name_props, main_description))
        if not singleton and (preview_demo_meta := getattr(self_obj, self.DEPLOY_ENV_PREVIEW_DEMO_META_)):
            setattr(
                self_obj,
                self.PLURAL_MAPPINGS[attr_name],
                {
                    deploy_env: self._secrets_manager_secret_secret_key(
                        self_obj,
                        name_props_short + [deploy_env, name_props_last],
                        self.join_sep_space([main_description, meta[1]]),
                    )
                    for deploy_env, meta in preview_demo_meta.items()
                    if (name_props_short := name_props[:-1]) and (name_props_last := name_props[-1])
                },
            )

    def _set_attrs_ecs_service_cloud_map_service_name(self, self_obj) -> None:
        if not hasattr(self_obj, self.ECS_SERVICE_CLOUD_MAP_SERVICE_NAME_):
            setattr(self_obj, self.ECS_SERVICE_CLOUD_MAP_SERVICE_NAME_, self.ECS_)

    def _set_attrs_word_map_project_name_comp(
        self, self_obj, project_name: str, component: str, is_custom: bool = False
    ) -> None:
        setattr(self_obj, self.WORD_MAP_COMPONENT_, self.lookup_word_map(component))
        word_map_project_name: str = self.lookup_word_map(project_name)
        if word_map_project_name is None:
            setattr(self_obj, self.WORD_MAP_PROJECT_NAME_, word_map_project_name)
        else:
            props: list[str] = [word_map_project_name]
            if is_custom:
                props.append(self.lookup_word_map(self.CUSTOM_))
            elif custom_val := getattr(self_obj, self.PRODUCT_CUSTOM_, None):
                props.append(self.lookup_word_map(custom_val))
            setattr(self_obj, self.WORD_MAP_PROJECT_NAME_, self.join_sep_space(props))

    def _simplify_database_server_deploy_env_map(
        self, orig_map: dict[str, dict], deploy_env_list: list[str]
    ) -> dict[str, dict]:
        new_map: dict[str, dict] = {}
        for database_server, meta in orig_map.items():
            for deploy_env in deploy_env_list:
                if deploy_env == database_server or deploy_env in meta[self.DEPLOY_ENV_LIST_]:
                    new_map[database_server] = meta
        return new_map

    def _ssm_string_parameter_ecs_container_env(self, self_obj, name_props: list[str]) -> ssm.StringParameter:
        """
        Generate a Systems Manager (SSM) string parameter, for any ECS container environment variable.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :return: The Systems Manager (SSM) string parameter.
        """
        ecs_container_env_props: list[str] = [self.ECS_, self.CONTAINER_, self.ENV_]
        string_parameter_name = self.get_path(
            [
                self.get_attr_project_name_comp(self_obj),
                self.join_sep_score(ecs_container_env_props),
                self.join_sep_under([i.upper() for i in name_props]),
            ],
            lead=True,
        )
        return ssm.StringParameter.from_string_parameter_name(
            scope=self_obj,
            id=self.get_construct_id(self_obj, ecs_container_env_props + name_props, "IStringParameter"),
            string_parameter_name=string_parameter_name,
        )

    # --- Public methods ---

    def acm_certificate(
        self,
        self_obj,
        name_props: list[str],
        domain_name: str,
        hosted_zone: route53.IHostedZone,
        alternative_names: list[str] = None,
    ) -> acm.Certificate:
        """
        Generate an AWS Certificate Manager (ACM) certificate.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param domain_name: The Fully Qualified Domain Name (FQDN) to request a certificate for.
        :param hosted_zone: The hosted zone where DNS records must be created.
        :param alternative_names: An optional list of alternative domain names on your certificate.
        :return: The AWS Certificate Manager (ACM) certificate.
        """
        return acm.Certificate(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "Certificate"),
            domain_name=domain_name,
            # certificate_name=,  # Will be recorded in the 'Name' tag. Default: the full, absolute path of this construct.
            subject_alternative_names=alternative_names,
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

    def add_tags_auto_start_stop(self, stacks: list[IConstruct], include_resource_type: list[str] = None) -> None:
        for stack in stacks:
            for k in [self.TAG_KEY_AUTO_START_, self.TAG_KEY_AUTO_STOP_]:
                self._add_tags_helper(stack, include_resource_type, k)

    def add_tags_required(
        self,
        stacks: list[IConstruct],
        project_name_val: str,
        company_val: str = None,
        custom_val: str = None,
        env_type_val: str = None,
        component_val: str = None,
        deploy_env_val: str = None,
    ) -> Optional[dict[str, str]]:
        if company_val is None:
            company_val = self.organisation
        if any(project_name_val == i for i in [self.TAG_VAL_CF_, self.TAG_VAL_CT_, self.TAG_VAL_INFRA_]):
            return self._add_tags_required_helper(stacks, project_name_val)
        for t in [self.TAG_KEY_ENV_TYPE_, component_val]:
            if not t:
                sys.exit(f"## Stacks: {stacks}\n## Required tag '{t}' must be set.")
        return self._add_tags_required_helper(
            stacks, project_name_val, company_val, custom_val, env_type_val, component_val, deploy_env_val
        )

    def add_tags_required_wrapper(
        self,
        stacks: dict[str, IConstruct],
        project_name: str,
        component: str,
        is_cache: bool = False,
        is_db_server: bool = False,
        custom_val: str = None,
    ) -> None:
        for d, s in stacks.items():
            self.add_tags_required(
                stacks=[s],
                project_name_val=self.lookup_word_map(project_name),
                custom_val=self.lookup_word_map(custom_val) if custom_val else self.TAG_VAL_NONE_,
                env_type_val=(
                    env_type if (env_type := getattr(s, self.DEPLOY_ENV_TYPE_)) and env_type else self.TAG_VAL_NONE_
                ),
                component_val=self.lookup_word_map(component),
                deploy_env_val=d,
            )
            if getattr(s, self.DEPLOY_ENV_NOT_24_7_, None):
                if is_db_server:
                    self._add_tags_required_wrapper_helper(s, ["AWS::RDS::DBInstance"])
                elif is_cache:
                    self._add_tags_required_wrapper_helper(s, ["AWS::ElastiCache::ReplicationGroup"])

    def autoscaling_auto_scaling_group_default(
        self, self_obj, role: iam.Role, security_group: ec2.SecurityGroup, lambda_func_sns: lambda_.Function, **kwargs
    ) -> autoscaling.AutoScalingGroup:
        """
        Generate an AutoScaling auto-scaling group, with default options.

        :param self_obj: The CDK stack class object.
        :param role: The role that will be associated with the instance profile assigned to this auto-scaling group.
        :param security_group: Security group to launch the instances in.
        :param lambda_func_sns: The Lambda function, for handling messages published to an assistive SNS topic.
        :return: The AutoScaling auto-scaling group, with default options.
        """
        name_props: list[str] = [self.ASG_]
        return self._autoscaling_auto_scaling_group(
            self_obj,
            name_props,
            role,
            security_group,
            self._file_read_ec2_user_data(self_obj),
            self.ssh_key,
            self.sns_topic(
                self_obj,
                name_props + [self.SNS_],
                subscriptions_=[subscriptions.LambdaSubscription(fn=lambda_func_sns)],
            ),
            **kwargs,
        )

    def cfn_output_acm_cert(self, self_obj, cert: acm.Certificate) -> None:
        """
        Generate an CfnOutput value for this stack.

        For an ACM certificate ARN.

        To be used as a ref for an SSL cert during CloudFront Distribution creation.

        :param self_obj: The CDK stack class object.
        :param cert: The ACM certificate.
        """
        CfnOutput(
            scope=self_obj,
            id=self.cfn_output_acm_cert_construct_id(self_obj),
            description=f"The ACM Certificate ARN for '{self_obj.fqdn}', and all multi-region names. "
            f"For example, arn:aws:acm:us-east-1:012345678912:certificate/????????-????-????-????-????????????.",
            value=cert.certificate_arn,
        )

    def cfn_output_acm_cert_construct_id(self, self_obj, is_key: bool = False) -> str:
        construct_id: str = self.get_construct_id(self_obj, [self.CF_, self.CERT_], self.CFN_OUTPUT_TYPE)
        if is_key:
            return construct_id.replace(self.SEP_SCORE_, self.SEP_EMPTY_)
        return construct_id

    def cfn_output_cf_waf_web_acl(self, self_obj, web_acl: waf.CfnWebACL, desc_insert: str = None) -> None:
        """
        Generate an CfnOutput value for this stack.

        For an CloudFront WAF web ACL ARN.

        To be used as a ref for an WAF web ACL during CloudFront Distribution creation.

        :param self_obj: The CDK stack class object.
        :param web_acl: The CloudFront WAF web ACL.
        :param desc_insert: An optional description insert, for all comments. Defaults to `CdkConstructsFactory.get_attr_word_map_project_name_comp()` method.
        """
        if desc_insert is None:
            desc_insert = self.get_attr_word_map_project_name_comp(self_obj)
        CfnOutput(
            scope=self_obj,
            id=self.cfn_output_cf_waf_web_acl_construct_id(self_obj),
            description=f"The CloudFront WAF Web ACL ARN for {desc_insert}. "
            f"For example, arn:aws:waf::111122223333:webacl/*.",
            value=web_acl.attr_arn,
        )

    def cfn_output_cf_waf_web_acl_construct_id(self, self_obj, is_key: bool = False) -> str:
        construct_id: str = self.get_construct_id(
            self_obj, [self.CF_, self.WAF_, self.WEB_, self.ACL_, self.ARN_], self.CFN_OUTPUT_TYPE
        )
        if is_key:
            return construct_id.replace(self.SEP_SCORE_, self.SEP_EMPTY_)
        return construct_id

    def cfn_output_dependant_stack_name(self, self_obj, alt_stack: Stack, name_prop: str) -> None:
        """
        Generate an CfnOutput value for this stack.

        The name of a dependant CDK stack.

        To be used during the EC2 user data of an EC2 instance (possibly being initialised by an ASG).

        :param self_obj: The CDK stack class object.
        :param alt_stack: The dependant CDK stack.
        :param name_prop: Specific property detail to include in the CDK construct ID.
        """
        name_props: list[str] = [self.STACK_, self.NAME_]
        if name_prop is not None:
            name_props = [name_prop] + name_props
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, self.CFN_OUTPUT_TYPE),
            description="The name of a dependant CDK stack. For example, CdkIpsecVpnBaseStack.",
            value=alt_stack.stack_name,
        )

    def cfn_output_ec2_instance_eip_allocation_id(
        self,
        self_obj,
        elastic_ip: ec2.CfnEIP,
    ) -> None:
        """
        Generate an CfnOutput value for this stack.

        The AllocationId of an Elastic IP.

        To be used during the EC2 user data of an EC2 instance (possibly being initialised by an ASG).

        :param self_obj: The CDK stack class object.
        :param elastic_ip: The Elastic IP.
        """
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(self_obj, ["AllocationId"], self.CFN_OUTPUT_TYPE),
            description="The AllocationId of the Elastic IP. For example, eipalloc-5723d13e.",
            value=elastic_ip.get_att("AllocationId").to_string(),
        )

    def cfn_output_ec2_instance_log_group_name(self, self_obj, log_group_name: str) -> None:
        """
        Generate an CfnOutput value for this stack.

        The Logs log group name for use in the EC2 instance setup.

        To be used during the EC2 user data of an EC2 instance (possibly being initialised by an ASG).

        :param self_obj: The CDK stack class object.
        :param log_group_name: The name of the Logs log group.
        """
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [self.LOG_, self.GROUP_, self.NAME_], self.CFN_OUTPUT_TYPE),
            description="The Logs log group name for use in the EC2 instance setup. For example, /aws/ec2/instance/ipsec-vpn-server.",
            value=log_group_name,
        )

    def cfn_output_ec2_instance_public_ipv4_parameter_name(self, self_obj, parameter_name: str) -> None:
        """
        Generate an CfnOutput value for this stack.

        The SSM parameter name to store the public (IPv4) address of the EC2 instance.

        To be used during the EC2 user data of an EC2 instance (possibly being initialised by an ASG).

        :param self_obj: The CDK stack class object.
        :param parameter_name: The name of the Logs log group.
        """
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(
                self_obj, [self.PUBLIC_, self.IPV4_, self.PARAMETER_, self.NAME_], self.CFN_OUTPUT_TYPE
            ),
            description="The SSM parameter name to store the public (IPv4) address of the EC2 instance. For example, /CdkIpsecVpnServerStack/public-ipv4.",
            value=parameter_name,
        )

    def cfn_output_ec2_instance_vpc_name(self, self_obj) -> None:
        """
        Generate an CfnOutput value for this stack.

        The VPC name for use in the EC2 instance name.

        To be used during the EC2 user data of an EC2 instance (possibly being initialised by an ASG).

        :param self_obj: The CDK stack class object.
        """
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [self.VPC_, self.NAME_], self.CFN_OUTPUT_TYPE),
            description="The VPC name for use in the EC2 instance name. For example, vpc-01-sih.",
            value=self.get_attr_vpc_name(self_obj),
        )

    def cfn_output_efs_file_system_id(self, self_obj, efs_: efs.FileSystem, desc_insert: str) -> None:
        """
        Generate an CfnOutput value for this stack.

        The Elastic File System (EFS) file system ID.

        To be used during the EC2 user data of an EC2 instance (possibly being initialised by an ASG),
        or viewable in the AWS CloudFormation console.

        :param self_obj: The CDK stack class object.
        :param efs_: The Elastic File System (EFS) file system.
        :param desc_insert: The description insert.
        """
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [self.EFS_, self.FILE_, self.SYSTEM_, self.ID_], self.CFN_OUTPUT_TYPE),
            description=f"The Elastic File System (EFS) file system ID, for use by {desc_insert}. For example, fs-c7a0456e.",
            value=efs_.file_system_id,
        )

    def cfn_output_int_val(self, self_obj, name_props: list[str], val: int) -> None:
        """
        Generate an CfnOutput value for this stack.

        An integer value, likely used in the name of an AWS Secrets Manager secret or SSM parameter.

        To be used during the EC2 user data of an EC2 instance (possibly being initialised by an ASG).

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param val: The integer value.
        """
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, self.CFN_OUTPUT_TYPE),
            description="An integer value, likely used in the name of an AWS Secrets Manager secret or SSM parameter. For example, 64.",
            value=str(val),
        )

    def cfn_output_server_description(self, self_obj, desc_insert: str) -> None:
        """
        Generate an CfnOutput value for this stack.

        The server description insert.

        To be used during the EC2 user data of an EC2 instance (possibly being initialised by an ASG),
        or viewable in the AWS CloudFormation console.

        :param self_obj: The CDK stack class object.
        :param desc_insert: The description insert.
        """
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [self.SERVER_, self.DESCRIPTION_], self.CFN_OUTPUT_TYPE),
            description="The server description insert. For example, Foobar Private PyPi server.",
            value=desc_insert,
        )

    def cfn_output_url(self, self_obj, desc_insert: str = None) -> None:
        """
        Generate an CfnOutput value for this stack.

        A (public) URL for either: Server, Micro-service (Ms), Gateway (Gw), etc.

        To be used for later reference, by other CDK stacks, or viewable in the AWS CloudFormation console.

        :param self_obj: The CDK stack class object.
        :param desc_insert: An optional description insert, for all comments. Defaults to `CdkConstructsFactory.get_attr_word_map_project_name_comp()` method.
        """
        url_cfn_output_id: str = self.get_construct_id(self_obj, [self.URL_], self.CFN_OUTPUT_TYPE)
        url_val: str = getattr(self_obj, self.URL_)
        CfnOutput(
            scope=self_obj,
            id=url_cfn_output_id,
            description=f"The {desc_insert if desc_insert else self.get_attr_word_map_project_name_comp(self_obj)} URL "
            f"as CloudFormation output. For example, {url_val}",
            value=url_val,
            export_name=url_cfn_output_id,
        )

    def cfn_output_url_private(self, self_obj, desc_insert: str = None) -> None:
        """
        Generate an CfnOutput value for this stack.

        A (private) URL for either: Server, Micro-service (Ms), Gateway (Gw), etc.

        To be used for later reference, by other CDK stacks, or viewable in the AWS CloudFormation console.

        :param self_obj: The CDK stack class object.
        :param desc_insert: An optional description insert, for all comments. Defaults to `CdkConstructsFactory.get_attr_word_map_project_name_comp()` method.
        """
        url_private_cfn_output_id: str = self.get_construct_id(
            self_obj, [self.URL_, self.PRIVATE_], self.CFN_OUTPUT_TYPE
        )
        url_private_val: str = getattr(self_obj, self.URL_PRIVATE_)
        CfnOutput(
            scope=self_obj,
            id=url_private_cfn_output_id,
            description=f"The {desc_insert if desc_insert else self.get_attr_word_map_project_name_comp(self_obj)} URL (Private) "
            f"as CloudFormation output. For example, {url_private_val}",
            value=url_private_val,
            export_name=url_private_cfn_output_id,
        )

    def check_env_exists(self, kwargs) -> Environment:
        """
        Check a CDK stack class has received an env kwarg.

        :param kwargs: The kwargs from the CDK stack class.
        :return: The CDK stack class env.
        """
        env = kwargs.get(self.ENV_)
        if env:
            return env
        sys.exit(f"## {kwargs.get(self.ID_)}: {self.ENV_} arg not set.")

    def cloudfront_distribution(
        self,
        self_obj,
        origin_load_balancer: elasticloadbalancing.ILoadBalancerV2,
        route53_hosted_zone_: route53.IHostedZone,
        route53_record_name: str,
        origin_path: str,
        origin_custom_headers: list[tuple[str, secretsmanager.Secret]] = None,
        cf_stack_outputs_inc_comp: bool = True,
        desc_insert: str = None,
        domain_names: list[str] = None,
        project_name_comp: str = None,
    ) -> cloudfront.Distribution:
        """
        Generate a CloudFront distribution, and a Route53 A-record to match.

        :param self_obj: The CDK stack class object.
        :param origin_load_balancer: A load balancer (ALB/NLB) to act as origin for the distribution.
        :param route53_hosted_zone_: The hosted zone where DNS records must be created.
        :param route53_record_name: The domain name (subdomain) for the created Route 53 record.
        :param origin_path: An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin.
        :param origin_custom_headers: An optional list of tuples, each containing: a HTTP header name and a AWS Secrets Manager secret, containing the value that CloudFront adds to requests it sends to the origin.
        :param cf_stack_outputs_inc_comp: True if the CloudFront CDK stack name includes the component, after the project name.
        :param desc_insert: An optional description insert, for all comments. Defaults to `CdkConstructsFactory.get_attr_word_map_project_name_comp()` method.
        :param domain_names: Alternative domain names for this distribution.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :return: The CloudFront distribution.
        """
        # Allow CloudFront to use the KMS key to deliver logs
        self.get_attr_kms_key_stack(self_obj).add_to_resource_policy(
            statement=iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.KMS_, i])
                    for i in ["Decrypt", self.join_sep_empty(["GenerateDataKey", self.SEP_ASTERISK_])]
                ],
                resources=self.ALL_RESOURCES,
                principals=[self.iam_service_principal(self.join_sep_dot([self.DELIVERY_, self.LOGS_]))],
            )
        )

        cf_stack_outputs: dict[str, str] = self.get_cloudfront_stack_outputs(
            self_obj.stack_name,
            getattr(self_obj, self.COMPONENT_).capitalize(),
            cf_stack_outputs_inc_comp,
        )

        name_props: list[str] = [self.CF_]
        name_dist_props: list[str] = name_props + [self.DIST_]
        cdk_stack_name_short: str = self.get_cdk_stack_name_short(self_obj.stack_name).lower()
        log_bucket_name_prefix_props: list[str] = [cdk_stack_name_short]
        if self.aws_profile is not None:
            log_bucket_name_prefix_props.append(self.aws_profile)

        if desc_insert is None:
            desc_insert = self.get_attr_word_map_project_name_comp(self_obj)

        cf_dist: cloudfront.Distribution = cloudfront.Distribution(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "Distribution"),
            default_behavior=cloudfront.BehaviorOptions(
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                # TODO: (NEXT) Decide on a new cache policy which makes use of CloudFront caching.
                # cache_policy=cloudfront.CachePolicy(
                #     scope=self_obj,
                #     id=self.get_construct_id(self_obj, name_dist_props, "CachePolicy"),
                #     cache_policy_name=self.get_construct_name_short(self_obj, name_dist_props + [self.CACHE_, self.POLICY_]),
                #     comment=f"CloudFront distribution cache policy for {desc_insert}.",
                #     cookie_behavior=cloudfront.CacheCookieBehavior.all(),
                #     # default_ttl=,  # Default: - The greater of 1 day and min_ttl
                #     enable_accept_encoding_brotli=True,
                #     enable_accept_encoding_gzip=True,
                #     header_behavior=cloudfront.CacheHeaderBehavior.allow_list(
                #         cf_origin_access_tokens_header
                #     ),  # cf_origin_access_tokens_header: str = "x-access-tokens"
                #     max_ttl=Duration.days(7),
                #     min_ttl=Duration.seconds(0),
                #     query_string_behavior=cloudfront.CacheQueryStringBehavior.all(),
                # ),
                compress=True,
                # edge_lambdas=,  # Default: - no Lambda functions will be invoked
                # function_associations=,  # Default: - no functions will be invoked
                origin_request_policy=cloudfront.OriginRequestPolicy(
                    scope=self_obj,
                    id=self.get_construct_id(self_obj, name_dist_props, "OriginRequestPolicy"),
                    comment=f"CloudFront distribution origin request policy for {desc_insert}.",
                    cookie_behavior=cloudfront.OriginRequestCookieBehavior.all(),
                    header_behavior=cloudfront.OriginRequestHeaderBehavior.all(),
                    origin_request_policy_name=self.get_construct_name_short(
                        self_obj,
                        name_dist_props + [self.ORIGIN_, "request", self.POLICY_],
                        project_name_comp=project_name_comp,
                    ),
                    query_string_behavior=cloudfront.OriginRequestQueryStringBehavior.all(),
                ),
                # realtime_log_config=,  # TODO: (NEXT) Add real-time logs to monitor, analyze, and take action based on content delivery performance. Default: - none.
                # response_headers_policy=,  # Default: - none
                smooth_streaming=False,  # For distributing media files in the Microsoft Smooth Streaming format
                # trusted_key_groups=[],  # For validating signed URLs or signed cookies. Default: - no KeyGroups are associated with cache behavior
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                origin=origins.LoadBalancerV2Origin(
                    load_balancer=origin_load_balancer,
                    origin_path=origin_path,
                    custom_headers=(
                        {h: s.secret_value_from_json(h).to_string() for h, s in origin_custom_headers}
                        if origin_custom_headers
                        else None
                    ),
                ),
            ),
            certificate=acm.Certificate.from_certificate_arn(
                scope=self_obj,
                id=self.get_construct_id(self_obj, name_dist_props, "ICertificate"),
                certificate_arn=cf_stack_outputs[self.cfn_output_acm_cert_construct_id(self_obj, is_key=True)],
            ),
            comment=f"CloudFront distribution for {desc_insert}, origin pointing to an "
            f"{(self.NLB_ if isinstance(origin_load_balancer, elasticloadbalancing.NetworkLoadBalancer) else self.ALB_).upper()}.",
            # default_root_object=,  # The request goes to the origin’s root (e.g., example.com/) if unset. Default: - no default root object
            domain_names=domain_names if domain_names else [self_obj.fqdn],
            enabled=True,
            enable_ipv6=False,
            enable_logging=True,
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    # response_page_path=,  # Default: - the default CloudFront response is shown.
                    ttl=Duration.seconds(0),
                    # response_http_status=200,  # If enabled, must specify 'response_page_path' also
                )
            ],
            # geo_restriction=cloudfront.GeoRestriction.allowlist("UK", "GB"),
            # TODO: (OPTIONAL) Dynamically update geo_restriction list per AWS region deployed to, see: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/GeoRestriction.html#aws_cdk.aws_cloudfront.GeoRestriction
            http_version=cloudfront.HttpVersion.HTTP2,
            log_bucket=self.s3_bucket(
                self_obj,
                self.join_sep_score(log_bucket_name_prefix_props + name_dist_props),
                bucket_key_enabled=True,
                lifecycle_rules=True,
            ),
            log_file_prefix=self.get_path([cdk_stack_name_short, self.SEP_EMPTY_]),
            log_includes_cookies=False,
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            price_class=self_obj.price_class,
            web_acl_id=cf_stack_outputs[self.cfn_output_cf_waf_web_acl_construct_id(self_obj, is_key=True)],
        )
        if origin_custom_headers:
            for _, s in origin_custom_headers:
                cf_dist.node.add_dependency(s)
        self._route53_a_record_cloudfront_distribution(
            self_obj,
            cf_dist,
            route53_hosted_zone_,
            f"An A-Record for {desc_insert}, pointing to CloudFront distribution.",
            route53_record_name,
        )
        return cf_dist

    def cloudfront_waf_ip_set_ipv4(
        self, self_obj, name_props: list[str], addresses: list[str], description: str
    ) -> waf.CfnIPSet:
        """
        Generate a CloudFront WAF ip set (IPv4).

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param addresses: List of IP addresses in CIDR notation (i.e. 12.34.56.78/32).
        :param description: A description of the CDK construct.
        :return: The CloudFront WAF ip set (IPv4).
        """
        return waf.CfnIPSet(
            scope_=self_obj,
            id=self.get_construct_id(self_obj, name_props, "CfnIPSet"),
            addresses=addresses,
            ip_address_version=self.IPV4_.upper(),
            scope=self.CF_.upper(),
            description=description,
            name=self.get_construct_name(self_obj, name_props, underscore=True),
        )

    def cloudfront_waf_regex_pattern_set(
        self, self_obj, description: str, regex_short_list: bool = False
    ) -> waf.CfnRegexPatternSet:
        """
        Generate a CloudFront WAF regex pattern set.

        :param self_obj: The CDK stack class object.
        :param description: A description of the CDK construct.
        :param regex_short_list: True if the regular expression list should be just the short list.
        :return: The CloudFront WAF regex pattern set.
        """
        regex_list_base_props: list[str] = [
            self.MOZILLA_.capitalize(),
            self.join_sep_empty([i.capitalize() for i in [self.POSTMAN_, self.RUNTIME_]]),
        ]
        if not regex_short_list:
            for i in [getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)]:
                regex_list_base_props.append(i)
        name_props: list[str] = [self.DEVICE_, self.DETECTOR_]
        return waf.CfnRegexPatternSet(
            scope_=self_obj,
            id=self.get_construct_id(self_obj, name_props, "CfnRegexPatternSet"),
            regular_expression_list=[f"^.*({i}).*$" for i in regex_list_base_props],
            scope=self.CF_.upper(),
            description=description,
            name=self.get_construct_name(self_obj, name_props, underscore=True),
        )

    def cloudfront_waf_web_acl(
        self,
        self_obj,
        regex_pattern_set_arn: str,
        rules: list[waf.CfnWebACL.RuleProperty],
        description: str,
        default_action: waf.CfnWebACL.DefaultActionProperty = None,
        aws_managed_rules_common_rule_set_excluded_rules: list[str] = None,
        rate_limit_request: int = 10000,
    ) -> waf.CfnWebACL:
        """
        Generate a CloudFront WAF web ACL.

        :param self_obj: The CDK stack class object.
        :param rules: The rule statements used to identify the web requests that you want to allow, block, or count.
        :param regex_pattern_set_arn: The CloudFront WAF regex pattern set ARN.
        :param description: A description of the CDK construct.
        :param default_action: An optional action to perform if none of the ``Rules`` contained in the ``WebACL`` match.
        :param aws_managed_rules_common_rule_set_excluded_rules: A list of AWS managed rules to exclude.
        :param rate_limit_request: An optional limit on requests per 5-minute period for a single originating IP address. Default: 10,000
        :return: The CloudFront WAF web ACL.
        """
        name_props: list[str] = [self.CF_, self.WAF_]
        if not aws_managed_rules_common_rule_set_excluded_rules:
            aws_managed_rules_common_rule_set_excluded_rules = []
        aws_managed_rules_common_rule_set_: str = "AWSManagedRulesCommonRuleSet"
        aws_aws_managed_rules_common_rule_set_: str = self.join_sep_score(
            [self.AWS_.upper(), aws_managed_rules_common_rule_set_]
        )
        return waf.CfnWebACL(
            scope_=self_obj,
            id=self.get_construct_id(self_obj, name_props, "CfnWebACL"),
            default_action=(
                default_action
                if default_action
                else (
                    waf.CfnWebACL.DefaultActionProperty(block={})
                    if getattr(self_obj, self.DEPLOY_ENV_INTERNAL_)
                    else waf.CfnWebACL.DefaultActionProperty(allow={})
                )
            ),
            scope=self.CF_.upper(),
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name=self.WAF_.upper(),
                sampled_requests_enabled=True,
            ),
            rules=[
                i
                for i in [
                    (
                        None
                        if getattr(self_obj, self.NO_PERMITTED_USER_AGENTS_, None)
                        else waf.CfnWebACL.RuleProperty(
                            name=self.join_sep_score(
                                [i.capitalize() for i in [self.PERMITTED_, self.USER_, self.AGENTS_]]
                            ),
                            priority=0,
                            action=waf.CfnWebACL.RuleActionProperty(block={}),
                            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                                cloud_watch_metrics_enabled=True,
                                metric_name=self.join_sep_score([self.ALLOW_, self.PERMITTED_, self.DEVICES_]),
                                sampled_requests_enabled=True,
                            ),
                            statement=waf.CfnWebACL.StatementProperty(
                                not_statement=waf.CfnWebACL.NotStatementProperty(
                                    statement=waf.CfnWebACL.StatementProperty(
                                        regex_pattern_set_reference_statement=waf.CfnWebACL.RegexPatternSetReferenceStatementProperty(
                                            arn=regex_pattern_set_arn,
                                            field_to_match=waf.CfnWebACL.FieldToMatchProperty(
                                                single_header={
                                                    self.NAME_.capitalize(): self.join_sep_score(
                                                        [i.capitalize() for i in [self.USER_, self.AGENT_]]
                                                    )
                                                }
                                            ),
                                            text_transformations=[
                                                waf.CfnWebACL.TextTransformationProperty(
                                                    priority=0, type=self.NONE_.upper()
                                                )
                                            ],
                                        )
                                    )
                                )
                            ),
                        )
                    ),
                    (
                        None
                        if getattr(self_obj, self.DEPLOY_ENV_INTERNAL_)
                        else waf.CfnWebACL.RuleProperty(
                            name=self.join_sep_score(
                                [i.capitalize() for i in [self.LIMIT_, self.REQUESTS_, str(rate_limit_request)]]
                            ),
                            priority=2,
                            action=waf.CfnWebACL.RuleActionProperty(block={}),
                            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                                cloud_watch_metrics_enabled=True,
                                metric_name=self.join_sep_score(
                                    [self.RATE_, self.LIMIT_, self.REQUESTS_, str(rate_limit_request)]
                                ),
                                sampled_requests_enabled=True,
                            ),
                            statement=waf.CfnWebACL.StatementProperty(
                                rate_based_statement=waf.CfnWebACL.RateBasedStatementProperty(
                                    aggregate_key_type=self.IP_.upper(),
                                    limit=rate_limit_request,
                                    # scope_down_statement=,
                                )
                            ),
                        )
                    ),
                    waf.CfnWebACL.RuleProperty(
                        name=aws_aws_managed_rules_common_rule_set_,
                        priority=3,
                        statement=waf.CfnWebACL.StatementProperty(
                            managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                                name=aws_managed_rules_common_rule_set_,
                                vendor_name=self.AWS_.upper(),
                                excluded_rules=[
                                    waf.CfnWebACL.ExcludedRuleProperty(name=i)
                                    for i in aws_managed_rules_common_rule_set_excluded_rules
                                ],
                            ),
                        ),
                        override_action=waf.CfnWebACL.OverrideActionProperty(none={}),
                        visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=True,
                            metric_name=aws_aws_managed_rules_common_rule_set_,
                            sampled_requests_enabled=True,
                        ),
                    ),
                ]
                if i
            ]
            + rules,
            description=description,
            name=self.get_construct_name(self_obj, name_props, underscore=True),
        )

    def cloudfront_waf_web_acl_default(
        self,
        self_obj,
        regex_pattern_set_arn: str,
        allow_ip_set: waf.CfnIPSet,
        block_ip_set: waf.CfnIPSet,
        description: str,
        additional_rules: list[waf.CfnWebACL.RuleProperty] = None,
        aws_managed_rules_common_rule_set_excluded_rules: list[str] = None,
    ) -> waf.CfnWebACL:
        """
        Generate a CloudFront WAF web ACL, with default security options.

        :param self_obj: The CDK stack class object.
        :param regex_pattern_set_arn: The CloudFront WAF regex pattern set ARN.
        :param allow_ip_set: A WAF ip set used to detect web requests coming from particular IP addresses or CIDR ranges.
        :param block_ip_set: A WAF ip set used to detect web requests coming from particular IP addresses or CIDR ranges.
        :param description: A description of the CDK construct.
        :param additional_rules: An optional list of additional rule statements used to identify the web requests that you want to allow, block, or count.
        :param aws_managed_rules_common_rule_set_excluded_rules: A list of AWS managed rules to exclude.
        :return: The CloudFront WAF web ACL, with default security options.
        """
        return self.cloudfront_waf_web_acl(
            self_obj,
            regex_pattern_set_arn,
            (
                (allow_or_block_rules + additional_rules)
                if (
                    allow_or_block_rules := [
                        self.cloudfront_waf_web_acl_rule_allow_or_block_ip(
                            self_obj, allow_ip_set=allow_ip_set, block_ip_set=block_ip_set
                        )
                    ]
                )
                and additional_rules
                else allow_or_block_rules
            ),
            description,
            aws_managed_rules_common_rule_set_excluded_rules=aws_managed_rules_common_rule_set_excluded_rules,
        )

    def cloudfront_waf_web_acl_logging_configuration_default(
        self, self_obj, web_acl: waf.CfnWebACL
    ) -> waf.CfnLoggingConfiguration:
        """
        Generate a CloudFront WAF web ACL logging configuration, with default options.

        :param self_obj: The CDK stack class object.
        :param web_acl: The CloudFront WAF web ACL.
        :return: The CloudFront WAF web ACL logging configuration, with default options.
        """
        log_group_name_props: list[str] = [
            self.AWS_,
            self.WAF_,
            self.LOGS_,
        ] + self.get_attr_project_name_comp_props(self_obj)
        if hasattr(self_obj, self.DEPLOY_ENV_):
            log_group_name_props.append(self.get_attr_deploy_env(self_obj))
        return self._cloudfront_waf_web_acl_logging_configuration(
            self_obj,
            web_acl,
            self.logs_log_group(
                self_obj,
                [self.CF_, self.WAF_],
                self.join_sep_score(log_group_name_props),
            ),
        )

    def cloudfront_waf_web_acl_rule_allow_or_block_ip(
        self,
        self_obj,
        allow_ip_set: waf.CfnIPSet = None,
        block_ip_set: waf.CfnIPSet = None,
    ):
        """
        Generate a CloudFront WAF web ACL rule property, which either allows or blocks IPs.

        :param self_obj: The CDK stack class object.
        :param allow_ip_set: A WAF ip set used to detect web requests coming from particular IP addresses or CIDR ranges.
        :param block_ip_set: A WAF ip set used to detect web requests coming from particular IP addresses or CIDR ranges.
        :return: The CloudFront WAF web ACL rule property, which either allows or blocks IPs.
        """
        ips_: str = self.IPS_.replace(self.IP_, self.IP_.upper(), 1)
        block_rule: waf.CfnWebACL.RuleProperty = (
            self._cloudfront_waf_web_acl_rule_property_allow_block_ip(
                self.join_sep_score([f"{self.BLOCK_.capitalize()}ed", ips_]),
                1,
                waf.CfnWebACL.RuleActionProperty(block={}),
                self.join_sep_score([self.BLOCK_, self.NON_, self.PERMITTED_, self.IPS_]),
                block_ip_set,
            )
            if block_ip_set
            else None
        )
        allow_rule: waf.CfnWebACL.RuleProperty = (
            self._cloudfront_waf_web_acl_rule_property_allow_block_ip(
                self.join_sep_score([self.PERMITTED_.capitalize(), ips_]),
                4,
                waf.CfnWebACL.RuleActionProperty(allow={}),
                self.join_sep_score([self.ALLOW_, self.PERMITTED_, self.IPS_]),
                allow_ip_set,
            )
            if allow_ip_set
            else None
        )
        return (
            block_rule
            if block_ip_set and not allow_ip_set
            else (
                allow_rule
                if allow_ip_set and not block_ip_set
                else (block_rule if not getattr(self_obj, self.DEPLOY_ENV_INTERNAL_) else allow_rule)
            )
        )

    def cloudwatch_alarm(
        self,
        self_obj,
        name_props: list[str],
        metric: cloudwatch.Metric,
        description: str,
        comparison_operator: cloudwatch.ComparisonOperator,
        treat_missing_data: cloudwatch.TreatMissingData,
        threshold: int,
        evaluation_periods: int = 1,
        actions_enabled: bool = True,
        alarm_name: str = None,
        datapoints_to_alarm: int = None,
    ) -> cloudwatch.Alarm:
        """
        Generate a CloudWatch alarm.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param metric: The metric to add the alarm on.
        :param description: A description of the CDK construct.
        :param comparison_operator: Comparison to use to check if metric is breaching.
        :param treat_missing_data: Sets how this alarm is to handle missing data points.
        :param threshold: The value against which the specified statistic is compared.
        :param evaluation_periods: The number of periods over which data is compared to the specified threshold.
        :param actions_enabled: Whether the actions for this alarm are enabled.
        :param alarm_name: An optional name for the alarm.
        :param datapoints_to_alarm: The number of datapoints that must be breaching to trigger the alarm.
        :return: The CloudWatch alarm.
        """
        return cloudwatch.Alarm(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "Alarm"),
            metric=metric,
            evaluation_periods=evaluation_periods,
            threshold=threshold,
            actions_enabled=actions_enabled,
            alarm_description=description,
            alarm_name=alarm_name if alarm_name else self.get_construct_name(self_obj, name_props, underscore=True),
            comparison_operator=comparison_operator,
            datapoints_to_alarm=datapoints_to_alarm if datapoints_to_alarm else evaluation_periods,
            # evaluate_low_sample_count_percentile=,  # Default: - Not configured.
            treat_missing_data=treat_missing_data,
        )

    def codebuild_build_environment(
        self,
        project_name_comp: str,
        base_ignore: bool = False,
    ) -> codebuild.BuildEnvironment:
        """
        Generate a CodeBuild build environment.

        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :param base_ignore: True if we are to ignore the fact that a project_name includes the substring 'base'.
        :return: The CodeBuild build environment.
        """
        return codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
            # certificate=,  # Default: - No PEM-encoded certificate is added to the project
            compute_type=(
                codebuild.ComputeType.MEDIUM
                if self.BASE_ in project_name_comp or base_ignore
                else codebuild.ComputeType.SMALL
            ),
            # environment_variables={},
            privileged=True,
        )

    def codepipeline_pipeline(
        self,
        self_obj,
        project_name_comp: str,
        project: codebuild.Project,
        role: iam.Role,
        repo: str = None,
        branch: str = None,
        trigger_on_push: bool = None,
        deploy: bool = True,
    ) -> codepipeline.Pipeline:
        """
        Generate a CodePipeline pipeline.

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :param project: The CodeBuild project to be used for a pipeline build stage.
        :param role: The service Role assumed by this pipeline.
        :param repo: An optional git repo name, different from the default project_name_comp.
        :param branch: An optional git repo branch, different from the default project_name_comp.
        :param trigger_on_push: True if desire pipeline automatically starting when a new commit is made on the configured repository and branch.
        :param deploy: An optional set to False force prevent deploy stage required.
        :return: The CodePipeline pipeline.
        """
        pipeline_artifacts: dict[str, codepipeline.Artifact] = {}
        return codepipeline.Pipeline(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [self.CODEPIPELINE_], "Pipeline", project_name_comp=project_name_comp),
            cross_account_keys=False,
            pipeline_name=(
                self.join_sep_score([project_name_comp, d])
                if (d := getattr(self_obj, self.DEPLOY_ENV_, None))
                else project_name_comp
            ),
            pipeline_type=codepipeline.PipelineType.V1,
            restart_execution_on_update=False,
            role=role,
            stages=[
                i
                for i in [
                    self._codepipeline_stage_props(
                        self_obj,
                        self_obj.name_source,
                        project_name_comp,
                        pipeline_artifacts,
                        actions=[self_obj.name_source],
                        repo=repo,
                        branch=branch,
                        trigger_on_push=trigger_on_push,
                    ),
                    self._codepipeline_stage_props(
                        self_obj,
                        self_obj.name_build,
                        project_name_comp,
                        pipeline_artifacts,
                        actions=[self_obj.name_build],
                        project=project,
                    ),
                    (
                        self._codepipeline_stage_props(
                            self_obj,
                            self_obj.name_deploy,
                            project_name_comp,
                            pipeline_artifacts,
                            actions=[self_obj.name_deploy],
                        )
                        if deploy and self.BASE_ not in project_name_comp
                        else None
                    ),
                ]
                if i
            ],
        )

    def codepipeline_pipelines_map(
        self,
        self_obj,
        project_name_list: list[str],
        repo_name_list: str = None,
        pypi_server_access: bool = False,
        version_meta_param_name: str = None,
        vpc_props: tuple[ec2.Vpc, list[ec2.SecurityGroup], ec2.SubnetType] = None,
        pypi_package: bool = False,
    ) -> dict[str, codepipeline.Pipeline]:
        """
        Generate a map of CodePipeline pipelines.

        :param self_obj: The CDK stack class object.
        :param project_name_list: The list of project names to create pipelines for.
        :param repo_name_list: An optional list of git repo names, different from the default project_name_comp.
        :param pypi_server_access: True if CodeBuild needs to generate a '.pypirc' or 'pip.conf' file, in order to access a PyPi server.
        :param version_meta_param_name: An optional name of an SSM parameter where version meta is stored.
        :param vpc_props: The VPC network to place CodeBuild network interfaces, a list of security groups to associate
            with the CodeBuild's network interfaces, and the type of subnets to select.
        :param pypi_package: True if the CodeBuild project will be used to build a PyPi package.
        :return: The map of CodePipeline pipelines.
        """
        return {
            p_deploy_env: self.codepipeline_pipeline(
                self_obj,
                p,
                self._codebuild_project_pipeline(
                    self_obj,
                    p,
                    self.get_buildspec_path(self_obj, p),
                    f"CodeBuild project for `{p_deploy_env}` pipeline.",
                    self.iam_role_codebuild(
                        self_obj, p, pypi_server_access=bool(pypi_package or (pypi_server_access and self.BASE_ in p))
                    ),
                    version_meta_param_name=version_meta_param_name if self.BASE_ not in p else None,
                    vpc_props=vpc_props,
                    pypi_package=pypi_package,
                ),
                self.iam_role_codepipeline(self_obj, p),
                repo=repo_name_list[i] if repo_name_list else None,
                **{
                    k: v
                    for k, v in {
                        "branch": self.get_attr_deploy_env(self_obj),
                        "trigger_on_push": getattr(self_obj, self.DEPLOY_ENV_DEV_, False),
                        "deploy": False,
                    }.items()
                    if pypi_package
                },
            )
            for i, p in enumerate(project_name_list)
            if (p_deploy_env := self.join_sep_score([p, self.get_attr_deploy_env(self_obj)]))
        }

    def codestar_notifications_notification_rule(
        self, self_obj, project_name_comp: str, base_ignore: bool = False
    ) -> codestar_notifications.NotificationRule:
        """
        Generate a CodeStar Notifications notification rule.

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :param base_ignore: True if we are to ignore the fact that a project_name includes the substring 'base'.
        :return: The CodeStar Notifications notification rule.
        """
        name_props: list[str] = [self.CODESTAR_, self.NOTIFICATIONS_]
        pipeline_name: str = (
            self.join_sep_score([project_name_comp, d])
            if (d := getattr(self_obj, self.DEPLOY_ENV_, None))
            else project_name_comp
        )
        return codestar_notifications.NotificationRule(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "NotificationRule", project_name_comp=project_name_comp),
            events=self.PIPELINE_EVENTS,
            source=self_obj.codepipeline_pipelines[pipeline_name],
            targets=[
                self_obj.sns_topics[
                    (
                        self.join_sep_score(
                            [
                                i
                                for i in self.get_attr_project_name_comp_props(
                                    self_obj, project_name_comp=project_name_comp
                                )
                                if i != self.BASE_
                            ]
                        )
                        if self.BASE_ in project_name_comp and not base_ignore
                        else project_name_comp
                    )
                ]
            ],
            detail_type=codestar_notifications.DetailType.FULL,
            enabled=True,
            notification_rule_name=self.get_construct_name(
                self_obj, name_props, underscore=True, project_name_comp=project_name_comp
            ),
        )

    @staticmethod
    def ec2_instance_type_t3_large() -> ec2.InstanceType:
        return ec2.InstanceType.of(instance_class=ec2.InstanceClass.BURSTABLE3, instance_size=ec2.InstanceSize.LARGE)

    @staticmethod
    def ec2_instance_type_t3_micro() -> ec2.InstanceType:
        return ec2.InstanceType.of(instance_class=ec2.InstanceClass.BURSTABLE3, instance_size=ec2.InstanceSize.MICRO)

    @staticmethod
    def ec2_instance_type_t3_small() -> ec2.InstanceType:
        return ec2.InstanceType.of(instance_class=ec2.InstanceClass.BURSTABLE3, instance_size=ec2.InstanceSize.SMALL)

    @staticmethod
    def ec2_instance_type_t3_xlarge() -> ec2.InstanceType:
        return ec2.InstanceType.of(instance_class=ec2.InstanceClass.BURSTABLE3, instance_size=ec2.InstanceSize.XLARGE)

    def ec2_interface_vpc_endpoint_map(
        self, self_obj, vpc: ec2.Vpc, service_list: list[str]
    ) -> dict[str, ec2.InterfaceVpcEndpoint]:
        """
        Generate a map of EC2 interface VPC endpoints.

        :param self_obj: The CDK stack class object.
        :param vpc: The VPC network in which the interface endpoint will be used.
        :param service_list: A list of service names, each for a custom-hosted service for an interface VPC endpoint.
        :return: The map of EC2 interface VPC endpoints.
        """
        return {
            service_name: ec2.InterfaceVpcEndpoint(
                scope=self_obj,
                id=self.get_construct_id(self_obj, [service_name], "InterfaceVpcEndpoint"),
                vpc=vpc,
                service=ec2.InterfaceVpcEndpointService(
                    name=self.join_sep_dot(
                        [self.COM_, self.AMAZONAWS_, self.get_attr_env_region(self_obj), service_name]
                    ),
                    port=self.HTTPS_PORT,
                ),
            )
            for service_name in service_list
        }

    @staticmethod
    def ec2_machine_image_openvpn_server() -> ec2.AmazonLinuxImage:
        """
        Look up a shared OpenVPN Access Server machine image (AMI).

        :return: The shared OpenVPN Access Server machine image.
        """
        return ec2.MachineImage.lookup(
            # IMPORTANT: Requires accepting the AMIs T&Cs in AMI marketplace, once specified and deployed.
            name="OpenVPN Access Server Community Image-fe8020db-5343-4c43-9e65-5ed4a825c931",
            # filters=,  # Default: - No additional filters
            # owners=,  # Default: - All owners
            # user_data=,  # Default: - Empty user data appropriate for the platform type
            windows=False,
        )

    @staticmethod
    def ec2_machine_image_ubuntu_22_04() -> ec2.AmazonLinuxImage:
        """
        Look up a shared Ubuntu 22.04 machine image (AMI).

        :return: The shared Ubuntu 22.04 machine image.
        """
        return ec2.MachineImage.lookup(
            # IMPORTANT: Requires accepting the AMIs T&Cs in AMI marketplace, once specified and deployed.
            name="ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-20240927",
            # filters=,  # Default: - No additional filters
            # owners=,  # Default: - All owners
            # user_data=,  # Default: - Empty user data appropriate for the platform type
            windows=False,
        )

    def ec2_security_group(
        self,
        self_obj,
        name_props: list[str],
        description: str,
        allow_all_outbound: bool = True,
        ingress_rules: list[tuple[ec2.IPeer, ec2.Port, str]] = None,
        full_description: bool = False,
    ) -> ec2.SecurityGroup:
        """
        Generate an EC2 security group.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param description: A description of the CDK construct.
        :param allow_all_outbound: Whether to allow all outbound traffic by default.
        :param ingress_rules: A list of ingress rules to add to the security group.
        :param full_description: True if the ``description`` arg needs to be the entire description of the CDK construct.
        :return: The EC2 security group.
        """
        security_group: ec2.SecurityGroup = ec2.SecurityGroup(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "SecurityGroup"),
            vpc=self.get_attr_vpc(self_obj),
            allow_all_outbound=allow_all_outbound,
            description=description if full_description else f"Security group used by {description}.",
            security_group_name=self.get_construct_name(self_obj, name_props),
        )
        if ingress_rules:
            for peer, port, ingress_rule_decs in ingress_rules:
                security_group.add_ingress_rule(peer=peer, connection=port, description=ingress_rule_decs)
        return security_group

    def ec2_security_group_add_support_infra(self, self_obj, sg: ec2.SecurityGroup, port: int = None) -> None:
        """
        Allow connections on ``port``, inbound from all support Infrastructure: Bastion Hosts, Client VPN, Elastic IPs, etc.

        :param self_obj: The CDK stack class object.
        :param sg: The EC2 security group.
        :param port: The port (TCP) to allow inbound into the EC2 security group. Default: 22 (SSH port).
        """
        if port is None:
            port = self.SSH_PORT
        for bastion_host_private_ip in self_obj.bastion_host_private_ips:
            sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(cidr_ip=self.get_path([bastion_host_private_ip, str(32)])),
                connection=ec2.Port.tcp(port),
                description=self.get_ec2_security_group_rule_description("Bastion host private IP", port),
            )
        if client_vpn_endpoint_sg := getattr(self_obj, self.CLIENT_VPN_ENDPOINT_PRIVATE_SG_, None):
            sg.connections.allow_from(
                other=client_vpn_endpoint_sg,
                port_range=ec2.Port.tcp(port),
                description=self.get_ec2_security_group_rule_description("Client VPN Endpoint PRIVATE", port),
            )
        for _, meta in getattr(self_obj, self.ELASTIC_IP_META_).items():
            sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(cidr_ip=self.get_path([meta[0], str(32)])),
                connection=ec2.Port.tcp(port),
                description=self.get_ec2_security_group_rule_description(f"{meta[1]} public IP", port),
            )

    def ec2_security_group_all(
        self,
        self_obj,
        all_vpc_traffic: tuple[list[int], str, str] = None,
        ec_redis: bool = False,
        db_server: bool = False,
        s3_lambda: bool = False,
        mq_rabbitmq: tuple[str, str] = None,
    ) -> None:
        """
        For a Base CDK stack, generate all EC2 security groups.

        :param self_obj: The CDK stack class object.
        :param all_vpc_traffic: If not None, adds ingress rules to the EC2 security groups
          needed for ECS Fargate containers, to allow all VPC traffic on specified  ports (TCP).
          Include: (ports, vpc_cidr, vpc_name). Default: None.
        :param ec_redis: If true, include EC2 security groups needed for ElastiCache Redis clusters. Default: False.
        :param db_server: If true, include EC2 security groups needed for RDS database instances. Default: False.
        :param s3_lambda: If true, include EC2 security groups needed for S3 storage Lambda functions. Default: False.
        :param mq_rabbitmq: If not None, include EC2 security groups needed for Amazon MQ RabbitMQs.
          Include: (vpc_cidr, vpc_name). Default: None.
        """
        word_map_project_name: str = getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)
        word_map_component: str = getattr(self_obj, self.WORD_MAP_COMPONENT_)

        alb_sg_description: str = self.ALB_.upper()
        alb_sg: ec2.SecurityGroup = self.ec2_security_group(
            self_obj, [self.ALB_], self.join_sep_space([word_map_project_name, word_map_component, alb_sg_description])
        )
        ecs_sg_description: str = f"{self.ECS_.upper()} Fargate containers"
        ecs_sg: ec2.SecurityGroup = self.ec2_security_group(
            self_obj,
            [self.ECS_],
            self.join_sep_space([word_map_project_name, word_map_component, ecs_sg_description]),
        )
        # HTTPS -> ALB
        alb_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(self.HTTPS_PORT), description="Allow HTTPS traffic."
        )
        # ALB -> (All TCP ports) -> ECS Fargate containers
        ecs_sg.connections.allow_from(
            other=alb_sg,
            port_range=ec2.Port.all_tcp(),
            description=f"Allow {alb_sg_description} traffic on all TCP ports.",
        )

        setattr(self_obj, self.ALB_SG_, alb_sg)

        # [Bastion Hosts, Client VPN, Elastic IPs] -> (SSH) -> ECS Fargate containers
        self.ec2_security_group_add_support_infra(self_obj, ecs_sg)

        if all_vpc_traffic:
            # [VPC traffic] -> [Ports...] -> ECS Fargate containers
            for port in all_vpc_traffic[0]:
                ecs_sg.add_ingress_rule(
                    peer=ec2.Peer.ipv4(cidr_ip=all_vpc_traffic[1]),
                    connection=ec2.Port.tcp(port),
                    description=self.get_ec2_security_group_rule_description(
                        f"VPC ({all_vpc_traffic[2]}) traffic", port
                    ),
                )

        if ec_redis:
            ec_redis_sg_description: str = "ElastiCache Redis cluster"
            ec_redis_sg: ec2.SecurityGroup = self.ec2_security_group(
                self_obj,
                [self.ELASTICACHE_, self.REDIS_, self.CLUSTER_],
                self.join_sep_space([word_map_project_name, word_map_component, ec_redis_sg_description]),
            )
            # [Bastion Hosts, Client VPN, Elastic IPs] -> (Redis Port) -> ElastiCache Redis cluster
            self.ec2_security_group_add_support_infra(self_obj, ec_redis_sg, getattr(self_obj, self.REDIS_PORT_))
            # ECS Fargate containers <-- (Redis Port) --> ElastiCache Redis cluster
            self.ec2_security_group_connections_allow_from_bi_direct(
                ecs_sg,
                ec_redis_sg,
                getattr(self_obj, self.REDIS_PORT_),
                self.join_sep_space(
                    [word_map_project_name, word_map_component, ecs_sg_description, self.TCT_, ec_redis_sg_description]
                ),
            )

            setattr(self_obj, self.EC_REDIS_SG_DESCRIPTION_, ec_redis_sg_description)
            setattr(self_obj, self.EC_REDIS_SG_, ec_redis_sg)

        if db_server:
            db_server_sg_description: str = f"{self.RDS_.upper()} database instance"
            db_server_lambda_sg_description: str = f"{db_server_sg_description} init Lambda function"
            db_server_sg: ec2.SecurityGroup = self.ec2_security_group(
                self_obj,
                [self.RDS_, self.DATABASE_, self.INSTANCE_],
                self.join_sep_space([word_map_project_name, word_map_component, db_server_sg_description]),
            )
            db_server_lambda_sg: ec2.SecurityGroup = self.ec2_security_group(
                self_obj,
                [self.RDS_, self.DATABASE_, self.INSTANCE_, self.INIT_, self.LAMBDA_],
                self.join_sep_space([word_map_project_name, word_map_component, db_server_lambda_sg_description]),
            )
            # [Bastion Hosts, Client VPN, Elastic IPs] -> (DB Port) -> RDS database instance
            self.ec2_security_group_add_support_infra(self_obj, db_server_sg, getattr(self_obj, self.DB_PORT_))
            # ECS Fargate containers <-- (DB Port) --> RDS database instance
            self.ec2_security_group_connections_allow_from_bi_direct(
                ecs_sg,
                db_server_sg,
                getattr(self_obj, self.DB_PORT_),
                self.join_sep_space(
                    [word_map_project_name, word_map_component, ecs_sg_description, self.TCT_, db_server_sg_description]
                ),
            )
            # RDS database instance <-- (DB Port) --> RDS database instance init Lambda function
            self.ec2_security_group_connections_allow_from_bi_direct(
                db_server_sg,
                db_server_lambda_sg,
                getattr(self_obj, self.DB_PORT_),
                self.join_sep_space(
                    [
                        word_map_project_name,
                        word_map_component,
                        db_server_sg_description,
                        self.TCT_,
                        db_server_lambda_sg_description,
                    ]
                ),
            )

            setattr(self_obj, self.DB_SERVER_LAMBDA_SG_, db_server_lambda_sg)
            setattr(self_obj, self.DB_SERVER_SG_, db_server_sg)

        if s3_lambda:
            s3_lambda_sg_description: str = f"{self.S3_.upper()} storage Lambda function"
            s3_lambda_sg: ec2.SecurityGroup = self.ec2_security_group(
                self_obj,
                [self.S3_, self.LAMBDA_],
                self.join_sep_space([word_map_project_name, word_map_component, s3_lambda_sg_description]),
            )
            # ECS Fargate containers <-- (All TCP ports) --> S3 storage Lambda function
            for sg in [ecs_sg, s3_lambda_sg]:
                sg.connections.allow_from(
                    other=ecs_sg if sg == s3_lambda_sg else s3_lambda_sg,
                    port_range=ec2.Port.all_tcp(),
                    description=self.get_ec2_security_group_rule_description(
                        self.join_sep_space(
                            [
                                word_map_project_name,
                                word_map_component,
                                ecs_sg_description,
                                self.TCT_,
                                s3_lambda_sg_description,
                            ]
                        ),
                    ),
                )

            setattr(self_obj, self.S3_LAMBDA_SG_, s3_lambda_sg)

        if mq_rabbitmq:
            mq_rabbitmq_sg_description: str = "Amazon MQ RabbitMQ"
            mq_rabbitmq_sg: ec2.SecurityGroup = self.ec2_security_group(
                self_obj,
                [self.AMAZONMQ_, self.RABBITMQ_, self.BROKER_],
                self.join_sep_space([word_map_project_name, word_map_component, mq_rabbitmq_sg_description]),
            )
            # ECS Fargate containers <-- (RabbitMQ Port) --> Amazon MQ RabbitMQ broker
            self.ec2_security_group_connections_allow_from_bi_direct(
                ecs_sg,
                mq_rabbitmq_sg,
                self_obj.mq_rabbitmq_port,
                self.join_sep_space(
                    [
                        word_map_project_name,
                        word_map_component,
                        ecs_sg_description,
                        self.TCT_,
                        mq_rabbitmq_sg_description,
                    ]
                ),
            )
            # [VPC traffic] -> [HTTPS, RabbitMQ Port] -> Amazon MQ RabbitMQ broker
            for port in [self.HTTPS_PORT, self_obj.mq_rabbitmq_port]:
                mq_rabbitmq_sg.add_ingress_rule(
                    peer=ec2.Peer.ipv4(cidr_ip=mq_rabbitmq[0]),
                    connection=ec2.Port.tcp(port),
                    description=self.get_ec2_security_group_rule_description(f"VPC ({mq_rabbitmq[1]}) traffic", port),
                )

            setattr(self_obj, self.MQ_RABBITMQ_SG_, mq_rabbitmq_sg)

        setattr(self_obj, self.ECS_SG_, ecs_sg)

    def ec2_security_group_connections_allow_from_bi_direct(
        self, primary_sg: ec2.SecurityGroup, secondary_sg: ec2.SecurityGroup, port: int, description: str
    ) -> None:
        """
        Allow connections on ``port``, between a pair of EC2 security group.

        :param primary_sg: The first EC2 security group.
        :param secondary_sg: The second EC2 security group.
        :param port: The port (TCP) to allow between the two EC2 security group.
        :param description: A description of the CDK construct.
        """
        for sg in [primary_sg, secondary_sg]:
            sg.connections.allow_from(
                other=primary_sg if sg == secondary_sg else secondary_sg,
                port_range=ec2.Port.tcp(port),
                description=self.get_ec2_security_group_rule_description(description, port),
            )

    def ec2_vpc_default(
        self,
        self_obj,
        vpc_name: str,
    ) -> ec2.IVpc:
        """
        Import the default EC2 VPC, for the current CDK stack's environment region.

        :param self_obj: The CDK stack class object.
        :param vpc_name: Specific detail to include in the CDK construct ID.
        :return: The default EC2 VPC.
        """
        return ec2.Vpc.from_lookup(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [vpc_name], "IVpc"),
            is_default=True,
        )

    def ecr_repository(self, self_obj, project_name_comp: str, max_image_age_days: int = 14) -> ecr.Repository:
        """
        Generate an ECR repository, for Docker images.

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name & component specifier.
        :param max_image_age_days: The number of days to keep an untagged Docker image. Default: 14 days.
        :return: The ECR repository, for Docker images.
        """
        return ecr.Repository(
            scope=self_obj,
            id=self.get_construct_id(
                self_obj,
                self.get_attr_project_name_comp_props(self_obj, project_name_comp=project_name_comp),
                "Repository",
            ),
            encryption=ecr.RepositoryEncryption.AES_256,
            # encryption_key=,  # If encryption == KMS, the KMS key to use for repository encryption.
            image_scan_on_push=True,
            image_tag_mutability=ecr.TagMutability.MUTABLE,
            # lifecycle_registry_id=,  # Default: The default registry is assumed.
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description=f"Expire untagged Docker images older than {max_image_age_days} days.",
                    max_image_age=Duration.days(max_image_age_days),
                    # max_image_count=,  # The maximum number of images to retain.
                    # rule_priority=,  # Default: Automatically assigned
                    # tag_prefix_list=[],  #  Only if tag_status == TagStatus.Tagged
                    tag_status=ecr.TagStatus.UNTAGGED,
                )
            ],
            removal_policy=RemovalPolicy.DESTROY,
            repository_name=self.get_path([self.organisation, project_name_comp]),
        )

    def ecs_fargate_service(
        self,
        self_obj,
        task_definition: ecs.TaskDefinition,
        fqdn: str,
        log_group: logs.LogGroup,
        http_error_code: int = 550,
        custom_filter_patterns: dict[str, str] = None,
        dependant_constructs: list[Resource] = None,
        target_group: elasticloadbalancing.ApplicationTargetGroup = None,
        admin: bool = False,
    ) -> ecs.FargateService:
        """
        Generate an ECS fargate service.

        :param self_obj: The CDK stack class object.
        :param task_definition: The ECS task definition.
        :param fqdn: The Fully Qualified Domain Name (FQDN) to be the name for the ECS CloudMap name space.
        :param log_group: The log group of the ECS task container to check for error/warning log lines in.
        :param http_error_code: The HTTP error code, which should raise an CloudWatch Alarm. Default: 550.
        :param custom_filter_patterns: An optional dictionary containing additional metric filter pattern values (and corresponding construct ID prop keys).
        :param dependant_constructs: A list of CDK constructs which are dependencies of the CDK construct being generated.
        :param target_group: An ALB target group to attach the ECS fargate service to.
        :param admin: True if the ECS service is for admin only.
        :return: The ECS fargate service.
        """
        self._set_attrs_ecs_service_cloud_map_service_name(self_obj)
        name_props: list[str] = [getattr(self_obj, self.ECS_SERVICE_CLOUD_MAP_SERVICE_NAME_)]
        security_groups: list[ec2.SecurityGroup] = [getattr(self_obj, self.ECS_SG_)]
        name_execute_command_props: list[str] = name_props + [self.EXECUTE_, self.COMMAND_]
        execute_command_key: kms.Key = self.get_attr_kms_key_stack(self_obj)
        ecs_service: ecs.FargateService = ecs.FargateService(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "FargateService"),
            task_definition=task_definition,
            assign_public_ip=False,
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
            security_groups=security_groups,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            cluster=ecs.Cluster(
                scope=self_obj,
                id=self.get_construct_id(self_obj, name_props, "Cluster"),
                cluster_name=self.get_construct_name_short(self_obj, name_props),
                container_insights=True,
                default_cloud_map_namespace=ecs.CloudMapNamespaceOptions(
                    name=fqdn, type=servicediscovery.NamespaceType.DNS_PRIVATE, vpc=self.get_attr_vpc(self_obj)
                ),
                enable_fargate_capacity_providers=False,
                execute_command_configuration=ecs.ExecuteCommandConfiguration(
                    kms_key=execute_command_key,
                    log_configuration=ecs.ExecuteCommandLogConfiguration(
                        cloud_watch_encryption_enabled=True,
                        cloud_watch_log_group=self.logs_log_group(
                            self_obj,
                            name_execute_command_props,
                            self.get_path(
                                [
                                    self.log_groups[self.ECS_],
                                    self.join_sep_score(
                                        self.get_attr_project_name_comp_props(self_obj)
                                        + [self.get_attr_deploy_env(self_obj)]
                                    ),
                                    self.join_sep_score(name_execute_command_props),
                                ]
                            ),
                            encryption_key=execute_command_key,
                        ),
                        # s3_bucket=,  # Default: - none
                        # s3_encryption_enabled=,  # Default: - encryption will be disabled.
                        # s3_key_prefix=,  # Default: - none
                    ),
                    logging=ecs.ExecuteCommandLogging.OVERRIDE,
                ),  # Config for ECS Exec debugging
                vpc=self.get_attr_vpc(self_obj),
            ),
            # capacity_provider_strategies=,  # Capacity Provider strategies used to place a service.
            # circuit_breaker=,  # Enable the deployment circuit breaker.
            cloud_map_options=ecs.CloudMapOptions(
                # cloud_map_namespace=,  # Default: - the default_cloud_map_namespace associated to the cluster
                # container=,  # Default: - the task definition’s default container
                # container_port=,  # Default: - the default port of the ECS task definition’s default container
                dns_record_type=servicediscovery.DnsRecordType.A,
                dns_ttl=Duration.minutes(1),
                # failure_threshold=,  # Used for HealthCheckCustomConfig
                name=getattr(self_obj, self.ECS_SERVICE_CLOUD_MAP_SERVICE_NAME_),
            ),  # For configuring an Amazon ECS service to use service discovery.
            # deployment_alarms=,  # Default: - No alarms will be monitored during deployment.
            deployment_controller=ecs.DeploymentController(
                type=ecs.DeploymentControllerType.ECS
                # TODO: (NEXT) Update type=ecs.DeploymentControllerType.CODE_DEPLOY for blue/green (CODE_DEPLOY)
                #  deployment type powered by AWS CodeDeploy, for prod env(s)
            ),
            desired_count=1,
            enable_ecs_managed_tags=False,
            enable_execute_command=True,  # Enable ability to execute into a container (ECS Exec).
            # health_check_grace_period=,  # Time in secs, ECS service scheduler ignores unhealthy ELB target health checks after a task has first started.
            # max_healthy_percent=,  # Default: - 100 if daemon, otherwise 200
            # min_healthy_percent=,  # Default: - 0 if daemon, otherwise 50
            propagate_tags=ecs.PropagatedTagSource.TASK_DEFINITION,
            # service_connect_configuration=,  # Default: No ports are advertised via Service Connect on this service, and the service cannot make requests to other services via Service Connect.
            service_name=self.get_construct_name(self_obj, name_props, underscore=True),
        )
        self.ssm_string_parameter(
            self_obj,
            name_props,
            self.AWS_PRIVATE_ECS_DESCRIPTION_,
            self.get_path(
                [
                    self.AWS_PRIVATE_PARAMETER_PREFIX_,
                    self.join_sep_score(
                        self.get_attr_project_name_comp_props(self_obj)
                        + [self.get_attr_deploy_env(self_obj)]
                        + name_props
                    ),
                ]
            ),
            ecs_service.cluster.cluster_arn,
            data_type=ssm.ParameterDataType.TEXT,
            tier=ssm.ParameterTier.STANDARD,
        )
        ecs_service_errors_props: list[str] = name_props + [self.ERRORS_]
        sns_topic_errors: sns.Topic = self.sns_topic(
            self_obj,
            ecs_service_errors_props,
            subscriptions_=[
                subscriptions.LambdaSubscription(
                    fn=self.lambda_function_cloudwatch(
                        self_obj,
                        self.join_sep_score(
                            self.get_attr_project_name_comp_props(self_obj)
                            + [self.get_attr_deploy_env(self_obj)]
                            + ecs_service_errors_props
                        ),
                        security_groups=security_groups,
                    )
                )
            ],
        )
        word_map_project_name_comp: str = self.get_attr_word_map_project_name_comp(self_obj)
        if getattr(self_obj, self.DEPLOY_ENV_PROD_) and getattr(self_obj, self.DEPLOY_ENV_24_7_):
            self.cloudwatch_alarm(
                self_obj,
                name_props + [self.RUNNING_],
                ecs_service.metric_cpu_utilization(period=Duration.minutes(5), statistic="SampleCount"),
                f"Send notifications to SNS for {word_map_project_name_comp} ESC service running.",
                cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                cloudwatch.TreatMissingData.BREACHING,
                threshold=1,
            ).add_alarm_action(cloudwatch_actions.SnsAction(sns_topic_errors))
        # TODO: (NEXT) Test why this ECS service deployment alarms setup considerably increases pipeline deploy stage time
        # elif getattr(self_obj, self.DEPLOY_ENV_INTERNAL_):
        #     cloudwatch_alarm_deployment_alarm_name: str = self.get_construct_name(
        #         self_obj, name_props + [self.DEPLOYMENT_], underscore=True
        #     )
        #     self.cloudwatch_alarm(
        #         self_obj,
        #         name_props + [self.DEPLOYMENT_],
        #         ecs_service.metric_cpu_utilization(period=Duration.minutes(5), statistic="Average"),
        #         f"Deployment alarm for {word_map_project_name_comp} ESC service deployment.",
        #         cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        #         cloudwatch.TreatMissingData.MISSING,
        #         threshold=80,
        #         evaluation_periods=2,
        #         alarm_name=cloudwatch_alarm_deployment_alarm_name,
        #     ).add_alarm_action(cloudwatch_actions.SnsAction(sns_topic_errors))
        #     ecs_service.enable_deployment_alarms(
        #         alarm_names=[cloudwatch_alarm_deployment_alarm_name], behavior=ecs.AlarmBehavior.ROLLBACK_ON_ALARM
        #     )
        custom_filter_patterns_base: dict[str, str] = {
            self.DEFAULT_: self._log_metric_filter_pattern_default_app(http_error_code)
        }
        for k, filter_pattern in (
            {**custom_filter_patterns_base, **custom_filter_patterns}
            if custom_filter_patterns
            else custom_filter_patterns_base
        ).items():
            name_custom_errors_props: list[str] = name_props + [self.CUSTOM_, self.ERRORS_]
            metric_name: str = log_group.log_group_name
            if k != self.DEFAULT_:
                name_custom_errors_props.append(k)
                metric_name = self.get_path([metric_name, k])
            self.cloudwatch_alarm(
                self_obj,
                name_custom_errors_props,
                self._cloudwatch_metric(
                    self._logs_metric_filter(
                        self_obj,
                        name_custom_errors_props,
                        metric_name,
                        log_group,
                        self.join_sep_fw([self.ECS_.upper(), self.ERRORS_.capitalize()]),
                        filter_pattern=filter_pattern,
                        metric_value=str(1),
                    ),
                    metric_name,
                    "Sum",
                ),
                f"Send notifications to SNS for {word_map_project_name_comp} ESC service error or warning log lines.",
                cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                cloudwatch.TreatMissingData.NOT_BREACHING,
                threshold=0,
            ).add_alarm_action(cloudwatch_actions.SnsAction(sns_topic_errors))
        if dependant_constructs:
            for i in dependant_constructs:
                ecs_service.node.add_dependency(i)
        if target_group:
            # TODO: (NEXT) Look to replace with ``listener.addTargets()``, for more detail,
            #  see ``ecs_service.attach_to_application_target_group()`` method description
            ecs_service.attach_to_application_target_group(target_group)
        self._ecs_fargate_service_auto_scaling(self_obj, name_props, ecs_service, admin)
        return ecs_service

    def ecs_fargate_service_task_definition(
        self, self_obj, cpu: str, memory_mib: int, execution_role: iam.Role, task_role: iam.Role
    ) -> ecs.TaskDefinition:
        """
        Generate an ECS fargate service task definition.

        :param self_obj: The CDK stack class object.
        :param cpu: The number of CPU units used by the task.
        :param memory_mib: The amount (in MiB) of memory used by the task.
        :param execution_role: The role that grants the ECS agent permission to call AWS APIs on your behalf.
        :param task_role: The role that grants containers in the task permission to call AWS APIs on your behalf.
        :return: The ECS fargate service task definition.
        """
        name_props: list[str] = [self.ECS_]
        return ecs.TaskDefinition(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "TaskDefinition"),
            compatibility=ecs.Compatibility.EC2_AND_FARGATE,
            cpu=cpu,
            # ephemeral_storage_gib=,  # Fargate launch type only. If set size should be at least 21. Default: 20GiB
            # inference_accelerators=,  # Not supported in Fargate.
            # ipc_mode=,  # Not supported in Fargate
            memory_mib=str(memory_mib),
            network_mode=ecs.NetworkMode.AWS_VPC,
            # pid_mode=,  # Not supported in Fargate.
            # placement_constraints=,  # Not supported in Fargate.
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.X86_64,
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
            ),
            execution_role=execution_role,
            family=self.join_sep_score(
                self.get_attr_project_name_comp_props(self_obj) + [self.get_attr_deploy_env(self_obj)]
            ),
            # proxy_configuration=,  # For AWS App Mesh proxy.
            task_role=task_role,
            # volumes=[],  # Default: - No volumes passed to Docker daemon on a container instance.
        )

    def ecs_fargate_service_task_definition_add_container(
        self,
        self_obj,
        task_definition: ecs.TaskDefinition,
        image: ecs.EcrImage,
        container_name: str,
        port: int,
        memory: int,
        log_group: logs.LogGroup,
        environment: dict[str, str],
        secrets: dict[str, ecs.Secret],
        project_name_comp: str = None,
        cpu: int = None,
        shared: int = 0,
        working_directory: str = None,
    ) -> ecs.ContainerDefinition:
        """
        Add a new container to an ECS fargate service task definition, and generate an ECS container definition.

        :param self_obj: The CDK stack class object.
        :param task_definition: The ECS fargate service task definition.
        :param image: The image used to start a container.
        :param container_name: The name of the container.
        :param port: The (container_port) port number on the container that is bound to the user-specified or
            automatically assigned host port, and (host_port) the port number on the container
            instance to reserve for your container.
        :param memory: The amount (in MiB) of memory to present to the container.
        :param log_group: The log group to log to.
        :param environment: The environment variables to pass to the container.
        :param secrets: The secret environment variables to pass to the container.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param cpu: An optional minimum number of CPU units to reserve for the container.
        :param shared: An optional number of other containers sharing the same ECS task definition. Default: 0.
        :param working_directory: The working directory in which to run commands inside the container.
        :return: The ECS container definition, having adding a new container to an ECS fargate service task definition.
        """
        name_props: list[str] = [self.ECS_, self.TASK_, self.CONTAINER_]
        return task_definition.add_container(
            id=self.get_construct_id(self_obj, name_props, "ContainerDefinition", project_name_comp=project_name_comp),
            image=image,
            # command=,  # Default: - CMD value built into container image.
            container_name=container_name,
            cpu=cpu,  # Default: - No minimum CPU units reserved.
            disable_networking=False,
            # dns_search_domains=[],  # Default: - No search domains.
            # dns_servers=[],  # Default: - Default DNS servers.
            # docker_labels={},  # Default: - No labels.
            # docker_security_options=[],  # Labels for SELinux and AppArmor multi-level security systems
            # entry_point=,  # Default: - ENTRYPOINT configured in container.
            environment=environment,  # Env vars to pass to the container.
            # environment_files=[],  # The environment files to pass to the container.
            essential=True,
            # extra_hosts={},  # Hostnames and IP address mappings to append to the /etc/hosts file on the container
            # gpu_count=,  # GPUs assigned to the container. Default: - No GPUs assigned.
            # health_check=,  # Default: - Health check configuration from container.
            # hostname=,  # Default: - Automatic hostname.
            # inference_accelerator_resources=,  # For Amazon Elastic Inference.
            linux_parameters=ecs.LinuxParameters(
                scope=self_obj,
                id=self.get_construct_id(
                    self_obj,
                    name_props + [self.CONTAINER_, self.DEFINITION_],
                    "LinuxParameters",
                    project_name_comp=project_name_comp,
                ),
                init_process_enabled=True,  # Must be True for ECS Exec.
                # shared_memory_size=,  # Default: No shared memory.
            ),  # Linux-specific modifications applied to the container, e.g. Linux kernel.
            logging=ecs.LogDriver.aws_logs(
                stream_prefix=self.join_sep_score(
                    self.get_attr_project_name_comp_props(self_obj) + [self.get_attr_deploy_env(self_obj), self.ECS_]
                ),
                log_group=log_group,
            ),
            memory_limit_mib=memory,
            memory_reservation_mib=int(memory / (shared + 2 if shared > 0 else 2)),
            port_mappings=[
                ecs.PortMapping(
                    container_port=port,
                    host_port=port,
                    # The port number on the container instance to reserve for your container.
                    protocol=ecs.Protocol.TCP,
                )
            ],
            privileged=False,  # Give container elevated privileges on the host container instance (root user).
            readonly_root_filesystem=False,
            # Give container read-only access to its root file system. Must be False for ECS Exec.
            secrets=secrets,  # Secret env vars to pass to the container.
            # start_timeout=,  # Default: - none
            # stop_timeout=,  # Default: - none
            # system_controls=[],  # Namespaced kernel parameters to set in the container.
            user="root",  # The username to use inside the container.
            working_directory=working_directory,  # The working directory in which to run commands inside the container.
        )

    def ecs_secret_from_secrets_manager(
        self,
        self_obj,
        secret_name: str,
        secret_full_arn: str,
        field: str = None,
        full_content: bool = False,
    ) -> ecs.Secret:
        """
        Import a Secrets Manager secret for use with ECS.

        :param self_obj: The CDK stack class object.
        :param secret_name: A name for the secret.
        :param secret_full_arn: The ARN for the secret.
        :param field: The name of the field with the value that you want to set as the environment variable value.
          Only values in JSON format are supported.
        :param full_content: True if the full content of the secret is to be used.
        :return: The Secrets Manager secret for use with ECS.
        """
        return ecs.Secret.from_secrets_manager(
            secret=secretsmanager.Secret.from_secret_complete_arn(
                scope=self_obj,
                id=self.get_construct_id(self_obj, [secret_name], "ISecret"),
                secret_complete_arn=secret_full_arn,
            ),
            field=(field if field else self.GENERATE_STRING_KEY_) if not full_content else None,
        )

    def ecs_secret_from_secrets_manager_db_password(
        self, self_obj, db_user_creds_secret: secretsmanager.Secret
    ) -> ecs.Secret:
        return self.ecs_secret_from_secrets_manager(
            self_obj, db_user_creds_secret.secret_name, db_user_creds_secret.secret_full_arn
        )

    def ecs_secret_from_secrets_manager_redis_password(
        self, self_obj, ec_redis_auth_secret: secretsmanager.Secret
    ) -> ecs.Secret:
        return self.ecs_secret_from_secrets_manager(
            self_obj, ec_redis_auth_secret.secret_name, ec_redis_auth_secret.secret_full_arn
        )

    @staticmethod
    def ecs_task_managed_policies_list() -> list[iam.IManagedPolicy]:
        """
        Generate a list of ECS tasks managed policies, needed by an IAM role
        attached to an ECS task definition.

        :return: The list of ECS tasks managed policies.
        """
        return [
            iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="service-role/AmazonECSTaskExecutionRolePolicy"
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="CloudWatchFullAccessV2"),
        ]

    def efs_file_system(
        self, self_obj, security_group: ec2.SecurityGroup, is_removal_policy_retain: bool = False
    ) -> efs.FileSystem:
        """
        Generate an Elastic File System (EFS) file system.

        :param self_obj: The CDK stack class object.
        :param security_group: Security group to associate with this file system.
        :param is_removal_policy_retain: True if the resource is to be retained in the account, but orphaned from the stack.
        :return: The EFS file system.
        """
        name_props: list[str] = [self.EFS_]
        efs_file_system_: efs.FileSystem = efs.FileSystem(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "FileSystem"),
            vpc=self.get_attr_vpc(self_obj),
            enable_automatic_backups=True,
            encrypted=True,
            file_system_name=self.get_construct_name(self_obj, name_props),
            kms_key=self.get_attr_kms_key_stack(self_obj),
            lifecycle_policy=efs.LifecyclePolicy.AFTER_14_DAYS,
            out_of_infrequent_access_policy=efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS,
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            # provisioned_throughput_per_second=,  # Required property if ThroughputMode.PROVISIONED. Must be at least 1MiB/s.
            removal_policy=RemovalPolicy.RETAIN if is_removal_policy_retain else RemovalPolicy.DESTROY,
            security_group=security_group,
            throughput_mode=efs.ThroughputMode.BURSTING,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )
        efs_file_system_.connections.allow_default_port_internally()
        return efs_file_system_

    def elasticache_replication_group(
        self,
        self_obj,
        auth_token_secret: secretsmanager.Secret,
        ec_redis_auto_scaling_custom: bool = None,
        ec_redis_instance_type_custom: str = None,
        engine_version: str = "6.x",
        num_node_groups_max: int = 1,
    ) -> elasticache.CfnReplicationGroup:
        """
        Generate an ElastiCache replication group.

        :param self_obj: The CDK stack class object.
        :param auth_token_secret: The secret storing the password used to access a password protected server.
        :param ec_redis_auto_scaling_custom: If not None, use a custom auto-scaling option.
        :param ec_redis_instance_type_custom: If not None, use a custom instance cache node type option.
        :param engine_version: The version number of the cache engine to be used for the clusters in this replication group. Default: "6.x".
        :param num_node_groups_max: An optional maximum number of node groups (shards) for
            this ElastiCache (cluster mode enabled) replication group.
        :return: The ElastiCache replication group.
        """
        replicas: int = self_obj.env_meta[self.EC_REDIS_REPLICAS_]
        security_groups: list[ec2.SecurityGroup] = [getattr(self_obj, self.EC_REDIS_SG_)]
        cache_parameter_group_family: str = f"redis{engine_version}"
        parameter_group: elasticache.CfnParameterGroup = elasticache.CfnParameterGroup(
            scope=self_obj,
            id=self.get_construct_id(self_obj, self_obj.ec_redis_props, "CfnParameterGroup"),
            cache_parameter_group_family=cache_parameter_group_family,
            description=f"ElastiCache Redis cluster parameter group for '{cache_parameter_group_family}'.",
            properties={
                "notify-keyspace-events": "AKE"  # https://repost.aws/knowledge-center/elasticache-redis-keyspace-notifications
            },
        )
        replication_group_props: list[str] = [self.REPLICATION_, self.GROUP_]
        replication_group_desc_prefix: str = "ElastiCache Redis cluster replication group"
        replication_group_kms_key: kms.Key = self._kms_key(
            self_obj,
            self_obj.ec_redis_props + replication_group_props,
            replication_group_desc_prefix,
            enable_key_rotation=True,
        )
        subnet_group: elasticache.CfnSubnetGroup = elasticache.CfnSubnetGroup(
            scope=self_obj,
            id=self.get_construct_id(self_obj, self_obj.ec_redis_props, "CfnSubnetGroup"),
            description=f"ElastiCache Redis subnet group for {self.get_attr_word_map_project_name_comp(self_obj)}.",
            subnet_ids=[s.subnet_id for s in self.get_attr_vpc(self_obj).private_subnets],
            cache_subnet_group_name=self.get_construct_name_short(
                self_obj, self_obj.ec_redis_props + [self.SUBNET_, self.GROUP_]
            ),
        )
        dependant_constructs: list = [
            parameter_group,
            replication_group_kms_key,
            subnet_group,
        ]

        auth_token_key: str = "auth_token"
        log_delivery_configurations_key: str = "log_delivery_configurations"
        replication_group_kwargs: dict[str, str] = {
            "replication_group_description": f"{replication_group_desc_prefix} for {self.get_attr_word_map_project_name_comp(self_obj)}.",
            "at_rest_encryption_enabled": True,
            auth_token_key: auth_token_secret.secret_value_from_json(
                self.GENERATE_STRING_KEY_
            ).to_string(),  # For HIPAA compliance.
            "automatic_failover_enabled": True,
            "auto_minor_version_upgrade": True,
            "cache_node_type": (
                (
                    ec_redis_instance_type_custom
                    if ec_redis_instance_type_custom.startswith(self.CACHE_)
                    else self.join_sep_dot([self.CACHE_, ec_redis_instance_type_custom])
                )
                if ec_redis_instance_type_custom
                else self_obj.env_meta[self.EC_REDIS_INSTANCE_TYPE_]
            ),
            "cache_parameter_group_name": parameter_group.ref,  # f"default.redis{engine_version}"
            "cache_subnet_group_name": subnet_group.cache_subnet_group_name,  # For HIPAA compliance
            "engine": self.REDIS_.capitalize(),
            "engine_version": engine_version,
            # "global_replication_group_id": ,  # The name of the Global datastore.
            "kms_key_id": replication_group_kms_key.key_id,
            log_delivery_configurations_key: [
                self._elasticache_log_delivery_config(
                    self_obj,
                    [i],
                    self.get_path(
                        [
                            self.log_groups[self.ELASTICACHE_],
                            self.join_sep_score(
                                self.get_attr_project_name_comp_props(self_obj) + [self.get_attr_deploy_env(self_obj)]
                            ),
                            i,
                        ]
                    ),
                    i,
                )
                for i in [self.join_sep_score([i, self.LOG_]) for i in [self.SLOW_, self.ENGINE_]]
            ],
            "multi_az_enabled": getattr(self_obj, self.DEPLOY_ENV_PROD_),
            "notification_topic_arn": self.sns_topic(
                self_obj,
                self_obj.ec_redis_props + [self.SNS_],
                subscriptions_=[
                    subscriptions.LambdaSubscription(
                        fn=self.lambda_function_sns(
                            self_obj,
                            self.join_sep_empty(
                                [
                                    i.capitalize()
                                    for i in self.get_construct_name_short(self_obj, self_obj.ec_redis_props).split(
                                        self.SEP_SCORE_
                                    )
                                ]
                            ),
                            security_groups=security_groups,
                        )
                    )
                ],
            ).topic_arn,
            # "num_cache_clusters": len(getattr(self_obj, self.vpc).availability_zones),
            # Cannot define num_cache_clusters with: num_node_groups, replicas_per_node_group or node_group_configuration
            "num_node_groups": 1,
            "port": getattr(self_obj, self.REDIS_PORT_),
            "preferred_cache_cluster_a_zs": (
                self.get_attr_vpc(self_obj).availability_zones[
                    : (len(self.get_attr_vpc(self_obj).availability_zones) - diff)
                ]
                if (diff := len(self.get_attr_vpc(self_obj).availability_zones) > (1 + replicas))
                else self.get_attr_vpc(self_obj).availability_zones
            ),
            "preferred_maintenance_window": getattr(
                self_obj, self.SCHEDULE_WINDOW_ELASTICACHE_WEEKLY_MAINTENANCE_TIMESTAMP_
            ),
            "replicas_per_node_group": (
                (replicas - diff)
                if (diff := len(self.get_attr_vpc(self_obj).availability_zones) < (1 + replicas))
                else replicas
            ),
            "replication_group_id": self.get_construct_name_short(
                self_obj, self_obj.ec_redis_props + replication_group_props
            ),
            "security_group_ids": [i.security_group_id for i in security_groups],
            # "snapshot_arns": ,
            # "snapshot_name": ,
            # "snapshot_retention_limit": ,
            # "snapshotting_cluster_id": ,
            "snapshot_window": self.schedules.window_ec_redis_daily_backup_all_days_timestamp,
            "transit_encryption_enabled": True,  # For HIPAA compliance
        }

        replication_group: elasticache.CfnReplicationGroup = elasticache.CfnReplicationGroup(
            scope=self_obj,
            id=self.get_construct_id(self_obj, self_obj.ec_redis_props, "CfnReplicationGroup"),
            **replication_group_kwargs,
        )
        if dependant_constructs:
            for i in dependant_constructs:
                replication_group.node.add_dependency(i)
        if num_node_groups_max > 1 and replication_group.cache_parameter_group_name.endswith(
            self.join_sep_empty([self.SEP_DOT_, self.CLUSTER_, self.SEP_DOT_, self.ON_])
        ):
            self._elasticache_replication_group_auto_scaling(
                self_obj, self_obj.ec_redis_props, replication_group, replication_group_props, num_node_groups_max
            )
        elif (
            getattr(self_obj, self.DEPLOY_ENV_NOT_24_7_)
            if ec_redis_auto_scaling_custom is None
            else ec_redis_auto_scaling_custom
        ):
            self._elasticache_replication_group_auto_scaling_custom(
                self_obj,
                self_obj.ec_redis_props,
                replication_group,
                self._elasticache_replication_group_sanitise_kwargs(
                    replication_group_kwargs, auth_token_key, log_delivery_configurations_key
                ),
                replication_group_kms_key,
                auth_token_key,
                auth_token_secret,
                security_groups,
            )
        return replication_group

    def elasticloadbalancing_application_listener(
        self,
        self_obj,
        load_balancer: elasticloadbalancing.ApplicationLoadBalancer,
        certificates: list[acm.Certificate],
        target_groups: list[elasticloadbalancing.ApplicationTargetGroup],
        conditions: list[tuple[str, secretsmanager.Secret]],
        port: int = None,
    ) -> elasticloadbalancing.ApplicationListener:
        """
        Generates an ElasticLoadBalancing application listener, and adds it to an ElasticLoadBalancing application load balancer (ALB).

        :param self_obj: The CDK stack class object.
        :param load_balancer: The ElasticLoadBalancing application load balancer (ALB).
        :param certificates: Certificate list of ACM cert ARNs.
        :param target_groups: Target groups to forward requests to.
        :param conditions: A list of tuples, each containing: a HTTP header name and a AWS Secrets Manager secret, containing the value that CloudFront adds to requests it sends to the origin.
        :param port: An optional port. Default: HTTPS.
        :return: The ElasticLoadBalancing application listener.
        """
        name_props: list[str] = [self.ALB_]
        if port is None:
            port = self.HTTPS_PORT
        listener: elasticloadbalancing.ApplicationListener = load_balancer.add_listener(
            id=self.get_construct_id(self_obj, name_props, "ApplicationListener"),
            certificates=certificates,
            # default_action=,  # Cannot be specified together with default_target_groups. Default: - None.
            # default_target_groups=,  # Cannot be specified together with default_action. Default: - None.
            open=True,
            port=port,
            protocol=(
                elasticloadbalancing.ApplicationProtocol.HTTPS
                if port == self.HTTPS_PORT
                else elasticloadbalancing.ApplicationProtocol.HTTP
            ),
            # ssl_policy=elasticloadbalancing.SslPolicy.RECOMMENDED,  # Default: - Current predefined security policy
        )
        # Add target group to listener, and set default fixed response
        listener.add_target_groups(
            id=self.get_construct_id(self_obj, name_props + [self.LISTENER_], "TargetGroup"),
            target_groups=target_groups,
            conditions=[self._elasticloadbalancing_listener_condition_http_header(h, s) for h, s in conditions],
            priority=1,
        )
        listener.add_action(
            id=self.get_construct_id(self_obj, name_props + [self.LISTENER_], "DefaultAction"),
            action=elasticloadbalancing.ListenerAction.fixed_response(
                status_code=403, content_type="text/plain", message_body="Access denied - CDK"
            ),
        )
        return listener

    def elasticloadbalancing_application_load_balancer(
        self, self_obj, security_group: ec2.SecurityGroup, load_balancer_name: str = None
    ) -> elasticloadbalancing.ApplicationLoadBalancer:
        """
        Generate an ElasticLoadBalancing application load balancer (ALB).

        :param self_obj: The CDK stack class object.
        :param security_group: Security group to associate with this load balancer.
        :param load_balancer_name: An optional load balancer name.
        :return: The ElasticLoadBalancing application load balancer (ALB).
        """
        name_props: list[str] = [self.ALB_]
        return elasticloadbalancing.ApplicationLoadBalancer(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "ApplicationLoadBalancer"),
            # desync_mitigation_mode=elasticloadbalancing.DesyncMitigationMode.DEFENSIVE,
            # drop_invalid_header_fields=False,
            http2_enabled=True,
            idle_timeout=Duration.seconds(60),
            ip_address_type=elasticloadbalancing.IpAddressType.IPV4,
            security_group=security_group,
            vpc=self.get_attr_vpc(self_obj),
            deletion_protection=True,
            internet_facing=True,
            load_balancer_name=(
                load_balancer_name if load_balancer_name else self.get_construct_name_short(self_obj, name_props)
            ),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

    def elasticloadbalancing_application_target_group(
        self,
        self_obj,
        target_type: elasticloadbalancing.TargetType,
        port: int = None,
        target_group_name: str = None,
        target_group_protocol_https: bool = False,
        healthy_http_codes: str = str(200),
        health_check_path: str = None,
        health_check_protocol_https: bool = False,
    ) -> elasticloadbalancing.ApplicationTargetGroup:
        """
        Generate an ElasticLoadBalancing application target group.

        :param self_obj: The CDK stack class object.
        :param target_type: The type of targets registered to this TargetGroup, either IP or Instance.
        :param port: An optional port on which the target receives traffic.
        :param target_group_name: An optional target group name.
        :param target_group_protocol_https: True if the target group protocol should be HTTPS.
        :param healthy_http_codes: HTTP code(s) to use when checking for a successful response from a target. Default: "200".
        :param health_check_path: An optional ping path destination where ElasticLoadBalancing sends health check requests.
        :param health_check_protocol_https: True if the health check protocol should be HTTPS.
        :return: The ElasticLoadBalancing application target group.
        """
        name_props: list[str] = [self.ALB_, self.TG_]
        if health_check_path is None:
            health_check_path = self.SEP_FW_
        return elasticloadbalancing.ApplicationTargetGroup(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "ApplicationTargetGroup"),
            load_balancing_algorithm_type=elasticloadbalancing.TargetGroupLoadBalancingAlgorithmType.ROUND_ROBIN,
            port=port if port else getattr(self_obj, self.ALB_PORT_),
            protocol=(
                elasticloadbalancing.ApplicationProtocol.HTTPS
                if target_group_protocol_https
                else elasticloadbalancing.ApplicationProtocol.HTTP
            ),
            # TODO: (OPTIONAL) look to upgrading to have ALBs use HTTP2?
            protocol_version=elasticloadbalancing.ApplicationProtocolVersion.HTTP1,
            # slow_start=Duration.seconds(0)
            stickiness_cookie_duration=Duration.days(1),
            # stickiness_cookie_name=,  # Default: - If stickiness_cookie_duration is set, a load-balancer generated cookie is used.
            # targets=[],
            deregistration_delay=Duration.seconds(120),
            health_check=elasticloadbalancing.HealthCheck(
                # enabled=,  # Default: - Determined automatically.
                # healthy_grpc_codes="12",  # Health check matcher cannot be set for both 'HTTP' and 'GRPC' codes at the same time.
                healthy_http_codes=healthy_http_codes,
                healthy_threshold_count=3,  # Default: 5 for ALBs
                interval=Duration.seconds(30),
                path=health_check_path,
                port=str(getattr(self_obj, self.ALB_PORT_)),  # Default: 'traffic-port'
                protocol=(
                    elasticloadbalancing.Protocol.HTTPS
                    if health_check_protocol_https
                    else elasticloadbalancing.Protocol.HTTP
                ),
                timeout=Duration.seconds(5),
                unhealthy_threshold_count=2,
            ),
            target_group_name=(
                target_group_name if target_group_name else self.get_construct_name_short(self_obj, name_props)
            ),
            target_type=target_type,
            vpc=self.get_attr_vpc(self_obj),
        )

    def elasticloadbalancing_application_target_group_health_check_path(self, origin_path: str) -> str:
        return self.join_sep_empty([origin_path, self.SEP_FW_]) if origin_path[-1] != self.SEP_FW_ else origin_path

    def elasticloadbalancing_application_target_group_health_check_path_status_route(
        self, self_obj, origin_path: str
    ) -> str:
        return self.join_sep_empty(
            [
                self.elasticloadbalancing_application_target_group_health_check_path(origin_path),
                self.get_path([self.STATUS_, self_obj.status_route]),
            ]
        )

    def events_event_pattern_s3_object_created(self, s3_bucket_arn: str) -> events.EventPattern:
        return events.EventPattern(
            detail={self.REASON_: ["PutObject"]},
            detail_type=["Object Created"],
            resources=[s3_bucket_arn],
            source=[self.join_sep_dot([self.AWS_, self.S3_])],
        )

    def events_rule(self, self_obj, name_props: list[str], description: str, schedule: events.Schedule) -> events.Rule:
        """
        Generate an Events rule.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param description: A description of the CDK construct.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule.
        :return: The Events rule.
        """
        return events.Rule(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "Rule"),
            description=description,
            rule_name=self.get_construct_name(self_obj, name_props, underscore=True),
            schedule=schedule,
        )

    def file_json_load_cdk_custom_outputs(self) -> dict:
        return self._file_json_load(self.cdk_custom_outputs_path)

    def file_yaml_safe_load_codebuild_buildspec(self, buildspec_path: str) -> codebuild.BuildSpec:
        with open(buildspec_path, "r", encoding=self.ENCODING) as f:
            try:
                buildspec: dict = yaml.safe_load(f)
            except yaml.YAMLError as err:
                sys.exit(f"## Error parsing {buildspec_path} file: {err}")
        return codebuild.BuildSpec.from_object_to_yaml(buildspec)

    def format_arn_custom(
        self, self_obj, service: str, resource: str, resource_name: str = None, account: str = None, region: str = None
    ) -> str:
        """
        Generate a formatted Amazon Resource Name (ARN).

        Extends: aws_cdk.Stack.format_arn()

        :param self_obj: The CDK stack class object.
        :param service: The service namespace that identifies the AWS product (for example, 's3', 'iam', 'codepipline').
        :param resource: Resource type (e.g. "table", "autoScalingGroup", "certificate").
            For some resource types, e.g. S3 buckets, this field defines the bucket name.
        :param resource_name: Resource name or path within the resource. Default: self.SEP_ASTERISK_
        :param account: The ID of the AWS account that owns the resource, without the hyphens. For example, 123456789012.
        :param region: The region the resource resides in.
        :return: The formatted ARN.
        """
        if resource_name is None:
            resource_name = self.SEP_ASTERISK_
        arn_format: ArnFormat = {
            self.ACM_: ArnFormat.SLASH_RESOURCE_NAME,
            self.CLOUDFORMATION_: ArnFormat.SLASH_RESOURCE_NAME,
            self.CODEBUILD_: ArnFormat.SLASH_RESOURCE_NAME,
            self.EC2_: ArnFormat.SLASH_RESOURCE_NAME,
            self.ELASTICACHE_: ArnFormat.COLON_RESOURCE_NAME,
            self.IAM_: ArnFormat.SLASH_RESOURCE_NAME,
            self.KMS_: ArnFormat.SLASH_RESOURCE_NAME,
            self.LAMBDA_: ArnFormat.COLON_RESOURCE_NAME,
            self.LOGS_: ArnFormat.COLON_RESOURCE_NAME,
            self.RDS_: ArnFormat.COLON_RESOURCE_NAME,
            self.S3_: ArnFormat.NO_RESOURCE_NAME,
            self.SECRETSMANAGER_: ArnFormat.COLON_RESOURCE_NAME,
            self.SES_: ArnFormat.SLASH_RESOURCE_NAME,
            self.SNS_: ArnFormat.SLASH_RESOURCE_NAME,
            self.SSM_: ArnFormat.SLASH_RESOURCE_NAME,
        }[service]
        return self_obj.format_arn(
            service=service,
            resource=resource,
            arn_format=arn_format,
            resource_name=resource_name if arn_format != ArnFormat.NO_RESOURCE_NAME else None,
            account=self.SEP_EMPTY_ if service == self.S3_ else account,
            region=self.SEP_EMPTY_ if service == self.S3_ else region,
        )

    def format_database_server(self, database_server: str, hyphen_sep: bool = False) -> str:
        return (
            (self.SEP_SCORE_ if hyphen_sep else self.SEP_EMPTY_).join(
                [d.capitalize() for d in database_server.split(self.SEP_UNDER_)]
            )
            if self.SEP_UNDER_ in database_server
            else database_server.capitalize()
        )

    def get_additional_allowed_origins_deploy_envs(self, deploy_env: str) -> list[str]:
        return (
            [self.join_sep_score([self.DEV_, self.UNSTABLE_])]
            if deploy_env == self.DEV_
            else ([self.DEV_] if deploy_env == self.STAGING_ else [])
        )

    def get_attr_deploy_env(self, self_obj):
        return getattr(self_obj, self.DEPLOY_ENV_)

    def get_attr_env_account(self, self_obj) -> str:
        return getattr(self_obj, self.ENV_).account

    def get_attr_env_region(self, self_obj) -> str:
        return getattr(self_obj, self.ENV_).region

    def get_attr_kms_key_stack(self, self_obj) -> kms.Key:
        return getattr(self_obj, self.KMS_KEY_STACK_)

    def get_attr_project_name(self, self_obj, no_custom: bool = False) -> str:
        return getattr(
            self_obj,
            self.PROJECT_NAME_BASE_ if no_custom and hasattr(self_obj, self.PROJECT_NAME_BASE_) else self.PROJECT_NAME_,
            None,
        )

    def get_attr_project_name_comp(self, self_obj, no_custom: bool = False) -> str:
        return getattr(
            self_obj,
            (
                self.PROJECT_NAME_COMP_BASE_
                if no_custom and hasattr(self_obj, self.PROJECT_NAME_COMP_BASE_)
                else self.PROJECT_NAME_COMP_
            ),
            getattr(self_obj, self.VPC_NAME_, self.SEP_EMPTY_),
        )

    def get_attr_project_name_comp_props(self, self_obj, project_name_comp: str = None, **kwargs) -> list[str]:
        return (project_name_comp if project_name_comp else self.get_attr_project_name_comp(self_obj, **kwargs)).split(
            self.SEP_SCORE_
        )

    def get_attr_vpc(self, self_obj) -> ec2.IVpc:
        return getattr(self_obj, self.VPC_)

    def get_attr_vpc_cidr(self, self_obj) -> str:
        return getattr(self_obj, self.VPC_CIDR_)

    def get_attr_vpc_name(self, self_obj) -> str:
        return getattr(self_obj, self.VPC_NAME_)

    def get_attr_word_map_project_name_comp(self, self_obj, inc_comp: bool = True, inc_deploy_env: bool = True) -> str:
        props: list[str] = [getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)]
        if inc_comp:
            props.append(getattr(self_obj, self.WORD_MAP_COMPONENT_))
        if inc_deploy_env:
            props.append(self.get_attr_deploy_env(self_obj).upper())
        return self.join_sep_space(props)

    def get_buildspec_path(self, self_obj, project_name_comp: str, amplify: bool = False) -> str:
        """
        Generate a relative system file path to a buildspec.yml
        (aws-codepipeline-examples git submodule), or an amplify.yml
        (aws-amplify-examples git submodule) file.

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :param amplify: True if requesting a buildspec file for AWS Amplify.
        :return: The relative system file path to a buildspec.yml file.
        """
        buildspec_path: str = self.sub_paths[self.AMPLIFY_ if amplify else self.CODEPIPELINE_]
        for i, v in enumerate(project_name_comp.split(self.SEP_SCORE_)):
            if (
                i != 1
                or not hasattr(self_obj, self.PRODUCT_CUSTOM_)
                or getattr(self_obj, self.PRODUCT_CUSTOM_, None) is None
            ):
                buildspec_path += self.join_sep_empty([self.SEP_FW_, v])
        if self.BASE_ in project_name_comp or getattr(self_obj, self.TAG_DEPLOY_, None):
            buildspec_path += self.join_sep_empty([self.SEP_FW_, self.TAG_])
        return buildspec_path + self.join_sep_empty(
            [self.SEP_FW_, self.get_file_name_yml([self.AMPLIFY_ if amplify else self.BUILDSPEC_])]
        )

    def get_cdk_stack_description(
        self,
        project_name: str,
        detail: str,
        custom_val: str = None,
        components: list[str] = None,
        base_comp: bool = False,
        deploy_env: str = None,
    ) -> str:
        props: list[str] = [self.lookup_word_map(project_name)]
        if custom_val is not None:
            props.append(self.lookup_word_map(custom_val))
        if components:
            props = props + [
                self.lookup_word_map(comp) if not isinstance(comp, tuple) else comp[0] for comp in components
            ]
        if base_comp:
            props.append(self.lookup_word_map(self.BASE_))
        elif deploy_env:
            props.append(deploy_env.upper())
        props.append(f"resources: {detail}, etc.")
        return self.join_sep_space(props)

    def get_cdk_stack_id(
        self,
        project_name: str,
        custom_val: str = None,
        components: list[str] = None,
        base_comp: bool = False,
        deploy_env: str = None,
    ) -> str:
        props: list[str] = [self.CDK_STACK_PREFIX, project_name.capitalize()]
        if custom_val is not None:
            props.append(custom_val.capitalize())
        if components:
            props = props + [
                (
                    (comp.capitalize() if comp != self.CF_ else self.lookup_word_map(self.CF_))
                    if not isinstance(comp, tuple)
                    else comp[0]
                )
                for comp in components
            ]
        if base_comp:
            props.append(self.lookup_word_map(self.BASE_))
        elif deploy_env:
            props.append(deploy_env if deploy_env[0].isupper() else deploy_env.capitalize())
        props.append(self.CDK_STACK_SUFFIX)
        return self.join_sep_empty(props)

    def get_cdk_stack_name_short(self, cdk_stack_name) -> str:
        """
        Generate a short CDK stack name.

        :param cdk_stack_name: The CDK stack name.
        :return: The short CDK stack name.
        """
        return cdk_stack_name[len(self.CDK_STACK_PREFIX) : -(len(self.CDK_STACK_SUFFIX))][:32]

    def get_cloudfront_dist_price_class(self, self_obj, default: bool = False) -> cloudfront.PriceClass:
        if default or (not getattr(self_obj, self.DEPLOY_ENV_PROD_)):
            return self._CF_PRICE_CLASS_DEFAULT
        return self._REGION_META[self.region][self._CF_PRICE_CLASS_]

    def get_cloudfront_stack_outputs(self, stack_name: str, comp_upper: str, inc_comp: bool) -> dict[str, str]:
        if comp_upper is None:
            comp_upper = self.lookup_word_map(self.SERVER_)
        replacement: str = self.lookup_word_map(self.CF_)
        if inc_comp:
            replacement = self.join_sep_empty([comp_upper, replacement])
        return self.file_json_load_cdk_custom_outputs()[stack_name.replace(comp_upper, replacement, 1)]

    def get_construct_id(
        self,
        self_obj,
        construct_id_props: list[str],
        construct_type: str,
        **kwargs,
    ) -> str:
        """
        Generate a CDK construct ID, using a CDK stack class object method instead, if such a method exists.

        :param self_obj: The CDK stack class object.
        :param construct_id_props: Specific property details to include in the CDK construct ID.
        :param construct_type: The CDK construct class name (e.g. for the 'aws_cdk.aws_s3.Bucket' construct, specify 'Bucket').
        :return: The CDK construct ID.
        """
        method_name: str = self.get_construct_id.__name__
        if hasattr(self_obj.__class__, method_name) and callable(getattr(self_obj.__class__, method_name)):
            return self_obj.get_construct_id(construct_id_props, construct_type, **kwargs)
        return self.get_construct_id_default(self_obj, construct_id_props, construct_type, **kwargs)

    def get_construct_id_default(
        self,
        self_obj,
        construct_id_props: list[str],
        construct_type: str,
        project_name_comp: str = None,
        deploy_env: str = None,
        global_: bool = False,
        lambda_layer: bool = False,
    ) -> str:
        """
        Generate a CDK construct ID, default options.

        :param self_obj: The CDK stack class object.
        :param construct_id_props: Specific property details to include in the CDK construct ID.
        :param construct_type: The CDK construct class name (e.g. for the 'aws_cdk.aws_s3.Bucket' construct, specify 'Bucket').
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param deploy_env: An optional deployment env name to use instead of the CDK stack class default.
        :param global_: True if ID needs to be both regionally and globally unique, not just regional.
        :param lambda_layer: True if ID is for a Lambda layer.
        :return: The CDK construct ID.
        """
        props: list[str] = [self.CDK_STACK_PREFIX]
        if global_:
            props.append(self.get_attr_env_region(self_obj))
        is_not_lambda_layer: bool = bool(not lambda_layer)
        for i in (
            (
                self.get_attr_project_name_comp_props(self_obj, project_name_comp=project_name_comp)
                if is_not_lambda_layer
                else [None]
            )
            + [
                (
                    (deploy_env if deploy_env else getattr(self_obj, self.DEPLOY_ENV_, None))
                    if is_not_lambda_layer
                    else None
                )
            ]
            + construct_id_props
            + [construct_type]
        ):
            if i:
                props.append(i)
        return self.join_sep_score(props)

    def get_construct_name(
        self,
        self_obj,
        name_props: list[str],
        project_name_comp: str = None,
        underscore: bool = False,
        no_trim: bool = False,
        global_: bool = False,
        is_codebuild: bool = False,
        is_codepipeline: bool = False,
    ) -> str:
        """
        Generate a CDK construct name.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param underscore: True if name should use an underscore seperator instead of a forward-slash (e.g. 'FooBar_foo-bar')
        :param no_trim: True if name length doesn't need to be <=64 chars.
        :param global_: True if name needs to be both regionally and globally unique, not just regional.
        :param is_codebuild: True if name is for a CodeBuild project.
        :param is_codepipeline: True if name is for a CodePipeline pipeline.
        :return: The CDK construct name.
        """
        props: list[str] = list(name_props)
        if project_name_comp is not None:
            props = self.get_attr_project_name_comp_props(self_obj, project_name_comp=project_name_comp) + props
        if global_:
            props.insert(0, self.get_attr_env_region(self_obj))
        s: str = self.get_cdk_stack_name_short(self_obj.stack_name)
        p: str = (
            self.join_sep_empty(props).replace(self.SEP_SCORE_, self.SEP_EMPTY_)
            if is_codebuild or is_codepipeline
            else self.join_sep_score(props)
        )
        name: str = self.join_sep_empty([s, self.SEP_UNDER_ if underscore else self.SEP_FW_, p])
        return name if no_trim else name[:64]

    def get_construct_name_short(
        self,
        self_obj,
        name_props: list[str],
        project_name_comp: str = None,
        deploy_env: str = None,
        global_: bool = False,
        length: int = 32,
    ) -> str:
        """
        Generate a short CDK construct name.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param deploy_env: An optional deployment env name to use instead of the CDK stack class default.
        :param global_: True if name needs to be both regionally and globally unique, not just regional.
        :param length: An optional length of construct name, as different AWS services can have different limits. Default: 32
        :return: The short CDK construct name.
        """
        props: list[str] = self.get_attr_project_name_comp_props(self_obj, project_name_comp=project_name_comp)
        if global_:
            props.insert(0, self.get_attr_env_region(self_obj))
        if d := deploy_env if deploy_env else getattr(self_obj, self.DEPLOY_ENV_, None):
            props.append(d)
        name: str = self.join_sep_score(props + name_props)[:length]
        return name[:-1] if name[-1] == self.SEP_SCORE_ else name  # Ensure must not end with a hyphen

    def get_database_server_deploy_env_map(
        self,
        deploy_envs_meta: dict[str, dict],
        orig_map_base: dict[str, dict] = None,
        opt_map_base: dict[str, dict] = None,
    ) -> dict[str, dict]:
        if orig_map_base is None:
            orig_map_base = self.DATABASE_SERVER_DEPLOY_ENV_MAP_BASE
        new_map: dict[str, dict] = {}
        for k, v in ({**orig_map_base, **opt_map_base} if opt_map_base else orig_map_base).items():
            for e in v[self.DEPLOY_ENV_LIST_]:
                if e in deploy_envs_meta:
                    v[self.TAG_KEY_ENV_TYPE_] = deploy_envs_meta[e][self.TAG_KEY_ENV_TYPE_]
                    break
            if self.TAG_KEY_ENV_TYPE_ in v and v[self.TAG_KEY_ENV_TYPE_]:
                new_map[k] = v
        return new_map

    def get_deploy_env_chosen(self, deploy_env: str, always_prod: bool = None) -> str:
        if always_prod is None:
            always_prod = True
        return self.STAGING_ if not always_prod and self.is_deploy_env_internal(deploy_env) else self.PROD_

    def get_deploy_env_database_server_map(self, orig_map: dict[str, dict]) -> dict[str, str]:
        new_map: dict[str, str] = {}
        for database_server, meta in orig_map.items():
            for deploy_env in meta[self.DEPLOY_ENV_LIST_]:
                new_map[deploy_env] = database_server
        return new_map

    def get_deploy_envs_meta(
        self,
        opt_meta: dict[str, tuple[str, str]] = None,
        ec_redis_instance_type_custom: str = None,
        ecs_service_max_val_custom: int = None,
    ) -> dict[str, dict]:
        meta: dict[str, dict] = {}
        for deploy_env, weight in {
            **self.DEPLOY_ENVS_INTERNAL,
            **self.DEPLOY_ENVS_EXTERNAL,
            **({k: v[0] for k, v in opt_meta.items()} if opt_meta else {}),
        }.items():
            ec_redis_meta: str = self.EC_REDIS_META[weight]
            ecs_service_min_val: int = self.ECS_META[weight][self.ECS_SERVICE_MIN_]
            ecs_service_max_val: int = self.ECS_META[weight][self.ECS_SERVICE_MAX_]
            is_stag_prod: bool = deploy_env in set(self.STAG_PROD_LIST)
            meta[deploy_env] = {
                self.EC_REDIS_INSTANCE_TYPE_: self.join_sep_dot(
                    [
                        self.CACHE_,
                        (
                            ec_redis_instance_type_custom
                            if ec_redis_instance_type_custom and is_stag_prod
                            else ec_redis_meta[self.EC_REDIS_INSTANCE_TYPE_]
                        ),
                    ]
                ),
                self.EC_REDIS_REPLICAS_: ec_redis_meta[self.EC_REDIS_REPLICAS_],
                self.ECS_SERVICE_MIN_: ecs_service_min_val,
                self.ECS_SERVICE_MAX_: (
                    (
                        max(ecs_service_max_val_custom, ecs_service_max_val)
                        if ecs_service_max_val_custom
                        else ecs_service_max_val
                    )
                    if is_stag_prod
                    else ecs_service_min_val
                ),
                self.TAG_KEY_ENV_TYPE_: (
                    EnvType.INTERNAL
                    if self.is_deploy_env_internal(deploy_env)
                    else (EnvType.PROD if self.is_deploy_env_prod(deploy_env) else EnvType.EXTERNAL)
                ).name,
                # Both Staging and Prod deployment environments, will have obfuscated strings prepended to their FQDNs
                self._MULTI_REGION_: self._REGION_META[self.region][self._MULTI_REGION_] if is_stag_prod else None,
                # Both Dev and Staging deployment environments do not use a git tag for specifying a release candidate
                self.TAG_DEPLOY_: bool(deploy_env not in set(self.DEV_STAG_LIST)),
            }
        return meta

    @staticmethod
    def get_ec2_security_group_rule_description(description: str, port: int = None) -> str:
        """
        Generate an EC2 security group rule description.

        :param description: A description of the CDK construct.
        :param port: The port info for the rule.
        :return: The EC2 security group rule description.
        """
        return f"Allow {description} on {f'port {port}' if port else 'all TCP ports'}."

    def get_ecs_container_name(self, self_obj, **kwargs) -> str:
        return self.get_construct_name_short(self_obj, [self.ECS_, self.TASK_, self.CONTAINER_], **kwargs)

    def get_ecs_secret_from_secrets_manager(self, self_obj, base_stack: IConstruct, attr_name: str) -> ecs.Secret:
        secret: secretsmanager.ISecret = (
            getattr(base_stack, self.PLURAL_MAPPINGS[attr_name])[self.get_attr_deploy_env(self_obj)]
            if getattr(self_obj, self.DEPLOY_ENV_PREVIEW_DEMO_)
            else getattr(base_stack, attr_name)
        )
        return self.ecs_secret_from_secrets_manager(self_obj, secret.secret_name, secret.secret_full_arn)

    def get_elastic_ip_ranges(
        self,
        self_obj,
        cdk_base_stack_name: str,
        elastic_ip_str_list: list[str],
        project_name_comp: str = None,
    ) -> list[str]:
        """
        Generate a list of IP addresses in CIDR notation (i.e. 12.34.56.78/32), for all Elastic IPs.

        :param self_obj: The CDK stack class object.
        :param cdk_base_stack_name: The name of the base CDK stack containing the 'public IPv4 address' outputs.
        :param elastic_ip_str_list: The list of strings to represent each Elastic IP.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :return: The list of IP addresses in CIDR notation.
        """
        return [
            self.get_path([self.file_json_load_cdk_custom_outputs()[cdk_base_stack_name][output_key], str(32)])
            for i in elastic_ip_str_list
            if (
                output_key := self.CDK_STACK_PREFIX
                + self.join_sep_score(
                    self.get_attr_project_name_comp_props(self_obj, project_name_comp=project_name_comp) + [i]
                ).replace(self.SEP_SCORE_, self.SEP_EMPTY_)
                + self.CFN_OUTPUT_TYPE
            )
        ]

    def get_file_name_yml(self, name_props: list[str]) -> str:
        return self._get_file_name_base(name_props, self.YML_)

    def get_file_name_zip(self, name_props: list[str]) -> str:
        return self._get_file_name_base(name_props, self.ZIP_)

    def get_lambda_func_name(
        self, self_obj, props: list[str], project_name_comp: str = None, code_path: bool = False
    ) -> str:
        func_name_props: list[str] = list(props)
        func_name_props = func_name_props + [
            i.capitalize()
            for i in self.get_attr_project_name_comp_props(
                self_obj, project_name_comp=project_name_comp, no_custom=code_path
            )
        ]
        if not code_path:
            func_name_props.append(self.get_attr_deploy_env(self_obj).capitalize())
        return self.join_sep_empty(func_name_props)

    def get_ms_teams_aws_notifications_webhook_url(self, self_obj, key: str) -> str:
        project_name: str = self.get_attr_project_name(self_obj)
        urls: dict = self.lookup_ms_teams(self.WEBHOOK_URL_AWS_NOTIFICATIONS_)
        if project_name in urls:
            return urls[project_name][key]
        return self.lookup_ms_teams(self.WEBHOOK_URL_AWS_NOTIFICATIONS_MISC_)[key]

    def get_params_and_secrets_ext_arn(self) -> str:
        return self._REGION_META[self.region][self._PARAMS_AND_SECRETS_EXT_ARN_]

    def get_path(self, props: list[str], lead: bool = False) -> str:
        props_joined: str = self.join_sep_fw([str(i) for i in props])
        if lead and (not props_joined.startswith(self.SEP_FW_)):
            props_joined = self.join_sep_empty([self.SEP_FW_, props_joined])
        return props_joined

    def get_region_meta_cidrs(self) -> list[str]:
        return self._REGION_META[self.region][self.CIDRS_]

    def get_repo_name_list(self, self_obj, project_name_comp_list: list[str], repo: str) -> list[str]:
        """
        Generate a list of repo names, based on a list of project names.

        :param self_obj: The CDK stack class object.
        :param project_name_comp_list: The list of project name & component specifiers.
        :param repo: The alternative component (of a project) repo.
        :return: The list of repo names.
        """
        return (
            [
                self.join_sep_score(
                    [repo if j == getattr(self_obj, self.COMPONENT_) else j for j in i.split(self.SEP_SCORE_)]
                )
                for i in project_name_comp_list
            ]
            if repo
            else None
        )

    def get_s3_bucket_name(self, self_obj, bucket_name_prefix: str) -> str:
        return self.join_sep_score([bucket_name_prefix, self.get_attr_env_region(self_obj)]).lower()

    def get_s3_bucket_tags(self, self_obj) -> list[dict[str, str]]:
        key_value_pairs: dict[str, str] = self.add_tags_required(
            stacks=None,
            project_name_val=getattr(self_obj, self.WORD_MAP_PROJECT_NAME_),
            custom_val=getattr(self_obj, self.PRODUCT_CUSTOM_, self.TAG_VAL_NONE_),
            env_type_val=getattr(self_obj, self.DEPLOY_ENV_TYPE_),
            component_val=getattr(self_obj, self.WORD_MAP_COMPONENT_),
            deploy_env_val=self.get_attr_deploy_env(self_obj),
        )
        return [{"Key": k, "Value": v} for k, v in key_value_pairs.items()]

    def get_termination_protection(self, deploy_env: str) -> Optional[bool]:
        return True if self.is_deploy_env_prod(deploy_env) else None

    def get_url_for_ms_from_cdk_stack(self, self_obj, stack: IConstruct = None, is_public: bool = False) -> str:
        is_stack: bool = bool(stack is not None)
        if is_stack:
            self_obj.add_dependency(stack)
        return getattr(
            stack if is_stack else self_obj, self.URL_ if is_public else self.URL_PRIVATE_, self.URL_NOT_FOUND_
        )

    def get_vpc_nat_gateway_ip_ranges(self, self_obj) -> list[str]:
        """
        Get the VPC NAT Gateway IP ranges.

        :param self_obj: The CDK stack class object.
        :return: The list of VPC NAT Gateway IP ranges.
        """
        return [
            self.get_path([i, str(32)])
            for i in ssm.StringParameter.value_from_lookup(
                scope=self_obj, parameter_name=getattr(self, self.VPC_NAT_GATEWAY_IP_RANGES_PARAMETER_NAME_)
            ).split(self.SEP_COMMA_)
        ]

    def iam_policy_statement_cloudformation_stack_all(self, self_obj, resource_name: str = None) -> iam.PolicyStatement:
        if resource_name is None:
            resource_name = self.SEP_ASTERISK_
        return iam.PolicyStatement(
            actions=[self.join_sep_colon([self.CLOUDFORMATION_, self.SEP_ASTERISK_])],
            resources=[
                self.format_arn_custom(
                    self_obj, service=self.CLOUDFORMATION_, resource=self.STACK_, resource_name=resource_name
                )
            ],
        )

    def iam_policy_statement_ec2_user_data(self) -> iam.PolicyStatement:
        return iam.PolicyStatement(
            actions=[
                self.join_sep_colon([self.EC2_, i])
                for i in [
                    "AssociateAddress",
                    "CreateTags",
                    "DescribeAddresses",
                    "DescribeVpcs",
                ]
            ],
            resources=self.ALL_RESOURCES,
        )

    def iam_policy_statement_ecs_access_to_dynamodb(self, dydb_table_arn: str) -> list[iam.PolicyStatement]:
        return [
            iam.PolicyStatement(
                actions=[self.join_sep_colon([self.DYNAMODB_, self.join_sep_empty(["List", self.SEP_ASTERISK_])])],
                resources=self.ALL_RESOURCES,
            ),
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.DYNAMODB_, i])
                    for i in [
                        "DeleteItem",
                        "DescribeTable",
                        "GetItem",
                        "PutItem",
                        "Query",
                    ]
                ],
                resources=[dydb_table_arn],
            ),
        ]

    def iam_policy_statement_ecs_access_to_s3(
        self,
        self_obj,
        s3_cdk_stack_name: str,
        s3_bucket_prefixes: list[str],
        s3_bucket_prefixes_read_only: list[str] = None,
    ) -> list[iam.PolicyStatement]:
        s3_bucket_prefixes_inc_read_only: list[str] = s3_bucket_prefixes + ["sihhds"]
        if s3_bucket_prefixes_read_only:
            for i in s3_bucket_prefixes_read_only:
                s3_bucket_prefixes_inc_read_only.append(i)
        context_key: str = getattr(self_obj, self.STORAGE_S3_ENCRYPTION_CONTEXT_KEY_)
        kms_key_arn: str = getattr(self_obj, self.STORAGE_S3_KMS_KEY_).key_arn
        return [
            self.iam_policy_statement_s3_delete_objects(self_obj, s3_bucket_prefixes=s3_bucket_prefixes),
            self.iam_policy_statement_s3_get_objects(self_obj, s3_bucket_prefixes=s3_bucket_prefixes_inc_read_only),
            self.iam_policy_statement_s3_list_buckets(self_obj, s3_bucket_prefixes=s3_bucket_prefixes_inc_read_only),
            self.iam_policy_statement_s3_put_objects(self_obj, s3_bucket_prefixes=s3_bucket_prefixes),
            iam.PolicyStatement(
                actions=[self.join_sep_colon([self.KMS_, "DescribeKey"])],
                resources=[kms_key_arn],
            ),
            iam.PolicyStatement(
                actions=[self.join_sep_colon([self.KMS_, i]) for i in ["Decrypt", "Encrypt", "GenerateDataKey"]],
                conditions={
                    "StringEquals": {
                        self.join_sep_colon([self.KMS_, "EncryptionContext", context_key]): s3_cdk_stack_name
                    }
                },
                resources=[kms_key_arn],
            ),
            iam.PolicyStatement(
                actions=[self.join_sep_colon([self.KMS_, "ReEncrypt"])],
                conditions={
                    "StringEquals": {
                        self.join_sep_colon(
                            [self.KMS_, "DestinationEncryptionContext", context_key]
                        ): s3_cdk_stack_name,
                        self.join_sep_colon([self.KMS_, "SourceEncryptionContext", context_key]): s3_cdk_stack_name,
                    }
                },
                resources=[kms_key_arn],
            ),
        ]

    def iam_policy_statement_ecs_access_to_sns(self, self_obj, resource_arn: str = None) -> list[iam.PolicyStatement]:
        try:
            arn: str = resource_arn if resource_arn else self_obj.sns_platform_application_arn
        except AttributeError:
            arn: str = self.format_arn_custom(
                self_obj,
                service=self.SNS_,
                resource=self.APP_,
                resource_name=self.get_path([self.GCM_.upper(), self.SEP_ASTERISK_]),
            )

        return [
            iam.PolicyStatement(
                actions=[
                    self.join_sep_colon([self.SNS_, i])
                    for i in [
                        "CreatePlatformEndpoint",
                        "GetPlatformApplicationAttributes",
                        "ListEndpointsByPlatformApplication",
                        "Publish",
                        "SetEndpointAttributes",
                    ]
                ],
                resources=[arn],
            )
        ]

    def iam_policy_statement_ecs_exec(self) -> iam.PolicyStatement:
        return iam.PolicyStatement(
            actions=[
                self.join_sep_colon([self.SSMMESSAGES_, i])
                for i in [
                    "CreateControlChannel",
                    "CreateDataChannel",
                    "OpenControlChannel",
                    "OpenDataChannel",
                ]
            ],
            resources=self.ALL_RESOURCES,
        )

    def iam_policy_statement_kms_key_encrypt_decrypt(
        self, self_obj, resources: list[str] = None
    ) -> iam.PolicyStatement:
        """
        Generate a KMS service key (encrypt & decrypt) custom policy.

        :param self_obj: The CDK stack class object.
        :param resources: An optional list of explicit KMS resources for this custom policy.
        :return: The KMS service key (encrypt & decrypt) custom policy.
        """
        return iam.PolicyStatement(
            actions=[
                self.join_sep_colon([self.KMS_, i])
                for i in [
                    "Decrypt",
                    "DescribeKey",
                    "Encrypt",
                    self.join_sep_empty(["GenerateDataKey", self.SEP_ASTERISK_]),
                    self.join_sep_empty(["ReEncrypt", self.SEP_ASTERISK_]),
                ]
            ],
            resources=(
                resources if resources else [self.format_arn_custom(self_obj, service=self.KMS_, resource=self.KEY_)]
            ),
        )

    def iam_policy_statement_kmy_key_decrypt(self, self_obj, resource_name: str = None) -> iam.PolicyStatement:
        if resource_name is None:
            resource_name = self.SEP_ASTERISK_
        return iam.PolicyStatement(
            actions=[self.join_sep_colon([self.KMS_, "Decrypt"])],
            resources=[
                self.format_arn_custom(self_obj, service=self.KMS_, resource=self.KEY_, resource_name=resource_name)
            ],
        )

    def iam_policy_statement_lambda_update_function_code(self, lambda_func_arns: list[str]) -> iam.PolicyStatement:
        return iam.PolicyStatement(
            actions=[self.join_sep_colon([self.LAMBDA_, "UpdateFunctionCode"])],
            resources=lambda_func_arns,
        )

    def iam_policy_statement_s3_delete_objects(self, self_obj, s3_bucket_prefixes: list[str]) -> iam.PolicyStatement:
        return iam.PolicyStatement(
            actions=[
                self.join_sep_colon([self.S3_, i])
                for i in [
                    "DeleteObject",
                    "DeleteObjectVersion",
                ]
            ],
            resources=[
                self.format_arn_custom(
                    self_obj,
                    service=self.S3_,
                    resource=self.join_sep_empty([i, self.SEP_ASTERISK_, self.SEP_FW_, self.SEP_ASTERISK_]),
                )
                for i in s3_bucket_prefixes
            ],
        )

    def iam_policy_statement_s3_get_objects(self, self_obj, s3_bucket_prefixes: list[str]) -> iam.PolicyStatement:
        return iam.PolicyStatement(
            actions=[
                self.join_sep_colon([self.S3_, i])
                for i in [
                    "GetObject",
                    "GetObjectAttributes",
                    "GetObjectVersion",
                ]
            ],
            resources=[
                self.format_arn_custom(
                    self_obj,
                    service=self.S3_,
                    resource=self.join_sep_empty([i, self.SEP_ASTERISK_, self.SEP_FW_, self.SEP_ASTERISK_]),
                )
                for i in s3_bucket_prefixes
            ],
        )

    def iam_policy_statement_s3_list_buckets(self, self_obj, s3_bucket_prefixes: list[str]) -> iam.PolicyStatement:
        return iam.PolicyStatement(
            actions=[self.join_sep_colon([self.S3_, "ListBucket"])],
            resources=[
                self.format_arn_custom(
                    self_obj, service=self.S3_, resource=self.join_sep_empty([i, self.SEP_ASTERISK_])
                )
                for i in s3_bucket_prefixes
            ],
        )

    def iam_policy_statement_s3_put_objects(self, self_obj, s3_bucket_prefixes: list[str]) -> iam.PolicyStatement:
        return iam.PolicyStatement(
            actions=[
                self.join_sep_colon([self.S3_, i])
                for i in [
                    "PutObject",
                    "PutObjectTagging",
                    "PutObjectAcl",
                ]
            ],
            resources=[
                self.format_arn_custom(
                    self_obj,
                    service=self.S3_,
                    resource=self.join_sep_empty([i, self.SEP_ASTERISK_, self.SEP_FW_, self.SEP_ASTERISK_]),
                )
                for i in s3_bucket_prefixes
            ],
        )

    def iam_policy_statement_secretsmanager_get_secret_value(
        self, self_obj, resource_name: str = None, secret_full_arn: str = None
    ) -> iam.PolicyStatement:
        if resource_name is None:
            resource_name = self.SEP_ASTERISK_
        return iam.PolicyStatement(
            actions=[self.join_sep_colon([self.SECRETSMANAGER_, "GetSecretValue"])],
            resources=[
                (
                    secret_full_arn
                    if secret_full_arn
                    else self.format_arn_custom(
                        self_obj, service=self.SECRETSMANAGER_, resource=self.SECRET_, resource_name=resource_name
                    )
                )
            ],
        )

    def iam_policy_statement_service_role_for_ecs(self, self_obj) -> iam.PolicyStatement:
        return iam.PolicyStatement(
            actions=[self.join_sep_colon([self.IAM_, "CreateServiceLinkedRole"])],
            conditions={
                "StringLike": {self.join_sep_colon([self.IAM_, "AWSServiceName"]): self._get_aws_service(self.ECS_)}
            },
            resources=[
                self.format_arn_custom(
                    self_obj,
                    service=self.IAM_,
                    resource=self.ROLE_,
                    resource_name=self.join_sep_fw(
                        [
                            self.join_sep_score([self.AWS_, self.SERVICE_, self.ROLE_]),
                            self._get_aws_service(self.ECS_),
                            self.join_sep_empty(["AWSServiceRoleForECS", self.SEP_ASTERISK_]),
                        ]
                    ),
                    region="",
                )
            ],
        )

    def iam_policy_statement_ssm_get_parameter(self, self_obj, resource_name: str = None) -> iam.PolicyStatement:
        if resource_name is None:
            resource_name = self.SEP_ASTERISK_
        return iam.PolicyStatement(
            actions=[
                self.join_sep_colon([self.SSM_, i])
                for i in [
                    "GetParameter",
                    "GetParameters",
                ]
            ],
            resources=[
                self.format_arn_custom(
                    self_obj, service=self.SSM_, resource=self.PARAMETER_, resource_name=resource_name
                )
            ],
        )

    def iam_policy_statement_ssm_put_parameter(self, self_obj, resource_name: str = None) -> iam.PolicyStatement:
        if resource_name is None:
            resource_name = self.SEP_ASTERISK_
        return iam.PolicyStatement(
            actions=[self.join_sep_colon([self.SSM_, "PutParameter"])],
            resources=[
                self.format_arn_custom(
                    self_obj, service=self.SSM_, resource=self.PARAMETER_, resource_name=resource_name
                )
            ],
        )

    def iam_role(
        self,
        self_obj,
        name_props: list[str],
        principal: iam.ServicePrincipal,
        description: str,
        project_name_comp: str = None,
        managed_policies: list[iam.ManagedPolicy] = None,
        custom_policies: list[iam.PolicyStatement] = None,
        codebuild_: bool = False,
        codepipeline_: bool = False,
    ) -> iam.Role:
        """
        Generate an IAM role.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param principal: The AWS service principal the role may be assumed by (i.e. sqs.amazonaws.com).
        :param description: A description of the CDK construct.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param managed_policies: A list of managed policies associated with this role.
        :param custom_policies: A list of custom policies associated with this role.
        :param codebuild_: True if role is for a CodeBuild project.
        :param codepipeline_: True if role is for a CodePipeline pipeline.
        :return: The IAM role.
        """
        role: iam.Role = iam.Role(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "Role", project_name_comp=project_name_comp, global_=True),
            assumed_by=principal,
            description=description,
            managed_policies=managed_policies,
            role_name=self.get_construct_name(
                self_obj,
                name_props,
                project_name_comp=project_name_comp,
                underscore=True,
                global_=True,
                is_codebuild=codebuild_,
                is_codepipeline=codepipeline_,
            ),
        )
        if custom_policies:
            for policy_statement in custom_policies:
                role.add_to_policy(statement=policy_statement)
        return role

    def iam_role_codebuild(
        self,
        self_obj,
        project_name_comp: str,
        managed_policies: list[iam.ManagedPolicy] = None,
        pypi_server_access: bool = False,
        params_and_secrets_ext_arn: str = None,
    ) -> iam.Role:
        """
        Generate an IAM role, for a CodeBuild service principal (i.e. codebuild.amazonaws.com).

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :param managed_policies: A list of managed policies associated with this role.
        :param pypi_server_access: True if CodeBuild needs to generate a '.pypirc' or 'pip.conf' file, in order to access a PyPi server.
        :param params_and_secrets_ext_arn: An optional ARN of a Lambda layer that CodeBuild needs to get for the AWS Parameters and Secrets Extension.
        :return: The IAM role, for a CodeBuild service principal.
        """
        custom_policies: list[iam.PolicyStatement] = (
            self._codebuild_custom_policies_list_pypi(self_obj, project_name_comp)
            if pypi_server_access
            else self._codebuild_custom_policies_list(self_obj, project_name_comp)
        )
        if params_and_secrets_ext_arn:
            custom_policies = custom_policies + self._codebuild_custom_policies_list_params_and_secrets_ext(
                params_and_secrets_ext_arn
            )
        description: str = f"CodeBuild role for {project_name_comp}"
        if d := getattr(self_obj, self.DEPLOY_ENV_, None):
            description = self.join_sep_space([description, d.upper()])
        return self.iam_role(
            self_obj,
            [self.BUILD_],
            self.iam_service_principal(self.CODEBUILD_),
            description,
            project_name_comp=project_name_comp,
            managed_policies=managed_policies,
            custom_policies=custom_policies,
            codebuild_=True,
        )

    def iam_role_codepipeline(
        self,
        self_obj,
        project_name_comp: str,
        managed_policies: list[iam.ManagedPolicy] = None,
    ) -> iam.Role:
        """
        Generate an IAM role, for a CodePipeline service principal (i.e. codepipeline.amazonaws.com).

        :param self_obj: The CDK stack class object.
        :param project_name_comp: The project name and component to use instead of the CDK stack class default.
        :param managed_policies: A list of managed policies associated with this role.
        :return: The IAM role, for a CodePipeline service principal.
        """
        description: str = f"CodePipeline role for {project_name_comp}"
        if d := getattr(self_obj, self.DEPLOY_ENV_, None):
            description = self.join_sep_space([description, d.upper()])
        return self.iam_role(
            self_obj,
            [self.PIPELINE_],
            self.iam_service_principal(self.CODEPIPELINE_),
            description,
            project_name_comp=project_name_comp,
            managed_policies=managed_policies,
            custom_policies=self._codepipeline_custom_policies_list(),
            codepipeline_=True,
        )

    def iam_role_ec2(
        self,
        self_obj,
        description: str,
        project_name_comp: str = None,
        managed_policies: list[iam.ManagedPolicy] = None,
        custom_policies: list[iam.PolicyStatement] = None,
    ) -> iam.Role:
        """
        Generate an IAM role, for an EC2 service principal (i.e. ec2.amazonaws.com).

        :param self_obj: The CDK stack class object.
        :param description: A description of the CDK construct.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param managed_policies: A list of managed policies associated with this role.
        :param custom_policies: A list of custom policies associated with this role.
        :return: The IAM role, for an EC2 service principal.
        """
        return self.iam_role(
            self_obj,
            [self.EC2_],
            self.iam_service_principal(self.EC2_),
            description,
            project_name_comp=project_name_comp,
            managed_policies=managed_policies,
            custom_policies=custom_policies,
        )

    def iam_role_ecs_task(
        self,
        self_obj,
        description: str,
        project_name_comp: str = None,
        managed_policies: list[iam.ManagedPolicy] = None,
        custom_policies: list[iam.PolicyStatement] = None,
    ) -> iam.Role:
        """
        Generate an IAM role, for ECS tasks.

        :param self_obj: The CDK stack class object.
        :param description: A description of the CDK construct.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param managed_policies: A list of managed policies associated with this role.
        :param custom_policies: A list of custom policies associated with this role.
        :return: The IAM role, for an ECS service principal.
        """
        name_props: list[str] = [self.ECS_, self.TASK_]
        return self.iam_role(
            self_obj,
            name_props,
            self.iam_service_principal(self.join_sep_score([self.ECS_, self.TASKS_])),
            description,
            project_name_comp=project_name_comp,
            managed_policies=managed_policies,
            custom_policies=custom_policies,
        )

    def iam_role_lambda(
        self,
        self_obj,
        function_name: str,
        project_name_comp: str = None,
        managed_policies: list[iam.ManagedPolicy] = None,
        custom_policies: list[iam.PolicyStatement] = None,
    ) -> iam.Role:
        """
        Generate an IAM role, for a Lambda service principal (i.e. lambda.amazonaws.com).

        :param self_obj: The CDK stack class object.
        :param function_name: A name for the Lambda function.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param managed_policies: A list of managed policies associated with this role.
        :param custom_policies: A list of custom policies associated with this role.
        :return: The IAM role, for a Lambda service principal.
        """
        return self.iam_role(
            self_obj,
            [function_name],
            self.iam_service_principal(self.LAMBDA_),
            f"Lambda role for {function_name}.",
            project_name_comp=project_name_comp,
            managed_policies=managed_policies,
            custom_policies=custom_policies,
        )

    def iam_service_principal(self, service: str) -> iam.ServicePrincipal:
        """
        Generate an IAM service principal, that represents an AWS service.
        :param service: The service to represent (e.g. 'sns', 'lambda', etc.).
        :return: The IAM service principal.
        """
        return iam.ServicePrincipal(service=self._get_aws_service(service))

    def is_deploy_env_internal(self, deploy_env: str) -> bool:
        return deploy_env in self.DEPLOY_ENVS_INTERNAL

    def is_deploy_env_prod(self, deploy_env: str) -> bool:
        return deploy_env == self.PROD_

    def join_sep_colon(self, props: list[str]) -> str:
        return self.SEP_COLON_.join(props)

    def join_sep_comma(self, props: list[str]) -> str:
        return self.SEP_COMMA_.join(props)

    def join_sep_dot(self, props: list[str]) -> str:
        return self.SEP_DOT_.join(props)

    def join_sep_empty(self, props: list[str]) -> str:
        return self.SEP_EMPTY_.join(props)

    def join_sep_fw(self, props: list[str]) -> str:
        return self.SEP_FW_.join(props)

    def join_sep_score(self, props: list[str]) -> str:
        return self.SEP_SCORE_.join(props)

    def join_sep_space(self, props: list[str]) -> str:
        return self.SEP_SPACE_.join(props)

    def join_sep_under(self, props: list[str]) -> str:
        return self.SEP_UNDER_.join(props)

    def kms_key_encryption(
        self,
        self_obj,
        name_props: list[str],
        description: str,
    ) -> kms.Key:
        """
        Generate a KMS key, for encryption purposes.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param description: A description of the CDK construct.
        :return: The KMS key, for encryption purposes.
        """
        return self._kms_key(
            self_obj,
            name_props + [self.ENCRYPTION_],
            self.join_sep_space([description, self.ENCRYPTION_]),
            enable_key_rotation=True,
        )

    @staticmethod
    def lambda_architecture_x86_64(str_: bool = False) -> Union[lambda_.Architecture, str]:
        """
        Generate a Lambda architecture (for 'x86_64').

        :param str_: True if needing the string representation of the architecture.
        :return: The Lambda architecture.
        """
        return "x86_64" if str_ else lambda_.Architecture.X86_64

    def lambda_docker_image_function(
        self,
        self_obj,
        function_name: str,
        project_repo: ecr.IRepository,
        description: str,
        environment: dict[str, str],
        role: iam.Role,
        environment_encryption: kms.Key = None,
        ephemeral_storage_size: Size = Size.mebibytes(512),
        filesystem: lambda_.FileSystem = None,
        vpc_props: tuple[ec2.Vpc, list[ec2.SecurityGroup], ec2.SubnetType] = None,
        memory_size: int = 128,
        log_group: logs.LogGroup = None,
        timeout: Duration = Duration.seconds(3),
        reserved_concurrent_executions: int = None,
        inc_sns_topic_errors: bool = True,
        events_rules: list[tuple[events.Rule, dict]] = None,
        retry_attempts: int = None,
        async_: bool = False,
        **kwargs,
    ) -> lambda_.Function:
        """
        Generate a Lambda Docker image function.

        :param self_obj: The CDK stack class object.
        :param function_name: A name for the Lambda function.
        :param project_repo: The ECR repository that the Docker image is in.
        :param description: A description of the CDK construct.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda function.
        :param role: Lambda execution role. The role that will be assumed by the Lambda function upon execution.
        :param environment_encryption: The KMS key to use for environment encryption, and optionally
            for DLQ (SQS queue) encryption, if ``async_`` is enabled.
        :param ephemeral_storage_size: The size of the function’s `/tmp` directory in MiB. Default: 512 MiB.
        :param filesystem: An optional filesystem configuration for the Lambda function.
        :param vpc_props: The VPC network to place Lambda network interfaces, a list of security groups to associate
            with the Lambda's network interfaces, and the type of subnets to select.
        :param memory_size: The amount of memory, in MiB, that is allocated to your Lambda function. Lambda uses this
            value to proportionally allocate the amount of CPU power. Default: 128 MiB.
        :param log_group: The log group to associate with the Lambda function.
        :param timeout: The execution time (in seconds) after which Lambda terminates the Lambda function.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function.
            Default: - No specific limit - account limit.
        :param inc_sns_topic_errors: True if to include an SNS topic to send function errors to from the assistive CloudWatch alarms.
        :param events_rules: An optional list of Events rules, each with a payload, to add the function as a target to.
        :param retry_attempts: An optional maximum number of times to retry when the function returns an error.
        :param async_: True if the Lambda function is to be used with asynchronous invocation:
            https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html. Default: False.
        :return: The Lambda Docker image function.
        """
        params_and_secrets_ext: bool = False
        lambda_func: lambda_.Function = lambda_.DockerImageFunction(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [function_name], "DockerImageFunction"),
            code=lambda_.DockerImageCode.from_ecr(
                repository=project_repo,
                # cmd=,  # Default: - use the CMD specified in the docker image or Dockerfile.
                # entrypoint=,  # Default: - use the ENTRYPOINT in the docker image or Dockerfile.
                tag_or_digest=self.get_attr_deploy_env(self_obj),
                # working_directory=,  # Default: - use the WORKDIR in the docker image or Dockerfile.
            ),
            # adot_instrumentation  # AWS Distro for OpenTelemetry (ADOT) instrumentation. Default: - No ADOT instrum.
            **self._lambda_function_kwargs(
                self_obj,
                function_name,
                description,
                environment,
                role,
                environment_encryption,
                ephemeral_storage_size,
                filesystem,
                vpc_props,
                memory_size,
                params_and_secrets_ext,
                log_group,
                timeout,
                reserved_concurrent_executions,
                retry_attempts,
                async_,
                docker_image=True,
            ),
        )
        self._lambda_function_support(
            self_obj,
            lambda_func,
            function_name,
            reserved_concurrent_executions,
            vpc_props[1] if vpc_props else None,
            inc_sns_topic_errors,
            events_rules,
            async_,
            **kwargs,
        )
        return lambda_func

    def lambda_function(
        self,
        self_obj,
        function_name: str,
        code_path: str,
        description: str,
        environment: dict[str, str],
        role: iam.Role,
        environment_encryption: kms.Key = None,
        ephemeral_storage_size: Size = Size.mebibytes(512),
        filesystem: lambda_.FileSystem = None,
        vpc_props: tuple[ec2.Vpc, list[ec2.SecurityGroup], ec2.SubnetType] = None,
        layers: list[lambda_.LayerVersion] = None,
        memory_size: int = 128,
        params_and_secrets_ext: bool = False,
        log_group: logs.LogGroup = None,
        timeout: Duration = Duration.seconds(3),
        reserved_concurrent_executions: int = None,
        inc_sns_topic_errors: bool = True,
        events_rules: list[tuple[events.Rule, dict]] = None,
        retry_attempts: int = None,
        async_: bool = False,
        **kwargs,
    ) -> lambda_.Function:
        """
        Generate a Lambda function.

        :param self_obj: The CDK stack class object.
        :param function_name: A name for the Lambda function.
        :param code_path: The relative system file path to a folder containing the Lambda function source files.
        :param description: A description of the CDK construct.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda function.
        :param role: Lambda execution role. The role that will be assumed by the Lambda function upon execution.
        :param environment_encryption: The KMS key to use for environment encryption, and optionally
            for DLQ encryption, if ``async_`` is enabled.
        :param ephemeral_storage_size: The size of the function’s `/tmp` directory in MiB. Default: 512 MiB.
        :param filesystem: An optional filesystem configuration for the Lambda function.
        :param vpc_props: The VPC network to place Lambda network interfaces, a list of security groups to associate
            with the Lambda's network interfaces, and the type of subnets to select.
        :param layers: A list of layers to add to the Lambda function's execution environment.
        :param memory_size: The amount of memory, in MiB, that is allocated to your Lambda function. Lambda uses this
            value to proportionally allocate the amount of CPU power. Default: 128 MiB.
        :param params_and_secrets_ext: True if the Lambda function is use AWS Parameters and Secrets Extension.
        :param log_group: The log group to associate with the Lambda function.
        :param timeout: The execution time (in seconds) after which Lambda terminates the Lambda function.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function.
            Default: - No specific limit - account limit.
        :param inc_sns_topic_errors: True if to include an SNS topic to send function errors to from the assistive CloudWatch alarms.
        :param events_rules: An optional list of Events rules, each with a payload, to add the function as a target to.
        :param retry_attempts: An optional maximum number of times to retry when the function returns an error.
        :param async_: True if the Lambda function is to be used with asynchronous invocation:
            https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html. Default: False.
        :return: The Lambda function.
        """
        lambda_func: lambda_.Function = lambda_.Function(
            scope=self_obj,
            id=self.get_construct_id(self_obj, [function_name], "Function"),
            code=lambda_.Code.from_asset(path=self.get_path([self.sub_paths[self.LAMBDA_], code_path])),
            handler=self.LAMBDA_HANDLER_PYTHON,
            runtime=self.lambda_runtime_python_3_9(),
            **self._lambda_function_kwargs(
                self_obj,
                function_name,
                description,
                environment,
                role,
                environment_encryption,
                ephemeral_storage_size,
                filesystem,
                vpc_props,
                memory_size,
                params_and_secrets_ext,
                log_group,
                timeout,
                reserved_concurrent_executions,
                retry_attempts,
                async_,
                layers=layers,
            ),
        )
        self._lambda_function_support(
            self_obj,
            lambda_func,
            function_name,
            reserved_concurrent_executions,
            vpc_props[1] if vpc_props else None,
            inc_sns_topic_errors,
            events_rules,
            async_,
            **kwargs,
        )
        return lambda_func

    def lambda_function_add_permission_invoke_by_sns(
        self, self_obj, lambda_func: Union[lambda_.Function, lambda_.DockerImageFunction], function_name: str
    ) -> None:
        lambda_func.add_permission(
            id=self.get_construct_id(self_obj, [function_name], "FunctionPermission"),
            principal=self.iam_service_principal(self.SNS_),
            action=self.join_sep_colon([self.LAMBDA_, "InvokeFunction"]),
            # event_source_token=,  # Default: The caller would not need to present a token.
            # function_url_auth_type=,
            # scope=,  # Default: - The instance of lambda_.IFunction
            source_account=self.get_attr_env_account(self_obj),
            source_arn=self_obj.format_arn(service=self.SNS_, resource=self.SEP_ASTERISK_),
        )

    def lambda_function_cloudwatch(
        self,
        self_obj,
        function_name_base: str,
        code_path_prefix: str = None,
        custom_policies: list[iam.PolicyStatement] = None,
        use_vpc: bool = True,
        security_groups: list[ec2.SecurityGroup] = None,
        vpc_subnets_type: ec2.SubnetType = None,
    ) -> lambda_.Function:
        """
        Generate a Lambda function, for handling Lambda function errors from the assistive CloudWatch alarms.

        :param self_obj: The CDK stack class object.
        :param function_name_base: A base name for the Lambda function.
        :param code_path_prefix: An optional code path prefix, to define a different Lambda function source code.
        :param custom_policies: An optional list of custom policies associated with the Lambda function role.
        :param use_vpc: True if the Lambda function is to access resources in a custom VPC.
        :param security_groups: An optional list of security groups to associate with the Lambda's network interfaces.
        :param vpc_subnets_type: An optional selection all subnets of the given type.
        :return: The Lambda function, for handling Lambda function errors from the assistive CloudWatch alarms.
        """
        cloudwatch_func_name_prefix: str = "CWMsTeamsNotif"
        function_name: str = self.join_sep_empty([cloudwatch_func_name_prefix, function_name_base])[:64]
        vpc_props = None
        if use_vpc and (v := getattr(self_obj, self.VPC_, None)):
            vpc_props = (
                v,
                (
                    security_groups
                    if security_groups
                    else ([sg] if (sg := getattr(self_obj, self.LAMBDA_SG_, None)) else [])
                ),
                vpc_subnets_type if vpc_subnets_type else ec2.SubnetType.PRIVATE_WITH_EGRESS,
            )
        code_path_props: list[str] = [self.CLOUDWATCH_, cloudwatch_func_name_prefix]
        if code_path_prefix:
            code_path_props = [code_path_prefix] + code_path_props
        lambda_func: lambda_.Function = self.lambda_function(
            self_obj,
            function_name,
            self.get_path(code_path_props),
            f"Handles `{function_name_base}` Lambda function errors from the assistive CloudWatch alarms.",
            {"WEBHOOK_URL": self.get_ms_teams_aws_notifications_webhook_url(self_obj, self.WEBHOOK_URL_CLOUDWATCH_)},
            self.iam_role_lambda(
                self_obj,
                function_name,
                managed_policies=self.lambda_managed_policies_vpc_list()
                + [iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="CloudWatchLogsReadOnlyAccess")],
                custom_policies=custom_policies,
            ),
            vpc_props=vpc_props,
            timeout=Duration.seconds(10),
            is_support=True,
            use_vpc=use_vpc,
        )
        self.lambda_function_add_permission_invoke_by_sns(self_obj, lambda_func, function_name)
        return lambda_func

    def lambda_function_events_rules_cron(
        self,
        self_obj,
        function_name: str,
        start_end: str,
        name_props_meta_payload: list[tuple[list[str], dict[str, dict[str, int]], dict]],
    ) -> list[tuple[events.Rule, dict]]:
        """
        Generate a list Events rules, with cron schedules, for a Lambda function.

        :param self_obj: The CDK stack class object.
        :param function_name: A name for the Lambda function.
        :param start_end: Whether each Event rule is for starting/ending. Either ``start`` or ``end``.
        :param name_props_meta_payload: A list of tuples, each tuple containing:
            name_props: Specific property details to include in the CDK construct ID.
            meta: A schedule window metadata object.
            payload: The payload (JSON) object to the event target.
        :return: The list Event rules, for a Lambda function.
        """
        key: str = self.join_sep_under([start_end, self.WEEK_, self.DAYS_])
        return [
            (
                self.events_rule(
                    self_obj,
                    name_props,
                    f"Trigger Lambda function {function_name} on {meta[key]} @ {s.zfill(2)}:00 UTC.",
                    events.Schedule.cron(minute=str(0), hour=s, week_day=meta[key]),
                ),
                payload,
            )
            for name_props, meta, payload in name_props_meta_payload
            if (s := str(meta[start_end]))
        ]

    def lambda_function_events_rules_rate(
        self, self_obj, function_name: str, rate: int, payload: dict = None
    ) -> list[tuple[events.Rule, dict]]:
        """
        Generate a list Events rules, with rate schedules, for a Lambda function.

        :param self_obj: The CDK stack class object.
        :param function_name: A name for the Lambda function.
        :param rate: The rate at which to schedule successive invocations of the function, in minutes.
        :param payload: An optional payload (JSON) object to the event target.
        :return: The list Events rules, for a Lambda function.
        """
        return [
            (
                self.events_rule(
                    self_obj,
                    [function_name],
                    f"Trigger Lambda function {function_name} every {rate} minutes.",
                    events.Schedule.cron(minute=self.get_path([self.SEP_ASTERISK_, rate])),
                ),
                payload if payload else {},
            )
        ]

    def lambda_function_kwargs_params_and_secrets(
        self,
        to_string: bool = False,
        reserved_concurrent_executions: int = None,
    ) -> dict:
        """
        Generate a kwargs dict, for the 'params_and_secrets' arg of a Lambda function.

        :param to_string: True if we want the string representation of the kwargs.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function.
            Default: - No specific limit - account limit.
        :return: The kwargs dict, for the 'params_and_secrets' arg of a Lambda function.
        """
        timeout_: int = 0
        ttl_: int = 300
        timeout_val = timeout_ if to_string else Duration.seconds(timeout_)
        ttl_val = ttl_ if to_string else Duration.seconds(ttl_)
        base = {
            "cache_enabled": True,
            "cache_size": 500,
            "http_port": 2773,
            "log_level": self.INFO_ if to_string else lambda_.ParamsAndSecretsLogLevel.INFO,
            "max_connections": (
                reserved_concurrent_executions
                if reserved_concurrent_executions and (reserved_concurrent_executions >= 1)
                else 3
            ),
        }
        base_no_prefix = {
            "secrets_manager_timeout": timeout_val,
            "secrets_manager_ttl": ttl_val,
        }
        base_ssm_prefix = {
            "parameter_store_timeout": timeout_val,
            "parameter_store_ttl": ttl_val,
        }
        if to_string:
            timeout_: str = self.join_sep_empty([self.SEP_UNDER_, self.TIMEOUT_])
            millis_: str = self.join_sep_empty([self.SEP_UNDER_, self.MILLIS_.upper()])
            ssm__: str = self.join_sep_empty([self.SSM_.upper(), self.SEP_UNDER_])
            base_to_string = {
                self.join_sep_under(["PARAMETERS", "SECRETS", "EXTENSION", k_upper]): v
                for k, v in base.items()
                if (k_upper := k.upper())
            }
            base_no_prefix_to_string = {
                self.join_sep_empty([k_upper, millis_]) if k.endswith(timeout_) else k_upper: v
                for k, v in base_no_prefix.items()
                if (k_upper := k.upper())
            }
            base_ssm_prefix_to_string = {
                self.join_sep_empty([ssm__, k_upper, millis_] if k.endswith(timeout_) else [ssm__, k_upper]): v
                for k, v in base_ssm_prefix.items()
                if (k_upper := k.upper())
            }
            return {
                k: json.dumps(v) if isinstance(v, bool) else str(v)
                for k, v in {**base_to_string, **base_no_prefix_to_string, **base_ssm_prefix_to_string}.items()
            }
        return {**base, **base_no_prefix, **base_ssm_prefix}

    def lambda_function_sns(
        self,
        self_obj,
        function_name_base: str,
        code_path_prefix: str = None,
        custom_policies: list[iam.PolicyStatement] = None,
        use_vpc: bool = True,
        security_groups: list[ec2.SecurityGroup] = None,
        vpc_subnets_type: ec2.SubnetType = None,
    ) -> lambda_.Function:
        """
        Generate a Lambda function, for handling messages published to an assistive SNS topic.

        :param self_obj: The CDK stack class object.
        :param function_name_base: A base name for the Lambda function.
        :param code_path_prefix: An optional code path prefix, to define a different Lambda function source code.
        :param custom_policies: An optional list of custom policies associated with the Lambda function role.
        :param use_vpc: True if the Lambda function is to access resources in a custom VPC.
        :param security_groups: An optional list of security groups to associate with the Lambda's network interfaces.
        :param vpc_subnets_type: An optional selection all subnets of the given type.
        :return: The Lambda function, for handling messages published to an assistive SNS topic.
        """
        sns_func_name_prefix: str = "SNSMsTeamsNotif"
        function_name: str = self.join_sep_empty([sns_func_name_prefix, function_name_base])[:64]
        vpc_props = None
        if use_vpc and (v := getattr(self_obj, self.VPC_, None)):
            vpc_props = (
                v,
                (
                    security_groups
                    if security_groups
                    else ([sg] if (sg := getattr(self_obj, self.LAMBDA_SG_, None)) else [])
                ),
                vpc_subnets_type if vpc_subnets_type else ec2.SubnetType.PRIVATE_WITH_EGRESS,
            )
        code_path_props: list[str] = [self.SNS_, sns_func_name_prefix]
        if code_path_prefix:
            code_path_props = [code_path_prefix] + code_path_props
        lambda_func: lambda_.Function = self.lambda_function(
            self_obj,
            function_name,
            self.get_path(code_path_props),
            f"Handles `{function_name_base}` Lambda function messages published to an assistive SNS topic.",
            {"WEBHOOK_URL": self.get_ms_teams_aws_notifications_webhook_url(self_obj, self.WEBHOOK_URL_SNS_)},
            self.iam_role_lambda(
                self_obj,
                function_name,
                managed_policies=self.lambda_managed_policies_vpc_list(),
                custom_policies=custom_policies,
            ),
            vpc_props=vpc_props,
            timeout=Duration.seconds(10),
            is_support=True,
            use_vpc=use_vpc,
        )
        self.lambda_function_add_permission_invoke_by_sns(self_obj, lambda_func, function_name)
        return lambda_func

    def lambda_function_sns_asg(self, self_obj, **kwargs) -> lambda_.Function:
        """
        Generate a Lambda function, for handling messages published to an assistive SNS topic,
        for an AutoScaling auto-scaling group (ASG).

        :param self_obj: The CDK stack class object.
        :return: The Lambda function, for handling messages published to an assistive SNS topic, for an ASG.
        """
        return self.lambda_function_sns(
            self_obj,
            self.join_sep_empty(
                [
                    i.capitalize()
                    for i in self.get_construct_name_short(self_obj, [self.ASG_, self.SNS_]).split(self.SEP_SCORE_)
                ]
            ),
            **kwargs,
        )

    def lambda_layer_version(
        self, self_obj, name_props: list[str], code_path: str, description: str
    ) -> lambda_.LayerVersion:
        """
        Generate a Lambda layer version.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param code_path: The relative system file path to a folder containing the Lambda layer source files.
        :param description: A description of the CDK construct.
        :return: The Lambda layer version.
        """
        return lambda_.LayerVersion(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "LayerVersion", lambda_layer=True),
            code=lambda_.Code.from_asset(path=self.get_path([self.sub_paths[self.LAMBDA_], code_path])),
            compatible_architectures=[self.lambda_architecture_x86_64()],
            compatible_runtimes=[self.lambda_runtime_python_3_9()],
            description=description,
            layer_version_name=self.join_sep_score(name_props),
            # license=,  # Default: - No license information will be recorded.
            removal_policy=RemovalPolicy.DESTROY,
        )

    def lambda_layer_version_base(self, self_obj, function_name: str) -> lambda_.LayerVersion:
        """
        Generate a Lambda layer version, inc. base resources.

        :param self_obj: The CDK stack class object.
        :param function_name: A name for the Lambda function.
        :return: The Lambda layer version.
        """
        name_props: list[str] = [self.PY_, self.LAYER_]
        return self.lambda_layer_version(
            self_obj,
            [function_name] + name_props,
            self.get_file_name_zip(name_props),
            "Lambda layer that contains: boto3 and botocore py modules.",
        )

    def lambda_layer_version_mysql(self, self_obj, function_name: str) -> lambda_.LayerVersion:
        """
        Generate a Lambda layer version, inc. MySQL.

        :param self_obj: The CDK stack class object.
        :param function_name: A name for the Lambda function.
        :return: The Lambda layer version.
        """
        name_props: list[str] = [self.PY_, self.LAYER_]
        return self.lambda_layer_version(
            self_obj,
            [function_name, self.MYSQL_] + name_props,
            self.join_sep_fw([self.RDS_, self.MYSQL_, self.get_file_name_zip(name_props)]),
            "Lambda layer that contains: mysql py modules.",
        )

    @staticmethod
    def lambda_managed_policies_list() -> list[iam.IManagedPolicy]:
        """
        Generate a list of Lambda service managed policies, needed by an IAM role
        attached to a Lambda function.

        :return: The list of Lambda service managed policies.
        """
        return [
            iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="service-role/AWSLambdaBasicExecutionRole"
            )
        ]

    def lambda_managed_policies_vpc_list(self) -> list[iam.IManagedPolicy]:
        """
        Generate a list of Lambda service managed policies, needed by an IAM role
        attached to a Lambda function with access to a VPC.

        :return: The list of Lambda service managed policies.
        """
        return self.lambda_managed_policies_list() + [
            iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="service-role/AWSLambdaVPCAccessExecutionRole"
            )
        ]

    def lambda_runtime_python_3_9(self, str_: bool = False) -> Union[lambda_.Runtime, str]:
        """
        Generate a Lambda runtime (for 'Python 3.9').

        :param str_: True if needing the string representation of the runtime.
        :return: The Lambda runtime.
        """
        return self.join_sep_empty([self.PYTHON_, self.PYTHON_VERSION]) if str_ else lambda_.Runtime.PYTHON_3_9

    def load_dotenv_vpn(self, self_obj) -> None:
        load_dotenv(
            dotenv_path=self.get_path(
                [
                    self.sub_paths[self.EC2_],
                    self.join_sep_under(self.get_attr_project_name_comp_props(self_obj)),
                    self.join_sep_dot([self.VPN_, self.ENV_]),
                ]
            ),
            verbose=True,
        )

    def logs_log_group(
        self,
        self_obj,
        name_props: list[str],
        log_group_name: str,
        project_name_comp: str = None,
        encryption_key: kms.Key = None,
    ) -> logs.LogGroup:
        """
        Generate a Logs log group.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param log_group_name: The name to give the log group.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param encryption_key: The KMS key to use for encryption.
        :return: The Logs log group.
        """
        return logs.LogGroup(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "LogGroup", project_name_comp=project_name_comp),
            # TODO: (OPTIONAL) Add data_protection_policy to select Logs log groups:
            #  https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_logs/DataProtectionPolicy.html#aws_cdk.aws_logs.DataProtectionPolicy
            # data_protection_policy=logs.DataProtectionPolicy(
            #     identifiers=[
            #         logs.DataIdentifier.ADDRESS,
            #         logs.DataIdentifier.AWSSECRETKEY,
            #         logs.DataIdentifier.BANKACCOUNTNUMBER_GB,
            #         logs.DataIdentifier.CREDITCARDNUMBER,
            #         logs.DataIdentifier.DRIVERSLICENSE_GB,
            #         logs.DataIdentifier.EMAILADDRESS,
            #         logs.DataIdentifier.HEALTHINSURANCECARDNUMBER_EU,
            #         logs.DataIdentifier.IPADDRESS,
            #         logs.DataIdentifier.NHSNUMBER_GB,
            #         logs.DataIdentifier.PASSPORTNUMBER_GB,
            #         logs.DataIdentifier.PHONENUMBER,
            #     ],  # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_logs/DataIdentifier.html#aws_cdk.aws_logs.DataIdentifier
            #     # delivery_stream_name_audit_destination=,  # Default: - no firehose delivery stream audit destination
            #     # description=,  # Default: - ‘cdk generated data protection policy’
            #     # log_group_audit_destination=,  # Default: - no CloudWatch Logs audit destination
            #     # name=,  # Default: - ‘data-protection-policy-cdk’
            #     # s3_bucket_audit_destination=,  # Default: - no S3 bucket audit destination
            # ),
            encryption_key=encryption_key,
            log_group_name=log_group_name,
            removal_policy=RemovalPolicy.DESTROY,
            retention=self.logs_retention_days(self_obj, default=bool(not hasattr(self_obj, self.DEPLOY_ENV_PROD_))),
        )

    def logs_log_group_ecs_task_container(self, self_obj, project_name_comp: str = None, **kwargs) -> logs.LogGroup:
        """
        Generate a Logs log group, for an ECS task container.

        :param self_obj: The CDK stack class object.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :return: The Logs log group, for an ECS task container.
        """
        ecs_task_container_props: list[str] = [self.ECS_, self.TASK_, self.CONTAINER_]
        return self.logs_log_group(
            self_obj,
            ecs_task_container_props,
            self.get_path(
                [
                    self.log_groups[self.ECS_],
                    self.join_sep_score(
                        self.get_attr_project_name_comp_props(self_obj, project_name_comp=project_name_comp)
                        + [self.get_attr_deploy_env(self_obj)]
                    ),
                    self.join_sep_score(ecs_task_container_props),
                ]
            ),
            project_name_comp=project_name_comp,
            **kwargs,
        )

    def logs_retention_days(self, self_obj, default: bool = False) -> logs.RetentionDays:
        """
        Generate a Logs retention days, differs on whether to be used in a production CDK stack.

        :param self_obj: The CDK stack class object.
        :param default: True if to default to the non-production Logs retention days.
        :return: The Logs retention days.
        """
        return (
            logs.RetentionDays.THREE_MONTHS
            if not default and getattr(self_obj, self.DEPLOY_ENV_PROD_)
            else logs.RetentionDays.TWO_WEEKS
        )

    def lookup_ms_teams(self, key: str) -> Union[dict[str, str], str]:
        return getattr(self, self.MS_TEAMS_).get(key)

    def lookup_word_map(self, word: str) -> str:
        return getattr(self, self.WORD_MAP_).get(word)

    def rds_database_instance(
        self,
        self_obj,
        db_name: str,
        allocated_storage: int = 100,
        max_allocated_storage: int = 250,
        engine_version: rds.MysqlEngineVersion = None,
    ) -> rds.DatabaseInstance:
        """
        Generate an RDS database instance.

        :param self_obj: The CDK stack class object.
        :param db_name: A name for the DB instance.
        :param allocated_storage: An optional allocated storage size, specified in gibibytes (GiB). Default: 100
        :param max_allocated_storage: An optional upper limit to which RDS can scale the storage in gibibytes (GiB). Default: 250
        :param engine_version: An optional MySQL engine version.
        :return: The RDS database instance.
        """
        desc_props: list[str] = [self.RDS_.upper(), self.DATABASE_, self.INSTANCE_]
        storage_props: list[str] = [self.STORAGE_]
        performance_insight_props: list[str] = [self.PERFORMANCE_, self.INSIGHT_]
        rds_database_instance_sg: list[ec2.SecurityGroup] = [getattr(self_obj, self.DB_SERVER_SG_)]
        rds_database_instance_: rds.DatabaseInstance = rds.DatabaseInstance(
            scope=self_obj,
            id=self_obj.get_construct_id(self_obj.rds_mysql_props, "DatabaseInstance"),
            credentials=rds.Credentials.from_secret(
                secret=self_obj.db_admin_creds_secret, username=self_obj.db_admin_username
            ),
            storage_encrypted=True,
            storage_encryption_key=self.kms_key_encryption(
                self_obj,
                self_obj.rds_mysql_props + storage_props,
                self.join_sep_space(desc_props + storage_props),
            ),
            engine=self.rds_database_instance_engine(version=engine_version),
            allocated_storage=allocated_storage,
            allow_major_version_upgrade=False,
            database_name=db_name.replace(self.SEP_SCORE_, self.SEP_EMPTY_),
            instance_type=ec2.InstanceType(instance_type_identifier=self_obj.database_meta[self.RDS_INSTANCE_TYPE_]),
            vpc=self.get_attr_vpc(self_obj),
            auto_minor_version_upgrade=True,
            backup_retention=self._rds_database_instance_backup_retention(self_obj),
            ca_certificate=rds.CaCertificate.RDS_CA_RDS2048_G1,
            cloudwatch_logs_exports=[
                self.ERROR_,
                self.GENERAL_,
                self.SLOWQUERY_,
                self.AUDIT_,
            ],  # Export all available MySQL-based logs
            cloudwatch_logs_retention=self.logs_retention_days(self_obj),
            # cloudwatch_logs_retention_role=,  # Default: - a new role is created.
            copy_tags_to_snapshot=True,
            delete_automated_backups=False,
            deletion_protection=True,
            enable_performance_insights=True,
            iam_authentication=False,  # TODO: (NEXT) Address terrascan (aws) policy 'AC_AWS_0053'
            instance_identifier=db_name,
            # iops=,  # Default: - no provisioned iops
            max_allocated_storage=(
                max_allocated_storage if max_allocated_storage > allocated_storage else None
            ),  # Default: - No autoscaling of RDS database instance
            monitoring_interval=Duration.seconds(5) if getattr(self_obj, self.DEPLOY_ENV_PROD_) else None,
            # monitoring_role=,  # Default: - A role is automatically created for you.
            multi_az=getattr(self_obj, self.DEPLOY_ENV_PROD_),
            # parameter_group=,  # Default: - no parameter group
            performance_insight_encryption_key=self.kms_key_encryption(
                self_obj,
                self_obj.rds_mysql_props + performance_insight_props,
                self.join_sep_space(desc_props + performance_insight_props),
            ),
            performance_insight_retention=rds.PerformanceInsightRetention.DEFAULT,
            port=getattr(self_obj, self.DB_PORT_),
            preferred_backup_window=getattr(self_obj, self.SCHEDULE_WINDOW_RDS_DAILY_BACKUP_TIMESTAMP_),
            preferred_maintenance_window=getattr(self_obj, self.SCHEDULE_WINDOW_RDS_WEEKLY_MAINTENANCE_TIMESTAMP_),
            security_groups=rds_database_instance_sg,  # Default: - a new security group is created
            storage_type=rds.StorageType.GP2,
            # subnet_group=,  # Default: - a new subnet group will be created.
            vpc_subnets=ec2.SubnetSelection(one_per_az=True, subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )
        free_storage_space_props: list[str] = [self.FREE_, self.STORAGE_, self.SPACE_]
        self.cloudwatch_alarm(
            self_obj,
            free_storage_space_props,
            rds_database_instance_.metric_free_storage_space(period=Duration.minutes(5), statistic="Minimum"),
            f"Send notifications to SNS for `{db_name}` concerning the 'FreeStorageSpace' metric.",
            cloudwatch.ComparisonOperator.LESS_THAN_OR_EQUAL_TO_THRESHOLD,
            cloudwatch.TreatMissingData.MISSING,
            threshold=int(allocated_storage * 0.1) * (2**30),  # e.g. alarms when 90% database instance storage used
            evaluation_periods=1,
        ).add_alarm_action(
            cloudwatch_actions.SnsAction(
                self.sns_topic(
                    self_obj,
                    free_storage_space_props,
                    subscriptions_=[
                        self.sns_subscriptions_email_subscription(),
                        subscriptions.LambdaSubscription(
                            fn=self.lambda_function_cloudwatch(
                                self_obj,
                                self.join_sep_score(
                                    self.get_attr_project_name_comp_props(self_obj)
                                    + [
                                        self.get_attr_deploy_env(self_obj).replace(self.SEP_UNDER_, self.SEP_SCORE_),
                                    ]
                                    + free_storage_space_props
                                ),
                                code_path_prefix=self.RDS_,
                                security_groups=rds_database_instance_sg,
                            )
                        ),
                    ],
                )
            )
        )
        return rds_database_instance_

    @staticmethod
    def rds_database_instance_engine(version: rds.MysqlEngineVersion = None) -> rds.DatabaseInstanceEngine:
        return rds.DatabaseInstanceEngine.mysql(
            version=version if version else rds.MysqlEngineVersion.VER_8_0_39
        )  # https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MySQL.Concepts.VersionMgmt.html

    def rds_database_secret(
        self,
        self_obj,
        name_props: list[str],
        username: str,
        encryption_key: kms.Key = None,
        exclude_characters: str = None,
        master_secret: secretsmanager.Secret = None,
        rotation_schedule: str = None,
    ) -> rds.DatabaseSecret:
        """
        Generate an RDS database secret.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param username: The username.
        :param encryption_key: An optional KMS key to use for encryption. Defaults to the KMS key for a CDK stack.
        :param exclude_characters: Characters to not include in the generated password.
        :param master_secret: The master secret which will be used to rotate this secret.
        :param rotation_schedule: If set, a rotation schedule should be added to the secret.
        :return: The RDS database secret.
        """
        name_props = list(self_obj.rds_mysql_props + name_props)
        rds_database_secret_: rds.DatabaseSecret = rds.DatabaseSecret(
            scope=self_obj,
            id=self_obj.get_construct_id(name_props, "DatabaseSecret"),
            username=username,
            # dbname=,  # Default: - whatever the secret generates after the attach method is run
            encryption_key=encryption_key if encryption_key else self.get_attr_kms_key_stack(self_obj),
            exclude_characters=exclude_characters,
            master_secret=master_secret,
            replace_on_password_criteria_changes=False,
            secret_name=self.get_construct_name(self_obj, name_props),
        )
        if rotation_schedule:
            func_name_base: str = self.join_sep_score(
                [rotation_schedule.capitalize()]
                + self.get_attr_project_name_comp_props(self_obj)
                + [
                    self.get_attr_deploy_env(self_obj).upper().replace(self.SEP_UNDER_, self.SEP_SCORE_),
                ]
            )
            rds_database_secret_.add_rotation_schedule(
                id=self_obj.get_construct_id(name_props, "RotationSchedule"),
                automatically_after=Duration.days(30),
                hosted_rotation=secretsmanager.HostedRotation.mysql_single_user(
                    exclude_characters=exclude_characters,
                    function_name=self.join_sep_empty([self.ROT_.capitalize(), func_name_base])[:64],
                    security_groups=[getattr(self_obj, self.DB_SERVER_LAMBDA_SG_)],
                    vpc=self.get_attr_vpc(self_obj),
                    vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                ),
                rotate_immediately_on_update=True,
                # rotation_lambda=,  # Default: - either rotation_lambda or hosted_rotation must be specified
            )
        return rds_database_secret_

    def route53_hosted_zone_from_lookup(self, self_obj, domain_name: str) -> route53.HostedZone:
        """
        Lookup a Route53 hosted zone.

        :param self_obj: The CDK stack class object.
        :param domain_name: The domain name of the Route53 hosted zone (e.g. 'example.com').
        :return: The Route53 hosted zone.
        """
        return route53.HostedZone.from_lookup(
            scope=self_obj,
            id=self.get_construct_id(self_obj, domain_name.split(self.SEP_DOT_), "HostedZone"),
            domain_name=domain_name,
        )

    def s3_bucket(
        self,
        self_obj,
        bucket_name_prefix: str,
        bucket_key_enabled: bool = False,
        encryption_key: kms.Key = None,
        event_bridge_enabled: bool = False,
        notifications_handler_role: iam.Role = None,
        lifecycle_rules: bool = False,
        server_access_logs_bucket: bool = False,
        custom_policies: list[iam.PolicyStatement] = None,
    ) -> s3.Bucket:
        """
        Generate a S3 bucket.

        :param self_obj: The CDK stack class object.
        :param bucket_name_prefix: Specific prefix to include in the S3 bucket name.
        :param bucket_key_enabled: True if the S3 bucket should use a KMS key for encryption.
        :param encryption_key: An optional KMS key to use for encryption. If this arg is not set, when `bucket_key_enabled` is True, this method generates a KMS key.
        :param event_bridge_enabled: True if this bucket should send notifications to Amazon EventBridge or not. Default: False
        :param notifications_handler_role: The role to be used by the notifications' handler. Default: - a new role will be created.
        :param lifecycle_rules: True if needing Amazon S3 to manage objects during their lifetime. Default: False
        :param server_access_logs_bucket: True if needing a destination bucket for the server access logs. Default: False
        :param custom_policies: A list of custom policies to associate with the S3 bucket policy.
        :return: The S3 bucket.
        """
        bucket_name: str = self.get_s3_bucket_name(self_obj, bucket_name_prefix)
        if bucket_key_enabled and (encryption_key is None):
            encryption_key = self.get_attr_kms_key_stack(self_obj)

        s3_bucket_: s3.Bucket = s3.Bucket(
            access_control=s3.BucketAccessControl.PRIVATE,
            **{
                **self._s3_bucket_kwargs(
                    self_obj,
                    bucket_name,
                    lifecycle_rules,
                    encryption_key=encryption_key,
                    event_bridge_enabled=event_bridge_enabled,
                    notifications_handler_role=notifications_handler_role,
                ),
                **(
                    {
                        "server_access_logs_bucket": s3.Bucket(
                            **self._s3_bucket_kwargs(
                                self_obj,
                                self.join_sep_score(
                                    [bucket_name_prefix, self.LOGS_, self.get_attr_env_region(self_obj)]
                                ),
                                lifecycle_rules,
                            )
                        ),
                        "server_access_logs_prefix": self.join_sep_empty([self.LOGS_, self.SEP_FW_]),
                    }
                    if server_access_logs_bucket
                    else {}
                ),
            },
        )
        if custom_policies:
            for policy_statement in custom_policies:
                s3_bucket_.add_to_resource_policy(permission=policy_statement)
        return s3_bucket_

    def s3_bucket_lifecycle_rules_delete_objects_days(
        self, self_obj, bucket_name: str, num_of_days: int, prefix: str = None
    ) -> list[s3.LifecycleRule]:
        """
        Generate a list of S3 bucket lifecycle rules, for deleting S3 objects are a number of days.

        :param self_obj: The CDK stack class object.
        :param bucket_name: The S3 bucket name.
        :param num_of_days: The number of days to keep S3 objects.
        :param prefix: An optional S3 object key prefix that identifies one or more objects to which this rule applies. Default: - Rule applies to all objects
        :return: The list of S3 bucket lifecycle rules.
        """
        return [
            s3.LifecycleRule(
                abort_incomplete_multipart_upload_after=Duration.days(num_of_days),
                enabled=True,
                expiration=Duration.days(num_of_days),
                expired_object_delete_marker=False,
                id=self.get_construct_id(
                    self_obj,
                    [bucket_name, self.DELETE_, self.OBJECTS_, str(num_of_days), self.DAYS_],
                    "LifecycleRule",
                ),
                prefix=prefix if prefix else None,  # Default: - Rule applies to all objects
                # tag_filters={},  # Default: - Rule applies to all objects
                # transitions=[],  # Default: - No transition rules
            )
        ]

    def secrets_manager_secret(
        self,
        self_obj,
        name_props: list[str],
        description: str,
        secret_name: str,
        encryption_key: kms.Key = None,
        exclude_punctuation: bool = None,
        exclude_characters: bool = True,
        generate_string_key: str = None,
        secret_string_template: dict = None,
        password_length: int = None,
        secret_string_value: SecretValue = None,
    ) -> secretsmanager.Secret:
        """
        Generate a Secrets Manager secret.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param description: A description of the CDK construct.
        :param secret_name: A name for the secret.
        :param encryption_key: An optional KMS key to use for encryption. Defaults to the KMS key for a CDK stack.
        :param exclude_punctuation: Specifies that the generated password shouldn’t include punctuation characters.
        :param exclude_characters: A string that includes characters that shouldn't be included in the generated password.
        :param generate_string_key: The JSON key name that's used to add the generated password.
        :param secret_string_template: A properly structured JSON string that the generated password can be added to.
        :param password_length: The desired length of the generated password. Default: 32 chars.
        :param secret_string_value: An optional initial value for the secret.
            NOTE: It is **highly* encouraged to leave this field undefined and allow Secrets Manager to create the
            secret value. The secret string – if provided – will be included in the output of the cdk
            as part of synthesis, and will appear in the CloudFormation template in the console.
        :return: The Secrets Manager secret.
        """
        return secretsmanager.Secret(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "Secret"),
            description=description,
            encryption_key=encryption_key if encryption_key else self.get_attr_kms_key_stack(self_obj),
            generate_secret_string=(
                secretsmanager.SecretStringGenerator(
                    exclude_punctuation=exclude_punctuation,
                    secret_string_template=json.dumps(
                        secret_string_template if secret_string_template else {}, default=str
                    ),
                    generate_string_key=generate_string_key if generate_string_key else self.GENERATE_STRING_KEY_,
                    exclude_characters=(
                        (self.SECRET_EXCLUDE_CHARS if exclude_characters else None) if not exclude_punctuation else None
                    ),
                    password_length=password_length,
                )
                if not secret_string_value
                else None
            ),
            removal_policy=RemovalPolicy.DESTROY,
            secret_name=secret_name,
            secret_string_value=secret_string_value if secret_string_value else None,
        )

    def secrets_manager_secret_api_keys_e_commerce(self, self_obj, singleton: bool = False) -> None:
        self._secrets_manager_secret_api_keys(
            self_obj,
            attr_name=self.E_COMMERCE_API_KEY_SECRET_,
            description=self.join_sep_score([i.capitalize() for i in [self.E_, self.COMMERCE_]]),
            singleton=singleton,
        )

    def secrets_manager_secret_api_keys_token(self, self_obj, singleton: bool = False) -> None:
        self._secrets_manager_secret_api_keys(
            self_obj, attr_name=self.TOKEN_KEY_SECRET_, description=self.TOKEN_.capitalize(), singleton=singleton
        )

    def secrets_manager_secret_cf_origin_custom_header(
        self, self_obj, cf_origin_custom_header: str, desc_insert: str = None
    ) -> secretsmanager.Secret:
        name_props: list[str] = [self.CF_, self.ORIGIN_, self.CUSTOM_, self.HEADER_]
        return self.secrets_manager_secret(
            self_obj,
            name_props,
            f"CloudFront origin custom header secret for "
            f"{desc_insert if desc_insert else self.get_attr_word_map_project_name_comp(self_obj)}.",
            self.get_construct_name(self_obj, name_props),
            generate_string_key=cf_origin_custom_header,
            password_length=128,
        )

    def secrets_manager_secret_ecs_container(self, self_obj, secret_suffix: str, attr_name: str = None):
        """
        Import a Secrets Manager secret, for the ECS container.

        :param self_obj: The CDK stack class object.
        :param secret_suffix: The (6-char) suffix of the manually created Secrets Manager secret (e.g. fEnTG8).
        :param attr_name: The name of the CDK stack class object to be set. Default: None.
        """
        if attr_name is None:
            attr_name = self.ECS_CONTAINER_SECRET_
        name_props: list[str] = attr_name.split(self.SEP_UNDER_)
        setattr(
            self_obj,
            attr_name,
            secretsmanager.Secret.from_secret_attributes(
                scope=self_obj,
                id=self.get_construct_id(self_obj, name_props, "ISecret"),
                secret_complete_arn=self.format_arn_custom(
                    self_obj,
                    service=self.SECRETSMANAGER_,
                    resource=self.SECRET_,
                    resource_name=self.get_path(
                        [self.get_attr_project_name_comp(self_obj), self.join_sep_score(name_props + [secret_suffix])]
                    ),
                ),  # Manually created AWS Secrets Manager secret, and replicated across all AWS regions
            ),
        )

    def secrets_manager_secret_secret_keys_secret(self, self_obj, singleton: bool = False) -> None:
        self._secrets_manager_secret_secret_keys(
            self_obj, attr_name=self.SECRET_KEY_SECRET_, description=None, singleton=singleton
        )

    def ses_templates(self, self_obj, project_name: str, template_name_prefix: str) -> dict[str, ses.CfnTemplate]:
        """
        Generate SES (email) templates.

        :param self_obj: The CDK stack class object.
        :param project_name: The project name to use for SES (email) template creation (e.g. "dog").
        :param template_name_prefix: The template name prefix for SES (email) template creation (e.g. "mail-ms-staging/").
        :return: The SES (email) templates.
        """
        email_templates: dict[str, ses.CfnTemplate] = {}
        ses_submodule_path_dir: str = self.get_path([self.sub_paths[self.SES_], project_name])
        if os.path.isdir(ses_submodule_path_dir):
            for filename in os.listdir(ses_submodule_path_dir):
                if os.path.isfile(os.path.join(ses_submodule_path_dir, filename)):
                    filename_no_ext: str = filename.rsplit(sep=self.SEP_DOT_, maxsplit=1)[0]
                    template_name_props: list[str] = [project_name, filename_no_ext]
                    template_name: str = self.join_sep_under(template_name_props)
                    email_templates[template_name] = ses.CfnTemplate(
                        scope=self_obj,
                        id=self.get_construct_id(self_obj, template_name_props, "CfnTemplate"),
                        template=ses.CfnTemplate.TemplateProperty(
                            subject_part=self._file_read(
                                self.get_path(
                                    [
                                        ses_submodule_path_dir,
                                        self.SUBJECT_,
                                        self.join_sep_dot([filename_no_ext, self.TXT_]),
                                    ]
                                )
                            ),
                            html_part=self._file_read(self.get_path([ses_submodule_path_dir, filename])),
                            template_name=self.join_sep_empty([template_name_prefix, template_name]),
                            # TODO: (OPTIONAL) Add email body that is visible to recipients
                            #  whose email clients do not display HTML content.
                            # text_part=,
                        ),
                    )
        return email_templates

    def ses_users(self, self_obj, external: bool = True) -> None:
        """
        Generate SES (email) users.

        :param self_obj: The CDK stack class object.
        :param external: If true, generate a mail user and a mail (support) user, for an external-facing domain name.
        """
        no_reply_: str = self.join_sep_score([self.NO_, self.REPLY_])
        hosted_zone_name: str = getattr(self_obj, self.HOSTED_ZONE_NAME_)
        if external:
            setattr(self_obj, self.MAIL_USER_, self._join_sep_at_sign([no_reply_, hosted_zone_name]))
            setattr(self_obj, self.MAIL_USER_SUPPORT_, self._join_sep_at_sign([self.SUPPORT_, hosted_zone_name]))
        else:
            comp_subdomain = getattr(self_obj, self.COMP_SUBDOMAIN_)
            setattr(
                self_obj,
                self.MAIL_USER_,
                self._join_sep_at_sign([no_reply_, self.join_sep_dot([comp_subdomain, hosted_zone_name])]),
            )
            setattr(
                self_obj,
                self.MAIL_USER_SUPPORT_,
                self._join_sep_at_sign([self.SUPPORT_, self.join_sep_dot([comp_subdomain, hosted_zone_name])]),
            )
        # Publish the project no-reply email address as CloudFormation output, to be used as a mail user.
        CfnOutput(
            scope=self_obj,
            id=self.get_construct_id(
                self_obj,
                [self.MAIL_, self.USER_],
                self.CFN_OUTPUT_TYPE,
                project_name_comp=self.get_attr_project_name(self_obj),
            ),
            description=f"The '{no_reply_}' email address for {getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)}. For example, {no_reply_}@example.com.",
            value=getattr(self_obj, self.MAIL_USER_),
        )

    def set_attrs_client_vpn_endpoint_sg(self, self_obj, client_vpn_endpoint_stack: IConstruct) -> None:
        if hasattr(client_vpn_endpoint_stack, self.CLIENT_VPN_ENDPOINT_PRIVATE_SG_):
            self.set_attrs_from_alt_stack(self_obj, client_vpn_endpoint_stack, self.CLIENT_VPN_ENDPOINT_PRIVATE_SG_)

    def set_attrs_codepipeline_stage_action_names(self, self_obj) -> None:
        for k, v in {
            self.NAME_BUILD_: self.BUILD_,
            self.NAME_DEPLOY_: self.DEPLOY_,
            self.NAME_SOURCE_: self.SOURCE_,
        }.items():
            setattr(self_obj, k, v.capitalize())

    def set_attrs_codestar_connection(self, self_obj, bitbucket_workspace: str = None) -> None:
        if bitbucket_workspace is None:
            bitbucket_workspace = self.BITBUCKET_WORKSPACE_SIH_PROD_DEV
        setattr(self_obj, self.CODESTAR_CONNECTIONS_ARN_, self.CODESTAR_CONNECTION_ARNS[bitbucket_workspace])
        setattr(self_obj, self.CODESTAR_CONNECTIONS_BITBUCKET_WORKSPACE_, bitbucket_workspace)

    def set_attrs_comp_subdomain(self, self_obj, comp_subdomain_custom: str) -> None:
        setattr(
            self_obj,
            self.COMP_SUBDOMAIN_,
            (
                comp_subdomain_custom
                if comp_subdomain_custom
                else (
                    getattr(self_obj, self.COMPONENT_)
                    if getattr(self_obj, self.HOSTED_ZONE_NAME_) != self.infrastructure_domain_name
                    else self.get_attr_project_name(self_obj, no_custom=True)
                )
            ),
        )

    def set_attrs_deploy_env(
        self,
        self_obj,
        base_stack: IConstruct,
        deploy_env: str,
        env_meta: dict,
        allow_24_7_disabling: bool = False,
        deploy_env_24_7_set: set[str] = None,
        deploy_env_weekend_set: set[str] = None,
        is_db_server: bool = False,
        no_subdomain: bool = False,
        custom_subdomain: str = None,
    ) -> None:
        """
        Set all CDK stack class object attributes, related to the 'deploy_env' attribute.

        :param self_obj: The CDK stack class object.
        :param base_stack: The base CDK stack, for the CDK stack class object.
        :param deploy_env: The deployment environment name.
        :param env_meta: The deployment environment metadata.
        :param allow_24_7_disabling: True if allowed to disable 24/7 running.
        :param deploy_env_24_7_set: The set of deployment environment for 24/7 running.
        :param deploy_env_weekend_set: The set of deployment environment for weekend running.
        :param is_db_server: True if the CDK stack class object is for a DB server CDK stack.
        :param no_subdomain: True if the CDK stack class object does not require a 'subdomain' attribute.
        :param custom_subdomain: An optional custom subdomain, to override the subdomain defined in the base CDK stack.
        """
        setattr(self_obj, self.DEPLOY_ENV_, deploy_env)
        if d := self.get_attr_deploy_env(self_obj):
            setattr(
                self_obj, self.DEPLOY_ENV_TYPE_, env_meta[self.TAG_KEY_ENV_TYPE_] if env_meta else None
            )  # Required: for AWS CDK tagging
            is_prod: bool = self.is_deploy_env_prod(d)
            setattr(self_obj, self.DEPLOY_ENV_PROD_, is_prod)
            is_24_7_running: bool = is_prod or (
                (
                    any(i in deploy_env_24_7_set for i in env_meta[self.DEPLOY_ENV_LIST_])
                    if is_db_server
                    else bool(d in deploy_env_24_7_set)
                )
                if deploy_env_24_7_set
                else False
            )
            if allow_24_7_disabling and getattr(base_stack, self.DISABLE_24_7_, None):
                is_24_7_running = False
            setattr(self_obj, self.DEPLOY_ENV_24_7_, is_24_7_running)
            is_not_24_7_running: bool = bool(not is_24_7_running)
            setattr(self_obj, self.DEPLOY_ENV_NOT_24_7_, is_not_24_7_running)
            setattr(
                self_obj,
                self.DEPLOY_ENV_WEEKEND_,
                (
                    (
                        any(i in deploy_env_weekend_set for i in env_meta[self.DEPLOY_ENV_LIST_])
                        if is_db_server
                        else bool(d in deploy_env_weekend_set)
                    )
                    if is_not_24_7_running and deploy_env_weekend_set
                    else False
                ),
            )
            if is_db_server:
                is_internal: bool = bool(env_meta[self.TAG_KEY_ENV_TYPE_] == EnvType.INTERNAL.name)
                setattr(self_obj, self.DEPLOY_ENV_TYPE_INTERNAL_, is_internal)
            else:
                is_internal: bool = self.is_deploy_env_internal(d)
                setattr(self_obj, self.DEPLOY_ENV_INTERNAL_, is_internal)
                setattr(self_obj, self.DEPLOY_ENV_EXTERNAL_, bool(not is_internal))
                preview_demo_meta: dict[str, str] = getattr(base_stack, self.DEPLOY_ENV_PREVIEW_DEMO_META_, None)
                if preview_demo_meta and (dp := preview_demo_meta.get(d)):
                    is_demo: bool = bool(dp[0] == self.DEMO_)
                    is_preview: bool = bool(dp[0] == self.PREVIEW_)
                    setattr(self_obj, self.DEPLOY_ENV_DEMO_, is_demo)
                    setattr(self_obj, self.DEPLOY_ENV_PREVIEW_, is_preview)
                    setattr(self_obj, self.DEPLOY_ENV_PREVIEW_DEMO_, bool(is_demo or is_preview))
                elif is_prod:
                    setattr(self_obj, self.DEPLOY_ENV_PREVIEW_DEMO_, False)
                if not no_subdomain:
                    setattr(
                        self_obj,
                        self.SUBDOMAIN_,
                        self._get_subdomain(
                            self_obj,
                            custom_subdomain if custom_subdomain else getattr(base_stack, self.COMP_SUBDOMAIN_),
                            custom_val=getattr(base_stack, self.PRODUCT_CUSTOM_, None),
                            project_subdomain=bool(
                                getattr(base_stack, self.HOSTED_ZONE_NAME_) == self.infrastructure_domain_name
                            ),
                        ),
                    )

    def set_attrs_deploy_env_preview_demo_meta(self, self_obj, deploy_env_preview_demo_meta: dict[str, str]) -> None:
        setattr(
            self_obj,
            self.DEPLOY_ENV_PREVIEW_DEMO_META_,
            (
                {k: (v, self.lookup_word_map(k)) for k, v in deploy_env_preview_demo_meta.items()}
                if deploy_env_preview_demo_meta
                else None
            ),
        )

    def set_attrs_disable_24_7_(self, self_obj, disable_24_7_: bool) -> None:
        setattr(self_obj, self.DISABLE_24_7_, disable_24_7_)

    def set_attrs_elastic_ips_meta(
        self, self_obj, elastic_ip_parameter_names: dict[str, str], inc_cfn_output: bool = True
    ) -> None:
        setattr(
            self_obj,
            self.ELASTIC_IP_META_,
            self._ec2_elastic_ips_meta(self_obj, elastic_ip_parameter_names, inc_cfn_output),
        )

    @staticmethod
    def set_attrs_from_alt_stack(self_obj, alt_stack: IConstruct, attr_name: str, new_attr_name: str = None) -> None:
        setattr(self_obj, new_attr_name if new_attr_name else attr_name, getattr(alt_stack, attr_name))

    def set_attrs_hosted_zone(
        self,
        self_obj,
        domain_name: str = None,
        hosted_zone: str = None,
        inc_comp_subdomain: bool = True,
        comp_subdomain_custom: str = None,
    ) -> None:
        is_infrastructure: bool = False
        if domain_name is None:
            domain_name = self.infrastructure_domain_name
            is_infrastructure = True
        setattr(self_obj, self.HOSTED_ZONE_NAME_, domain_name)
        setattr(
            self_obj,
            self.HOSTED_ZONE_,
            (
                self.route53_hosted_zone_from_lookup(self_obj, domain_name)
                if is_infrastructure
                else (hosted_zone if hosted_zone else self._route53_hosted_zone(self_obj))
            ),
        )
        if inc_comp_subdomain:
            self.set_attrs_comp_subdomain(self_obj, comp_subdomain_custom)

    def set_attrs_kms_key_stack(
        self, self_obj, alt_stack: IConstruct = None, no_trim: bool = False, existing_key: kms.Key = None
    ) -> None:
        """
        Generate a KMS key for a CDK stack.

        :param self_obj: The CDK stack class object.
        :param alt_stack: An optional alternative CDK stack, for the CDK stack class object.
        :param no_trim: True if name length doesn't need to be <=64 chars.
        :param existing_key: An optional KMS key, which already exists.
        """
        setattr(
            self_obj,
            self.KMS_KEY_STACK_,
            (
                existing_key
                if existing_key
                else (
                    self.get_attr_kms_key_stack(alt_stack)
                    if alt_stack
                    else self._kms_key(
                        self_obj,
                        [],
                        self_obj.stack_name,
                        no_trim=no_trim,
                        enable_key_rotation=True,
                    )
                )
            ),
        )

    def set_attrs_ports_default(self, self_obj, alb_port: int = None) -> None:
        setattr(self_obj, self.DB_PORT_, self._DB_PORT)
        setattr(self_obj, self.REDIS_PORT_, self._REDIS_PORT)
        if alb_port is not None:
            setattr(self_obj, self.ALB_PORT_, alb_port)

    def set_attrs_project_name_comp(
        self, self_obj, project_name: str, component: str, is_custom: bool = False, inc_cfn_output: bool = False
    ) -> None:
        props: list[str] = [project_name]
        if is_custom:
            setattr(self_obj, self.PROJECT_NAME_BASE_, project_name)
            setattr(self_obj, self.PROJECT_NAME_COMP_BASE_, self.join_sep_score(props + [component]))
            props.append(self.CUSTOM_)
        elif custom_val := getattr(self_obj, self.PRODUCT_CUSTOM_, None):
            setattr(self_obj, self.PROJECT_NAME_BASE_, project_name)
            setattr(self_obj, self.PROJECT_NAME_COMP_BASE_, self.join_sep_score(props + [component]))
            props.append(custom_val)
        setattr(self_obj, self.PROJECT_NAME_, self.join_sep_score(props))
        setattr(self_obj, self.COMPONENT_, component)
        setattr(self_obj, self.PROJECT_NAME_COMP_, self.join_sep_score(props + [component]))
        self._set_attrs_word_map_project_name_comp(self_obj, project_name, component, is_custom=is_custom)
        if inc_cfn_output:
            self._cfn_output_project_name_comp(self_obj)

    def set_attrs_route53_record_cloudfront_distribution(
        self,
        self_obj,
        cf_dist: cloudfront.Distribution,
        hosted_zone: route53.IHostedZone,
        record_name: str,
        enable_ipv6: bool = False,
    ) -> None:
        word_map_project_name_comp: str = self.get_attr_word_map_project_name_comp(self_obj)
        setattr(
            self_obj,
            self.ROUTE_53_A_RECORD_,
            self._route53_a_record_cloudfront_distribution(
                self_obj,
                cf_dist,
                hosted_zone,
                f"An A-Record for {word_map_project_name_comp}, pointing to CloudFront distribution.",
                record_name,
            ),
        )
        if enable_ipv6:
            setattr(
                self_obj,
                self.ROUTE_53_AAAA_RECORD_,
                self._route53_aaaa_record_cloudfront_distribution(
                    self_obj,
                    cf_dist,
                    hosted_zone,
                    f"An AAAA-Record for {word_map_project_name_comp}, pointing to CloudFront distribution.",
                    record_name,
                ),
            )

    def set_attrs_schedule_windows(self, self_obj, key: str) -> None:
        is_weekend: bool = getattr(self_obj, self.DEPLOY_ENV_WEEKEND_, False)
        if key == self.RDS_:
            setattr(
                self_obj,
                self.SCHEDULE_WINDOW_RDS_DAILY_BACKUP_TIMESTAMP_,
                (
                    self.schedules.window_rds_mysql_daily_backup_all_days_timestamp
                    if is_weekend
                    else self.schedules.window_rds_mysql_daily_backup_week_days_timestamp
                ),
            )
            setattr(
                self_obj,
                self.SCHEDULE_WINDOW_RDS_WEEKLY_MAINTENANCE_TIMESTAMP_,
                self.schedules.window_rds_mysql_weekly_maintenance_timestamp,
            )
        elif key == self.ELASTICACHE_:
            setattr(self_obj, self.SCHEDULE_WINDOW_ELASTICACHE_ALL_DAYS_, self.schedules.window_ec_rds_all_days)
            setattr(self_obj, self.SCHEDULE_WINDOW_ELASTICACHE_WEEK_DAYS_, self.schedules.window_ec_rds_week_days)
            setattr(
                self_obj,
                self.SCHEDULE_WINDOW_ELASTICACHE_WEEKEND_,
                self.schedules.window_ec_rds_weekend if is_weekend else None,
            )
            setattr(
                self_obj,
                self.SCHEDULE_WINDOW_ELASTICACHE_WEEKLY_MAINTENANCE_TIMESTAMP_,
                self.schedules.window_ec_redis_weekly_maintenance_timestamp,
            )
        elif key == self.ECS_:
            setattr(
                self_obj,
                self.SCHEDULE_WINDOW_ECS_,
                self.schedules.window_ec2_ecs_all_days if is_weekend else self.schedules.window_ec2_ecs_week_days,
            )

    def set_attrs_url(self, self_obj, origin_path: str) -> None:
        setattr(self_obj, self.URL_, self._generate_url(self_obj, origin_path))

    def set_attrs_url_private(self, self_obj, origin_path: str) -> None:
        self._set_attrs_ecs_service_cloud_map_service_name(self_obj)
        setattr(
            self_obj,
            self.URL_PRIVATE_,
            self._generate_url_private(self_obj, origin_path),
        )

    def set_factory_ms_teams(self, ms_teams: dict) -> None:
        setattr(self, self.MS_TEAMS_, ms_teams)

    def set_factory_nat_gateway_ip_ranges_parameter_name(self, stack_name: str) -> None:
        # NAT Gateway Public IPs
        #  (NB. parameter created in AWS Systems Manager Parameter Store using:
        #  https://bitbucket.org/foobar-products-development/aws-scripts/src/main/aws-nat-gateway/aws-nat-gateway-public-ips.sh)
        setattr(
            self,
            self.VPC_NAT_GATEWAY_IP_RANGES_PARAMETER_NAME_,
            self.get_path([stack_name, self.join_sep_score([self.NGW_, self.PUBLIC_, self.IPS_])], lead=True),
        )

    def set_factory_pipeline_event_lambda_function_arn(self, lambda_function_arn: str) -> None:
        setattr(self, self.PIPELINE_EVENT_LAMBDA_FUNCTION_ARN_, lambda_function_arn)

    def set_factory_word_map(self, word_map: dict[str, str]) -> None:
        setattr(self, self.WORD_MAP_, word_map)

    def sns_subscriptions_email_subscription(self, recipient: str = None) -> subscriptions.EmailSubscription:
        """
        Generate an SNS subscriptions email subscription.

        :param recipient: The email address of the intended recipient.
        :return: The SNS subscriptions email subscription.
        """
        return subscriptions.EmailSubscription(
            email_address=recipient if recipient else self.email_notification_recipient, json=False
        )

    def sns_subscriptions_lambda_function(
        self, self_obj, name_props: list[str], function_arn: str
    ) -> subscriptions.LambdaSubscription:
        """
        Generate an SNS subscriptions lambda subscription.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param function_arn: The Lambda function ARN.
        :return: The SNS subscriptions lambda subscription.
        """
        return subscriptions.LambdaSubscription(
            fn=lambda_.Function.from_function_attributes(
                scope=self_obj,
                id=self.get_construct_id(
                    self_obj, name_props + [self.SNS_, self.SUBSCRIPTIONS_, self.LAMBDA_], "IFunction"
                ),
                function_arn=function_arn,
                same_environment=True,
                skip_permissions=True,
            )
        )

    def sns_topic(
        self,
        self_obj,
        name_props: list[str],
        project_name_comp: str = None,
        master_key: kms.Key = None,
        subscriptions_: list = None,
    ) -> sns.Topic:
        """
        Generate an SNS topic.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param master_key: The KMS customer-managed key (CMK) to use for encryption.
        :param subscriptions_: An optional list of subscriptions to add to the generated SNS topic.
        :return: The SNS topic.
        """
        topic: sns.Topic = sns.Topic(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "Topic", project_name_comp=project_name_comp),
            display_name=self.get_construct_name(
                self_obj, name_props, project_name_comp=project_name_comp, underscore=True
            ),
            master_key=master_key,
            topic_name=self.get_construct_name(
                self_obj, name_props, project_name_comp=project_name_comp, underscore=True
            ),
        )
        if subscriptions_:
            for i in subscriptions_:
                topic.add_subscription(i)
        return topic

    def sns_topic_codestar_notifications_sns(self, self_obj, p: str) -> sns.Topic:
        name_props: list[str] = [self.CODESTAR_, self.NOTIFICATIONS_, self.SNS_]
        return self.sns_topic(
            self_obj,
            name_props,
            project_name_comp=p,
            subscriptions_=[
                self.sns_subscriptions_lambda_function(
                    self_obj,
                    [p] + name_props,
                    self._get_factory_pipeline_event_lambda_function_arn(),
                )
            ],
        )

    def sqs_queue(
        self,
        self_obj,
        name_props: list[str],
        queue_name: str,
        encryption_master_key: kms.Key = None,
        fifo: bool = False,
        content_based_deduplication: bool = False,
        dead_letter_queue: sqs.DeadLetterQueue = None,
        deduplication_scope: sqs.DeduplicationScope = None,
        delivery_delay: Duration = None,
        max_message_size_bytes: int = None,
        receive_message_wait_time: Duration = None,
        retention_period: Duration = None,
        visibility_timeout: Duration = None,
    ) -> sqs.Queue:
        """
        Generate an SQS queue.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param queue_name: A name for the SQS queue.
        :param encryption_master_key: The KMS key to use for queue encryption.
        :param fifo: True if this a first-in-first-out (FIFO) queue. Default: False.
        :param content_based_deduplication: True if this FIFO queue, is to have
            content-based deduplication enabled. Default: False.
        :param dead_letter_queue: Send messages to this SQS queue if they were unsuccessfully dequeued
            a number of times. Default: no dead-letter queue.
        :param deduplication_scope: For high throughput for FIFO queues, specifies whether message deduplication occurs
            at the message group or queue level. Default: sqs.DeduplicationScope.QUEUE if FIFO queue.
        :param delivery_delay: The time in seconds that the delivery of all messages
            in the queue is delayed. Max: 900 seconds (15 minutes). Default: 0 seconds.
        :param max_message_size_bytes: The limit of how many bytes that a message can contain
            before SQS rejects it. Valid: 1024 bytes (1 KiB) - 262144 bytes (256 KiB). Default: 262144 (256 KiB).
        :param receive_message_wait_time: Default wait time for ReceiveMessage calls. Max: 20 seconds. Default: 0 seconds.
        :param retention_period: The number of seconds that SQS retains a message. Default: 4 days.
        :param visibility_timeout: Timeout of processing a single message.
            Valid: 0 to 43200 seconds (12 hours). Default: 0 seconds.
        :return: The SQS queue.
        """
        # TODO: (OPTIONAL) Since this method is not currently in use, could be removed
        return sqs.Queue(
            scope=self_obj,
            id=self.get_construct_id(self_obj, name_props, "Queue"),
            content_based_deduplication=bool(fifo and content_based_deduplication),
            data_key_reuse=Duration.minutes(5),
            dead_letter_queue=dead_letter_queue if dead_letter_queue else None,
            deduplication_scope=(
                (deduplication_scope if deduplication_scope else sqs.DeduplicationScope.QUEUE) if fifo else None
            ),
            delivery_delay=delivery_delay if delivery_delay else Duration.seconds(0),
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=encryption_master_key,
            fifo=fifo,
            fifo_throughput_limit=sqs.FifoThroughputLimit.PER_QUEUE if fifo else None,
            max_message_size_bytes=max_message_size_bytes if max_message_size_bytes else 262144,
            queue_name=queue_name,
            receive_message_wait_time=receive_message_wait_time if receive_message_wait_time else Duration.seconds(0),
            removal_policy=RemovalPolicy.DESTROY,
            retention_period=retention_period if retention_period else Duration.days(4),
            visibility_timeout=visibility_timeout if visibility_timeout else Duration.seconds(30),
        )

    def ssm_string_list_parameter(
        self,
        self_obj,
        name_props: list[str],
        description: str,
        parameter_name: str,
        string_list_value: str,
        project_name_comp: str = None,
        deploy_env: str = None,
        tier: ssm.ParameterTier = None,
    ) -> ssm.StringListParameter:
        """
        Generate a Systems Manager (SSM) string list parameter.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param description: A description of the CDK construct.
        :param parameter_name: The name of the parameter.
        :param string_list_value: The value of the parameter.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param deploy_env: An optional deployment env name to use instead of the CDK stack class default.
        :param tier: The tier of the string list parameter.
        :return: The Systems Manager (SSM) string list parameter.
        """
        return ssm.StringListParameter(
            scope=self_obj,
            id=self.get_construct_id(
                self_obj, name_props, "StringListParameter", project_name_comp=project_name_comp, deploy_env=deploy_env
            ),
            string_list_value=string_list_value,
            # allowed_pattern=,  # A regular expression used to validate the parameter value.
            description=description,
            parameter_name=parameter_name,
            simple_name=False,
            tier=tier,
        )

    def ssm_string_parameter(
        self,
        self_obj,
        name_props: list[str],
        description: str,
        parameter_name: str,
        string_value: str,
        project_name_comp: str = None,
        deploy_env: str = None,
        data_type: ssm.ParameterDataType = None,
        tier: ssm.ParameterTier = None,
    ) -> ssm.StringParameter:
        """
        Generate a Systems Manager (SSM) string parameter.

        :param self_obj: The CDK stack class object.
        :param name_props: Specific property details to include in the CDK construct ID.
        :param description: A description of the CDK construct.
        :param parameter_name: The name of the parameter.
        :param string_value: The value of the parameter.
        :param project_name_comp: An optional project name and component to use instead of the CDK stack class default.
        :param deploy_env: An optional deployment env name to use instead of the CDK stack class default.
        :param data_type: The data type of the parameter, such as ``text`` or ``aws:ec2:image``.
        :param tier: The tier of the string parameter.
        :return: The Systems Manager (SSM) string parameter.
        """
        return ssm.StringParameter(
            scope=self_obj,
            id=self.get_construct_id(
                self_obj, name_props, "StringParameter", project_name_comp=project_name_comp, deploy_env=deploy_env
            ),
            string_value=string_value,
            data_type=data_type,
            # allowed_pattern=,  # A regular expression used to validate the parameter value.
            description=description,
            parameter_name=parameter_name,
            simple_name=False,
            tier=tier,
        )

    def ssm_string_parameter_ecs_container_env_firebase_account_info(self, self_obj) -> ssm.StringParameter:
        """
        Generate a Systems Manager (SSM) string parameter, for an ECS container environment variable,
          concerning Firebase account info.

        :param self_obj: The CDK stack class object.
        :return: The Systems Manager (SSM) string parameter.
        """
        return self._ssm_string_parameter_ecs_container_env(self_obj, [self.FIREBASE_, self.ACCOUNT_, self.INFO_])

    def ssm_string_parameter_version_meta(self, self_obj) -> ssm.StringParameter:
        """
        Generate a Systems Manager (SSM) string parameter, for version meta.

        :param self_obj: The CDK stack class object.
        :return: The Systems Manager (SSM) string parameter.
        """
        version_meta_props: list[str] = [self.VERSION_, self.META_]
        version_meta_param_name = self.get_path(
            [self.get_attr_project_name_comp(self_obj)] + version_meta_props,
            lead=True,
        )
        setattr(self_obj, self.VERSION_META_PARAM_NAME_, version_meta_param_name)
        return ssm.StringParameter.from_string_parameter_name(
            scope=self_obj,
            id=self.get_construct_id(self_obj, version_meta_props, "IStringParameter"),
            string_parameter_name=version_meta_param_name,
        )

    def ssm_string_parameter_webhook_url(self, self_obj) -> ssm.StringParameter:
        """
        Generate a Systems Manager (SSM) string parameter, for an MS Teams (CI/CD) Webhook URL.

        :param self_obj: The CDK stack class object.
        :return: The Systems Manager (SSM) string parameter.
        """
        project_name: str = self.get_attr_project_name(self_obj, no_custom=True)
        return self.ssm_string_parameter(
            self_obj,
            [self.WEBHOOK_, self.URL_],
            f"MS Teams Webhook URL for {getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)} CI-CD channel.",
            self.get_path([self.MS_TEAMS_, project_name, self.WEBHOOK_URL_], lead=True),
            self._get_ms_teams_codepipeline_webhook_url(self_obj),
            project_name_comp=project_name,
            data_type=ssm.ParameterDataType.TEXT,
            tier=ssm.ParameterTier.STANDARD,
        )

    def stepfunctions_choice_failed_succeeded(
        self,
        self_obj,
        choice_comment: str,
        lambda_invoke_last_lambda_func: lambda_.Function,
        lambda_invoke_last_comment: str,
        lambda_invoke_last: stepfunctions_tasks.LambdaInvoke,
        adjective_past: str,
        continue_: stepfunctions.IChainable = None,
        wait_duration: int = 30,
    ) -> stepfunctions.Choice:
        wait_comment: str = f"Wait {str(wait_duration)} Seconds, retry {lambda_invoke_last_comment}"
        return (
            stepfunctions.Choice(
                scope=self_obj,
                id=self.get_construct_id(self_obj, [lambda_invoke_last_lambda_func.function_name], "Choice"),
                comment=choice_comment,
                # input_path="$",  # Default: $
                # output_path="$",  # Default: $
            )
            .when(
                condition=self.stepfunctions_condition_string_equals(self.STATUS_FAILED_),
                next=(
                    stepfunctions.Wait(
                        scope=self_obj,
                        id=self.get_construct_id(self_obj, [lambda_invoke_last_lambda_func.function_name], "Wait"),
                        time=stepfunctions.WaitTime.duration(Duration.seconds(wait_duration)),
                        comment=wait_comment,
                    ).next(next=lambda_invoke_last)
                    if continue_
                    else self.stepfunctions_fail(self_obj, lambda_invoke_last_lambda_func, adjective_past, end=True)
                ),
            )
            .when(
                condition=self.stepfunctions_condition_string_equals(self.STATUS_SUCCEEDED_),
                next=(
                    continue_
                    if continue_
                    else stepfunctions.Succeed(
                        scope=self_obj,
                        id=self.get_construct_id(self_obj, [self_obj.step_func_state_machine_name], "Succeeded"),
                        comment=f"Successfully {adjective_past} the latest {getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)} Sat Data.\n"
                        f"See Lambda function logs: {lambda_invoke_last_lambda_func.log_group.log_group_arn}",
                        # input_path="$",  # Default: $
                        # output_path="$",  # Default: $
                    )
                ),
            )
            .otherwise(def_=self.stepfunctions_fail(self_obj, lambda_invoke_last_lambda_func, adjective_past))
        )

    def stepfunctions_condition_string_equals(self, value: str) -> stepfunctions.Condition:
        return stepfunctions.Condition.string_equals(variable=self.join_sep_dot(["$", self.STATUS_]), value=value)

    def stepfunctions_fail(
        self, self_obj, lambda_func: lambda_.Function, adjective_current: str, end: bool = False
    ) -> stepfunctions.Fail:
        cause_msg_prefix: str = (
            f"Invalid '{self.STATUS_}'" if not end else f"The '{self.STATUS_} == {self.STATUS_FAILED_}' found"
        )
        error_msg_suffix: str = f": '{lambda_func.function_name}'." if not end else ", exiting Step Function ..."
        return stepfunctions.Fail(
            scope=self_obj,
            id=self.get_construct_id(
                self_obj, [self_obj.step_func_state_machine_name if end else lambda_func.function_name], "Fail"
            ),
            cause=f"{cause_msg_prefix} in response from: '{lambda_func.function_name}'.",
            comment=f"Check Lambda function logs: {lambda_func.log_group.log_group_arn}.",
            error=f"Failed to {adjective_current} the latest {getattr(self_obj, self.WORD_MAP_PROJECT_NAME_)} Sat Data{error_msg_suffix}",
        )
