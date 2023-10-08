import path = require("path");
import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sns from "aws-cdk-lib/aws-sns";
import * as subs from "aws-cdk-lib/aws-sns-subscriptions";
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

    // Create SNS topic to push new trade events too
    const newMarketDataEventTopic = new sns.Topic(this, "newMarketDataEvent");
    const newMarketDataEventTopicPolicy = new iam.PolicyStatement({
      actions: ["SNS:Publish"],
      resources: [newMarketDataEventTopic.topicArn],
    });

    // Application to connect to get market data
    const marketDataLambda = new NodejsFunction(this, "market-data-lambda", {
      runtime: lambda.Runtime.NODEJS_LATEST,
      entry: path.join(__dirname, `/../resources/market-data/app.ts`),
      handler: "handler",
      environment: {},
    });
    marketDataLambda.addToRolePolicy(newMarketDataEventTopicPolicy);
    secrets.Secret.fromSecretNameV2(this, "customer-broker-credentials", "customer-broker-credentials").grantRead(marketDataLambda);

    // Application to listen to events and add data to RDS
    const dataHandler = new NodejsFunction(this, "data-handler", {
      runtime: lambda.Runtime.NODEJS_LATEST,
      entry: path.join(__dirname, `/../resources/data-handler/app.ts`),
      handler: "handler",
      environment: {},
    });

    //Get Topics and subscribe datahandler to them
    const tradeBrokerResponseTopic = sns.Topic.fromTopicArn(this, "tradeBrokerResponseTopic", "arn:aws:sns:ap-southeast-2:302826945104:TradeExecutionStack-tradeBrokerResponseTopicD9846919-piHtcPICMuyH");
    tradeBrokerResponseTopic.addSubscription(new subs.LambdaSubscription(dataHandler));

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
