import { APIGatewayProxyResult } from "aws-lambda";
import publishNewTradeEvent from "./utils/publishEvent";
import getCustomerCredentials from "./utils/getSecrets";

// The event being passed is newTradeEvent. It will contain which account name it originated from
export const handler = async (event: any): Promise<APIGatewayProxyResult> => {
  // Load data from secrets manager and route to IG or CI handler
  let customerCredentials = await getCustomerCredentials();
  for (let customerCredential of customerCredentials) {
    console.log(customerCredential.accountName);
    if (customerCredential.accountName == event.accountName) {
      // Get broker, add to promises then execute
    } else {
      console.warn("There were not customer credentials that matched the inbound trade event");
    }
  }
  return {
    statusCode: 200,
    body: `Successfully ran trade-execution-lambda`,
  };
};

export const handlerIG = async (event: any): Promise<APIGatewayProxyResult> => {
  await publishNewTradeEvent({ account: "IG_ROBOTICFUND", broker: "IG" });
  return {
    statusCode: 200,
    body: `Successfully ran trade-execution-lambda`,
  };
};

export const handlerCI = async (event: any): Promise<APIGatewayProxyResult> => {
  await publishNewTradeEvent({ account: "CI_ROBOTICFUND", broker: "CI" });
  return {
    statusCode: 200,
    body: `Successfully ran trade-execution-lambda`,
  };
};
