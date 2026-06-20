#!/usr/bin/env python3
import aws_cdk as cdk
from cdk_stack import ChatbotRagStack

app = cdk.App()
ChatbotRagStack(app, "ChatbotRagBackendStack",
    env=cdk.Environment(
        account=cdk.Aws.ACCOUNT_ID,
        region=cdk.Aws.REGION
    )
)

app.synth()
