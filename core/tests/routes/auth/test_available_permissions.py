
from cat.auth.utils import get_permissions_matrix

def test_get_available_permissions(client):

    response = client.get("/auth/available-permissions")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, dict)
    assert data == get_permissions_matrix()