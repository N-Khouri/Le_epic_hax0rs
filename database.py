import json

from pymongo import MongoClient


mongo_client = MongoClient("mongo")
database = mongo_client["battle_ships"]
leaderboard = database["leaderboard"]
users = database["users"]
active_users = database["active_users"]
chat = database["chat"]


def insert_user(username, password):
    lookup = users.find_one({"username": username})
    if lookup != None:
        return 0#"An account with the inputted username already exists. Please log-in with that account."
    else:
        users.insert_one({"username": username, "password": password})
        leaderboard.insert_one({"username": username, "score": 0})
        return 1#"An account with the username " + username + " has been successfully created."

def all_users():
    list_to_json = list()
    collection = list(users.find_one({}))
    for i in collection:
        list_to_json.append(i["username"])
    return json.dumps(list_to_json)

def add_score(username, decider):
    if decider == True:
        old_score = leaderboard.find_one({"username": username})["score"]
        leaderboard.update_one({"username": username}, {'$set': {"username": username, "score": old_score + 1}})
        return "You're win score is: " + old_score + 1


# def update_leaderboard():
#     leaderboard.find_one({}).sort({"score": -1})







######################### TESTING PURPOSES ONLY #######################

def clear_db(): #for testing purposes only
    database.drop_collection(users)
    database.drop_collection(leaderboard)


def print_users_db():
    cur = users.find()
    results = list(cur)
    users_list = ""
    for line in results:
        users_list += (line.get("username") + "\r\n") 
    return users_list    


###########################################################################