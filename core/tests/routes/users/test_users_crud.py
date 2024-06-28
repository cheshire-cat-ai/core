from uuid import UUID
from cat.auth.utils import get_default_permissions, get_permissions_matrix

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

def create_new_user(client):
    new_user = {"username": "Alice", "password": "wandering_in_wonderland"}
    response = client.post("/users", json=new_user)
    assert response.status_code == 200
    return response.json()

def test_create_user(client):

    # create user
    data = create_new_user(client)

    # assertion on user structure
    check_user_fields(data)

    assert data["username"] == "Alice"
    assert data["permissions"] == get_default_permissions()

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
    assert len(data) == 1 # admin

    # create user
    create_new_user(client)

    # get updated list of users
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2 # admin and Alice

    # check users integrity and values
    for idx, d in enumerate(data):
        check_user_fields(d)
        assert d["username"] in ["admin", "Alice"]
        if d["username"] == "Alice":
            assert d["permissions"] == get_default_permissions()
        else:
            assert d["permissions"] == get_permissions_matrix()

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
    assert data["permissions"] == get_default_permissions()

def test_update_user(client):

    # update unexisting user
    response = client.put(f"/users/non_existent_id", json={"username": "Red Queen"})
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "User not found"

    # create user and obtain id
    user_id = create_new_user(client)["id"]

    # update unexisting attribute (shoud be ignored)
    updated_user = {"username": "Alice", "something": 42}
    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Alice"
    assert data["permissions"] == get_default_permissions()
    assert "something" not in data.keys()
    
    # change username
    updated_user = {"username": "Alice2"}
    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Alice2"
    assert data["permissions"] == get_default_permissions()

    # change username and permissions
    updated_user = {"username": "Alice3", "permissions": {"UPLOAD":["WRITE"]}}
    response = client.put(f"/users/{user_id}", json=updated_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Alice3"
    expected_permissions = {"UPLOAD":["WRITE"]}
    assert data["permissions"] == expected_permissions

    # get list of users, should be admin and Alice3
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for d in data:
        check_user_fields(d)
        assert d["username"] in ["admin", "Alice3"]
        if d["username"] == "Alice3":
            assert d["permissions"] == expected_permissions
        else:
            assert d["permissions"] == get_permissions_matrix()

def test_delete_user(client):

    # delete unexisting user
    response = client.delete(f"/users/non_existent_id")
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
    assert len(data) == 1 # admin
    assert data[0]["username"] == "admin"

def test_superuser(client):

    # cannot create another user called admin (it's the only one available at install)
    response = client.post("/users", json={"username": "admin", "password": "password"})
    assert response.status_code == 403

    # cannot edit admin user
    response = client.put("/users/admin", json={"permissions": {"MEMORY": ["READ"]}})

# note: using secure client (api key set both for http and ws)
def test_no_access_if_api_keys_active(secure_client):

    # create user
    response = secure_client.post(
        "/users",
        json={"username": "Alice", "password": "wandering_in_wonderland"}
    )
    assert response.status_code == 403

    # read users
    response = secure_client.get("/users")
    assert response.status_code == 403

    # edit user
    response = secure_client.put(
        "/users/non_existent_id", # is does not exist, but request should be blocked before the check
        json={"username": "Alice"}
    )
    assert response.status_code == 403

    # check default list giving the correct CCAT_API_KEY
    headers = {"Authorization": "Bearer meow_http"}
    response = secure_client.get("/users", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["username"] == "admin"

# TODOAUTH: test endpoints with different permissions