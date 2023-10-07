import { APIGatewayProxyResult } from "aws-lambda";

// lambdaHandler takes event, e.g. {fromDate: 2022-03-01, toDate: 2022-03-02}
export const handler = async (event: any): Promise<APIGatewayProxyResult> => {
  return {
    statusCode: 200,
    body: `Successfully ran trade-execution-lambda`,
  };
};
