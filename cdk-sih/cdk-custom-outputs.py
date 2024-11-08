#!/usr/bin/env python3.9
import json
import os

encoding: str = "utf-8"
cdk_outputs_path: str = "cdk-outputs.json"
aws_profile: str = os.getenv("PROFILE")
cdk_custom_outputs_path: str = (
    f"{str(os.path.basename(__file__)).rsplit(sep='.', maxsplit=1)[0]}"
    f"{f'-{aws_profile.lower()}' if aws_profile else ''}.json"
)
print(f"## cdk_custom_outputs_path: {cdk_custom_outputs_path}")

with open(cdk_custom_outputs_path, "r", encoding=encoding) as f:
    cdk_custom_outputs_old: dict = json.load(f)

with open(cdk_outputs_path, "r", encoding=encoding) as f:
    outputs = json.load(f)
    cdk_custom_outputs_new: dict = {
        k: v for k, v in list(outputs.items()) if any(ext in k for ext in ["BastionHost", "Base", "CloudFront"])
    }
    if regional_outputs := {k: v for k, v in list(outputs.items()) if any(ext in k for ext in ["Events"])}:
        cdk_deploy_region: str = os.getenv("CDK_DEPLOY_REGION")
        cdk_custom_outputs_new = {
            **cdk_custom_outputs_new,
            **{cdk_deploy_region: {**cdk_custom_outputs_old[cdk_deploy_region], **regional_outputs}},
        }


with open(cdk_custom_outputs_path, "w+", encoding=encoding) as f:
    json.dump({**cdk_custom_outputs_old, **cdk_custom_outputs_new}, f, indent=2, sort_keys=True)
