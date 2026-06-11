# TODOV2: uploads moved to a plugin (21c0605b). The /uploads/ endpoint no longer
# exists in core routes. These tests need to move to the uploads plugin test suite.


def test_call(client):
    response = client.get("/uploads/")
    assert response.status_code == 404


def test_call_specific_file(client):
    # ask for nonexistent file
    response = client.get("/uploads/Meooow.txt")
    assert response.status_code == 404
