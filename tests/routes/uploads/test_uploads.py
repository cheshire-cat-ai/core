import os
from cat import paths

# TODOV": update for uploads api (no uploads files)

def test_call(client):
    response = client.get("/uploads/")
    assert response.status_code == 404


def test_call_specific_file(client):
    uploads_file_name = "Meooow.txt"
    uploads_file_path = os.path.join(paths.UPLOADS_PATH, uploads_file_name)

    # ask for inexistent file
    response = client.get(f"/uploads/{uploads_file_name}")
    assert response.status_code == 404

    # insert file in uploads folder
    with open(uploads_file_path, "w") as f:
        f.write("Meow")

    response = client.get(f"/uploads/{uploads_file_name}")
    assert response.status_code == 200 # TODOV2: should this be 403?

