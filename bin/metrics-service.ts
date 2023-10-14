#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { MetricsServiceStack } from "../lib/metrics-service";

const app = new cdk.App();
new MetricsServiceStack(app, "MetricsServiceStack", {
  env: { account: "302826945104", region: "ap-southeast-2" },
});
