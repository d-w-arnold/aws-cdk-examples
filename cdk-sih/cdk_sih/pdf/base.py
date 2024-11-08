from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecr as ecr,
)

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkPdfBaseStack(Stack):
    def __init__(
        self,
        component: str,
        factory: CdkConstructsFactory,
        project_name: str,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)
        factory.set_attrs_project_name_comp(self, project_name, component)

        self.codepipeline_source_repo: str = "aws-lambda"  # Git repo name, as shown in Bitbucket
        self.codepipeline_source_branch: str = "main"  # TODO: (OPTIONAL) Change branch for testing purposes

        # ---------- ECR ----------

        self.repo: ecr.Repository = factory.ecr_repository(self, factory.get_attr_project_name_comp(self))

        # ---------- EC2 ----------

        s3_lambda_sg_description = f"{factory.S3_.upper()} storage Lambda function"
        self.s3_lambda_sg = factory.ec2_security_group(
            self,
            [factory.S3_, factory.LAMBDA_],
            factory.join_sep_space(
                [factory.get_attr_word_map_project_name_comp(self, inc_deploy_env=False), s3_lambda_sg_description]
            ),
        )
        # [VPC traffic] -> (All TCP ports) -> S3 storage Lambda function
        self.s3_lambda_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(cidr_ip=factory.get_attr_vpc_cidr(self)),
            connection=ec2.Port.all_tcp(),
            description=factory.get_ec2_security_group_rule_description(
                f"VPC ({factory.get_attr_vpc_name(self)}) traffic"
            ),
        )
