import json
import boto3
from utils.dbConnect import dbConnect
from utils.algoClass import AlgoClass

# Example input event
event = [{
    "instrument": "AUDUSD",
    "resolution": "MINUTE_10",
    "datetime": "2023-01-04 17:00:00",
    "snapshotTimeUTC": "2023-01-04 06:00:00",
    "openPrice": 0.68049,
    "closePrice": 0.68025,
    "highPrice": 0.68049,
    "lowPrice": 0.68024,
    "volume": 158,
  },{
    "instrument": "AUDUSD",
    "resolution": "MINUTE_30",
    "datetime": "2023-01-04 17:00:00",
    "snapshotTimeUTC": "2023-01-04 06:00:00",
    "openPrice": 0.68049,
    "closePrice": 0.68025,
    "highPrice": 0.68049,
    "lowPrice": 0.68024,
    "volume": 158,
  }]

# This function will listen to a new data event, e.g. new 10 MIN tick data.
def handler(event, context):
    
    print('request: {}'.format(json.dumps(event)))
    # con = dbConnect()

    # #Calcualte the metrics for the incoming tick, i.e. new 10 MIN metric tick data
    # for tick in event:
    #     algoClass = AlgoClass(tick, con)
    #     algoClass.saveTickMetricsToDB()
    
    # # Once metrics are saved to DB, query data to get all metrics to emit in message and emit publish event
    # client = boto3.client('sns')
    # client.publish(TargetArn="arn:aws:sns:ap-southeast-2:302826945104:MetricsServiceStack-newMetricEvent885A66BF-fgteNLvebgi4"
    #                 ,Message=returnDataForNewMetricEvent()
    #                 ,MessageStructure='json')
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, CDK! You have hit the metrics handler lambda'}


def returnDataForNewMetricEvent():
    # return all data for newMetric event
    pass