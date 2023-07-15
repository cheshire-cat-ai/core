
def test_get_llm_settings(client):
    
    # act
    response = client.get("/settings/llm/")
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["status"] == "success"
    assert "LLMDefaultConfig" in json["schemas"].keys()
    assert "LLMDefaultConfig" in json["allowed_configurations"]
    assert json["selected_configuration"] == None # no llm configured at startup


def test_upsert_llm_settings_success(client):
    
    # set a different LLM
    invented_url = "https://example.com"
    payload = {
        "url": invented_url,
        "options": {}
    }
    response = client.put("/settings/llm/LLMCustomConfig", json=payload)
    json = response.json()

    # check immediate response
    assert response.status_code == 200
    assert json["status"] == "success"
    assert json["setting"]["value"]["url"] == invented_url

    # retrieve data to check if it was saved in DB
    response = client.get("/settings/llm/")
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["selected_configuration"] == 'LLMCustomConfig'
    assert json["settings"][0]["value"]["url"] == invented_url