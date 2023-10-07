import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";
import customerCredential from "../schema/customerCredentials";

export default async function getCustomerCredentials(): Promise<customerCredential[]> {
  const secret_name = "customer-broker-credentials";
  const client = new SecretsManagerClient();
  let secretString: string;
  let response;
  let secretAsObject: customerCredential[];
  try {
    response = await client.send(new GetSecretValueCommand({ SecretId: secret_name }));
    secretString = response.SecretString as string;
    secretAsObject = JSON.parse(secretString);
  } catch (error) {
    throw error;
  }
  return secretAsObject;
}
