import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sns from "aws-cdk-lib/aws-sns";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import path = require("path");
import { tradeBrokerResponse } from "../resources/schema/tradeBrokerResponse";

export class TradeExecutionStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Main application to connect to IG broker
    const tradeExecutionLambdaIG = new NodejsFunction(this, "trade-execution-lambda-ig", {
      runtime: lambda.Runtime.NODEJS_LATEST,
      entry: path.join(__dirname, `/../resources/app.ts`),
      handler: "handlerIG",
      environment: { BROKER: "IG" },
    });

    // Main application to connect to CityIndex broker
    const tradeExecutionLambdaCI = new NodejsFunction(this, "trade-execution-lambda-ci", {
      runtime: lambda.Runtime.NODEJS_LATEST,
      entry: path.join(__dirname, `/../resources/app.ts`),
      handler: "handlerCI",
      environment: { BROKER: "CI" },
    });

    // Need to create SNS topic to push new trade events too

    // Need to register schema
    const tradeBrokerResponseSchema = new cdk.aws_eventschemas.CfnSchema(this, "tradeBrokerResponseSchema", {
      registryName: "roboticfund-custom-schema-registry",
      type: "JSONSchemaDraft4",
      content: JSON.stringify(tradeBrokerResponse),
      description: "Schema for the response returned from the broker when attempting to place a trade.",
      tags: [],
    });
  }
}
