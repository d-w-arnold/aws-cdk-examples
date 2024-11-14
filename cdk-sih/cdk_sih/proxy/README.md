# proxy-server

Inspired by (blog post): [How to Setup a Free Proxy Server on Amazon EC2](https://webrobots.io/how-to-setup-a-free-proxy-server-on-amazon-ec2/)

This Proxy server uses a [Tinyproxy](https://tinyproxy.github.io/) configuration, running on an EC2 instance** (with an Elastic IP), automatically created by an Auto Scaling Group (ASG).

Intended use with [CloudFront WAF Web ACLs, which restrict access to certain public IP addresses](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-awswaf.html).

[Configure in Postman proxy settings](https://learning.postman.com/docs/getting-started/proxy/)

See [Entrypoint](https://github.com/d-w-arnold/aws-cdk-examples/blob/main/cdk-sih/app.py) file, for CDK stack usages\*.

(*) Search: `CdkProxyServerStack`

### Get started provisioning CDK stack(s):

```bash
cdk diff CdkProxyServerStack
```

(**) See here for the [EC2 User Data](https://github.com/d-w-arnold/aws-ec2-examples/tree/main/proxy_server).
