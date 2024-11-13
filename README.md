# aws-cdk-examples

What is [AWS Cloud Development Kit](https://docs.aws.amazon.com/cdk/v2/guide/home.html)?

For the existing `cdk-sih` CDK project, see:

- Entrypoint\* [cdk-sih/app.py](cdk-sih/app.py) file.

- Source [cdk-sih/cdk_sih](cdk-sih/cdk_sih) directory, containing all CDK stack classes.

- CDK constructs factory class [cdk-sih/cdk_sih/constructs/factory.py](cdk-sih/cdk_sih/constructs/factory.py) file.

(*) For the CDK app starting point, search: `# ---------- CDK app ----------`

---

### Create a new CDK Project

Use the convenient `cdk-init.sh` shell script:

```bash
# To create a CDK project called "cdk-my-project"
./cdk-init.sh cdk-my-project
```

### CDK project info

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project. The initialization process also creates a virtualenv within this
project, stored under the `venv`
directory. To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```bash
$ python3 -m venv venv
```

After the init process completes and the virtualenv is created, you can use the following step to activate your
virtualenv.

```bash
$ source venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ python3 -m pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add them to your `setup.py` file and rerun
the `python3 -m pip install -r requirements.txt`
command.

### Useful commands

* `cdk ls`          list all stacks in the app
* `cdk synth`       emits the synthesized CloudFormation template
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk docs`        open CDK documentation

### CDK Bootstrap

What is CDK [Bootstrapping](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)?

Use the `cdk bootstrap` command to bootstrap one or more AWS environments.

```bash
cdk bootstrap aws://ACCOUNT-NUMBER-1/REGION-1 aws://ACCOUNT-NUMBER-2/REGION-2 ...
```

The following examples illustrate bootstrapping of one and two environments, respectively. Note: The `aws://` prefix is optional when specifying an environment.

```bash
cdk bootstrap aws://123456789123/us-east-1
cdk bootstrap 123456789123/eu-west-2 123456789123/eu-west-1
````

Use the `--verbose` option to show debug logs.

```bash
cdk bootstrap --verbose 123456789123/eu-west-2
````

### CDK Deploy

Use the convenient `cdk-deploy-to-*.sh` shell scripts, to run CDK Deploy against your stacks.

See below example usages:

**Deploy to:** `123456789123` (foobar) account, in the `us-east-1` (N. Virginia) region, the
stacks (`CdkPypiCloudFrontStack`):

```bash
./cdk-deploy-to-sih-N-Virginia.sh CdkPypiCloudFrontStack
```

**Deploy to:** `123456789123` (foobar) account, in the `eu-west-2` (London) region, the
stacks (`CdkLambdaEc2InstanceAutoStack`,`CdkCodepipelineCiCdStack`):

```bash
./cdk-deploy-to-sih-London.sh CdkLambdaEc2InstanceAutoStack CdkCodepipelineCiCdStack
```

---

### Add Git Hooks

See `pre-push` shell script in `hooks/`.

When pushing to the `main` branch, a push is successful unless Black formatter returns a non-zero exit code, in which it
will show the diff regarding what Black would change.

To utilise this pre-push git hook, run the following commands in the project root directory:

```bash
# Copy all repo git hooks, into the `.git/hooks/` dir.
cp -av hooks/* .git/hooks

# Set all git hooks to executable, if not already set.
chmod +x .git/hooks/*
```
