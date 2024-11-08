# TODO: (NEXT) Add tests for all CDK stacks, in separate test files as needed

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_sih/vpc_sih.py
# def test_sqs_queue_created():
#     app = core.App()
#     stack = CdkQueueStack()
#     template = assertions.Template.from_stack(stack)
#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
