# openvpn-vpn-server

Inspired by (git repo): [mattmcclean/openvpn-cdk-demo](https://github.com/mattmcclean/openvpn-cdk-demo/tree/master)

This OpenVPN server uses a [OpenVPN Access Server AMI](https://aws.amazon.com/marketplace/pp/prodview-y3m73u6jd5srk) configuration, running on an EC2 instance** (with an Elastic IP), automatically created by an Auto Scaling Group (ASG), and served up at a custom URL (via CloudFront).

Intended use with [CloudFront WAF Web ACLs, which restrict access to certain public IP addresses](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-awswaf.html).

[Scripts to support CDK stack(s) creation](https://github.com/d-w-arnold/aws-scripts-examples/blob/main/README.md#aws-openvpn-vpn-server-nlb)

See [Entrypoint](https://github.com/d-w-arnold/aws-cdk-examples/blob/main/cdk-sih/app.py) file, for CDK stack usages\*.

(*) Search: `CdkOpenvpnVpnServerStack`

### Get started provisioning CDK stack(s):

```bash
cdk diff CdkOpenvpnVpnServerStack
```

(**) See here for the [EC2 User Data](https://github.com/d-w-arnold/aws-ec2-examples/tree/main/openvpn_vpn_server).
