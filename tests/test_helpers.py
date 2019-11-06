from angery_cms_server.helpers.images import unique_file_naming


def test_unique_file_naming():
    assert unique_file_naming("test.jpg")[-8:] == "test.jpg"
