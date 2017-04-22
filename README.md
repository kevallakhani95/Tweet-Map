# Tweet-Map

This is a scalable version of the **Tweet-Map** web application deployed on cloud. This application uses Twitter Streaming API to get tweets with 
geolocation to plot the tweets on a map along with the sentiment of the tweet. This version of the application refreshes itself from time 
to time to collect and stream live tweets on the map. This application is developed using Python Django framework and deployed on AWS Elastic Beanstalk.


The application uses - (application workflow is in the presented order below)
* **Twitter Streaming API** - To collect live tweets from twitter. 
* **Amazon SQS** - A queueing service that asynchronously processes the tweet and stores the streamed tweets making them available for consumption.
* **Worker pool** - A worker pool is defined that picks up message from the queue to process, each on a different pool thread.
* **MonkeyLearn Sentiment Analysis API** - For calculating the sentiment of the tweet text.
* **Amazon SNS** - A notification service that sends a notofication to an HTTP endpoint containing the information about the tweet.
* **AWS Elastic Search** - For efficient searching of tweets based on keywords stored in JSON format.
* **Google Maps API** - For plotting live tweets on a map.

Finally, deployed the application on AWS Elastic Beanstalk and configured EC2 for deploying different components of the application.

Application architechture - 
![alt tag](http://i.imgur.com/ouIDUJT.png)

Web application screenshot - 


