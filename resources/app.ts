import { APIGatewayProxyResult } from "aws-lambda";
import * as aws from "aws-sdk";

// lambdaHandler takes event, e.g. {fromDate: 2022-03-01, toDate: 2022-03-02}
export const handlerIG = async (event: any): Promise<APIGatewayProxyResult> => {
  var params = {
    Message: "Test Message",
    TopicArn: "arn:aws:sns:ap-southeast-2:302826945104:TradeExecutionStack-tradeBrokerResponseTopicD9846919-piHtcPICMuyH",
  };

  let publishTextPromise = new aws.SNS({ apiVersion: "2010-03-31" }).publish(params).promise();

  // Handle promise's fulfilled/rejected states
  await publishTextPromise
    .then(function (data) {
      console.log(`Message ${params.Message} sent to the topic ${params.TopicArn}`);
      console.log("MessageID is " + data.MessageId);
    })
    .catch(function (err) {
      console.error(err, err.stack);
    });

  return {
    statusCode: 200,
    body: `Successfully ran trade-execution-lambda`,
  };
};

export const handlerCI = async (event: any): Promise<APIGatewayProxyResult> => {
  return {
    statusCode: 200,
    body: `Successfully ran trade-execution-lambda`,
  };
};
