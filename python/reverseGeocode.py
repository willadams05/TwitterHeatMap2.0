import pandas
import sqlite3
import numpy as np
import os

sentMap = {
    'AL': 0.0,
    'AK': 0.0,
    'AZ': 0.0,
    'AR': 0.0,
    'CA': 0.0,
    'CO': 0.0,
    'CT': 0.0,
    'DE': 0.0,
    'DC': 0.0,
    'FL': 0.0,
    'GA': 0.0,
    'HI': 0.0,
    'ID': 0.0,
    'IL': 0.0,
    'IN': 0.0,
    'IA': 0.0,
    'KS': 0.0,
    'KY': 0.0,
    'LA': 0.0,
    'ME': 0.0,
    'MD': 0.0,
    'MA': 0.0,
    'MI': 0.0,
    'MN': 0.0,
    'MS': 0.0,
    'MO': 0.0,
    'MT': 0.0,
    'NE': 0.0,
    'NV': 0.0,
    'NH': 0.0,
    'NJ': 0.0,
    'NM': 0.0,
    'NY': 0.0,
    'NC': 0.0,
    'ND': 0.0,
    'OH': 0.0,
    'OK': 0.0,
    'OR': 0.0,
    'PA': 0.0,
    'RI': 0.0,
    'SC': 0.0,
    'SD': 0.0,
    'TN': 0.0,
    'TX': 0.0,
    'UT': 0.0,
    'VT': 0.0,
    'VA': 0.0,
    'WA': 0.0,
    'WV': 0.0,
    'WI': 0.0,
    'WY': 0.0
}

countMap = {
    'AL': 0.0,
    'AK': 0.0,
    'AZ': 0.0,
    'AR': 0.0,
    'CA': 0.0,
    'CO': 0.0,
    'CT': 0.0,
    'DE': 0.0,
    'DC': 0.0,
    'FL': 0.0,
    'GA': 0.0,
    'HI': 0.0,
    'ID': 0.0,
    'IL': 0.0,
    'IN': 0.0,
    'IA': 0.0,
    'KS': 0.0,
    'KY': 0.0,
    'LA': 0.0,
    'ME': 0.0,
    'MD': 0.0,
    'MA': 0.0,
    'MI': 0.0,
    'MN': 0.0,
    'MS': 0.0,
    'MO': 0.0,
    'MT': 0.0,
    'NE': 0.0,
    'NV': 0.0,
    'NH': 0.0,
    'NJ': 0.0,
    'NM': 0.0,
    'NY': 0.0,
    'NC': 0.0,
    'ND': 0.0,
    'OH': 0.0,
    'OK': 0.0,
    'OR': 0.0,
    'PA': 0.0,
    'RI': 0.0,
    'SC': 0.0,
    'SD': 0.0,
    'TN': 0.0,
    'TX': 0.0,
    'UT': 0.0,
    'VT': 0.0,
    'VA': 0.0,
    'WA': 0.0,
    'WV': 0.0,
    'WI': 0.0,
    'WY': 0.0
}

#https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
def dist1(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295    # PI / 180
    c = np.cos
    a = 0.5 - c((lat2 - lat1) * p)/2 + c(lat1 * p) * c(lat2 * p) * (1 - c((lon2 - lon1) * p))/2

    return 12742 * np.arcsin(np.sqrt(a)) # 2 * R; R = 6371 km

def dist2(lat1, long1, lat2, long2):
    return np.sqrt((lat1-lat2)**2 + (long1-long2)**2)

db = sqlite3.connect(os.getcwd() + "\\data\\tweetDB.db")
cursor = db.cursor()
cursor.execute("SELECT latitude, longitude, sentiment FROM trump")
rows = cursor.fetchall()
df = pandas.read_csv(os.getcwd() + "\\data\\coordinates.csv")
values = df.values
count = 0
for row in rows:
    count += 1
    minDist = 100000000
    minState = ""
    minSent = 0.0
    dbLat = row[0]
    dbLong = row[1]
    dbSent = row[2]
    for i in range(len(values)):
        tempState = values[i][2]
        tempLat = values[i][3]
        tempLong = values[i][4]
        tempDist = dist2(dbLat, dbLong, tempLat, tempLong)
        if(tempDist < minDist):
            minDist = tempDist
            minState = tempState
    if minDist > 2 or minState not in sentMap:
        continue
    #print("Lat/Long: " + str(dbLat) + "/" + str(dbLong))
    #print("State: " + minState + " Distance: " + str(minDist))
    sentMap[minState] += dbSent
    countMap[minState] += 1
    print(count)

for key in sentMap:
    if(countMap[key] == 0):
        continue
    sentMap[key] = sentMap[key] / countMap[key]
    print("State: " + key + " # Tweets: " + str(countMap[key]) + " Sentiment: " + str(sentMap[key]))