import boto3

###
# Once metrics are saved to DB, query data to get all metrics to emit in message and emit publish event
###


def publishEvent(event):
    client = boto3.client('sns')
    client.publish(TargetArn="arn:aws:sns:ap-southeast-2:302826945104:MetricsServiceStack-newMetricEvent885A66BF-fgteNLvebgi4",
                   Message=event, MessageStructure='json')
