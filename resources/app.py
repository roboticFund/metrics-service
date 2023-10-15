import json

# This function will listen to a new data event, e.g. new 10 MIN tick data.
# The handler will:
# 1. Calcualte the metrics for the incoming tick, i.e. new 10 MIN metric tick data
# 2. Save that data to DB, if saved successfully it will then
# 3. Retrieve other data from the the DB and publish a newMetricEvent

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, CDK! You have hit the metrics handler lambda'}
