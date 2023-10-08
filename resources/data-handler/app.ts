import { APIGatewayProxyResult } from "aws-lambda";

/****
  1. Decide which customer the trade event is for
  2. Load the customer's secrets + trading configuration (position size etc)
  3. Place trade on the configured brokers
  ***/
export const handler = async (event: any): Promise<APIGatewayProxyResult> => {
  return {
    statusCode: 200,
    body: `Successfully ran data-management-lambda`,
  };
};
