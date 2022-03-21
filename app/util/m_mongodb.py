import pymongo
import urllib.parse


def get_client(uri):
    return pymongo.MongoClient(uri)


def get_db(client, db_name):
    return client[db_name]


def get_collection(db, collection_name):
    return db[collection_name]


def insert_new_tweet(tweet_data):
    client = get_client(mongodb_uri)
    db = get_db(client, db_name)
    collection_tweets = get_collection(db, collection_name_tweets)
    insert_status = collection_tweets.insert_one(tweet_data)
    collection_users = get_collection(db, collection_name_users)
    user_data = {"createdBy": tweet_data["createdBy"]}
    try:
        collection_users.insert_one(user_data)
        collection_users.create_index("createdBy", unique=True)
    except:
        pass
    return insert_status


def get_tweet_data(tweetId):
    client = get_client(mongodb_uri)
    db = get_db(client, db_name)
    collection_tweets = get_collection(db, collection_name_tweets)
    return collection_tweets.find_one({"tweetId": tweetId})


def delete_tweet(tweetId):
    client = get_client(mongodb_uri)
    db = get_db(client, db_name)
    collection_tweets = get_collection(db, collection_name_tweets)
    delete_status = collection_tweets.delete_one({"tweetId": tweetId})
    return delete_status


def match_tweets(query_params_dict):
    """
    limit:
        min: 1
        max: 100
        def: 50
    { $limit: <positive 64-bit integer> }

    offset:
         min: 0
         def: 0
    { $skip: <positive 64-bit integer> }
    """

    limit_min = 1
    limit_max = 100
    limit_def = 50
    offset_min = 0
    offset_def = 0

    client = get_client(mongodb_uri)
    db = get_db(client, db_name)
    collection_tweets = get_collection(db, collection_name_tweets)
    d_keys = query_params_dict.keys()
    if "createdBy" not in d_keys:
        query_params_dict["createdBy"] = []
    if "hashTags" not in d_keys:
        query_params_dict["hashTags"] = []
    if "limit" in d_keys:
        limit = query_params_dict["limit"]
        if limit and limit is not None:
            limit = int(limit)
            if limit < limit_min or limit > limit_max:
                limit = limit_def
        else:
            limit = limit_def
    else:
        limit = limit_def
    if "offset" in d_keys:
        offset = query_params_dict["offset"]
        if offset and offset is not None:
            offset = int(offset)
            if offset < offset_min:
                offset = offset_def
        else:
            offset = offset_def
    else:
        offset = offset_def

    next_page_offset = offset + limit

    created_by_val = "&createdBy=".join([i for i in query_params_dict["createdBy"]])
    if created_by_val:
        created_by_val = "&createdBy={}".format(created_by_val)
    hash_tag_val = "&hashTags=".join([urllib.parse.quote(i) for i in query_params_dict["hashTags"]])
    if hash_tag_val:
        hash_tag_val = "&hashTags={}".format(hash_tag_val)
    query_params_val = "{}{}".format(created_by_val, hash_tag_val)

    query_result = collection_tweets.aggregate([
        {
            "$project": {
                "_id": 0,
                "matched_tweets": {
                    "$cond": {
                        "if": {
                            "$and": [
                                {"$eq": [{"$setIntersection": ["$hashTags", query_params_dict["hashTags"]]}, []]},
                                {"$eq": [{"$setIntersection": [["$createdBy"], query_params_dict["createdBy"]]}, []]},
                            ]
                        },
                        "then": [],
                        "else": True
                    },
                },
                "createdBy": "$createdBy",
                "tweetId": "$tweetId",
                "hashTags": "$hashTags",
                "tweetBody": "$tweetBody",
                "created_at": "$created_at",
            },
        },
        {"$unwind": "$matched_tweets"},
        {"$sort": {"created_at": 1}},

        {"$skip": offset},
        {"$limit": limit},
    ])  # USERNAMES AND HASHTAGS
    output_lst = list(query_result)

    query_result_count = collection_tweets.aggregate([
        {
            "$project": {
                "_id": 0,
                "matched_tweets": {
                    "$cond": {
                        "if": {
                            "$and": [
                                {"$eq": [{"$setIntersection": ["$hashTags", query_params_dict["hashTags"]]}, []]},
                                {"$eq": [{"$setIntersection": [["$createdBy"], query_params_dict["createdBy"]]}, []]},
                            ]
                        },
                        "then": [],
                        "else": True
                    },
                },
            },
        },
        {"$unwind": "$matched_tweets"},
        {"$count": "total_matched_tweets"},

    ])  # TOTAL MATCHED TWEETS
    total_matched_tweets = 0
    for i in query_result_count:
        total_matched_tweets = i["total_matched_tweets"]

    if offset < total_matched_tweets - 1:
        next_page = "http://127.0.0.1:5000/v1/tweets?offset={}&limit={}{}".format(next_page_offset, limit, query_params_val)
        next_page_dct = {
            "total_matched_tweets": total_matched_tweets,
            "next_page": next_page
        }
        output_lst.append({"metadata": next_page_dct})
    else:
        next_page_dct = {"total_matched_tweets": total_matched_tweets}
        output_lst.append({"metadata": next_page_dct})

    return output_lst


mongodb_uri = "mongodb://localhost:27017/"
db_name = "db1"
collection_name_tweets = "tweets"
collection_name_users = "users"
