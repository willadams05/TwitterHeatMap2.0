import tweepy
import time
import json
import sqlite3
import os
import keys
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class JsonLoader():

    def __init__(self, filename):
        self.filename = filename
    
    # Appends all tweets with location information to a JSON file
    # TODO: Get this to append in proper JSON format
    def store_json(self, status):
        tweet_json = status._json
        coordinates = tweet_json["coordinates"]
        place = tweet_json["place"]
        if(coordinates != None or place != None):
            sentiment = self.get_sentiment(status)
            result = {
                "text" : tweet_json["text"],
                "date" : tweet_json["created_at"],
                "place" : place,
                "coordinates" : coordinates,
                "sentiment" : sentiment
            }
            json_string = json.dumps(result)
            print("Appending to file")
            with open(self.filename, 'a') as outfile:
                json.dump(json_string, outfile, indent=4, separators=(',', ': '))
            print("Done")
    
    def get_sentiment(self, status):
        sid = SentimentIntensityAnalyzer()
        ss = sid.polarity_scores(status.text)
        return ss["compound"]


class SqlLoader():
    
    def __init__(self, tablename):
        self.db = sqlite3.connect(os.getcwd() + "\\data\\tweetDB.db")
        self.cursor = self.db.cursor()
        self.tablename = tablename
        self.create_table()

    # Creates a new table in the tweetDB if the table does not already exist
    def create_table(self):
        #https://www.pythoncentral.io/introduction-to-sqlite-in-python/
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS
                            {}(id INTEGER PRIMARY KEY, text TEXT, date TEXT, 
                            longitude REAL, latitude REAL, sentiment REAL)'''.format(self.tablename))
        self.db.commit()
    
    # Stores a tweet in a SQLite table
    def store_sql(self, status):
        if(status.place != None or status.coordinates != None):
            # Have to parse lat/long out of coordiantes, since SQLite can't handle the JSON style coordinates
            longitude, latitude = self.get_coordinates(status)
            #text = ""
            #if hasattr(status, 'full_text'):
            #    text = status.full_text
            #else:
            #    text = status.text
            text = status.full_text if hasattr(status, 'full_text') else status.text
            date = status.created_at
            sentiment = self.get_sentiment(text)
            self.cursor.execute('''INSERT INTO {}(text, date, longitude, latitude, sentiment)
                                   VALUES(:text, :date, :longitude, :latitude, :sentiment)'''.format(self.tablename),
                                   {'text':text, 'date':date, 'longitude':longitude, 'latitude':latitude, 'sentiment':sentiment})
            self.db.commit()
            print("Added entry to {}".format(self.tablename))
    
    def get_sentiment(self, text):
        sid = SentimentIntensityAnalyzer()
        ss = sid.polarity_scores(text)
        return ss["compound"]

    # This cancer pulls out the latitude and longitude from a Tweet object.
    def get_coordinates(self, status):
        if(status.coordinates != None):
            #https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/geo-objects#coordinates-dictionary
            coordinates = status.coordinates["coordinates"]
            print("Longitude: ", coordinates[0], "Latitude: ", coordinates[1])
            return coordinates[0], coordinates[1]
        else:
            #bounding_box holds a 3D array of coordinates, but it looks like it's always only 1 2D array inside
            #So, get rid of the outermost array by assigning to coordinates[0]. (float[][] coordinates = ...)
            coordinates = status.place.bounding_box.coordinates[0]
            # Pick the mid-point between all of the coordinates
            latitude = longitude = 0
            for i in range(0,4):
                longitude += coordinates[i][0]
                latitude += coordinates[i][1]
            #TODO: Probably need to find a better way to do this than averaging
            return longitude/4, latitude/4


class SqlStreamListener(tweepy.StreamListener):

    # @param tablename is the name of the SQL table to load the tweets into
    # @param flag is true for SQL loading and false for JSON loading
    def __init__(self, tablename):
        super(SqlStreamListener, self).__init__()
        # Reset the system time for streaming to work
        self.time = time.time()
        self.sqlLoader = SqlLoader(tablename)
        
    # Overrides StreamListener.on_status()
    def on_status(self, status):
        self.sqlLoader.store_sql(status)

    #Overrides SteramListener.on_error()
    def on_error(self, status_code):
        print(status_code)
        self.sqlLoader.db.close()
        return False


class JsonStreamListener(tweepy.StreamListener):
    
    def __init__(self, filename):
        super(JsonStreamListener, self).__init__()
        self.jsonLoader = JsonLoader(filename)
    
    def on_status(self, status):
        self.jsonLoader.store_json(status)
    
    def on_error(self, status_code):
        print(status_code)
        return False


class SqlSearcher():

    def __init__(self, tablename, api):
        self.api = api
        self.sqlLoader = SqlLoader(tablename)

    def search(self, query):
        # tweet_mode = "extended" returns the full tweet even if it's > 140 characters
        # lang="en" restricts to only english tweets
        #for status in tweepy.Cursor(self.api.search, q=query, tweet_mode="extended", lang="en").items():
        #    self.sqlLoader.store_sql(status)
        
        # https://stackoverflow.com/questions/21308762/avoid-twitter-api-limitation-with-tweepy
        c = tweepy.Cursor(self.api.search, q=query, tweet_mode="extended", lang="en").items()
        while True:
            try:
                tweet = c.next()
                self.sqlLoader.store_sql(tweet)
                # Insert into db
            except tweepy.TweepError:
                time.sleep(60 * 15)
                continue
            except StopIteration:
                break

    def throughput_test(self, query, geoflag):
        count = 0
        c = tweepy.Cursor(self.api.search, q=query, tweet_mode="extended", lang="en").items()
        t_end = time.time() + 60
        t_start = time.time()
        print("Start Time: " + str(t_start))
        while time.time() < t_end:
            try:
                tweet = c.next()
                if(geoflag):
                    if(tweet.place == None and tweet.coordinates == None):
                        continue
                text = tweet.full_text if hasattr(tweet, 'full_text') else tweet.text
                self.sqlLoader.get_sentiment(text)
                count+=1
            except tweepy.TweepError:
                break
        print("Final Count: " + str(count) + " Final Time: " + str(time.time() - t_start)) 



def main():

    auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
    auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Stream for live tweets (True for sql loading, False for JSON loading)
    #myTrumpListener = SqlStreamListener("trump")
    #myStream = tweepy.Stream(auth = api.auth, listener=myTrumpListener)
    #myStream.filter(track=['trump'])

    sqlSearcher = SqlSearcher("trump", api)
    # queries can be formed as boolean queries "trump OR president OR food"
    sqlSearcher.search("trump")

    #sqlTester = SqlSearcher("test", api)
    #sqlTester.throughput_test("trump", True)

if __name__ == "__main__":
    main()