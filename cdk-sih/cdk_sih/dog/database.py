from aws_cdk import aws_rds as rds

from cdk_sih.generic.database import CdkDatabaseStack


class CdkDogDatabaseStack(CdkDatabaseStack):
    def __init__(self, customisations: list[str] = None, **kwargs) -> None:
        super().__init__(customisations=customisations, engine_version=rds.MysqlEngineVersion.VER_8_0_35, **kwargs)
