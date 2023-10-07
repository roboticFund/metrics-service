import { APIGatewayProxyResult } from "aws-lambda";
import publishNewTradeEvent from "./utils/publishEvent";

// lambdaHandler takes event, e.g. {fromDate: 2022-03-01, toDate: 2022-03-02}
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
