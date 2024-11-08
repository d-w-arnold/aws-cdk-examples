#!/usr/bin/env python3.9
import os
import sys
from typing import Union

import aws_cdk as cdk
from constructs import IConstruct

from cdk_sih.bastion_host.linux import CdkBastionHostLinuxStack
from cdk_sih.bird.base import CdkBirdBaseStack
from cdk_sih.bird.cache import CdkBirdCacheStack
from cdk_sih.bird.cloudfront.base import CdkBirdCloudFrontBaseStack
from cdk_sih.bird.cloudfront.main import CdkBirdCloudFrontStack
from cdk_sih.bird.database import CdkBirdDatabaseStack
from cdk_sih.bird.gw import CdkBirdGwStack
from cdk_sih.bird.notif import CdkBirdNotifStack
from cdk_sih.bird.pipeline import CdkBirdPipelineStack
from cdk_sih.bird.storage import CdkBirdStorageStack
from cdk_sih.cat.base import CdkCatBaseStack
from cdk_sih.cat.cache import CdkCatCacheStack
from cdk_sih.cat.cloudfront.base import CdkCatCloudFrontBaseStack
from cdk_sih.cat.cloudfront.main import CdkCatCloudFrontStack
from cdk_sih.cat.database import CdkCatDatabaseStack
from cdk_sih.cat.gw import CdkCatGwStack
from cdk_sih.cat.notif import CdkCatNotifStack
from cdk_sih.cat.pipeline import CdkCatPipelineStack
from cdk_sih.cat.storage import CdkCatStorageStack
from cdk_sih.ci_cd.amplify import CdkAmplifyCiCdStack
from cdk_sih.ci_cd.codepipeline import CdkCodepipelineCiCdStack
from cdk_sih.client_vpn.endpoint import CdkClientVpnEndpointStack
from cdk_sih.cloudtrail.trails import CdkCloudTrailTrailsStack
from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.cow.base import CdkCowBaseStack
from cdk_sih.cow.cache import CdkCowCacheStack
from cdk_sih.cow.cloudfront.base import CdkCowCloudFrontBaseStack
from cdk_sih.cow.cloudfront.main import CdkCowCloudFrontStack
from cdk_sih.cow.database import CdkCowDatabaseStack
from cdk_sih.cow.gw import CdkCowGwStack
from cdk_sih.cow.pipeline import CdkCowPipelineStack
from cdk_sih.dog.base import CdkDogBaseStack
from cdk_sih.dog.cache import CdkDogCacheStack
from cdk_sih.dog.cloudfront.base import CdkDogCloudFrontBaseStack
from cdk_sih.dog.cloudfront.main import CdkDogCloudFrontStack
from cdk_sih.dog.database import CdkDogDatabaseStack
from cdk_sih.dog.em.fs import CdkDogFsStack
from cdk_sih.dog.em.main import CdkDogEmStack
from cdk_sih.dog.gw import CdkDogGwStack
from cdk_sih.dog.notif import CdkDogNotifStack
from cdk_sih.dog.pipeline import CdkDogPipelineStack
from cdk_sih.dog.spain.base import CdkDogSpainBaseStack
from cdk_sih.dog.storage import CdkDogStorageStack
from cdk_sih.elastic_ips import CdkElasticIpsStack
from cdk_sih.fish.base import CdkFishBaseStack
from cdk_sih.fish.cache import CdkFishCacheStack
from cdk_sih.fish.cloudfront.base import CdkFishCloudFrontBaseStack
from cdk_sih.fish.cloudfront.main import CdkFishCloudFrontStack
from cdk_sih.fish.database import CdkFishDatabaseStack
from cdk_sih.fish.gw import CdkFishGwStack
from cdk_sih.fish.pipeline import CdkFishPipelineStack
from cdk_sih.fish.storage import CdkFishStorageStack
from cdk_sih.internal_domain.bkg.base import CdkBkgBaseStack
from cdk_sih.internal_domain.bkg.broker import CdkBkgBrokerStack
from cdk_sih.internal_domain.bkg.broker_web import CdkBkgMqStack
from cdk_sih.internal_domain.bkg.cache import CdkBkgCacheStack
from cdk_sih.internal_domain.bkg.cloudfront.base import CdkBkgCloudFrontBaseStack
from cdk_sih.internal_domain.bkg.cloudfront.main import CdkBkgCloudFrontStack
from cdk_sih.internal_domain.bkg.database import CdkBkgDatabaseStack
from cdk_sih.internal_domain.bkg.ms import CdkBkgMsStack
from cdk_sih.internal_domain.bkg.pipeline import CdkBkgPipelineStack
from cdk_sih.internal_domain.bkg.storage import CdkBkgStorageStack
from cdk_sih.internal_domain.cdn.assets import CdkCdnAssetsStack
from cdk_sih.internal_domain.cdn.base import CdkCdnBaseStack
from cdk_sih.internal_domain.cdn.cloudfront.base import CdkCdnCloudFrontBaseStack
from cdk_sih.internal_domain.cdn.cloudfront.main import CdkCdnCloudFrontStack
from cdk_sih.internal_domain.cdn.storage import CdkCdnStorageStack
from cdk_sih.internal_domain.lion.base import CdkLionBaseStack
from cdk_sih.internal_domain.lion.cache import CdkLionCacheStack
from cdk_sih.internal_domain.lion.cloudfront.base import CdkLionCloudFrontBaseStack
from cdk_sih.internal_domain.lion.cloudfront.main import CdkLionCloudFrontStack
from cdk_sih.internal_domain.lion.collector import CdkLionCollectorStack
from cdk_sih.internal_domain.lion.events import CdkLionEventsStack
from cdk_sih.internal_domain.lion.extractor import CdkLionExtractorStack
from cdk_sih.internal_domain.lion.ms import CdkLionMsStack
from cdk_sih.internal_domain.lion.pipeline import CdkLionPipelineStack
from cdk_sih.internal_domain.lion.processor import CdkLionProcessorStack
from cdk_sih.internal_domain.lion.storage import CdkLionStorageStack
from cdk_sih.internal_domain.openvpn_vpn.base import CdkOpenvpnVpnBaseStack
from cdk_sih.internal_domain.openvpn_vpn.cloudfront import CdkOpenvpnVpnCloudFrontStack
from cdk_sih.internal_domain.openvpn_vpn.server import CdkOpenvpnVpnServerStack
from cdk_sih.internal_domain.openvpn_vpn.user import CdkOpenvpnVpnUserStack
from cdk_sih.internal_domain.pypi.base import CdkPypiBaseStack
from cdk_sih.internal_domain.pypi.cloudfront import CdkPypiCloudFrontStack
from cdk_sih.internal_domain.pypi.package.base import CdkPypiPackageBaseStack
from cdk_sih.internal_domain.pypi.package.pipeline import CdkPypiPackagePipelineStack
from cdk_sih.internal_domain.pypi.server import CdkPypiServerStack
from cdk_sih.internal_domain.pypi.storage import CdkPypiStorageStack
from cdk_sih.ipsec_vpn.base import CdkIpsecVpnBaseStack
from cdk_sih.ipsec_vpn.psk import CdkIpsecVpnPskStack
from cdk_sih.ipsec_vpn.server import CdkIpsecVpnServerStack
from cdk_sih.lambda_instance_auto.ec2 import CdkLambdaEc2InstanceAutoStack
from cdk_sih.lambda_instance_auto.rds import CdkLambdaRdsInstanceAutoStack
from cdk_sih.mail.base import CdkMailBaseStack
from cdk_sih.mail.ms import CdkMailMsStack
from cdk_sih.metoffice.storage import CdkMetofficeStorageStack
from cdk_sih.pdf.base import CdkPdfBaseStack
from cdk_sih.pdf.ms import CdkPdfMsStack
from cdk_sih.proxy.server import CdkProxyServerStack
from cdk_sih.vpc_sih import CdkVpcSihStack
from cdk_sih.weatherapi.storage import CdkWeatherapiStorageStack

# CDK app environment
account: str = os.getenv("CDK_DEPLOY_ACCOUNT", default=os.environ["CDK_DEFAULT_ACCOUNT"])
region: str = os.getenv("CDK_DEPLOY_REGION", default=os.environ["CDK_DEFAULT_REGION"])
env = cdk.Environment(
    account=account,
    region=region,
)

# CDK app - env vars
aws_profile_: str = "aws_profile"
cdk_custom_outputs_path_: str = "cdk_custom_outputs_path"
email_notification_recipient_: str = "email_notification_recipient"
infrastructure_domain_name_: str = "infrastructure_domain_name"
organisation_: str = "organisation"
organisation_abbrev: str = "organisation_abbrev"
ssh_key_: str = "ssh_key"
cdk_app_env_vars: dict[str, str] = {
    aws_profile_: os.getenv("PROFILE"),
    email_notification_recipient_: os.getenv("EMAIL_NOTIFICATION_RECIPIENT", default="cloud@foobar.co.uk"),
    infrastructure_domain_name_: os.getenv("INFRASTRUCTURE_DOMAIN_NAME", default="sihgnpwtbf.com"),
    organisation_: "foobar",
}
profile_format: str = f"-{profile.lower()}" if (profile := cdk_app_env_vars.get(aws_profile_)) else ""
cdk_app_env_vars[cdk_custom_outputs_path_] = f"cdk-custom-outputs{profile_format}.json"
cdk_app_env_vars[organisation_abbrev] = cdk_app_env_vars[organisation_][:3]
cdk_app_env_vars[ssh_key_] = os.getenv("SSH_KEY", default=f"aws_{cdk_app_env_vars[organisation_]}_default_key")

# Keywords - General
api_: str = "api"
assets_: str = "assets"
autoiod_: str = "autoiod"
base_: str = "base"
beat_: str = "beat"
bird_: str = "bird"
bkg_: str = "bkg"
broker_: str = "broker"
broker_web_: str = "mq"
cache_: str = "cache"
cat_: str = "cat"
cdn_: str = "cdn"
cf_: str = "cloudfront"
collector_: str = "collector"
cow_: str = "cow"
database_: str = "database"
dog_: str = "dog"
dos_: str = "dos"
dosimetry_: str = "dosimetry"
ecomm_: str = "ecomm"
em_: str = "em"
events_: str = "events"
extractor_: str = "extractor"
fish_: str = "fish"
fs_: str = "fs"
global_: str = "global"
gw_: str = "gw"
hds_: str = "hds"
lion_: str = "lion"
mail_: str = "mail"
metoffice_: str = "metoffice"
ms_: str = "ms"
notif_: str = "notif"
package_: str = "package"
pdf_: str = "pdf"
pipeline_: str = "pipeline"
processor_: str = "processor"
pypi_: str = "pypi"
server_: str = "server"
sih_: str = cdk_app_env_vars[organisation_abbrev]
sihd_: str = f"{sih_}d"
sihp_: str = f"{sih_}p"
spain_: str = "spain"
spectrum_: str = "spectrum"
storage_: str = "storage"
uat_: str = "uat"
util_: str = "util"
weatherapi_: str = "weatherapi"

factory: CdkConstructsFactory = CdkConstructsFactory(aws_region=region, **cdk_app_env_vars)

# CDK app environment - for CloudFront CDK stacks
env_cloudfront = cdk.Environment(
    account=account,
    region=factory.US_EAST_1_,  # CloudFront resources must be located in N. Virginia (us-east-1) region
)

# Word map for getting formatted general keywords
word_map: dict[str, str] = {
    factory.CUSTOM_: factory.CUSTOM_.capitalize(),
    api_: "API",
    assets_: "Assets",
    autoiod_: "AutoIOD",
    base_: "Base",
    beat_: "Beat",
    bird_: "Bird",
    bkg_: "Bkg",
    broker_: "Broker",
    broker_web_: "Amazon MQ RabbitMQ Web Console",
    cache_: "Cache",
    cat_: "Cat",
    cdn_: "CDN",
    cf_: "CloudFront",
    collector_: "Collector",
    cow_: "Cow",
    database_: "Database",
    dog_: "Dog",
    dos_: "Dosimetry Worker",
    dosimetry_: "Dosimetry",
    em_: "E-Commerce",
    events_: "Events",
    extractor_: "Extractor",
    fish_: "Fish",
    fs_: "File System",
    global_: "Global",
    gw_: "Gateway",
    hds_: "HDS",
    lion_: "LION",
    mail_: "Mail",
    metoffice_: "Metoffice",
    ms_: "Micro-service",
    notif_: "Notifications",
    package_: "Package",
    pdf_: "DOCX-to-PDF",
    pipeline_: "Pipeline",
    processor_: "Processor",
    pypi_: "PyPi",
    server_: "Server",
    sihd_: "Sih Demo",
    sihp_: "Sih Preview",
    spain_: "Spain",
    spectrum_: "Spectrum",
    storage_: "Storage",
    uat_: "UAT",
    util_: "Utility Worker",
    weatherapi_: "WeatherAPI",
}
factory.set_factory_word_map(word_map)

# Webhook URLs - MS Teams
ms_teams: dict = {
    factory.WEBHOOK_URL_AWS_NOTIFICATIONS_MISC_: {
        factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/1c0d49000bfc49cebc56fdd0630c82fd/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2tzxaG7F0OTiZIrdHPWVypYyO4gelr6ywn2UXwjhW3g81",
        factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/41133474ca4d4f5e8cb91f75759deb5c/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2yOrC4a7giYQNXwklOyKdpAOe9utdLT2DuQrS3qxYBNU1",
        factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/58d7ac452b214020a0523b427ef23a9b/71b0843c-25cd-4d4a-be5c-b5e954aad055/V23ViDpKyOn-yo_aMlee5SR8gg9dYYZ5pnPvPxvjc3kaw1",
    },
    factory.WEBHOOK_URL_AWS_NOTIFICATIONS_: {
        bird_: {
            factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/7d647977ae664ec78e51290616ec1baa/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2A1OrzfuUXP9QSVgf27mMI4VMO2gEqJ7ip-fXlMqyQSI1",
            factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/bb2ea157f5624700a2ff8d4eb881b1c2/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2DTmjHOtIM8WQ-ylvcBPAuHjZRFiqYXcdf2tNO3Ith_41",
            factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/93a10f0476294f888191734979ea0f1f/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2vL80GREFKoJesWzcv7whpVvfbkbXdTo96Rh2MltnYV41",
        },
        bkg_: {
            factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/a7b667304d5147c7baf389675475d50a/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2U6zFMlxqmnEPy0IVdOHYED7Bt534JV47M2iQbc0CE1M1",
            factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/583cdf76441441f98947ed2ba8be5a69/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2ReFTXSm13sCxCg46ZddsEiAndkgN2Pii8GnKImLwVhw1",
            factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/629a24164b3d4f1ab371dedeb44fd471/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2z84EEy8P7hciMriXdATjd56_3QZyhR0KKdVUv-xBoxM1",
        },
        cat_: {
            factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/18a211d57a3f47d1861196126d8eaf7b/71b0843c-25cd-4d4a-be5c-b5e954aad055/V24OtT4ZyKIuZBo5AGOhcOSA-qztsU8UjKjxqY_HBZlfQ1",
            factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/213e9c00d0f14371b27a7edf4bcf3388/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2QRY0Ut6Tt3anlGlh7aGkXGQmperlrl41AOAtboRUgjA1",
            factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/9f588f29fa1a40fbb441dc723e2f2db5/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2G2XHZTHgGdnfdOo5TUPg_PaHLZjiVQUDhIEaEZseKLs1",
        },
        cow_: {
            factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/f7339136c35348cca83feb875bdf3377/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2x58LnPETbfUtGs9nu0m_RRgjCyHwBy2h2LuhY1yh_0Y1",
            factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/039e12a95a47427c96d0e929be45d944/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2p1m29ula7Q5ZDe9XDneUUJ4CPc84XU0dP2yaaKz9r7o1",
            factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/cf89658c1a7644ee80c03c44fa08e619/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2Ufjj4pvg6nIUsMt6nkD6WLWkWehaacejwPuAnbNs6jc1",
        },
        dog_: {
            factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/030a7ab0da71426aac6cb9f7792128d3/71b0843c-25cd-4d4a-be5c-b5e954aad055/V22dgZZNQL2g0_T_gIoVLVv0MBfA1BVbbi9inPm87PZTY1",
            factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/9ecb464ef52a40f698f83efcae010750/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2Cr-cxgHRTbHh5JF7od3boDtI4fntxdOiOZL16M3S5pM1",
            factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/54bef812cdae4f6ca509dff414345f40/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2b9UDB49w_X1Qa2uuC4KzPPrjYIMQL6eRF7bNYZXyRcc1",
        },
        fish_: {
            factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/de73799d76064bb89cb4d839d4e16f20/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2lX5JLRcbc93GH76Nm1HF5yLPbI1OjBD1vIdyLzZtFmw1",
            factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/a6acb7c050cd4b8e8c81214ddd82fd9f/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2NxeY3xsBMA3lmq-mHFMNS6enNgaUzmyzwmESX5Xh3tA1",
            factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/def5f5651c7f43ce8c8e383fb152298f/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2EeVdE4Av0XgKx36EwfpO5Vg5rujkLfN20NGgXkaDoRo1",
        },
        lion_: {
            factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/a3b55c4a3a684404834bda8b8f9a410b/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2Ktkkj-fl_Zlhh39QHQKK7diKTfz6sbdlTEvogYkjm8w1",
            factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/1481fc4fb19f439b86cc35e7a1ad1bd0/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2Osc7xeZGscxBFuOlCMwIlVv0l8_VbAVso-hqHIflrEs1",
            factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/343cbe86592944599b4f14f8dbff2ba5/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2QIiIfvfLh2QxB328umMTgosvyPj6jc8pNYtSz9ah1ZI1",
        },
        mail_: {
            factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/a8f55308cc4f4c83b65903f28160a04a/71b0843c-25cd-4d4a-be5c-b5e954aad055/V249NZ8eBa3DqeLZcZl6nYh6MyHXhhfFXJpOFXHnuV8LI1",
            factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/a07370d08209499b9dc418af72fd0b91/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2K58hTTm-zpYzktEYeFSdIMWPpey0u1R0WXzoqalng8s1",
            factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/906fbec59286455ebec07d8b5c81793c/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2cSASSNVTjBEXkubfAw05GRvayg20oo8I4kt0cIMFr_01",
        },
        pdf_: {
            factory.WEBHOOK_URL_CLOUDWATCH_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/f8f824f2681446b58458c8a00d131c0c/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2ZxopEkB6VT8YdI_mQrzu6NixI0A2AXHpr5gz5Jb_c6w1",
            factory.WEBHOOK_URL_LAMBDA_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/66de84e9b0b6407e8928d1f49bf2099c/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2hnHYfJPvuRkEeCnvvnazEZZCsNVaopfgdqWHRCBaFjU1",
            factory.WEBHOOK_URL_SNS_: "https://foobarcouk.webhook.office.com/webhookb2/c1e5b2c2-0321-42aa-bd97-d850530acf11@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/e968c92060b647fa9f29971320bfbd8f/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2oXf5fLSdQ1Hv0AFb2iVaJCyLQdm2tvVMR1sJs2BSQ7o1",
        },
    },
    factory.WEBHOOK_URL_AMPLIFY_: {
        bird_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/15e6cd0fb7af47f7b3f211e880ac8b1a/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2oMmVcDlGOpPId3d7UnOM9KGEWPc1ojKqUfkyIbhVVpg1",
        cat_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/91274dd140c64863aa9c0b0f581ebfb0/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2xu3za4DRsNH4NIDaywYsUTyUNZx6VUtwk8qXNXWQxIw1",
        cow_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/1e4edba977fe4cdab4398b5f869cfd5c/71b0843c-25cd-4d4a-be5c-b5e954aad055/V24u4Qztaw_ObFcXKK-XcrjBLRjRHBgnAYDfFf50QE0yM1",
        dog_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/ae622734517a4a1daacfd32909b91edc/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2A3ZV5WXtpmcijCSy-EgAX6C70to4ZoBQhA0sTaps26I1",
        fish_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/ee16041bd173415198e8e64d19508802/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2CAEmSVfAORjTF0qA5M8eGA9Vl4D5NVZVCt23qBMXHuw1",
    },
    factory.WEBHOOK_URL_CODEPIPELINE_MISC_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/a900ef471dbd41ef9bd510143a379461/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2-TTzoni8soWu1Vc3hVE90X5_yKv-m-AJJT09hWB6bs01",
    factory.WEBHOOK_URL_CODEPIPELINE_: {
        bird_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/4cbf6bbcf7c842c8b47b758121c7df24/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2s16bWXjj1dh3KsXsT7S0gHkSJo3fDL53P8tvIenh-5Q1",
        bkg_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/13a7ddf7a6854ab6af7599b2a92b4661/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2PgKmO1H1xtfpWWuVsl2DbUVyYlfp-W26RVfd7Vyua7c1",
        cat_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/5e9d6a6d13af45e19007cce4a266b8a5/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2tBZC5PJFRFwyZzSV2eRiZVZBLMJC2mIboCykEvUT3Hg1",
        cow_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/1837899db0cd4ad68e187f29fd21e1e7/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2U0tR43ZjygR13K-Ns1tGu9rshI4qEgHnmdL5S0WzHkI1",
        dog_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/d3ada025608a4924bfc0a9cc2ed7601e/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2QBYamr_vpSBILVfuDu2cat5PdviA0jfLCpWK5Oz8aGI1",
        fish_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/87aa65f05b024c85a6f11b8c5e2bd6b1/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2hooI_upvQOnep6DpikHIZG3Onh8qVT9WAA41RWbKnLU1",
        lion_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/53e8904aad3742048b79b3ff8c2a40f7/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2kA4HjrzLQVkVaLWl5bHMfGCInyNcU8dC283MKdzUW2Y1",
        pdf_: "https://foobarcouk.webhook.office.com/webhookb2/91f73841-1783-4aa2-931e-bf57b0f6b2f9@f670d7ce-50c9-4c74-b98f-49edf7903c82/IncomingWebhook/bbfb6690a9a84127aca63ebe1bf04404/71b0843c-25cd-4d4a-be5c-b5e954aad055/V2Fx-k5x-2Bi2MWtVdeLQnTGW4kuyvjbCdct289EORPSg1",
    },
}
ms_teams[factory.WEBHOOK_URL_CODEPIPELINE_][sih_] = ms_teams[factory.WEBHOOK_URL_CODEPIPELINE_MISC_]
factory.set_factory_ms_teams(ms_teams)

project_name_comp_lookup: dict[str, list[str]] = {
    ms_: [lion_, bkg_],
    gw_: [bird_, cat_, cow_, dog_, fish_],
}
project_name_ec_redis_instance_type_custom_meta: dict[str, int] = {
    # NB. This is Gw only, does not support Ms
    # gw-project-name: factory.M5_LARGE_
}
project_name_ecs_service_max_val_custom_meta: dict[str, int] = {
    # NB. This is Gw only, does not support Ms
    # gw-project-name: 5
}
project_name_comp_lists: dict[str, list[str]] = {}
for k, v in project_name_comp_lookup.items():
    for p in v:
        project_name_comp_lists[p] = [factory.join_sep_score([p, k] + j) for j in [[], [base_]]]

deploy_envs_preview_demo_base: dict[str, dict[str, tuple[str, str]]] = {
    sihp_: (factory.LIGHT_, factory.PREVIEW_),
    sihd_: (factory.LIGHT_, factory.DEMO_),
}

# The list of additonal* preview/demo deploy envs, for each project.
#   (*) All projects, by default, have deploy envs: 'sihp' & 'sihd'.
deploy_envs_preview_demo: dict[str, dict[str, tuple[str, str]]] = {
    # project-name: {uat_: (factory.HEAVY_, factory.PREVIEW_)},
    # project-name: {foo_: (factory.LIGHT_, factory.DEMO_)},
    cat_: {
        sihp_: (factory.HEAVY_, factory.PREVIEW_),
        sihd_: (factory.LIGHT_, factory.DEMO_),
        uat_: (factory.HEAVY_, factory.PREVIEW_),
    },
}

deploy_env_preview_demo_metas: dict[str, dict[str, tuple[str, str]]] = {}
deploy_envs_metas: dict[str, dict[str, dict]] = {}
database_server_deploy_env_maps: dict[str, dict[str, dict]] = {}
deploy_env_database_server_maps: dict[str, dict[str, str]] = {}
for p in project_name_comp_lookup[gw_]:
    deploy_env_preview_demo_metas[p] = deploy_envs_preview_demo.get(p, deploy_envs_preview_demo_base)
    deploy_envs_metas[p] = factory.get_deploy_envs_meta(
        deploy_env_preview_demo_metas[p],
        ec_redis_instance_type_custom=project_name_ec_redis_instance_type_custom_meta.get(p),
        ecs_service_max_val_custom=project_name_ecs_service_max_val_custom_meta.get(p),
    )
    if m := deploy_envs_metas[p]:
        database_server_deploy_env_maps[p] = factory.get_database_server_deploy_env_map(
            m,
            opt_map_base=factory.get_database_server_deploy_env_map(
                m,
                orig_map_base={
                    factory.PREVIEW_DEMO_: {
                        factory.DEPLOY_ENV_LIST_: list(deploy_env_preview_demo_metas[p].keys()),
                        factory.RDS_INSTANCE_TYPE_: factory.RDS_INSTANCE_TYPE_DEFAULT_VALUE,
                    }
                },
            ),
        )
    deploy_env_database_server_maps[p] = factory.get_deploy_env_database_server_map(database_server_deploy_env_maps[p])


def get_deploy_env_preview_demo_meta(project_name: str) -> dict[str, str]:
    return {deploy_env: meta[1] for deploy_env, meta in deploy_env_preview_demo_metas[project_name].items()}


def get_db_server_preview_demo(project_name: str, database_server: str) -> dict[str, str]:
    return get_deploy_env_preview_demo_meta(project_name) if database_server == factory.PREVIEW_DEMO_ else None


# The list of project names, which depend on other projects running at the same time.
#   e.g. If 'cat' is selected for 24/7 (or weekend) running,
#   this option enforces that we also need 24/7 (or weekend) running: 'bkg' & 'lion'
project_dependant_meta: dict[str, dict[str, bool]] = {
    # project-name: {dependant-project-name: always_prod, ...}
    lion_: {},
    bkg_: {lion_: True},
    bird_: {bkg_: False, lion_: True},
    cat_: {bkg_: True, lion_: True},
    cow_: {bkg_: True, lion_: True},
    dog_: {bkg_: True, lion_: True},
    fish_: {bkg_: True, lion_: True},
}
project_dependant_map: dict[str, dict[str, cdk.Stack]] = {
    # NB. Values will get populated later in CDK app
    # ms-project-name: cdk_project_ms_stacks
    lion_: None,
    bkg_: None,
}


def _get_ms_stack(project_name: str, deploy_env: str, ms_project_name: str) -> cdk.Stack:
    return project_dependant_map[ms_project_name][
        factory.get_deploy_env_chosen(
            deploy_env, always_prod=project_dependant_meta[project_name].get(ms_project_name, None)
        )
    ]


def get_lion_ms_stack(project_name: str, deploy_env: str) -> cdk.Stack:
    return _get_ms_stack(project_name, deploy_env, lion_)


def get_bkg_ms_stack(project_name: str, deploy_env: str) -> cdk.Stack:
    return _get_ms_stack(project_name, deploy_env, bkg_)


# Project deploy envs for weekend running (business hours, MON-SUN).
#   and not just weekday running (business hours, MON-FRI).
#   NB. All `prod` deploy envs are automatically 24/7 running.
deploy_env_weekend_sets: dict[str, set[str]] = {
    # project-name: {dev_, staging_}
    # project-name: {uat_, sihp, sihd}
    lion_: {},
    bkg_: {},
    bird_: {},
    cat_: {},
    cow_: {},
    dog_: {},
    fish_: {},
}

# Project deploy envs for 24/7 running, and not just business hours running.
#   NB. This setting overrides weekend running (business hours, MON-SUN) options.
#   NB. All `prod` deploy envs are automatically 24/7 running.
deploy_env_24_7_sets: dict[str, set[str]] = {
    # project-name: {dev_, staging_}
    # project-name: {uat_, sihp, sihd}
    lion_: {},
    bkg_: {},
    bird_: {sihp_},
    cat_: {sihp_},
    cow_: {},
    dog_: {},
    fish_: {},
}


def update_deploy_env_lists(
    project_name: str, dependant_project_name: str, deploy_env_sets: dict[str, set[str]], weekend: bool
) -> None:
    for x, y in deploy_env_sets.items():
        if x != dependant_project_name and x == project_name and y:
            for z in y:
                if factory.is_deploy_env_internal(z):
                    deploy_env_sets[dependant_project_name] = set(deploy_env_sets[dependant_project_name]).union(
                        {factory.STAGING_}
                    )
                elif z == factory.PROD_:
                    sys.exit(
                        f"## Do not include '{factory.PROD_}' deploy env (in the '{x}' {'weekend' if weekend else '24/7'} list):\n{y}"
                    )
                elif (meta := deploy_env_preview_demo_metas[x]) and z not in meta:
                    sys.exit(
                        f"## Cannot find '{z}' deploy env (in the '{x}' {'weekend' if weekend else '24/7'} list) in the preview/demo metadata:\n{m}"
                    )


for k, v in project_dependant_meta.items():
    for p, always_prod in v.items():
        if not always_prod:
            update_deploy_env_lists(k, p, deploy_env_24_7_sets, weekend=False)
            update_deploy_env_lists(k, p, deploy_env_weekend_sets, weekend=True)


# ---------- CDK app ----------

####################################################################################################
# --- Infrastructure ---
####################################################################################################

app = cdk.App()


# TODO: (IMPORTANT) Incorporate usage of new function
def get_cdk_stack_args_default(
    deploy_env: str,
    stack_id_props: Union[str, dict],
    description: str,
    is_full_desc: bool = False,
    is_cloudfront: bool = None,
    is_protected: bool = None,
    is_db_server: bool = False,
) -> dict:
    is_stack_id_str: bool = isinstance(stack_id_props, str)
    id_: str = "id"
    desc_: str = "description"
    args: dict = {
        "scope": app,
        id_: stack_id_props if is_stack_id_str else None,
        desc_: description if is_full_desc else None,
        factory.ENV_: env_cloudfront if is_cloudfront else env,
        "termination_protection": (
            True
            if is_cloudfront
            else (is_protected if is_protected else factory.get_termination_protection(deploy_env))
        ),
    }
    if not is_stack_id_str:
        if is_db_server:
            stack_id_props[factory.DEPLOY_ENV_] = factory.format_database_server(deploy_env)
        args[id_] = factory.get_cdk_stack_id(**stack_id_props)
        if not is_full_desc:
            if is_db_server:
                stack_id_props[factory.DEPLOY_ENV_] = factory.format_database_server(deploy_env, hyphen_sep=True)
            args[desc_] = factory.get_cdk_stack_description(**{**stack_id_props, **{"detail": description}})
    return args


cdk_vpc_sih_stack = CdkVpcSihStack(
    scope=app,
    id="CdkVpcSihStack",
    description="Virtual Private Cloud (VPC) resources: VPCs, subnets, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    factory=factory,
)

# IMPORTANT: This CDK stack can get very expensive!! Proceed with caution.
cdk_cloudtrail_trails_stack = CdkCloudTrailTrailsStack(
    scope=app,
    id="CdkCloudTrailTrailsStack",
    description="CloudTrail resources: Trails, S3, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    factory=factory,
)
factory.add_tags_required(stacks=[cdk_cloudtrail_trails_stack], project_name_val=factory.TAG_VAL_CT_)

cdk_client_vpn_endpoint_stack = CdkClientVpnEndpointStack(
    scope=app,
    id="CdkClientVpnEndpointStack",
    description="Virtual Private Cloud (VPC) resources: Client VPN endpoint, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    client_vpn_endpoint_internet=False,  # bool(factory.aws_profile is None)  # TODO: (NEXT) Add a Client VPN Endpoint (Internet) to AWS Foobar Products A/c, as needed
    client_vpn_endpoint_server_certificate_id=os.getenv(
        "CLIENT_VPN_ENDPOINT_SERVER_CERTIFICATE_ID", default="8ac31cc0-d5af-49e0-b8f9-8d7817cfa424"
    ),  # The ACM certificate ID ('server'). Default: Lives in London (eu-west-2) region, A/C: 7832***
    factory=factory,
    vpc_stack=cdk_vpc_sih_stack,
)

client_vpn_endpoint_override: bool = True
client_vpn_endpoint_stack = (
    None if factory.aws_profile or client_vpn_endpoint_override else cdk_client_vpn_endpoint_stack
)

cdk_bastion_host_linux_stack_name: str = "CdkBastionHostLinuxStack"
cdk_bastion_host_linux_stack = CdkBastionHostLinuxStack(
    scope=app,
    id=cdk_bastion_host_linux_stack_name,
    description="Bastion Host resources: BastionHostLinux EC2 instances, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    factory=factory,
    vpc_stack=cdk_vpc_sih_stack,
)

bastion_host_private_ips: list[str] = cdk_bastion_host_linux_stack.get_bastion_host_private_ips()

ipsec_vpn_: str = "ipsec-vpn"
ipsec_vpn_server_: str = factory.join_sep_score([ipsec_vpn_, server_])
proxy_: str = "proxy"
proxy_server_: str = factory.join_sep_score([proxy_, server_])
openvpn_vpn_: str = "openvpn-vpn"
openvpn_vpn_server_: str = factory.join_sep_score([openvpn_vpn_, server_])

elastic_ip_str_list: list[str] = [ipsec_vpn_server_, proxy_server_, openvpn_vpn_server_]

cdk_elastic_ips_stack = CdkElasticIpsStack(
    scope=app,
    id="CdkElasticIpsStack",
    description=f"Elastic IP resources: Elastic IPs (static IP addresses) for use by VPN/Proxy/{word_map[pypi_]} servers, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    vpc_stack=cdk_vpc_sih_stack,
)
elastic_ip_parameter_names: dict[str, str] = {}

cdk_ipsec_vpn_base_stack = CdkIpsecVpnBaseStack(
    scope=app,
    id="CdkIpsecVpnBaseStack",
    description="VPN base resources: IPsec VPN server role, VPN user password secrets, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    component=server_,
    factory=factory,
    project_name=ipsec_vpn_,
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_ipsec_vpn_psk_stack = CdkIpsecVpnPskStack(
    scope=app,
    id="CdkIpsecVpnPskStack",
    description="VPN PSK resources: VPN Pre-Shared Key (PSK) secret, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_ipsec_vpn_base_stack,
    component=server_,
    factory=factory,
    project_name=ipsec_vpn_,
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_ipsec_vpn_server_stack = CdkIpsecVpnServerStack(
    scope=app,
    id="CdkIpsecVpnServerStack",
    description="VPN resources: IPsec VPN server EC2 instance launched by an ASG, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_ipsec_vpn_base_stack,
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    component=server_,
    elastic_ip=cdk_elastic_ips_stack.elastic_ips[ipsec_vpn_server_],
    factory=factory,
    project_name=ipsec_vpn_,
    psk_stack=cdk_ipsec_vpn_psk_stack,
    vpc_stack=cdk_vpc_sih_stack,
)
elastic_ip_parameter_names[ipsec_vpn_server_] = cdk_ipsec_vpn_server_stack.public_ipv4_parameter_name

cdk_proxy_server_stack = CdkProxyServerStack(
    scope=app,
    id="CdkProxyServerStack",
    description="Proxy resources: Proxy server EC2 instance launched by an ASG, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    component=server_,
    elastic_ip=cdk_elastic_ips_stack.elastic_ips[proxy_server_],
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=proxy_,
)
elastic_ip_parameter_names[proxy_server_] = cdk_proxy_server_stack.public_ipv4_parameter_name

openvpn_vpn_vpc_default: bool = True  # Whether to use the default VPC
cdk_openvpn_vpn_base_stack_name: str = "CdkOpenvpnVpnBaseStack"
cdk_openvpn_vpn_base_stack = CdkOpenvpnVpnBaseStack(
    scope=app,
    id=cdk_openvpn_vpn_base_stack_name,
    description="VPN base resources: OpenVPN VPN server role, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    component=server_,
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=openvpn_vpn_,
)

cdk_openvpn_vpn_cloudfront_stack = CdkOpenvpnVpnCloudFrontStack(
    scope=app,
    id="CdkOpenvpnVpnCloudFrontStack",
    description="VPN CloudFront resources: ACM certificates, WAF Web ACLs, etc.",
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_openvpn_vpn_base_stack,
    component=server_,
    factory=factory,
    project_name=openvpn_vpn_,
)

cdk_openvpn_vpn_user_stack = CdkOpenvpnVpnUserStack(
    scope=app,
    id="CdkOpenvpnVpnUserStack",
    description="VPN User resources: VPN user password secrets, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_openvpn_vpn_base_stack,
    component=server_,
    factory=factory,
    project_name=openvpn_vpn_,
    vpc_default=openvpn_vpn_vpc_default,
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_openvpn_vpn_server_stack = CdkOpenvpnVpnServerStack(
    scope=app,
    id="CdkOpenvpnVpnServerStack",
    description="VPN resources: ALB, NLB, OpenVPN VPN server EC2 instance launched by an ASG, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_openvpn_vpn_base_stack,
    component=server_,
    elastic_ip=cdk_elastic_ips_stack.elastic_ips[openvpn_vpn_server_],
    factory=factory,
    project_name=openvpn_vpn_,
    user_stack=cdk_openvpn_vpn_user_stack,
    vpc_default=openvpn_vpn_vpc_default,
    vpc_stack=cdk_vpc_sih_stack,
)
elastic_ip_parameter_names[openvpn_vpn_server_] = cdk_openvpn_vpn_server_stack.public_ipv4_parameter_name

cdk_lambda_ec2_instance_auto_stack = CdkLambdaEc2InstanceAutoStack(
    scope=app,
    id="CdkLambdaEc2InstanceAutoStack",
    description="EC2 instance auto start/stop resources: Lambda functions, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    factory=factory,
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_lambda_rds_instance_auto_stack = CdkLambdaRdsInstanceAutoStack(
    scope=app,
    id="CdkLambdaRdsInstanceAutoStack",
    description="RDS database instance auto start/stop resources: Lambda functions, etc.",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    factory=factory,
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_amplify_ci_cd_stack = CdkAmplifyCiCdStack(
    scope=app,
    id="CdkAmplifyCiCdStack",
    description="Pipeline support resources for all deployment envs",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    factory=factory,
)

cdk_codepipeline_ci_cd_stack = CdkCodepipelineCiCdStack(
    scope=app,
    id="CdkCodepipelineCiCdStack",
    description="Pipeline support resources for all deployment envs",
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    factory=factory,
)

cdk_pypi_base_stack_name: str = factory.get_cdk_stack_id(pypi_, base_comp=True)
cdk_pypi_base_stack = CdkPypiBaseStack(
    scope=app,
    id=cdk_pypi_base_stack_name,
    description=factory.get_cdk_stack_description(pypi_, base_comp=True, detail="Security Groups"),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    bastion_host_private_ips=bastion_host_private_ips,
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    component=server_,
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=pypi_,
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_pypi_cloudfront_stack = CdkPypiCloudFrontStack(
    scope=app,
    id=factory.get_cdk_stack_id(pypi_, components=[cf_]),
    description=factory.get_cdk_stack_description(pypi_, components=[cf_], detail="ACM certificates, WAF Web ACLs"),
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_pypi_base_stack,
    component=server_,
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    project_name=pypi_,
)

cdk_pypi_storage_stack = CdkPypiStorageStack(
    scope=app,
    id=factory.get_cdk_stack_id(pypi_, components=[storage_]),
    description=factory.get_cdk_stack_description(pypi_, components=[storage_], detail="EFS"),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_pypi_base_stack,
    component=server_,
    factory=factory,
    project_name=pypi_,
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_pypi_server_stack = CdkPypiServerStack(
    scope=app,
    id=factory.get_cdk_stack_id(pypi_, components=[server_]),
    description=factory.get_cdk_stack_description(
        pypi_,
        components=[server_],
        detail=f"ALB, {word_map[pypi_]} {word_map[server_]} EC2 instance launched by an ASG",
    ),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_pypi_base_stack,
    component=server_,
    factory=factory,
    project_name=pypi_,
    storage_stack=cdk_pypi_storage_stack,
    vpc_stack=cdk_vpc_sih_stack,
)

sih_autoiod_: str = factory.join_sep_score([sih_, autoiod_])
sih_bkg_: str = factory.join_sep_score([sih_, bkg_])
sih_dosimetry_: str = factory.join_sep_score([sih_, dosimetry_])
sih_lion_: str = factory.join_sep_score([sih_, lion_])
sih_hds_: str = factory.join_sep_score([sih_, hds_])
sih_spectrum_: str = factory.join_sep_score([sih_, spectrum_])
pypi_package_mappings: dict[str] = {lion_: sih_lion_}
pypi_package_list: list[str] = [sih_, sih_autoiod_, sih_bkg_, sih_dosimetry_, sih_lion_, sih_hds_, sih_spectrum_]
pypi_package_list_word_map: dict[str, str] = {
    i: factory.join_sep_empty([j.capitalize() for j in i.split(factory.SEP_SCORE_)]) for i in pypi_package_list
}

cdk_pypi_package_base_stack = CdkPypiPackageBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(pypi_, components=[package_], base_comp=True),
    description=factory.get_cdk_stack_description(
        pypi_, components=[package_], base_comp=True, detail="SSM Parameters"
    ),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    factory=factory,
    project_name=pypi_,
    pypi_package_list=pypi_package_list,
)

cdk_pypi_package_pipeline_stacks: dict[str, dict[str, CdkPypiPackagePipelineStack]] = {
    pypi_package: {
        branch: CdkPypiPackagePipelineStack(
            scope=app,
            id=factory.get_cdk_stack_id(
                pypi_, components=[package_, (pypi_package_list_word_map[pypi_package],), pipeline_], deploy_env=branch
            ),
            description=factory.get_cdk_stack_description(
                pypi_,
                components=[package_, (pypi_package_list_word_map[pypi_package],), pipeline_],
                deploy_env=branch,
                detail="CodeBuild, CodePipeline",
            ),
            env=env,
            termination_protection=True,
            # --- ^ super() ---
            base_stack=cdk_pypi_package_base_stack,
            branch=branch,
            factory=factory,
            project_name=pypi_package,
            pypi_base_stack=cdk_pypi_base_stack,
            vpc_stack=cdk_vpc_sih_stack,
        )
        for branch in factory.DEV_MAIN_BRANCH_LIST
    }
    for pypi_package in pypi_package_list
}
for _, v in cdk_pypi_package_pipeline_stacks.items():
    factory.add_tags_required(stacks=[j for _, j in v.items()], project_name_val=factory.TAG_VAL_INFRA_)

cdk_metoffice_storage_stack = CdkMetofficeStorageStack(
    scope=app,
    id=factory.get_cdk_stack_id(metoffice_, components=[storage_]),
    description=factory.get_cdk_stack_description(
        metoffice_,
        components=[storage_],
        detail=f"S3, IAM, Lambda, {word_map[metoffice_]} {word_map[storage_]} solution, "
        f"for remote ingestion, alternative to FTP server",
    ),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    component=storage_,
    factory=factory,
    project_name=metoffice_,
)

cdk_weatherapi_storage_stack = CdkWeatherapiStorageStack(
    scope=app,
    id=factory.get_cdk_stack_id(weatherapi_, components=[storage_]),
    description=factory.get_cdk_stack_description(
        weatherapi_,
        components=[storage_],
        detail=f"Lambda, {word_map[weatherapi_]} {word_map[storage_]} solution, for downloading of WeatherAPI data",
    ),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    component=storage_,
    factory=factory,
    project_name=weatherapi_,
)

factory.add_tags_required(
    stacks=[
        cdk_amplify_ci_cd_stack,
        cdk_bastion_host_linux_stack,
        cdk_client_vpn_endpoint_stack,
        cdk_codepipeline_ci_cd_stack,
        cdk_elastic_ips_stack,
        cdk_ipsec_vpn_base_stack,
        cdk_ipsec_vpn_psk_stack,
        cdk_ipsec_vpn_server_stack,
        cdk_lambda_ec2_instance_auto_stack,
        cdk_lambda_rds_instance_auto_stack,
        cdk_metoffice_storage_stack,
        cdk_openvpn_vpn_base_stack,
        cdk_openvpn_vpn_cloudfront_stack,
        cdk_openvpn_vpn_server_stack,
        cdk_openvpn_vpn_user_stack,
        cdk_proxy_server_stack,
        cdk_pypi_base_stack,
        cdk_pypi_cloudfront_stack,
        cdk_pypi_package_base_stack,
        cdk_pypi_storage_stack,
        cdk_pypi_server_stack,
        cdk_vpc_sih_stack,
        cdk_weatherapi_storage_stack,
    ],
    project_name_val=factory.TAG_VAL_INFRA_,
)

factory.add_tags_auto_start_stop(stacks=[cdk_bastion_host_linux_stack], include_resource_type=["AWS::EC2::Instance"])

####################################################################################################
# --- Base Stacks ---
####################################################################################################

bkg_ms_comp_subs_meta: dict[str, tuple[int, float]] = {
    # name: (port, cpu_unit_weighting)
    api_: (5000, 0.1),
    beat_: (6380, None),
    util_: (8001, 0.2),
    dos_: (8002, 0.3),
}
bkg_ms_comp_subs: list[str] = list(bkg_ms_comp_subs_meta.keys())

cdk_bkg_base_stack_name: str = factory.get_cdk_stack_id(bkg_, base_comp=True)
cdk_bkg_base_stack = CdkBkgBaseStack(
    scope=app,
    id=cdk_bkg_base_stack_name,
    description=factory.get_cdk_stack_description(bkg_, base_comp=True, detail="ECR, Security Groups, Secrets Manager"),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    bastion_host_private_ips=bastion_host_private_ips,
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    component=ms_,
    component_sub_ports={
        k: (v, bool(k == api_)) for k, v in {k: v[0] for k, v in bkg_ms_comp_subs_meta.items()}.items()
    },
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=bkg_,
    project_name_comp_list=[
        factory.join_sep_score([bkg_, ms_] + j) for j in [[k] for k in bkg_ms_comp_subs] + [[base_]]
    ],
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_dog_base_stack_name: str = factory.get_cdk_stack_id(dog_, base_comp=True)
cdk_dog_base_stack = CdkDogBaseStack(
    scope=app,
    id=cdk_dog_base_stack_name,
    description=factory.get_cdk_stack_description(dog_, base_comp=True, detail="ECR, Security Groups, Secrets Manager"),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    bastion_host_private_ips=bastion_host_private_ips,
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    component=gw_,
    deploy_env_preview_demo_meta=get_deploy_env_preview_demo_meta(dog_),
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=dog_,
    project_name_comp_list=project_name_comp_lists[dog_],
    project_name_ecomm=factory.join_sep_score([dog_, ecomm_]),
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_cat_base_stack_name: str = factory.get_cdk_stack_id(cat_, base_comp=True)
cdk_cat_base_stack = CdkCatBaseStack(
    scope=app,
    id=cdk_cat_base_stack_name,
    description=factory.get_cdk_stack_description(cat_, base_comp=True, detail="ECR, Security Groups, Secrets Manager"),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    bastion_host_private_ips=bastion_host_private_ips,
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    component=gw_,
    deploy_env_preview_demo_meta=get_deploy_env_preview_demo_meta(cat_),
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=cat_,
    project_name_comp_list=project_name_comp_lists[cat_],
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_bird_base_stack_name: str = factory.get_cdk_stack_id(bird_, base_comp=True)
cdk_bird_base_stack = CdkBirdBaseStack(
    scope=app,
    id=cdk_bird_base_stack_name,
    description=factory.get_cdk_stack_description(
        bird_, base_comp=True, detail="ECR, Security Groups, Secrets Manager"
    ),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    bastion_host_private_ips=bastion_host_private_ips,
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    component=gw_,
    deploy_env_preview_demo_meta=get_deploy_env_preview_demo_meta(bird_),
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=bird_,
    project_name_comp_list=project_name_comp_lists[bird_],
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_cow_base_stack_name: str = factory.get_cdk_stack_id(cow_, base_comp=True)
cdk_cow_base_stack = CdkCowBaseStack(
    scope=app,
    id=cdk_cow_base_stack_name,
    description=factory.get_cdk_stack_description(cow_, base_comp=True, detail="ECR, Security Groups, Secrets Manager"),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    bastion_host_private_ips=bastion_host_private_ips,
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    component=gw_,
    deploy_env_preview_demo_meta=get_deploy_env_preview_demo_meta(cow_),
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=cow_,
    project_name_comp_list=project_name_comp_lists[cow_],
    vpc_stack=cdk_vpc_sih_stack,
)

cdk_fish_base_stack_name: str = factory.get_cdk_stack_id(fish_, base_comp=True)
cdk_fish_base_stack = CdkFishBaseStack(
    scope=app,
    id=cdk_fish_base_stack_name,
    description=factory.get_cdk_stack_description(
        fish_, base_comp=True, detail="ECR, Security Groups, Secrets Manager"
    ),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    bastion_host_private_ips=bastion_host_private_ips,
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    component=gw_,
    deploy_env_preview_demo_meta=get_deploy_env_preview_demo_meta(fish_),
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=fish_,
    project_name_comp_list=project_name_comp_lists[fish_],
    vpc_stack=cdk_vpc_sih_stack,
)

####################################################################################################
# --- Mail (SES) ---
####################################################################################################

mail_ms_: str = factory.join_sep_score([mail_, ms_])
mail_supported_base_stacks: list[IConstruct] = [
    cdk_bkg_base_stack,
    cdk_dog_base_stack,
    cdk_cat_base_stack,
    cdk_bird_base_stack,
    cdk_fish_base_stack,
]

cdk_mail_base_stack_name: str = factory.get_cdk_stack_id(mail_, base_comp=True)
cdk_mail_base_stack = CdkMailBaseStack(
    scope=app,
    id=cdk_mail_base_stack_name,
    description=factory.get_cdk_stack_description(mail_, base_comp=True, detail="Security Groups, SES"),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    component=ms_,
    factory=factory,
    mail_users_hosted_zones={
        getattr(i, factory.MAIL_USER_): getattr(i, factory.HOSTED_ZONE_) for i in mail_supported_base_stacks
    },
    project_name=mail_,
    vpc_stack=cdk_vpc_sih_stack,
)
factory.add_tags_required(
    stacks=[cdk_mail_base_stack],
    project_name_val=word_map[mail_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_mail_ms_stacks: dict[str, CdkMailMsStack] = {
    deploy_env: CdkMailMsStack(
        scope=app,
        id=factory.get_cdk_stack_id(mail_, components=[ms_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            mail_, components=[ms_], deploy_env=deploy_env, detail="Lambda functions"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_mail_base_stack,
        component=ms_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=mail_,
        project_names_ses_email_templates=[factory.get_attr_project_name(i) for i in mail_supported_base_stacks],
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_mail_ms_stacks, project_name=mail_, component=ms_)

####################################################################################################
# --- Pdf (DOCX-to-PDF) ---
####################################################################################################

pdf_ms_: str = factory.join_sep_score([pdf_, ms_])
pdf_supported_base_stacks: list = [
    cdk_bkg_base_stack,
    cdk_dog_base_stack,
    cdk_cat_base_stack,
    cdk_bird_base_stack,
    cdk_fish_base_stack,
]

cdk_pdf_base_stack_name: str = factory.get_cdk_stack_id(pdf_, base_comp=True)
cdk_pdf_base_stack = CdkPdfBaseStack(
    scope=app,
    id=cdk_pdf_base_stack_name,
    description=factory.get_cdk_stack_description(pdf_, base_comp=True, detail="Security Groups, SES"),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    component=ms_,
    factory=factory,
    project_name=pdf_,
    vpc_stack=cdk_vpc_sih_stack,
)
factory.add_tags_required(
    stacks=[cdk_pdf_base_stack],
    project_name_val=word_map[pdf_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_pdf_ms_stacks: dict[str, CdkPdfMsStack] = {
    deploy_env: CdkPdfMsStack(
        scope=app,
        id=factory.get_cdk_stack_id(pdf_, components=[ms_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            pdf_, components=[ms_], deploy_env=deploy_env, detail="Lambda functions"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_pdf_base_stack,
        component=ms_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=pdf_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_pdf_ms_stacks, project_name=pdf_, component=ms_)

####################################################################################################
# --- CDN (Content Delivery Network) ---
####################################################################################################

cdn_assets_: str = factory.join_sep_score([cdn_, assets_])

cdk_cdn_base_stack_name: str = factory.get_cdk_stack_id(cdn_, base_comp=True)
cdk_cdn_base_stack = CdkCdnBaseStack(
    scope=app,
    id=cdk_cdn_base_stack_name,
    description=factory.get_cdk_stack_description(cdn_, base_comp=True, detail="ECR, Security Groups, Secrets Manager"),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    component=assets_,
    factory=factory,
    project_name=cdn_,
)
cdk_cdn_cloudfront_base_stack = CdkCdnCloudFrontBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(cdn_, components=[cf_], base_comp=True),
    description=factory.get_cdk_stack_description(
        cdn_, components=[cf_], base_comp=True, detail="WAF Regex Pattern Set"
    ),
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_cdn_base_stack,
    component=assets_,
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    project_name=cdn_,
)
factory.add_tags_required(
    stacks=[cdk_cdn_base_stack, cdk_cdn_cloudfront_base_stack],
    project_name_val=word_map[cdn_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_cdn_assets_cloudfront_stacks: dict[str, CdkCdnCloudFrontStack] = {
    deploy_env: CdkCdnCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(cdn_, components=[assets_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cdn_, components=[assets_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_cdn_base_stack,
        cloudfront_base_stack=cdk_cdn_cloudfront_base_stack,
        component=assets_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=cdn_,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_cdn_assets_cloudfront_stacks, project_name=cdn_, component=cf_)

cdk_cdn_storage_stacks: dict[str, CdkCdnStorageStack] = {
    deploy_env: CdkCdnStorageStack(
        scope=app,
        id=factory.get_cdk_stack_id(cdn_, components=[storage_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(cdn_, components=[storage_], deploy_env=deploy_env, detail="S3"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cdn_base_stack,
        component=assets_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=cdn_,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_cdn_storage_stacks, project_name=cdn_, component=assets_)

cdk_cdn_assets_stacks: dict[str, CdkCdnAssetsStack] = {
    deploy_env: CdkCdnAssetsStack(
        scope=app,
        id=factory.get_cdk_stack_id(cdn_, components=[assets_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cdn_, components=[assets_], deploy_env=deploy_env, detail="CloudFront Distribution, ALB, ECS"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cdn_base_stack,
        component=assets_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=cdn_,
        storage_stack=cdk_cdn_storage_stacks[deploy_env],
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_cdn_assets_stacks, project_name=cdn_, component=assets_)

####################################################################################################
# --- LION ---
####################################################################################################

# Global resources chosen to be centrally located in London (eu-west-2) region
lion_global_region: str = factory.EU_WEST_2_

lion_cache_region_af: str = "AF"
lion_cache_region_ant: str = "ANT"
lion_cache_region_arc: str = "ARC"
lion_cache_region_asi: str = "ASI"
lion_cache_region_au: str = "AU"
lion_cache_region_eu: str = "EU"
lion_cache_region_na: str = "NA"
lion_cache_region_oc: str = "OC"
lion_cache_region_sa: str = "SA"

lion_cache_region_meta: dict[str, tuple[str, list[str]]] = {
    # lion_cache_region_af: (factory.EU_WEST_2_, []),
    # lion_cache_region_ant: (factory.EU_WEST_2_, []),
    # lion_cache_region_arc: (factory.EU_WEST_2_, []),
    # lion_cache_region_asi: (factory.EU_WEST_2_, []),
    lion_cache_region_au: (factory.EU_WEST_2_, [CdkLionCollectorStack.CAMS_, CdkLionProcessorStack.HIMAWARI9_]),
    lion_cache_region_eu: (factory.EU_WEST_2_, [CdkLionCollectorStack.CAMS_, CdkLionProcessorStack.MSG0DEG_]),
    # lion_cache_region_na: (factory.EU_WEST_2_, []),
    # lion_cache_region_oc: (factory.EU_WEST_2_, []),
    # lion_cache_region_sa: (factory.EU_WEST_2_, []),
}

lion_ms_regions_set: set[str] = {
    v[0] for _, v in lion_cache_region_meta.items()
}  # AWS regions to serve LION Micro-service CDK stack(s)

cdk_lion_base_stack_name: str = factory.get_cdk_stack_id(lion_, base_comp=True)
cdk_lion_base_stack = CdkLionBaseStack(
    scope=app,
    id=cdk_lion_base_stack_name,
    description=factory.get_cdk_stack_description(
        lion_, base_comp=True, detail="ECR, Security Groups, Secrets Manager"
    ),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    bastion_host_private_ips=bastion_host_private_ips,
    client_vpn_endpoint_stack=client_vpn_endpoint_stack,
    component=ms_,
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=lion_,
    project_name_comp_list=project_name_comp_lists[lion_],
    pypi_package_name=pypi_package_mappings[lion_],
    vpc_stack=cdk_vpc_sih_stack,
)
cdk_lion_cloudfront_base_stack = CdkLionCloudFrontBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(lion_, components=[cf_], base_comp=True),
    description=factory.get_cdk_stack_description(
        lion_, components=[cf_], base_comp=True, detail="WAF Regex Pattern Set"
    ),
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_lion_base_stack,
    component=ms_,
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    project_name=lion_,
)
factory.add_tags_required(
    stacks=[cdk_lion_base_stack, cdk_lion_cloudfront_base_stack],
    project_name_val=word_map[lion_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_lion_ms_cloudfront_stacks: dict[str, CdkLionCloudFrontStack] = {
    deploy_env: CdkLionCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(lion_, components=[ms_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            lion_, components=[ms_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_lion_base_stack,
        cloudfront_base_stack=cdk_lion_cloudfront_base_stack,
        component=ms_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=lion_,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_lion_ms_cloudfront_stacks, project_name=lion_, component=cf_)

cdk_lion_ms_stacks: dict[str, CdkLionMsStack] = {}
if env.region in lion_ms_regions_set:
    cdk_lion_events_stacks: dict[str, CdkLionEventsStack] = {
        deploy_env: CdkLionEventsStack(
            scope=app,
            id=factory.get_cdk_stack_id(lion_, components=[events_], deploy_env=deploy_env),
            description=factory.get_cdk_stack_description(
                lion_, components=[events_], deploy_env=deploy_env, detail="Events Buses"
            ),
            env=env,
            termination_protection=True,
            # --- ^ super() ---
            base_stack=cdk_lion_base_stack,
            component=global_,
            deploy_env=deploy_env,
            env_meta=env_meta,
            factory=factory,
            project_name=lion_,
        )
        for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
    }
    factory.add_tags_required_wrapper(cdk_lion_events_stacks, project_name=lion_, component=global_)

    cdk_lion_storage_stacks: dict[str, CdkLionStorageStack] = {}
    if env.region == lion_global_region:
        cdk_lion_storage_stacks = {
            deploy_env: CdkLionStorageStack(
                scope=app,
                id=factory.get_cdk_stack_id(lion_, components=[storage_], deploy_env=deploy_env),
                description=factory.get_cdk_stack_description(
                    lion_, components=[storage_], deploy_env=deploy_env, detail="S3"
                ),
                env=env,
                termination_protection=True,
                # --- ^ super() ---
                base_stack=cdk_lion_base_stack,
                component=global_,
                deploy_env=deploy_env,
                env_meta=env_meta,
                event_bus_regions=lion_ms_regions_set,
                events_stack=cdk_lion_events_stacks[deploy_env],
                factory=factory,
                project_name=lion_,
            )
            for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
        }
        factory.add_tags_required_wrapper(cdk_lion_storage_stacks, project_name=lion_, component=global_)

        cdk_lion_collector_stacks: dict[str, CdkLionCollectorStack] = {
            deploy_env: CdkLionCollectorStack(
                scope=app,
                id=factory.get_cdk_stack_id(lion_, components=[collector_], deploy_env=deploy_env),
                description=factory.get_cdk_stack_description(
                    lion_, components=[collector_], deploy_env=deploy_env, detail="Step Functions, Lambda functions"
                ),
                env=env,
                termination_protection=True,
                # --- ^ super() ---
                base_stack=cdk_lion_base_stack,
                component=global_,
                deploy_env=deploy_env,
                env_meta=env_meta,
                factory=factory,
                project_name=lion_,
                pypi_package_base_stack=cdk_pypi_package_base_stack,
                storage_stack=cdk_lion_storage_stacks[deploy_env],
                vpc_stack=cdk_vpc_sih_stack,
            )
            for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
        }
        factory.add_tags_required_wrapper(cdk_lion_collector_stacks, project_name=lion_, component=global_)

        cdk_lion_processor_stacks: dict[str, CdkLionProcessorStack] = {
            deploy_env: CdkLionProcessorStack(
                scope=app,
                id=factory.get_cdk_stack_id(lion_, components=[processor_], deploy_env=deploy_env),
                description=factory.get_cdk_stack_description(
                    lion_, components=[processor_], deploy_env=deploy_env, detail="Step Functions, Lambda functions"
                ),
                env=env,
                termination_protection=True,
                # --- ^ super() ---
                base_stack=cdk_lion_base_stack,
                component=global_,
                deploy_env=deploy_env,
                env_meta=env_meta,
                factory=factory,
                project_name=lion_,
                pypi_package_base_stack=cdk_pypi_package_base_stack,
                storage_stack=cdk_lion_storage_stacks[deploy_env],
                vpc_stack=cdk_vpc_sih_stack,
            )
            for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
        }
        factory.add_tags_required_wrapper(cdk_lion_processor_stacks, project_name=lion_, component=global_)

    cdk_lion_cache_stacks: dict[str, CdkLionCacheStack] = {
        deploy_env: CdkLionCacheStack(
            scope=app,
            id=factory.get_cdk_stack_id(lion_, components=[cache_], deploy_env=deploy_env),
            description=factory.get_cdk_stack_description(
                lion_, components=[cache_], deploy_env=deploy_env, detail="ElastiCache Redis"
            ),
            env=env,
            termination_protection=factory.get_termination_protection(deploy_env),
            # --- ^ super() ---
            base_stack=cdk_lion_base_stack,
            component=ms_,
            deploy_env=deploy_env,
            deploy_env_24_7_set=deploy_env_24_7_sets[lion_],
            deploy_env_weekend_set=deploy_env_weekend_sets[lion_],
            env_meta=env_meta,
            factory=factory,
            project_name=lion_,
            vpc_stack=cdk_vpc_sih_stack,
        )
        for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
    }
    factory.add_tags_required_wrapper(cdk_lion_cache_stacks, project_name=lion_, component=cache_, is_cache=True)

    cdk_lion_ms_stacks = {
        deploy_env: CdkLionMsStack(
            scope=app,
            id=factory.get_cdk_stack_id(lion_, components=[ms_], deploy_env=deploy_env),
            description=factory.get_cdk_stack_description(
                lion_, components=[ms_], deploy_env=deploy_env, detail="CloudFront Distribution, ALB, ECS"
            ),
            env=env,
            termination_protection=factory.get_termination_protection(deploy_env),
            # --- ^ super() ---
            base_stack=cdk_lion_base_stack,
            cache_regions=[k for k, v in lion_cache_region_meta.items() if env.region == v[0]],
            cache_stack=cdk_lion_cache_stacks[deploy_env],
            component=ms_,
            deploy_env=deploy_env,
            deploy_env_24_7_set=deploy_env_24_7_sets[lion_],
            deploy_env_weekend_set=deploy_env_weekend_sets[lion_],
            env_meta=env_meta,
            factory=factory,
            project_name=lion_,
            vpc_stack=cdk_vpc_sih_stack,
        )
        for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
    }
    project_dependant_map[lion_] = cdk_lion_ms_stacks
    factory.add_tags_required_wrapper(cdk_lion_ms_stacks, project_name=lion_, component=ms_)

    cdk_lion_ms_pipeline_stacks: dict[str, CdkLionPipelineStack] = {
        deploy_env: CdkLionPipelineStack(
            scope=app,
            id=factory.get_cdk_stack_id(lion_, components=[ms_, pipeline_], deploy_env=deploy_env),
            description=factory.get_cdk_stack_description(
                lion_, components=[ms_, pipeline_], deploy_env=deploy_env, detail="CodeBuild, CodePipeline"
            ),
            env=env,
            termination_protection=factory.get_termination_protection(deploy_env),
            # --- ^ super() ---
            base_stack=cdk_lion_base_stack,
            component=ms_,
            deploy_env=deploy_env,
            env_meta=env_meta,
            factory=factory,
            ms_stack=cdk_lion_ms_stacks[deploy_env],
            project_name=lion_,
            project_name_comp_list=project_name_comp_lists[lion_],
            pypi_base_stack=cdk_pypi_base_stack,
            vpc_stack=cdk_vpc_sih_stack,
        )
        for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
    }
    factory.add_tags_required_wrapper(cdk_lion_ms_pipeline_stacks, project_name=lion_, component=pipeline_)

    # TODO: (NEXT) Handle when LION 'storage_stack' is in a different AWS region to the LION Extractor
    cdk_lion_extractor_stacks: dict[str, CdkLionExtractorStack] = {
        deploy_env: CdkLionExtractorStack(
            scope=app,
            id=factory.get_cdk_stack_id(lion_, components=[extractor_], deploy_env=deploy_env),
            description=factory.get_cdk_stack_description(
                lion_, components=[extractor_], deploy_env=deploy_env, detail="Lambda functions"
            ),
            env=env,
            termination_protection=factory.get_termination_protection(deploy_env),
            # --- ^ super() ---
            base_stack=cdk_lion_base_stack,
            cache_regions={k: v[1] for k, v in lion_cache_region_meta.items() if env.region == v[0]},
            cache_stack=cdk_lion_cache_stacks[deploy_env],
            component=ms_,
            deploy_env=deploy_env,
            lion_global_region=lion_global_region,
            env_meta=env_meta,
            events_stack=cdk_lion_events_stacks[deploy_env],
            factory=factory,
            project_name=lion_,
            pypi_package_base_stack=cdk_pypi_package_base_stack,
            storage_stack=cdk_lion_storage_stacks.get(deploy_env),
            vpc_stack=cdk_vpc_sih_stack,
        )
        for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
    }
    factory.add_tags_required_wrapper(cdk_lion_extractor_stacks, project_name=lion_, component=extractor_)

####################################################################################################
# --- Bkg ---
####################################################################################################

cdk_bkg_cloudfront_base_stack = CdkBkgCloudFrontBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(bkg_, components=[cf_], base_comp=True),
    description=factory.get_cdk_stack_description(
        bkg_, components=[cf_], base_comp=True, detail="WAF Regex Pattern Set"
    ),
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_bkg_base_stack,
    component=ms_,
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    project_name=bkg_,
)
factory.add_tags_required(
    stacks=[cdk_bkg_base_stack, cdk_bkg_cloudfront_base_stack],
    project_name_val=word_map[bkg_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_bkg_ms_cloudfront_stacks: dict[str, CdkBkgCloudFrontStack] = {
    deploy_env: CdkBkgCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(bkg_, components=[ms_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bkg_, components=[ms_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_bkg_base_stack,
        cloudfront_base_stack=cdk_bkg_cloudfront_base_stack,
        component=ms_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=bkg_,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_bkg_ms_cloudfront_stacks, project_name=bkg_, component=cf_)

cdk_bkg_cache_stacks: dict[str, CdkBkgCacheStack] = {
    deploy_env: CdkBkgCacheStack(
        scope=app,
        id=factory.get_cdk_stack_id(bkg_, components=[cache_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bkg_, components=[cache_], deploy_env=deploy_env, detail="ElastiCache Redis"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bkg_base_stack,
        component=ms_,
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[bkg_],
        deploy_env_weekend_set=deploy_env_weekend_sets[bkg_],
        env_meta=env_meta,
        factory=factory,
        project_name=bkg_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_bkg_cache_stacks, project_name=bkg_, component=cache_, is_cache=True)

cdk_bkg_broker_stacks: dict[str, CdkBkgBrokerStack] = {
    deploy_env: CdkBkgBrokerStack(
        scope=app,
        id=factory.get_cdk_stack_id(bkg_, components=[broker_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bkg_, components=[broker_], deploy_env=deploy_env, detail="Amazon MQ RabbitMQ"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bkg_base_stack,
        component=ms_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        mq_rabbitmq_user_prefix=sih_,
        project_name=bkg_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_bkg_broker_stacks, project_name=bkg_, component=broker_)

cdk_bkg_mq_cloudfront_stacks: dict[str, CdkBkgCloudFrontStack] = {
    deploy_env: CdkBkgCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(bkg_, components=[broker_web_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bkg_, components=[broker_web_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_bkg_base_stack,
        cloudfront_base_stack=cdk_bkg_cloudfront_base_stack,
        component=broker_web_,
        component_alt=broker_web_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=bkg_,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_bkg_mq_cloudfront_stacks, project_name=bkg_, component=cf_)

cdk_bkg_mq_stacks: dict[str, CdkBkgMqStack] = {
    deploy_env: CdkBkgMqStack(
        scope=app,
        id=factory.get_cdk_stack_id(bkg_, components=[broker_web_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bkg_, components=[broker_web_], deploy_env=deploy_env, detail="Amazon MQ RabbitMQ Web Console"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bkg_base_stack,
        broker_stack=cdk_bkg_broker_stacks[deploy_env],
        component=broker_web_,
        component_alt=broker_web_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=bkg_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_bkg_mq_stacks, project_name=bkg_, component=broker_)

cdk_bkg_database_stacks: dict[str, CdkBkgDatabaseStack] = {
    deploy_env: CdkBkgDatabaseStack(
        scope=app,
        id=factory.get_cdk_stack_id(bkg_, components=[database_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bkg_, components=[database_], deploy_env=deploy_env, detail="DynamoDB"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bkg_base_stack,
        component=ms_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=bkg_,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_bkg_database_stacks, project_name=bkg_, component=database_, is_db_server=True)

cdk_bkg_storage_stacks: dict[str, CdkBkgStorageStack] = {
    deploy_env: CdkBkgStorageStack(
        scope=app,
        id=factory.get_cdk_stack_id(bkg_, components=[storage_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(bkg_, components=[storage_], deploy_env=deploy_env, detail="S3"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bkg_base_stack,
        component=ms_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=bkg_,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_bkg_storage_stacks, project_name=bkg_, component=ms_)

cdk_bkg_ms_stacks: dict[str, CdkBkgMsStack] = {
    deploy_env: CdkBkgMsStack(
        scope=app,
        id=factory.get_cdk_stack_id(bkg_, components=[ms_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bkg_, components=[ms_], deploy_env=deploy_env, detail="CloudFront Distribution, ALB, ECS"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bkg_base_stack,
        broker_stack=cdk_bkg_broker_stacks[deploy_env],
        cache_stack=cdk_bkg_cache_stacks[deploy_env],
        component=ms_,
        database_stack=cdk_bkg_database_stacks[deploy_env],
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[bkg_],
        deploy_env_weekend_set=deploy_env_weekend_sets[bkg_],
        ecs_container_service_access={
            getattr(s, factory.HOSTED_ZONE_NAME_): getattr(s, factory.MAIL_USER_, None)
            for s in [
                cdk_dog_base_stack,
                cdk_cat_base_stack,
                cdk_bird_base_stack,
                cdk_fish_base_stack,
            ]
        },
        ecs_container_service_access_task_subscriptions={
            getattr(s, factory.HOSTED_ZONE_NAME_): s.task_subscriptions
            for s in [cdk_dog_base_stack, cdk_cat_base_stack, cdk_bird_base_stack]
        },
        lion_ms_stack=get_lion_ms_stack(bkg_, deploy_env),
        env_meta=env_meta,
        factory=factory,
        project_name=bkg_,
        project_name_comp_subs={
            k: (word_map[k], v, bool(k == api_), cpu_unit_weightings[k])
            for k, v in cdk_bkg_base_stack.comp_sub_ports.items()
            if (cpu_unit_weightings := {k: v[1] for k, v in bkg_ms_comp_subs_meta.items()})
        },
        ses_lambda_func=cdk_mail_ms_stacks[factory.PROD_].ses_lambda_func,
        storage_stack=cdk_bkg_storage_stacks[deploy_env],
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
project_dependant_map[bkg_] = cdk_bkg_ms_stacks
factory.add_tags_required_wrapper(cdk_bkg_ms_stacks, project_name=bkg_, component=ms_)

cdk_bkg_ms_pipeline_stacks: dict[str, CdkBkgPipelineStack] = {
    deploy_env: CdkBkgPipelineStack(
        scope=app,
        id=factory.get_cdk_stack_id(bkg_, components=[ms_, pipeline_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bkg_, components=[ms_, pipeline_], deploy_env=deploy_env, detail="CodeBuild, CodePipeline"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bkg_base_stack,
        component=ms_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        ms_stack=cdk_bkg_ms_stacks[deploy_env],
        project_name=bkg_,
        project_name_comp_list=project_name_comp_lists[bkg_],
        pypi_base_stack=cdk_pypi_base_stack,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_bkg_ms_pipeline_stacks, project_name=bkg_, component=pipeline_)

####################################################################################################
# --- Dog ---
####################################################################################################

cdk_dog_cloudfront_base_stack = CdkDogCloudFrontBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(dog_, components=[cf_], base_comp=True),
    description=factory.get_cdk_stack_description(
        dog_, components=[cf_], base_comp=True, detail="WAF Regex Pattern Set"
    ),
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_dog_base_stack,
    component=gw_,
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    project_name=dog_,
)
factory.add_tags_required(
    stacks=[cdk_dog_base_stack, cdk_dog_cloudfront_base_stack],
    project_name_val=word_map[dog_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_dog_gw_cloudfront_stacks: dict[str, CdkDogCloudFrontStack] = {
    deploy_env: CdkDogCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[gw_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_, components=[gw_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        cloudfront_base_stack=cdk_dog_cloudfront_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=dog_,
    )
    for deploy_env, env_meta in deploy_envs_metas[dog_].items()
}
factory.add_tags_required_wrapper(cdk_dog_gw_cloudfront_stacks, project_name=dog_, component=cf_)

cdk_dog_database_stacks: dict[str, CdkDogDatabaseStack] = {
    database_server: CdkDogDatabaseStack(
        scope=app,
        id=factory.get_cdk_stack_id(
            dog_, components=[database_], deploy_env=factory.format_database_server(database_server)
        ),
        description=factory.get_cdk_stack_description(
            dog_,
            components=[database_],
            deploy_env=factory.format_database_server(database_server, hyphen_sep=True),
            detail="RDS",
        ),
        env=env,
        termination_protection=factory.get_termination_protection(database_server),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=gw_,
        database_meta=database_meta,
        db_server_name=database_server,
        db_server_preview_demo=get_db_server_preview_demo(dog_, database_server),
        deploy_env_24_7_set=deploy_env_24_7_sets[dog_],
        deploy_env_weekend_set=deploy_env_weekend_sets[dog_],
        factory=factory,
        project_name=dog_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for database_server, database_meta in database_server_deploy_env_maps[dog_].items()
}
factory.add_tags_required_wrapper(
    cdk_dog_database_stacks,
    project_name=dog_,
    component=database_,
    is_db_server=True,
)

cdk_dog_cache_stacks: dict[str, CdkDogCacheStack] = {
    deploy_env: CdkDogCacheStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[cache_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_, components=[cache_], deploy_env=deploy_env, detail="ElastiCache Redis"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[dog_],
        deploy_env_weekend_set=deploy_env_weekend_sets[dog_],
        env_meta=env_meta,
        factory=factory,
        project_name=dog_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[dog_].items()
}
factory.add_tags_required_wrapper(
    cdk_dog_cache_stacks,
    project_name=dog_,
    component=cache_,
    is_cache=True,
)

cdk_dog_storage_stacks: dict[str, CdkDogStorageStack] = {
    deploy_env: CdkDogStorageStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[storage_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(dog_, components=[storage_], deploy_env=deploy_env, detail="S3"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=dog_,
    )
    for deploy_env, env_meta in deploy_envs_metas[dog_].items()
}
factory.add_tags_required_wrapper(cdk_dog_storage_stacks, project_name=dog_, component=gw_)

cdk_dog_notif_stacks: dict[str, CdkDogNotifStack] = {
    deploy_env: CdkDogNotifStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[notif_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(dog_, components=[notif_], deploy_env=deploy_env, detail="SNS"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=dog_,
    )
    for deploy_env, env_meta in deploy_envs_metas[dog_].items()
}
factory.add_tags_required_wrapper(
    cdk_dog_notif_stacks,
    project_name=dog_,
    component=gw_,
)

cdk_dog_gw_stacks: dict[str, CdkDogGwStack] = {
    deploy_env: CdkDogGwStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[gw_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_, components=[gw_], deploy_env=deploy_env, detail="CloudFront Distribution, ALB, ECS"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        bkg_ms_stack=get_bkg_ms_stack(dog_, deploy_env),
        cache_stack=cdk_dog_cache_stacks[deploy_env],
        component=gw_,
        database_stack=cdk_dog_database_stacks[deploy_env_database_server_maps[dog_][deploy_env]],
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[dog_],
        deploy_env_weekend_set=deploy_env_weekend_sets[dog_],
        lion_ms_stack=get_lion_ms_stack(dog_, deploy_env),
        env_meta=env_meta,
        factory=factory,
        mail_ms_stack=cdk_mail_ms_stacks[factory.PROD_],
        notif_stack=cdk_dog_notif_stacks[deploy_env],
        pdf_ms_stack=cdk_pdf_ms_stacks[factory.PROD_],
        project_name=dog_,
        storage_stack=cdk_dog_storage_stacks[deploy_env],
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[dog_].items()
}
factory.add_tags_required_wrapper(cdk_dog_gw_stacks, project_name=dog_, component=gw_)

cdk_dog_gw_pipeline_stacks: dict[str, CdkDogPipelineStack] = {
    deploy_env: CdkDogPipelineStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[gw_, pipeline_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_, components=[gw_, pipeline_], deploy_env=deploy_env, detail="CodeBuild, CodePipeline"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        gw_stack=cdk_dog_gw_stacks[deploy_env],
        project_name=dog_,
        project_name_comp_list=project_name_comp_lists[dog_],
        pypi_base_stack=cdk_pypi_base_stack,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[dog_].items()
}
factory.add_tags_required_wrapper(cdk_dog_gw_pipeline_stacks, project_name=dog_, component=pipeline_)

cdk_dog_em_cloudfront_stacks: dict[str, CdkDogCloudFrontStack] = {
    deploy_env: CdkDogCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[em_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_, components=[em_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        cloudfront_base_stack=cdk_dog_cloudfront_base_stack,
        component=em_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=dog_,
        wordpress=True,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_dog_em_cloudfront_stacks, project_name=dog_, component=cf_)

cdk_dog_em_database_stacks: dict[str, CdkDogDatabaseStack] = {
    database_server: CdkDogDatabaseStack(
        scope=app,
        id=factory.get_cdk_stack_id(
            dog_, components=[em_, database_], deploy_env=factory.format_database_server(database_server)
        ),
        description=factory.get_cdk_stack_description(
            dog_,
            components=[em_, database_],
            deploy_env=factory.format_database_server(database_server, hyphen_sep=True),
            detail="RDS",
        ),
        env=env,
        termination_protection=factory.get_termination_protection(database_server),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=em_,
        database_meta=database_meta,
        db_server_name=database_server,
        db_server_preview_demo=get_db_server_preview_demo(dog_, database_server),
        deploy_env_24_7_set=deploy_env_24_7_sets[dog_],
        deploy_env_weekend_set=deploy_env_weekend_sets[dog_],
        factory=factory,
        project_name=dog_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for database_server, database_meta in factory.database_server_deploy_env_stag_prod_map.items()
}
factory.add_tags_required_wrapper(
    cdk_dog_em_database_stacks,
    project_name=dog_,
    component=database_,
    is_db_server=True,
)

cdk_dog_em_fs_stacks: dict[str, CdkDogFsStack] = {
    deploy_env: CdkDogFsStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[em_, fs_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(dog_, components=[em_, fs_], deploy_env=deploy_env, detail="EFS"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=em_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=dog_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_dog_em_fs_stacks, project_name=dog_, component=em_)

cdk_dog_em_stacks: dict[str, CdkDogEmStack] = {
    deploy_env: CdkDogEmStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[em_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_, components=[em_], deploy_env=deploy_env, detail="CloudFront Distribution, ALB, ECS"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=em_,
        custom_subdomain="store",
        database_stack=cdk_dog_em_database_stacks[factory.deploy_env_database_server_map[deploy_env]],
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[dog_],
        deploy_env_weekend_set=deploy_env_weekend_sets[dog_],
        env_meta=env_meta,
        factory=factory,
        fs_stack=cdk_dog_em_fs_stacks[deploy_env],
        project_name=dog_,
        url_gw=getattr(cdk_dog_gw_stacks[factory.PROD_], factory.URL_PRIVATE_),
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_dog_em_stacks, project_name=dog_, component=em_)

cdk_dog_em_pipeline_stacks: dict[str, CdkDogPipelineStack] = {
    deploy_env: CdkDogPipelineStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, components=[em_, pipeline_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_, components=[em_, pipeline_], deploy_env=deploy_env, detail="CodeBuild, CodePipeline"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=em_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        gw_stack=cdk_dog_em_stacks[deploy_env],
        project_name=dog_,
        project_name_comp_list=[factory.join_sep_score([dog_, ecomm_])],
        pypi_base_stack=cdk_pypi_base_stack,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_dog_em_pipeline_stacks, project_name=dog_, component=pipeline_)

####################################################################################################
# --- Dog Custom ---
####################################################################################################

deploy_env_24_7_set_dog_spain: set[str] = set()
deploy_env_weekend_set_dog_spain: set[str] = set()

cdk_dog_custom_database_stacks: dict[str, CdkDogDatabaseStack] = {
    database_server: CdkDogDatabaseStack(
        scope=app,
        id=factory.get_cdk_stack_id(
            dog_,
            custom_val=factory.CUSTOM_,
            components=[database_],
            deploy_env=factory.format_database_server(database_server),
        ),
        description=factory.get_cdk_stack_description(
            dog_,
            custom_val=factory.CUSTOM_,
            components=[database_],
            deploy_env=factory.format_database_server(database_server, hyphen_sep=True),
            detail="RDS",
        ),
        env=env,
        termination_protection=factory.get_termination_protection(database_server),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=gw_,
        customisations=[spain_],
        database_meta=database_meta,
        db_server_name=database_server,
        db_server_preview_demo=None,
        deploy_env_24_7_set=deploy_env_24_7_set_dog_spain,
        deploy_env_weekend_set=deploy_env_weekend_set_dog_spain,
        factory=factory,
        project_name=dog_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for database_server, database_meta in factory.database_server_deploy_env_stag_prod_map.items()
}
factory.add_tags_required_wrapper(
    cdk_dog_custom_database_stacks,
    project_name=dog_,
    custom_val=factory.CUSTOM_,
    component=database_,
    is_db_server=True,
)

####################################################################################################
# --- Dog Spain ---
####################################################################################################

project_name_comp_list_dog_spain: list[str] = [factory.join_sep_score([dog_, spain_, gw_] + j) for j in [[], [base_]]]

cdk_dog_spain_base_stack = CdkDogSpainBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(dog_, custom_val=spain_, base_comp=True),
    description=factory.get_cdk_stack_description(
        dog_, custom_val=spain_, base_comp=True, detail="ECR, Secrets Manager"
    ),
    env=env,
    termination_protection=True,
    # --- ^ super() ---
    component=gw_,
    custom_val=spain_,
    elastic_ip_parameter_names=elastic_ip_parameter_names,
    factory=factory,
    project_name=dog_,
    project_name_comp_list=project_name_comp_list_dog_spain,
)
factory.add_tags_required(
    stacks=[cdk_dog_spain_base_stack],
    project_name_val=word_map[dog_],
    custom_val=word_map[spain_],
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_dog_spain_gw_cloudfront_stacks: dict[str, CdkDogCloudFrontStack] = {
    deploy_env: CdkDogCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, custom_val=spain_, components=[gw_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_,
            custom_val=spain_,
            components=[gw_, cf_],
            deploy_env=deploy_env,
            detail="ACM certificates, WAF Web ACLs",
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        cloudfront_base_stack=cdk_dog_cloudfront_base_stack,
        component=gw_,
        custom_val=spain_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=dog_,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(
    cdk_dog_spain_gw_cloudfront_stacks, project_name=dog_, custom_val=spain_, component=cf_
)

cdk_dog_spain_cache_stacks: dict[str, CdkDogCacheStack] = {
    deploy_env: CdkDogCacheStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, custom_val=spain_, components=[cache_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_, custom_val=spain_, components=[cache_], deploy_env=deploy_env, detail="ElastiCache Redis"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=gw_,
        custom_val=spain_,
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_set_dog_spain,
        deploy_env_weekend_set=deploy_env_weekend_set_dog_spain,
        env_meta=env_meta,
        factory=factory,
        project_name=dog_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(
    cdk_dog_spain_cache_stacks,
    project_name=dog_,
    component=cache_,
    is_cache=True,
)

cdk_dog_spain_storage_stacks: dict[str, CdkDogStorageStack] = {
    deploy_env: CdkDogStorageStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, custom_val=spain_, components=[storage_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_, custom_val=spain_, components=[storage_], deploy_env=deploy_env, detail="S3"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        component=gw_,
        custom_val=spain_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=dog_,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(cdk_dog_spain_storage_stacks, project_name=dog_, component=gw_)

cdk_dog_spain_gw_stacks: dict[str, CdkDogGwStack] = {
    deploy_env: CdkDogGwStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, custom_val=spain_, components=[gw_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_,
            custom_val=spain_,
            components=[gw_],
            deploy_env=deploy_env,
            detail="CloudFront Distribution, ALB, ECS",
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_base_stack,
        base_stack_alt=cdk_dog_spain_base_stack,
        bkg_ms_stack=get_bkg_ms_stack(dog_, deploy_env),
        cache_stack=cdk_dog_spain_cache_stacks[deploy_env],
        component=gw_,
        custom_val=spain_,
        database_stack=cdk_dog_custom_database_stacks[factory.deploy_env_database_server_map[deploy_env]],
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_set_dog_spain,
        deploy_env_weekend_set=deploy_env_weekend_set_dog_spain,
        lion_ms_stack=get_lion_ms_stack(dog_, deploy_env),
        env_meta=env_meta,
        factory=factory,
        mail_ms_stack=cdk_mail_ms_stacks[factory.PROD_],
        notif_stack=cdk_dog_notif_stacks[deploy_env],  # TODO: (NEXT) Add dedicated Notif CDK stacks for a custom
        pdf_ms_stack=cdk_pdf_ms_stacks[factory.PROD_],
        project_name=dog_,
        storage_stack=cdk_dog_spain_storage_stacks[deploy_env],
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(
    cdk_dog_spain_gw_stacks,
    project_name=dog_,
    custom_val=spain_,
    component=gw_,
)

cdk_dog_spain_gw_pipeline_stacks: dict[str, CdkDogPipelineStack] = {
    deploy_env: CdkDogPipelineStack(
        scope=app,
        id=factory.get_cdk_stack_id(dog_, custom_val=spain_, components=[gw_, pipeline_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            dog_,
            custom_val=spain_,
            components=[gw_, pipeline_],
            deploy_env=deploy_env,
            detail="CodeBuild, CodePipeline",
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_dog_spain_base_stack,
        component=gw_,
        custom_val=spain_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        gw_stack=cdk_dog_spain_gw_stacks[deploy_env],
        project_name=dog_,
        project_name_comp_list=project_name_comp_list_dog_spain,
        pypi_base_stack=cdk_pypi_base_stack,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in factory.deploy_envs_stag_prod_meta.items()
}
factory.add_tags_required_wrapper(
    cdk_dog_spain_gw_pipeline_stacks, project_name=dog_, custom_val=spain_, component=pipeline_
)

####################################################################################################
# --- Cat ---
####################################################################################################

cdk_cat_cloudfront_base_stack = CdkCatCloudFrontBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(cat_, components=[cf_], base_comp=True),
    description=factory.get_cdk_stack_description(
        cat_, components=[cf_], base_comp=True, detail="WAF Regex Pattern Set"
    ),
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_cat_base_stack,
    component=gw_,
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    project_name=cat_,
)
factory.add_tags_required(
    stacks=[cdk_cat_base_stack, cdk_cat_cloudfront_base_stack],
    project_name_val=word_map[cat_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_cat_gw_cloudfront_stacks: dict[str, CdkCatCloudFrontStack] = {
    deploy_env: CdkCatCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(cat_, components=[gw_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cat_, components=[gw_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_cat_base_stack,
        cloudfront_base_stack=cdk_cat_cloudfront_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=cat_,
    )
    for deploy_env, env_meta in deploy_envs_metas[cat_].items()
}
factory.add_tags_required_wrapper(cdk_cat_gw_cloudfront_stacks, project_name=cat_, component=cf_)

cdk_cat_database_stacks: dict[str, CdkCatDatabaseStack] = {
    database_server: CdkCatDatabaseStack(
        scope=app,
        id=factory.get_cdk_stack_id(
            cat_, components=[database_], deploy_env=factory.format_database_server(database_server)
        ),
        description=factory.get_cdk_stack_description(
            cat_,
            components=[database_],
            deploy_env=factory.format_database_server(database_server, hyphen_sep=True),
            detail="RDS",
        ),
        env=env,
        termination_protection=factory.get_termination_protection(database_server),
        # --- ^ super() ---
        base_stack=cdk_cat_base_stack,
        component=gw_,
        database_meta=database_meta,
        db_server_name=database_server,
        db_server_preview_demo=get_db_server_preview_demo(cat_, database_server),
        deploy_env_24_7_set=deploy_env_24_7_sets[cat_],
        deploy_env_weekend_set=deploy_env_weekend_sets[cat_],
        factory=factory,
        project_name=cat_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for database_server, database_meta in database_server_deploy_env_maps[cat_].items()
}
factory.add_tags_required_wrapper(
    cdk_cat_database_stacks,
    project_name=cat_,
    component=database_,
    is_db_server=True,
)

cdk_cat_cache_stacks: dict[str, CdkCatCacheStack] = {
    deploy_env: CdkCatCacheStack(
        scope=app,
        id=factory.get_cdk_stack_id(cat_, components=[cache_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cat_, components=[cache_], deploy_env=deploy_env, detail="ElastiCache Redis"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cat_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[cat_],
        deploy_env_weekend_set=deploy_env_weekend_sets[cat_],
        env_meta=env_meta,
        factory=factory,
        project_name=cat_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[cat_].items()
}
factory.add_tags_required_wrapper(
    cdk_cat_cache_stacks,
    project_name=cat_,
    component=cache_,
    is_cache=True,
)

cdk_cat_storage_stacks: dict[str, CdkCatStorageStack] = {
    deploy_env: CdkCatStorageStack(
        scope=app,
        id=factory.get_cdk_stack_id(cat_, components=[storage_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(cat_, components=[storage_], deploy_env=deploy_env, detail="S3"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cat_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=cat_,
    )
    for deploy_env, env_meta in deploy_envs_metas[cat_].items()
}
factory.add_tags_required_wrapper(cdk_cat_storage_stacks, project_name=cat_, component=gw_)

cdk_cat_notif_stacks: dict[str, CdkCatNotifStack] = {
    deploy_env: CdkCatNotifStack(
        scope=app,
        id=factory.get_cdk_stack_id(cat_, components=[notif_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(cat_, components=[notif_], deploy_env=deploy_env, detail="SNS"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cat_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=cat_,
    )
    for deploy_env, env_meta in deploy_envs_metas[cat_].items()
}
factory.add_tags_required_wrapper(
    cdk_cat_notif_stacks,
    project_name=cat_,
    component=gw_,
)

cdk_cat_gw_stacks: dict[str, CdkCatGwStack] = {
    deploy_env: CdkCatGwStack(
        scope=app,
        id=factory.get_cdk_stack_id(cat_, components=[gw_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cat_, components=[gw_], deploy_env=deploy_env, detail="CloudFront Distribution, ALB, ECS"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cat_base_stack,
        bkg_ms_stack=get_bkg_ms_stack(cat_, deploy_env),
        cache_stack=cdk_cat_cache_stacks[deploy_env],
        component=gw_,
        database_stack=cdk_cat_database_stacks[deploy_env_database_server_maps[cat_][deploy_env]],
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[cat_],
        deploy_env_weekend_set=deploy_env_weekend_sets[cat_],
        lion_ms_stack=get_lion_ms_stack(cat_, deploy_env),
        env_meta=env_meta,
        factory=factory,
        mail_ms_stack=cdk_mail_ms_stacks[factory.PROD_],
        notif_stack=cdk_cat_notif_stacks[deploy_env],
        pdf_ms_stack=cdk_pdf_ms_stacks[factory.PROD_],
        project_name=cat_,
        storage_stack=cdk_cat_storage_stacks[deploy_env],
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[cat_].items()
}
factory.add_tags_required_wrapper(cdk_cat_gw_stacks, project_name=cat_, component=gw_)

cdk_cat_gw_pipeline_stacks: dict[str, CdkCatPipelineStack] = {
    deploy_env: CdkCatPipelineStack(
        scope=app,
        id=factory.get_cdk_stack_id(cat_, components=[gw_, pipeline_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cat_, components=[gw_, pipeline_], deploy_env=deploy_env, detail="CodeBuild, CodePipeline"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cat_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        gw_stack=cdk_cat_gw_stacks[deploy_env],
        project_name=cat_,
        project_name_comp_list=project_name_comp_lists[cat_],
        pypi_base_stack=cdk_pypi_base_stack,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[cat_].items()
}
factory.add_tags_required_wrapper(cdk_cat_gw_pipeline_stacks, project_name=cat_, component=pipeline_)

####################################################################################################
# --- Bird ---
####################################################################################################

cdk_bird_cloudfront_base_stack = CdkBirdCloudFrontBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(bird_, components=[cf_], base_comp=True),
    description=factory.get_cdk_stack_description(
        bird_, components=[cf_], base_comp=True, detail="WAF Regex Pattern Set"
    ),
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_bird_base_stack,
    component=gw_,
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    project_name=bird_,
)
factory.add_tags_required(
    stacks=[cdk_bird_base_stack, cdk_bird_cloudfront_base_stack],
    project_name_val=word_map[bird_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_bird_gw_cloudfront_stacks: dict[str, CdkBirdCloudFrontStack] = {
    deploy_env: CdkBirdCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(bird_, components=[gw_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bird_, components=[gw_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_bird_base_stack,
        cloudfront_base_stack=cdk_bird_cloudfront_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=bird_,
    )
    for deploy_env, env_meta in deploy_envs_metas[bird_].items()
}
factory.add_tags_required_wrapper(cdk_bird_gw_cloudfront_stacks, project_name=bird_, component=cf_)

cdk_bird_database_stacks: dict[str, CdkBirdDatabaseStack] = {
    database_server: CdkBirdDatabaseStack(
        scope=app,
        id=factory.get_cdk_stack_id(
            bird_, components=[database_], deploy_env=factory.format_database_server(database_server)
        ),
        description=factory.get_cdk_stack_description(
            bird_,
            components=[database_],
            deploy_env=factory.format_database_server(database_server, hyphen_sep=True),
            detail="RDS",
        ),
        env=env,
        termination_protection=factory.get_termination_protection(database_server),
        # --- ^ super() ---
        base_stack=cdk_bird_base_stack,
        component=gw_,
        database_meta=database_meta,
        db_server_name=database_server,
        db_server_preview_demo=get_db_server_preview_demo(bird_, database_server),
        deploy_env_24_7_set=deploy_env_24_7_sets[bird_],
        deploy_env_weekend_set=deploy_env_weekend_sets[bird_],
        factory=factory,
        project_name=bird_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for database_server, database_meta in database_server_deploy_env_maps[bird_].items()
}
factory.add_tags_required_wrapper(
    cdk_bird_database_stacks,
    project_name=bird_,
    component=database_,
    is_db_server=True,
)

cdk_bird_cache_stacks: dict[str, CdkBirdCacheStack] = {
    deploy_env: CdkBirdCacheStack(
        scope=app,
        id=factory.get_cdk_stack_id(bird_, components=[cache_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bird_, components=[cache_], deploy_env=deploy_env, detail="ElastiCache Redis"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bird_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[bird_],
        deploy_env_weekend_set=deploy_env_weekend_sets[bird_],
        env_meta=env_meta,
        factory=factory,
        project_name=bird_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[bird_].items()
}
factory.add_tags_required_wrapper(
    cdk_bird_cache_stacks,
    project_name=bird_,
    component=cache_,
    is_cache=True,
)

cdk_bird_storage_stacks: dict[str, CdkBirdStorageStack] = {
    deploy_env: CdkBirdStorageStack(
        scope=app,
        id=factory.get_cdk_stack_id(bird_, components=[storage_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(bird_, components=[storage_], deploy_env=deploy_env, detail="S3"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bird_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=bird_,
    )
    for deploy_env, env_meta in deploy_envs_metas[bird_].items()
}
factory.add_tags_required_wrapper(cdk_bird_storage_stacks, project_name=bird_, component=gw_)

cdk_bird_notif_stacks: dict[str, CdkBirdNotifStack] = {
    deploy_env: CdkBirdNotifStack(
        scope=app,
        id=factory.get_cdk_stack_id(bird_, components=[notif_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(bird_, components=[notif_], deploy_env=deploy_env, detail="SNS"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bird_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=bird_,
    )
    for deploy_env, env_meta in deploy_envs_metas[bird_].items()
}
factory.add_tags_required_wrapper(
    cdk_bird_notif_stacks,
    project_name=bird_,
    component=gw_,
)

cdk_bird_gw_stacks: dict[str, CdkBirdGwStack] = {
    deploy_env: CdkBirdGwStack(
        scope=app,
        id=factory.get_cdk_stack_id(bird_, components=[gw_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bird_, components=[gw_], deploy_env=deploy_env, detail="CloudFront Distribution, ALB, ECS"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bird_base_stack,
        bkg_ms_stack=get_bkg_ms_stack(bird_, deploy_env),
        cache_stack=cdk_bird_cache_stacks[deploy_env],
        component=gw_,
        database_stack=cdk_bird_database_stacks[deploy_env_database_server_maps[bird_][deploy_env]],
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[bird_],
        deploy_env_weekend_set=deploy_env_weekend_sets[bird_],
        lion_ms_stack=get_lion_ms_stack(bird_, deploy_env),
        env_meta=env_meta,
        factory=factory,
        mail_ms_stack=cdk_mail_ms_stacks[factory.PROD_],
        notif_stack=cdk_bird_notif_stacks[deploy_env],
        pdf_ms_stack=cdk_pdf_ms_stacks[factory.PROD_],
        project_name=bird_,
        storage_stack=cdk_bird_storage_stacks[deploy_env],
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[bird_].items()
}
factory.add_tags_required_wrapper(cdk_bird_gw_stacks, project_name=bird_, component=gw_)

cdk_bird_gw_pipeline_stacks: dict[str, CdkBirdPipelineStack] = {
    deploy_env: CdkBirdPipelineStack(
        scope=app,
        id=factory.get_cdk_stack_id(bird_, components=[gw_, pipeline_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            bird_, components=[gw_, pipeline_], deploy_env=deploy_env, detail="CodeBuild, CodePipeline"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_bird_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        gw_stack=cdk_bird_gw_stacks[deploy_env],
        project_name=bird_,
        project_name_comp_list=project_name_comp_lists[bird_],
        pypi_base_stack=cdk_pypi_base_stack,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[bird_].items()
}
factory.add_tags_required_wrapper(cdk_bird_gw_pipeline_stacks, project_name=bird_, component=pipeline_)

####################################################################################################
# --- Cow ---
####################################################################################################

cdk_cow_cloudfront_base_stack = CdkCowCloudFrontBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(cow_, components=[cf_], base_comp=True),
    description=factory.get_cdk_stack_description(
        cow_, components=[cf_], base_comp=True, detail="WAF Regex Pattern Set"
    ),
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_cow_base_stack,
    component=gw_,
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    project_name=cow_,
)
factory.add_tags_required(
    stacks=[cdk_cow_base_stack, cdk_cow_cloudfront_base_stack],
    project_name_val=word_map[cow_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_cow_gw_cloudfront_stacks: dict[str, CdkCowCloudFrontStack] = {
    deploy_env: CdkCowCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(cow_, components=[gw_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cow_, components=[gw_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_cow_base_stack,
        cloudfront_base_stack=cdk_cow_cloudfront_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=cow_,
    )
    for deploy_env, env_meta in deploy_envs_metas[cow_].items()
}
factory.add_tags_required_wrapper(cdk_cow_gw_cloudfront_stacks, project_name=cow_, component=cf_)

cdk_cow_database_stacks: dict[str, CdkCowDatabaseStack] = {
    database_server: CdkCowDatabaseStack(
        scope=app,
        id=factory.get_cdk_stack_id(
            cow_, components=[database_], deploy_env=factory.format_database_server(database_server)
        ),
        description=factory.get_cdk_stack_description(
            cow_,
            components=[database_],
            deploy_env=factory.format_database_server(database_server, hyphen_sep=True),
            detail="RDS",
        ),
        env=env,
        termination_protection=factory.get_termination_protection(database_server),
        # --- ^ super() ---
        base_stack=cdk_cow_base_stack,
        component=gw_,
        database_meta=database_meta,
        db_server_name=database_server,
        db_server_preview_demo=get_db_server_preview_demo(cow_, database_server),
        deploy_env_24_7_set=deploy_env_24_7_sets[cow_],
        deploy_env_weekend_set=deploy_env_weekend_sets[cow_],
        factory=factory,
        project_name=cow_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for database_server, database_meta in database_server_deploy_env_maps[cow_].items()
}
factory.add_tags_required_wrapper(
    cdk_cow_database_stacks,
    project_name=cow_,
    component=database_,
    is_db_server=True,
)

cdk_cow_cache_stacks: dict[str, CdkCowCacheStack] = {
    deploy_env: CdkCowCacheStack(
        scope=app,
        id=factory.get_cdk_stack_id(cow_, components=[cache_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cow_, components=[cache_], deploy_env=deploy_env, detail="ElastiCache Redis"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cow_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[cow_],
        deploy_env_weekend_set=deploy_env_weekend_sets[cow_],
        env_meta=env_meta,
        factory=factory,
        project_name=cow_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[cow_].items()
}
factory.add_tags_required_wrapper(
    cdk_cow_cache_stacks,
    project_name=cow_,
    component=cache_,
    is_cache=True,
)

cdk_cow_gw_stacks: dict[str, CdkCowGwStack] = {
    deploy_env: CdkCowGwStack(
        scope=app,
        id=factory.get_cdk_stack_id(cow_, components=[gw_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cow_, components=[gw_], deploy_env=deploy_env, detail="CloudFront Distribution, ALB, ECS"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cow_base_stack,
        cache_stack=cdk_cow_cache_stacks[deploy_env],
        component=gw_,
        database_stack=cdk_cow_database_stacks[deploy_env_database_server_maps[cow_][deploy_env]],
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[cow_],
        deploy_env_weekend_set=deploy_env_weekend_sets[cow_],
        env_meta=env_meta,
        factory=factory,
        project_name=cow_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[cow_].items()
}
factory.add_tags_required_wrapper(cdk_cow_gw_stacks, project_name=cow_, component=gw_)

cdk_cow_gw_pipeline_stacks: dict[str, CdkCowPipelineStack] = {
    deploy_env: CdkCowPipelineStack(
        scope=app,
        id=factory.get_cdk_stack_id(cow_, components=[gw_, pipeline_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            cow_, components=[gw_, pipeline_], deploy_env=deploy_env, detail="CodeBuild, CodePipeline"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_cow_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        gw_stack=cdk_cow_gw_stacks[deploy_env],
        project_name=cow_,
        project_name_comp_list=project_name_comp_lists[cow_],
        pypi_base_stack=cdk_pypi_base_stack,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[cow_].items()
}
factory.add_tags_required_wrapper(cdk_cow_gw_pipeline_stacks, project_name=cow_, component=pipeline_)

####################################################################################################
# --- Fish ---
####################################################################################################

cdk_fish_cloudfront_base_stack = CdkFishCloudFrontBaseStack(
    scope=app,
    id=factory.get_cdk_stack_id(fish_, components=[cf_], base_comp=True),
    description=factory.get_cdk_stack_description(
        fish_, components=[cf_], base_comp=True, detail="WAF Regex Pattern Set"
    ),
    env=env_cloudfront,
    termination_protection=True,
    # --- ^ super() ---
    base_stack=cdk_fish_base_stack,
    component=gw_,
    elastic_ip_str_list=elastic_ip_str_list,
    factory=factory,
    project_name=fish_,
)
factory.add_tags_required(
    stacks=[cdk_fish_base_stack, cdk_fish_cloudfront_base_stack],
    project_name_val=word_map[fish_],
    custom_val=factory.TAG_VAL_NONE_,
    env_type_val=factory.TAG_VAL_NONE_,
    component_val=word_map[base_],
    deploy_env_val=factory.TAG_VAL_NONE_,
)

cdk_fish_gw_cloudfront_stacks: dict[str, CdkFishCloudFrontStack] = {
    deploy_env: CdkFishCloudFrontStack(
        scope=app,
        id=factory.get_cdk_stack_id(fish_, components=[gw_, cf_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            fish_, components=[gw_, cf_], deploy_env=deploy_env, detail="ACM certificates, WAF Web ACLs"
        ),
        env=env_cloudfront,
        termination_protection=True,
        # --- ^ super() ---
        base_stack=cdk_fish_base_stack,
        cloudfront_base_stack=cdk_fish_cloudfront_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=fish_,
    )
    for deploy_env, env_meta in deploy_envs_metas[fish_].items()
}
factory.add_tags_required_wrapper(cdk_fish_gw_cloudfront_stacks, project_name=fish_, component=cf_)

cdk_fish_database_stacks: dict[str, CdkFishDatabaseStack] = {
    database_server: CdkFishDatabaseStack(
        scope=app,
        id=factory.get_cdk_stack_id(
            fish_, components=[database_], deploy_env=factory.format_database_server(database_server)
        ),
        description=factory.get_cdk_stack_description(
            fish_,
            components=[database_],
            deploy_env=factory.format_database_server(database_server, hyphen_sep=True),
            detail="RDS",
        ),
        env=env,
        termination_protection=factory.get_termination_protection(database_server),
        # --- ^ super() ---
        base_stack=cdk_fish_base_stack,
        component=gw_,
        database_meta=database_meta,
        db_server_name=database_server,
        db_server_preview_demo=get_db_server_preview_demo(fish_, database_server),
        deploy_env_24_7_set=deploy_env_24_7_sets[fish_],
        deploy_env_weekend_set=deploy_env_weekend_sets[fish_],
        factory=factory,
        project_name=fish_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for database_server, database_meta in database_server_deploy_env_maps[fish_].items()
}
factory.add_tags_required_wrapper(
    cdk_fish_database_stacks,
    project_name=fish_,
    component=database_,
    is_db_server=True,
)

cdk_fish_cache_stacks: dict[str, CdkFishCacheStack] = {
    deploy_env: CdkFishCacheStack(
        scope=app,
        id=factory.get_cdk_stack_id(fish_, components=[cache_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            fish_, components=[cache_], deploy_env=deploy_env, detail="ElastiCache Redis"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_fish_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[fish_],
        deploy_env_weekend_set=deploy_env_weekend_sets[fish_],
        env_meta=env_meta,
        factory=factory,
        project_name=fish_,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[fish_].items()
}
factory.add_tags_required_wrapper(
    cdk_fish_cache_stacks,
    project_name=fish_,
    component=cache_,
    is_cache=True,
)

cdk_fish_storage_stacks: dict[str, CdkFishStorageStack] = {
    deploy_env: CdkFishStorageStack(
        scope=app,
        id=factory.get_cdk_stack_id(fish_, components=[storage_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(fish_, components=[storage_], deploy_env=deploy_env, detail="S3"),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_fish_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        project_name=fish_,
    )
    for deploy_env, env_meta in deploy_envs_metas[fish_].items()
}
factory.add_tags_required_wrapper(cdk_fish_storage_stacks, project_name=fish_, component=gw_)

cdk_fish_gw_stacks: dict[str, CdkFishGwStack] = {
    deploy_env: CdkFishGwStack(
        scope=app,
        id=factory.get_cdk_stack_id(fish_, components=[gw_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            fish_, components=[gw_], deploy_env=deploy_env, detail="CloudFront Distribution, ALB, ECS"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_fish_base_stack,
        cache_stack=cdk_fish_cache_stacks[deploy_env],
        component=gw_,
        database_stack=cdk_fish_database_stacks[deploy_env_database_server_maps[fish_][deploy_env]],
        deploy_env=deploy_env,
        deploy_env_24_7_set=deploy_env_24_7_sets[fish_],
        deploy_env_weekend_set=deploy_env_weekend_sets[fish_],
        env_meta=env_meta,
        factory=factory,
        mail_ms_stack=cdk_mail_ms_stacks[factory.PROD_],
        project_name=fish_,
        storage_stack=cdk_fish_storage_stacks[deploy_env],
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[fish_].items()
}
factory.add_tags_required_wrapper(cdk_fish_gw_stacks, project_name=fish_, component=gw_)

cdk_fish_gw_pipeline_stacks: dict[str, CdkFishPipelineStack] = {
    deploy_env: CdkFishPipelineStack(
        scope=app,
        id=factory.get_cdk_stack_id(fish_, components=[gw_, pipeline_], deploy_env=deploy_env),
        description=factory.get_cdk_stack_description(
            fish_, components=[gw_, pipeline_], deploy_env=deploy_env, detail="CodeBuild, CodePipeline"
        ),
        env=env,
        termination_protection=factory.get_termination_protection(deploy_env),
        # --- ^ super() ---
        base_stack=cdk_fish_base_stack,
        component=gw_,
        deploy_env=deploy_env,
        env_meta=env_meta,
        factory=factory,
        gw_stack=cdk_fish_gw_stacks[deploy_env],
        project_name=fish_,
        project_name_comp_list=project_name_comp_lists[fish_],
        pypi_base_stack=cdk_pypi_base_stack,
        vpc_stack=cdk_vpc_sih_stack,
    )
    for deploy_env, env_meta in deploy_envs_metas[fish_].items()
}
factory.add_tags_required_wrapper(cdk_fish_gw_pipeline_stacks, project_name=fish_, component=pipeline_)

####################################################################################################
# --- End of Infrastructure ---
####################################################################################################

app.synth()
