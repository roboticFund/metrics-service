import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";

export default async function getCustomerCredentials(): Promise<any> {
  const secret_name = "customer-broker-credentials";
  const client = new SecretsManagerClient();
  let secretString: string;
  let response;
  let secretAsObject: any;

  try {
    response = await client.send(new GetSecretValueCommand({ SecretId: secret_name }));
    secretString = response.SecretString as string;
    secretAsObject = JSON.parse(secretString);
    console.log(`Secret is ${secretAsObject}`);
  } catch (error) {
    throw error;
  }

  return secretAsObject;
}
