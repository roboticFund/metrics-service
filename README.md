# metrics-service

## Useful commands

- `npm run build` compile typescript to js
- `npm run watch` watch for changes and compile
- `npm run test` perform the jest unit tests
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk synth` emits the synthesized CloudFormation template

## Commands to run locally (requires Docker)

Reference article - https://docs.aws.amazon.com/lambda/latest/dg/python-image.html

```
cd resources
docker build -t metrics-service:test .
docker run -p 9000:8080 metrics-service:test
```
