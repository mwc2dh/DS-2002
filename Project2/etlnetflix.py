#khn8ur Kevin Namkung
#mwc2dh Micah Cho

import pandas as pd
import os
import pymongo
import pprint

#list containing all different csv files into dataframes
datalist = []

#extract csvs into pandas dfs
for i in os.listdir('Netflix Tv Shows and Movies/'):
    df=pd.read_csv('Netflix Tv Shows and Movies/' + i, encoding = "utf-8")
    datalist.append(df)

#print(datalist)

#connecting to MongoDB
host_name = "localhost"
port = "27017"
atlas_cluster_name = "sandbox"
atlas_default_dbname = "local"

conn_str = {
    "local" : f"mongodb://{host_name}:{port}/",
#    "atlas" : f"mongodb+srv://{atlas_user_name}:{atlas_password}@{atlas_cluster_name}.zibbf.mongodb.net/{atlas_default_dbname}"
}
client = pymongo.MongoClient(conn_str["local"])

#create DB
db_name = "netflixData"
db = client[db_name]

#special cases for characters
datalist[0].loc[43,['TITLE']] = 'BAhubali 2: The Conclusion'
datalist[1].loc[27,['TITLE']] = 'BAhubali 2: The Conclusion'
datalist[1].loc[68,['TITLE']] = 'BAhubali : The Beginning'
datalist[1].loc[169,['TITLE']] = 'Les Miserables'

#omit raw credits and raw titles because we will not use them for our questions
datalist = datalist[:-2]
mongolist = []

#load into mongodb
for file in datalist:
    collec = []
    cols = file.columns[1:]
    for index, row in file.iterrows():
        entry = {}
        for i in cols:
            if i != 'MAIN_PRODUCTION':
                entry[i] = row[i]
        collec.append(entry)
    mongolist.append(collec)

#create collecions
bestMovieByYear = db.bestMovieByYear
bestMoviesNetflix = db.bestMoviesNetflix
bestShowByYear = db.bestShowByYear
bestShowsNetflix = db.bestShowsNetflix

#import into mongo
post_ids0 = bestMovieByYear.insert_many(mongolist[0])
post_ids1 = bestMoviesNetflix.insert_many(mongolist[1])
post_ids2 = bestShowByYear.insert_many(mongolist[2])
post_ids3 = bestShowsNetflix.insert_many(mongolist[3])
