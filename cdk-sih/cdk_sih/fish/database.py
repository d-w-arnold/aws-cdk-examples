from aws_cdk import aws_rds as rds

from cdk_sih.generic.database import CdkDatabaseStack


class CdkFishDatabaseStack(CdkDatabaseStack):
    def __init__(self, **kwargs) -> None:
        super().__init__(engine_version=rds.MysqlEngineVersion.VER_8_0_35, **kwargs)
