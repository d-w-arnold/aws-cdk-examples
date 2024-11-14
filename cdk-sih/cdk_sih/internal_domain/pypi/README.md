# pypi-server

Inspired by (blog post): [Private PyPi Server on AWS](https://faun.pub/private-pypi-server-on-aws-with-terraform-1c6b9409b450)

This Python Package Index (PyPi) server uses a [pypiserver](https://pypi.org/project/pypiserver/) configuration, running on an EC2 instance** (with an Elastic IP), automatically created by an Auto Scaling Group (ASG), and served up at a custom URL (via CloudFront).

[Scripts to generate config files](https://github.com/d-w-arnold/aws-scripts-examples/blob/main/README.md#pypi-server): `.pypirc` and `pip.conf`

See [Entrypoint](https://github.com/d-w-arnold/aws-cdk-examples/blob/main/cdk-sih/app.py) file, for CDK stack usages\*.

(*) Search: `CdkPypiServerStack`

### Get started provisioning CDK stack(s):

```bash
cdk diff CdkPypiServerStack
```

(**) See here for the [EC2 User Data](https://github.com/d-w-arnold/aws-ec2-examples/tree/main/pypi_server).
