from django.shortcuts import render
import tweepy
import json
from textwrap import TextWrapper
import time
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import urllib3
from queue import Queue

flag = False
tweetQueue = Queue(maxsize=10)



consumer_key = 'YOUR_CONSUMER_KEY'
consumer_secret = 'YOUR_CONSUMER_SECRET_KEY'
access_token = 'YOUR_ACCESS_TOKEN'
access_secret = 'YOUR_ACCESS_SECRET_KEY'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)


es = Elasticsearch()
host = 'YOUR_ELASTIC_SEARCH_HOSTNAME'
awsauth = AWS4Auth('' , '','us-west-2', 'es')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
print(es.info())

class StreamListener(tweepy.StreamListener):
    status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')

    def __init__(self, time_limit=10):
        self.start_time = time.time()
        self.limit = time_limit
        super(StreamListener, self).__init__()

@csrf_exempt
def init_index(request):
    return render(request, 'index.html')

@csrf_exempt
def notifications(request):
    body = json.loads(request.body.decode("utf-8"))
    print(type(body))
    hdr = body['Type']

    if hdr == 'SubscriptionConfirmation':
        url = body['SubscribeURL']
        print("Subscription Confirmation - Visiting URL : " + url)
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        print(r.status)

    if hdr == 'Notification':
        print("SNS Notification")
        tweet = json.loads(body['Message'])
        es.index(index='stweets', doc_type='tweet', id=tweet["id"], body=tweet)
        count += 1

        if not tweetQueue.full() and flag == False:
            tweetQueue.put(tweet)
            print("Tweet in queue")

    return HttpResponse(status=200)



#streamer = tweepy.Stream(auth=auth, listener=StreamListener())
@csrf_protect
def filter(request):
    if request.method == "POST":
        #print(request.POST)
        if 'searchname' in request.POST:
            query = str(request.POST.get('searchname', ''))

            if query is None:
                elasticQuery = {
                    'match_all': {}
                }
            else:
                elasticQuery = {
                    "query_string": {
                        "query": query.lower()
                    }
                }

            searchResult = es.search(index="stweets", body={
                "sort": [{"id": {"order": "desc"}}],
                "size": 500,
                "query": elasticQuery
            })

            # print(searchResult)

            features= []

            try:
                for entry in searchResult['hits']['hits']:
                    result = entry['_source']
                    if 'query' not in str(result):
                        features.append(result)

            except KeyError:
                print("No Results found")

            # print(features)

            pass_list = json.dumps(features)
            print(pass_list)

            return render(request, 'map.html', {
                        "mydata": pass_list,
                     })


