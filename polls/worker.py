import json
import time
import boto3
from monkeylearn import MonkeyLearn
# from configparser import ConfigParser
# from elasticsearch import Elasticsearch
from multiprocessing.dummy import Pool

sqs = boto3.resource(
    'sqs',
    aws_access_key_id='',
    aws_secret_access_key='',
)
queue = sqs.get_queue_by_name(QueueName='Tweets')

sns = boto3.resource(
    'sns',
    aws_access_key_id='',
    aws_secret_access_key='',
)

topic = sns.Topic('')

#MonkeyLearn Authentication
ml = MonkeyLearn('')

def getSentiment(tweetText):
    sentences = [ tweetText ]
    sentimentResult = ml.classifiers.classify('', sentences, sandbox=True).result
    # print(sentimentResult)
    for result in sentimentResult:
        sentiment = result[0]['label']
        return sentiment

def getSQSQueue(n):

    # code to retrieve all text data from the SQS

    messages = queue.receive_messages()
    count = 0
    for message in messages:
        try:
            tweet = json.loads(message.body)
            text = tweet["text"]
            sentiment = getSentiment(text)
            tweet["sentiment"] = sentiment
            #time.sleep(1)

            response = topic.publish(
                                    Message = json.dumps(tweet),
                                    MessageAttributes = {

                                    }
            )
            print(response)
            count += 1

        except Exception as e:
            print(e)


    return tweet


# function to be mapped over
def calculateParallel(numbers, threads):
    # configuring the worker pool
    pool = Pool(processes=1)
    results = pool.map(getSQSQueue,numbers)
    #print(results)
    pool.close()
    pool.join()
    return results




if __name__ == "__main__":

    numbers = [1, 2, 3, 4, 5, 6]

    while True:
        tweet_text = calculateParallel(numbers, 10)
        #print "Tweet is ", tweet_text
        #print(n)
