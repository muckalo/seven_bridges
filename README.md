## Homework is done.
#### I was using MongoDB.
#### You must have mongodb installed.
#### You don't need to create any DB or tables.
#### You just need to start mongod service.

#### run mongod service
```bash
$ sudo service mongod start
```

### Commands to run (after you clone it from GitLab):

#### cd into folder project folder "seven_bridges" and install requirements
```bash
$ cd seven_bridges && pip install -r requirements.txt
```

#### cd into folder "app/src" folder
```bash
$ cd app/src
```

#### export "FLASK_APP"
```bash
$ export FLASK_APP=my_apis.py
```

#### run Flask
```bash
$ flask run
```

#### insert new tweet - API call
```bash
$ curl -X POST -H 'Content-Type: application/json' -H 'X-Username: [USERNAME]' '127.0.0.1:5000/v1/tweets?hashTags=[ENCODED_HASHTAG]&hashTags=[ENCODED_HASHTAG]' -d '{"tweetBody": [TWEET_TEXT]}'
$ curl -X POST -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets?hashTags=%23hashtag1&hashTags=%23hashtag2' -d '{"tweetBody": "This is some new tweet text weio2938ur2foj."}'
```

#### View tweets - API call
```bash
$ curl -X GET -H 'Content-Type: application/json' -H 'X-Username: [USERNAME]' '127.0.0.1:5000/v1/tweets?limit=[LIMIT]&offset=[OFFSET]&createdBy=[CREATED_BY]&hashTags=[ENCODED_HASHTAG]'
$ curl -X GET -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets?limit=2&offset=2&createdBy=sbg_user1'
$ curl -X GET -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets?limit=2&offset=2&hashTags=%23life'
$ curl -X GET -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets?limit=2&offset=2&createdBy=sbg_user1&hashTags=%23life'
```

#### Delete tweet - API call
```bash
$ curl -X POST -H 'Content-Type: application/json' -H 'X-Username: [USERNAME]' '127.0.0.1:5000/v1/tweets/[TWEET_ID]'
$ curl -X POST -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets/eTW2RaylKUB7AH4aldpP'
```
