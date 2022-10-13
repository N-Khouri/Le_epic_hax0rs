import json

from pymongo import MongoClient

mongo_client = MongoClient("mongo")
database = mongo_client["battle_ships"]
leaderboard = database["leaderboard"]
users = database["users"]
active_users = database["active_users"]
chat = database["chat"]

# TLDR -> Inserts a user if the user doesn't exist.
# Functionality -> Call the DB to find the username. If the DB catches a username with the inputted username then exit; otherwise, insert the username and the password as a record into the users collectiion.
def insert_user(username, password):
    lookup = users.find_one({"username": username})
    if lookup != None:
        return 0  # "An account with the inputted username already exists. Please log-in with that account."
    else:
        users.insert_one({"username": username, "password": password, "score": 0})
        return 1  # "An account with the username " + username + " has been successfully created."


# Call this function to get all the users' usernames.
def all_users():
    list_to_json = list()
    collection = list(users.find({}))
    for i in collection:
        list_to_json.append(i["username"])
    return json.dumps(list_to_json)


# Call this function to increment a user's score by 1.
def add_score(username, decider):
    if decider == True:
        old_score = users.find_one({"username": username})["score"]
        users.update_one({"username": username}, {'$set': {"score": old_score + 1}})
        return "Your new win score is: " + old_score + 1


# TLDR -> Call this function to sort the leaderboard.
# Functionality -> It gets all the users and turns them into python readable, drops the current collection in the leaderboard, adds the new sorted list into the collection.
def update_leaderboard():
    db_users = json.loads(all_users())
    readable = sorted(db_users, key=lambda key: key["score"])
    leaderboard.drop()
    for i in readable:
        leaderboard.insert_one(i)
    lb = leaderboard.find({})
    to_return = []
    for i in lb:
        to_return.append(i)
    return to_return



######################### TESTING PURPOSES ONLY #######################

def clear_db():  # for testing purposes only
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
