import hashlib
import database
import os


# Before you call any of these functions is it your responsibility to check whether the user already has an account or needs one.

###################### For database usage only ######################
def user_hash(username, password):
    salt = os.urandom(32)
    database.insert_salt(username, salt)
    hash = hashlib.pbkdf2_hmac(
        'sha-256',
        password.encode('utf-8'),
        salt,
        500_000
    )
    return hash


#####################################################################

# Call this function to verify a returning user's password
def verify(username, password):
    salt = database.get_salt(username)
    if salt == 0:
        return "An account does not exist for the inputted username."
    hash = hashlib.pbkdf2_hmac(
        'sha-256',
        password.encode('utf-8'),
        salt,
        500_000
    )
    stored_password = database.get_user_password(username)
    if stored_password == hash:
        return 1
    else:
        return 0
