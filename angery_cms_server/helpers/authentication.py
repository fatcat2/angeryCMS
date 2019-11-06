import os
from google.cloud import firestore


def auth(username: str, password: str) -> bool:
    """Helper function to authenticae with library.

    :type username: str
    :param username: The requester's username.

    :type password: str
    :param password: The reqeuster's password.

    :ret type: bool
    :returns: True or false depending on successful authentication.
    """
    db = firestore.Client()
    user_ref = db.collection(u"users").where("username", "==", username).stream()

    users = [user.to_dict() for user in user_ref]

    if len(users) > 1:
        return False

    user = users[0]

    if users[0]["password"] == password:
        return True
    else:
        return False
