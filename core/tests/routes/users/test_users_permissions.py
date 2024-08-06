
# test endpoints with different user permissions
# NOTE: we are using here the secure_client:
# - CCAT_API_KEY and CCAT_API_KEY_WS are active
# - we will auth with JWT

def test_users_endpoint_permissions(secure_client):

    # admin credentials
    admin_creds = {
        "username": "admin",
        "password": "admin"
    }

    # user credentials (does not exist yet)
    user_creds = {
        "username": "Alice",
        "password": "12345"
    }

    # no JWT, no pass
    for c in [admin_creds, user_creds]:
        res = secure_client.post("/users", json=c)
        assert res.status_code == 403
        assert res.json()["detail"]["error"] == "Invalid Credentials"

    # obtain JWT as admin
    res = secure_client.post("/auth/token", json=admin_creds)
    assert res.status_code == 200
    admin_token = res.json()["access_token"]

    # admin creates a new user (can do it because he has WRITE permission on USERS)
    res =secure_client.post("/users", json=user_creds, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    
    # user obtains JWT
    res = secure_client.post("/auth/token", json=user_creds)
    assert res.status_code == 200
    user_token = res.json()["access_token"]
    print(user_token)

    # user tries to create a new user (should be forbidden)
    third_user_cred = {
        "username": "Caterpillar",
        "password": "hookah!"
    }
    res = secure_client.post("/users", json=third_user_cred, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403
    assert res.json()["detail"]["error"] == "Invalid Credentials"


# TODOAUTH: more tests here on critical endpoints