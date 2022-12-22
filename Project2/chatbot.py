#khn8ur Kevin Namkung
#mwc2dh Micah Cho

import nltk 
nltk.download('punkt')

from nltk import word_tokenize, sent_tokenize

from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import numpy as np 
import tflearn
import tensorflow as tf
import random
import json
import pickle
import pymongo
import pprint

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
db_name = "netflixData"
db = client[db_name]

#mongo querying

#top 5 shows 2020
bestShows2020 = []
for show in db.bestShowsNetflix.find( {"RELEASE_YEAR" : 2020} )[0:5]:
    bestShows2020.append(show)

#top 5 movies 2020
bestMovies2020 = []
for show in db.bestMoviesNetflix.find( {"RELEASE_YEAR" : 2020} )[0:5]:
    bestMovies2020.append(show)

#top 10 dramas in shows
bestDramaShows = []
for show in db.bestShowsNetflix.find( {"MAIN_GENRE" : "drama"} )[0:3]:
    bestDramaShows.append(show)

#top 10 comedies in movies
bestComedyMovies = []
for show in db.bestMoviesNetflix.find( {"MAIN_GENRE" : "comedy"} )[0:3]:
    bestComedyMovies.append(show)

#longest movie
longestMovie = db.bestMoviesNetflix.find().sort("DURATION")[386]

#edit json file to include responses
with open("questions.json") as file:
    data = json.load(file)
    
    #q1
    for i in range(len(bestShows2020)):
        data['questions'][0]['responses'].append(str(i+1) + ") " + bestShows2020[i]['TITLE'] + " (Score: " + str(bestShows2020[i]["SCORE"]) + ")")
    
    #q2
    for i in range(len(bestMovies2020)):
        data['questions'][1]['responses'].append(str(i+1) + ") " + bestMovies2020[i]['TITLE'] + " (Score: " + str(bestMovies2020[i]["SCORE"]) + ")")

    #q3
    for i in range(len(bestDramaShows)):
        data['questions'][2]['responses'].append(str(i+1) + ") " + bestDramaShows[i]['TITLE'] + " (Score: " + str(bestDramaShows[i]["SCORE"]) + ")")

    #q4
    for i in range(len(bestComedyMovies)):
        data['questions'][3]['responses'].append(str(i+1) + ") " + bestComedyMovies[i]['TITLE'] + " (Score: " + str(bestComedyMovies[i]["SCORE"]) + ")")

    #q5
    data['questions'][4]['responses'].append("The top show in 2020 was " + bestShows2020[0]['TITLE'] + " with a score of " + str(bestShows2020[0]['SCORE']))

    #q6
    data['questions'][5]['responses'].append("The genre of the top show of 2020 was " + bestShows2020[0]['MAIN_GENRE'] + ". The show was " + bestShows2020[0]['TITLE'])

    #q7
    data['questions'][6]['responses'].append("The top movie in 2020 was " + bestMovies2020[0]['TITLE'] + " with a score of " + str(bestMovies2020[0]['SCORE']))
    
    #q8
    data['questions'][7]['responses'].append("The genre of the top movie of 2020 was " + bestMovies2020[0]['MAIN_GENRE'] + ". The show was " + bestMovies2020[0]['TITLE'])
    
    #q9
    data['questions'][8]['responses'].append("The longest movie on Netflix is " + longestMovie['TITLE'] + " with a duration of " + str(longestMovie['DURATION']))

    #q10
    data['questions'][9]['responses'].append("The number of seasons for the top show on Netflix in 2020 was " + str(bestShows2020[0]['NUMBER_OF_SEASONS']) + ". The show was " + bestShows2020[0]['TITLE'])

    


try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []
    for question in data["questions"]:
        for pattern in question["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(question["tag"])
            
        if question["tag"] not in labels:
            labels.append(question["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))
    labels = sorted(labels)

    training = []
    output = []
    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w.lower()) for w in doc]
        for w in words:
            if w in wrds:
               bag.append(1)
            else:
              bag.append(0)
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1
        training.append(bag)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)
    
    with open("data.pickle","wb") as f:
        pickle.dump((words, labels, training, output), f)

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
model.save("model.tflearn")

try:
    model.load("model.tflearn")
except:
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]
    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
    return np.array(bag)

def chat():
    print("Start talking with the bot! (type quit to stop)")
    print("Here are some example questions you can ask:")
    print(" - What were the top 5 shows on Netflix in 2020?")
    print(" - What were the top 5 movies on Netflix in 2020?")
    print(" - What was the top show on Netflix in 2020?")
    print(" - What was the genre of the top show on Netflix in 2020?")
    print(" - What is the longest movie on Netflix?")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break
        if inp.lower() == "help":
            print("Here are some example questions you can ask:")
            print(" - What were the top 5 shows on Netflix in 2020?")
            print(" - What were the top 5 movies on Netflix in 2020?")
            print(" - What was the top show on Netflix in 2020?")
            print(" - What was the genre of the top show on Netflix in 2020?")
            print(" - What is the longest movie on Netflix?")
            continue
        result = model.predict([bag_of_words(inp, words)])[0]
        result_index = np.argmax(result)
        tag = labels[result_index]

        if result[result_index] > 0.7:
            for tg in data["questions"]:
                if tg['tag'] == tag:
                    responses = tg['responses']
            print(responses)

        else:
            print("I didnt get that. Can you explain or try again.")

chat()
