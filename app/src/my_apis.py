import json
import re
import urllib.parse
import datetime
import secrets
import string

from functools import wraps
from flask import Flask, request, jsonify

from app.util import insert_new_tweet, get_tweet_data, delete_tweet, match_tweets


app = Flask(__name__)


def get_current_utc_datetime_obj():
    return datetime.datetime.today()


def generate_secure_str(length):
    password_characters = string.ascii_letters + string.digits
    secure_str = ''.join((secrets.choice(password_characters) for i in range(length)))
    return secure_str


def username_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers and request.headers.get('X-Username'):
            createdBy = request.headers.get('X-Username')
            if isinstance(createdBy, str) and re.compile('^[a-zA-Z0-9_]{4,32}$').match(createdBy):
                return view_function(*args, **kwargs)
            else:
                return {"error": "Username is not valid"}, 400
        else:
            return {"error": "Username header is missing"}, 401
    return decorated_function


def content_type_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers and request.headers.get('Content-Type') and request.headers.get('Content-Type') == 'application/json':
            return view_function(*args, **kwargs)
        else:
            return {"error": "Content-Type must be 'application/json'"}, 400
    return decorated_function


def request_body_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.get_data():
            return view_function(*args, **kwargs)
        return {"error": "Request must be JSON"}, 400
    return decorated_function


@app.route('/v1/tweets', methods=['POST'])
@username_required
@content_type_required
@request_body_required
def api_insert_new_tweet():
    """
    # COMMAND:
    $ curl -X POST -H 'Content-Type: application/json' -H 'X-Username: [USERNAME]' '127.0.0.1:5000/v1/tweets?hashTags=[ENCODED_HASHTAG]&hashTags=[ENCODED_HASHTAG]' -d '{"tweetBody": [TWEET_TEXT]}'
    $ curl -X POST -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets?hashTags=%23hashtag1&hashTags=%23hashtag2' -d '{"tweetBody": "This is some new tweet text weio2938ur2foj."}'
    """
    """ INSERT NEW TWEET """
    tweet_b = request.get_data()
    tweet_dict = json.loads(tweet_b)
    createdBy = request.headers.get('X-Username')
    tweetId = generate_secure_str(20)
    current_url = request.url
    current_url_split = current_url.split("hashTags=")[1:]
    hashTags = [urllib.parse.unquote(i.split('&')[0]) for i in current_url_split]
    hashTags = [i for i in hashTags if re.compile('^#[a-zA-Z]{2,16}$').match(i)]
    current_datetime_obj = get_current_utc_datetime_obj()
    tweet_data = {
        "createdBy": createdBy,
        "tweetId": tweetId,
        "hashTags": hashTags,
        "tweetBody": tweet_dict["tweetBody"],
        "created_at": current_datetime_obj
    }
    insert_status = insert_new_tweet(tweet_data)
    if insert_status:
        return {"ok": "Created tweet."}, 201
    else:
        return {"error": "Failed to insert tweet."}, 400


@app.route('/v1/tweets/<tweetId>', methods=['POST'])
@username_required
@content_type_required
def api_delete_tweet(tweetId):
    """
    # COMMAND:
    $ curl -X POST -H 'Content-Type: application/json' -H 'X-Username: [USERNAME]' '127.0.0.1:5000/v1/tweets/[TWEET_ID]'
    $ curl -X POST -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets/eTW2RaylKUB7AH4aldpP'
    """
    """ DELETE TWEET """
    createdBy = request.headers.get('X-Username')
    tweet_data = get_tweet_data(tweetId)
    if tweet_data:
        db_user = tweet_data['createdBy']
        if createdBy == db_user:
            delete_status = delete_tweet(tweetId)
            if delete_status:
                return {"ok": "Tweet deleted successfully."}, 200
            else:
                return {"error": "Tweet not found"}, 404
        else:
            return {"error": "You tried to delete somebody elses tweet."}, 403
    else:
        return {"error": "Tweet not found"}, 404


@app.route('/v1/tweets', methods=['GET'])
@username_required
@content_type_required
def query_tweets():
    """
    # COMMAND:
    $ curl -X GET -H 'Content-Type: application/json' -H 'X-Username: [USERNAME]' '127.0.0.1:5000/v1/tweets?limit=[LIMIT]&offset=[OFFSET]&createdBy=[CREATED_BY]&hashTags=[ENCODED_HASHTAG]'
    $ curl -X GET -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets?limit=2&offset=2&createdBy=sbg_user1'
    $ curl -X GET -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets?limit=2&offset=2&hashTags=%23life'
    $ curl -X GET -H 'Content-Type: application/json' -H 'X-Username: sbg_user1' '127.0.0.1:5000/v1/tweets?limit=2&offset=2&createdBy=sbg_user1&hashTags=%23life'
    """
    """ QUERY TWEETS"""
    current_url = request.url
    current_url_split = current_url.split("createdBy=")[1:]
    createdBy = [urllib.parse.unquote(i.split('&')[0]) for i in current_url_split]
    current_url_split = current_url.split("hashTags=")[1:]
    hashTags = [urllib.parse.unquote(i.split('&')[0]) for i in current_url_split]
    hashTags = [i for i in hashTags if re.compile('^#[a-zA-Z]{2,16}$').match(i)]
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    tweet_dict = {"createdBy": createdBy, "hashTags": hashTags, "limit": limit, "offset": offset}
    matched_tweets = match_tweets(tweet_dict)
    if matched_tweets:
        return jsonify(list(matched_tweets)), 200
    else:
        return {"error": "Bad request, some of the specified parameters are not valid."}, 400
