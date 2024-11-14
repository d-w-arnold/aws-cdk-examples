# ipsec-vpn-server

Inspired by (git repo): [hwdsl2/docker-ipsec-vpn-server](https://github.com/hwdsl2/docker-ipsec-vpn-server)

This IPsec VPN server uses a IPsec/L2TP configured docker image, running on an EC2 instance** (with an Elastic IP), automatically created by an Auto Scaling Group (ASG).

Intended use with [CloudFront WAF Web ACLs, which restrict access to certain public IP addresses](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-awswaf.html).

[How to setup VPN Clients](https://github.com/hwdsl2/setup-ipsec-vpn/blob/master/docs/clients.md)

See [Entrypoint](https://github.com/d-w-arnold/aws-cdk-examples/blob/main/cdk-sih/app.py) file, for CDK stack usages\*.

(*) Search: `CdkIpsecVpnServerStack`

### Get started provisioning CDK stack(s):

```bash
cdk diff CdkIpsecVpnServerStack
```

(**) See here for the [EC2 User Data](https://github.com/d-w-arnold/aws-ec2-examples/tree/main/ipsec_vpn_server).
