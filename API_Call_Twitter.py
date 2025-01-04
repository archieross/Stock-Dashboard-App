import tweepy

class NewTweet:
    def __init__(self):
        self.author_id = None
        self.created_at = None
        self.text = None
        self.username = None
        pass

def GetTweets(tickerSymbol):

    import secret

    #Authentication - Twitter API
    client = tweepy.Client(bearer_token=secret.X_BEARER_TOKEN)

    #tweets mentioning the ticker symbol
    query = f"{tickerSymbol} -is:retweet"  #ignoring retweets for cleaner results

    #Fetch recent tweets
    tweets = client.search_recent_tweets(
        query=query, 
        max_results=10, 
        tweet_fields=['created_at', 'text', 'author_id'], 
        expansions='author_id',  #user information is included
        user_fields=['username']  #fields to fetch for users
    )


    #Mapping author IDs to usernames
    users = {user['id']: user['username'] for user in tweets.includes['users']}



    newTweets = []

    # Display tweets with usernames
    for tweet in tweets.data:
        newTweet = NewTweet()
        newTweet.authorid = tweet.author_id
        newTweet.username = users.get(tweet.author_id)
        newTweet.text = tweet.text
        newTweet.created_at = str(tweet.created_at)

        
        newTweets.append(newTweet)

    return newTweets
