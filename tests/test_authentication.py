from angery_cms_server.helpers.authentication import auth


def test_auth():
    assert auth("csculley", "yeet")
