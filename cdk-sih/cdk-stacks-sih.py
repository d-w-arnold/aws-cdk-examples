#!/usr/bin/env python3.9
import json
import sys

encoding: str = "utf-8"
cdk_deployed_to_sih_path: str = "stacks.txt"

obj = json.load(sys.stdin)

stacks: list[str] = "\n".join([i for i in obj if i != "CDKToolkit"])

with open("stacks.txt", "w+", encoding=encoding) as f:
    f.write(stacks)

print(
    f"\nWritten list of deployed CDK stacks to: '{cdk_deployed_to_sih_path}'\n\n"
    f"# ---------- {cdk_deployed_to_sih_path} ----------\n{stacks}\n"
)
