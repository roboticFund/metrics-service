import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";

export default async function getCustomerCredentials(): Promise<any> {
  const secret_name = "customer-broker-credentials";
  const client = new SecretsManagerClient();

  let response;

  try {
    response = await client.send(new GetSecretValueCommand({ SecretId: secret_name }));
  } catch (error) {
    // For a list of exceptions thrown, see
    // https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    throw error;
  }
  const secret = response.SecretString;
  console.log(`Secret is ${secret}`);
  return secret;
}
