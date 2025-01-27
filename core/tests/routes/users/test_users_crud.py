from uuid import UUID
from cat.auth.permissions import get_base_permissions, get_full_permissions
from tests.utils import create_new_user


def check_user_fields(u):
    assert set(u.keys()) == {"id", "username", "permissions"}
    assert isinstance(u["username"], str)
    assert isinstance(u["permissions"], dict)
    try:
        # Attempt to create a UUID object from the string to validate it
        uuid_obj = UUID(u["id"], version=4)
        assert str(uuid_obj) == u["id"]
    except ValueError:
        # If a ValueError is raised, the UUID string is invalid
        assert False, "Not a UUID"

def test_create_user(client):

    # create user
    data = create_new_user(client)

    # assertions on user structure
    check_user_fields(data)

    assert data["username"] == "Alice"
    assert data["permissions"] == get_base_permissions()

def test_cannot_create_duplicate_user(client):

    # create user
    response = create_new_user(client)

    # create user with same username
    response = client.post("/users", json={"username": "Alice", "password": "ecilA"})
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Cannot duplicate user"

def test_get_users(client):

    # get list of users
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2 # admin and user

    # create user
    create_new_user(client)

    # get updated list of users
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3 # admin, user and Alice

    # check users integrity and values
    for idx, d in enumerate(data):
        check_user_fields(d)
        assert d["username"] in ["admin", "user", "Alice"]
        if d["username"] == "admin":
            assert d["permissions"] == get_full_permissions()
        else:
            assert d["permissions"] == get_base_permissions()

def test_get_user(client):

    # get unexisting user
    response = client.get("/users/wrong_user_id")
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "User not found"

    # create user and obtain id
    user_id = create_new_user(client)["id"]

    # get specific existing user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()

    # check user integrity and values
    check_user_fields(data)
    assert data["username"] == "Alice"
    assert data["permissions"] == get_base_permissions()

def test_update_user(client):

    # update unexisting user
    response = client.put("/users/non_existent_id", json={"username": "Red Queen"})
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "User not found"

    # create user and obtain id
    user_id = create_new_user(client)["id"]

    # update unexisting attribute (bad request)
    updated_user = {"username": "Alice", "something": 42}
    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 400

    # change nothing
    response = client.put(f"/users/{user_id}", json={})
    assert response.status_code == 200
    data = response.json()

    # nothing changed so far
    check_user_fields(data)
    assert data["username"] == "Alice"
    assert data["permissions"] == get_base_permissions()
    
    # update password
    updated_user = {"password": "12345"}
    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 200
    data = response.json()
    check_user_fields(data)
    assert data["username"] == "Alice"
    assert data["permissions"] == get_base_permissions()
    assert "password" not in data # api will not send passwords around
    
    # change username
    updated_user = {"username": "Alice2"}
    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 200
    data = response.json()
    check_user_fields(data)
    assert data["username"] == "Alice2"
    assert data["permissions"] == get_base_permissions()

    # change permissions
    updated_user = {"permissions": {"MEMORY": ["READ"]}}
    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 200
    data = response.json()
    check_user_fields(data)
    assert data["username"] == "Alice2"
    assert data["permissions"] == {"MEMORY": ["READ"]}

    # change username and permissions
    updated_user = {"username": "Alice3", "permissions": {"UPLOAD":["WRITE"]}}
    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 200
    data = response.json()
    check_user_fields(data)
    assert data["username"] == "Alice3"
    assert data["permissions"] == {"UPLOAD":["WRITE"]}

    # get list of users, should be admin, user and Alice3
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for d in data:
        check_user_fields(d)
        assert d["username"] in ["admin", "user", "Alice3"]
        if d["username"] == "Alice3":
            assert d["permissions"] == {"UPLOAD":["WRITE"]}
        elif d["username"] == "admin":
            assert d["permissions"] == get_full_permissions()
        else:
            assert d["permissions"] == get_base_permissions()

def test_delete_user(client):

    # delete unexisting user
    response = client.delete("/users/non_existent_id")
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "User not found"

    # create user and obtain id
    user_id = create_new_user(client)["id"]

    # delete user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id

    # check that the user is not in the db anymore
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "User not found"

    # check user is no more in the list of users
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2 # admin and user
    assert data[0]["username"] == "admin"
    assert data[1]["username"] == "user"


# note: using secure client (api key set both for http and ws)
def test_no_access_if_api_keys_active(secure_client):

    # create user (forbidden)
    response = secure_client.post(
        "/users",
        json={"username": "Alice", "password": "wandering_in_wonderland"}
    )
    assert response.status_code == 403

    # read users (forbidden)
    response = secure_client.get("/users")
    assert response.status_code == 403

    # edit user (forbidden)
    response = secure_client.put(
        "/users/non_existent_id", # is does not exist, but request should be blocked before the check
        json={"username": "Alice"}
    )
    assert response.status_code == 403

    # check default list giving the correct CCAT_API_KEY
    headers = {"Authorization": "Bearer meow_http"}
    response = secure_client.get("/users", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["username"] == "admin"
    assert response.json()[1]["username"] == "user"
