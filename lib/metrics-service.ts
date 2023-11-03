import path = require("path");
import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sns from "aws-cdk-lib/aws-sns";
import * as subs from "aws-cdk-lib/aws-sns-subscriptions";
import * as iam from "aws-cdk-lib/aws-iam";
import { CodePipeline, CodePipelineSource, ShellStep } from "aws-cdk-lib/pipelines";
import { standardMetrics } from "./metrics";

export class MetricsServiceStack extends cdk.Stack {
  appName = "metrics-service";

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create CI/CD pipeline
    const pipeline = new CodePipeline(this, `${this.appName}-pipeline`, {
      pipelineName: `${this.appName}-pipeline`,
      dockerEnabledForSynth: true,
      synth: new ShellStep("Synth", {
        input: CodePipelineSource.gitHub("roboticFund/metrics-service", "main"),
        commands: ["npm ci", "npm run build", "npx cdk synth"],
      }),
    });

    // Create SNS topic to push new trade events too
    const newMetricEventTopic = new sns.Topic(this, "newMetricEvent");
    const newMetricEventTopicPolicy = new iam.PolicyStatement({
      actions: ["SNS:Publish"],
      resources: [newMetricEventTopic.topicArn],
    });

    // Test new lambda using Docker
    const createMetricLambda = new lambda.Function(this, "create-metric-lambda", {
      runtime: lambda.Runtime.FROM_IMAGE,
      code: lambda.Code.fromAssetImage(path.join(__dirname, `/../resources/`)),
      handler: lambda.Handler.FROM_IMAGE,
      architecture: lambda.Architecture.ARM_64,
      environment: {},
    });
    createMetricLambda.addToRolePolicy(newMetricEventTopicPolicy);

    //Subscribe Lambda to newMarketDataEvent
    const newMarketDataEventTopic = sns.Topic.fromTopicArn(this, "newMarketDataEvent", "arn:aws:sns:ap-southeast-2:302826945104:DataManagementStack-newMarketDataEvent76B32543-axBYtKvlCazr");
    newMarketDataEventTopic.addSubscription(new subs.LambdaSubscription(createMetricLambda));

    // Schema registry for newMetricEventSchema
    const newMetricEventSchema = new cdk.aws_eventschemas.CfnSchema(this, "newMetricEventSchema", {
      registryName: "roboticfund-custom-schema-registry",
      type: "JSONSchemaDraft4",
      content: JSON.stringify({
        instrument: "string",
        inputEvent: "string",
        tick_10_min: {
          t0: standardMetrics,
          tMinus1: standardMetrics,
          tMinus2: standardMetrics,
        },
        tick_30_min: {
          t0: standardMetrics,
          tMinus1: standardMetrics,
          tMinus2: standardMetrics,
        },
      }),
      description: "Schema for to define a a new metric event which is the input into the trading decision logic.",
      tags: [],
    });
  }
}
