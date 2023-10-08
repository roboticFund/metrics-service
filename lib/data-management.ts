import path = require("path");
import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sns from "aws-cdk-lib/aws-sns";
import * as iam from "aws-cdk-lib/aws-iam";
import * as secrets from "aws-cdk-lib/aws-secretsmanager";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { CodePipeline, CodePipelineSource, ShellStep } from "aws-cdk-lib/pipelines";

export class DataManagementStack extends cdk.Stack {
  appName = "data-management";

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create CI/CD pipeline
    const pipeline = new CodePipeline(this, `${this.appName}-pipeline`, {
      pipelineName: `${this.appName}-pipeline`,
      dockerEnabledForSynth: true,
      synth: new ShellStep("Synth", {
        input: CodePipelineSource.gitHub("roboticFund/data-management", "main"),
        commands: ["npm ci", "npm run build", "npx cdk synth"],
      }),
    });

    // // Create SNS topic to push new trade events too
    // const tradeBrokerResponseTopic = new sns.Topic(this, "tradeBrokerResponseTopic");
    // const tradeBrokerResponseTopicPolicy = new iam.PolicyStatement({
    //   actions: ["SNS:Publish"],
    //   resources: [tradeBrokerResponseTopic.topicArn],
    // });

    // // Main application to connect to IG broker
    // const marketDataLambda = new NodejsFunction(this, "market-data-lambda", {
    //   runtime: lambda.Runtime.NODEJS_LATEST,
    //   entry: path.join(__dirname, `/../resources/app.ts`),
    //   handler: "handler",
    //   environment: {},
    // });
    // tradeExecutionLambda.addToRolePolicy(tradeBrokerResponseTopicPolicy);
    // secrets.Secret.fromSecretNameV2(this, "customer-broker-credentials", "customer-broker-credentials").grantRead(tradeExecutionLambda);

    // Schema registry for genericError
    const genericErrorSchema = new cdk.aws_eventschemas.CfnSchema(this, "genericErrorSchema", {
      registryName: "roboticfund-custom-schema-registry",
      type: "JSONSchemaDraft4",
      content: JSON.stringify({
        datetime: "date-time",
        accountName: "string",
        originatingService: "string",
        inputEvent: "string",
        errorDescription: "string",
      }),
      description: "Schema for to define a generic error in any microservice. Will be stored in the DB according to this schema.",
      tags: [],
    });
  }
}
