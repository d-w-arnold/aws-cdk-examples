from aws_cdk import Stack, aws_ec2 as ec2

from cdk_sih.constructs.factory import CdkConstructsFactory
from cdk_sih.vpc_sih import CdkVpcSihStack


class CdkElasticIpsStack(Stack):
    def __init__(
        self,
        elastic_ip_str_list: list[str],
        factory: CdkConstructsFactory,
        vpc_stack: CdkVpcSihStack,
        **kwargs,
    ) -> None:
        setattr(self, factory.ENV_, factory.check_env_exists(kwargs))
        super().__init__(**kwargs)

        vpc_stack.set_attrs_vpc(self)

        self.elastic_ips: dict[str, ec2.CfnEIP] = {
            i: ec2.CfnEIP(scope=self, id=factory.get_construct_id(self, [i], "CfnEIP"), domain=factory.VPC_)
            for i in elastic_ip_str_list
        }
