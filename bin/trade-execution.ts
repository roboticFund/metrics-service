#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { TradeExecutionStack } from "../lib/trade-execution-stack";

const app = new cdk.App();
new TradeExecutionStack(app, "TradeExecutionStack", {
  env: { account: "302826945104", region: "ap-southeast-2" },
});
