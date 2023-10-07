import * as aws from "aws-sdk";
import { tradeBrokerResponse } from "../schema/tradeBrokerResponse";

// Publish new trade event once complete
export default async function publishNewTradeEvent(body: tradeBrokerResponse): Promise<void> {
  const params = {
    Message: JSON.stringify(body),
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
}
