
def test_get_all_llm_settings(client):
    
    # act
    response = client.get("/llm/settings/")
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["status"] == "success"
    assert "LLMDefaultConfig" in json["schemas"].keys()
    assert "LLMDefaultConfig" in json["allowed_configurations"]
    assert json["selected_configuration"] == None # no llm configured at startup


def test_get_llm_settings_non_existent(client):

    non_existent_llm_name = "LLMNonExistentConfig"
    response = client.get(f"/llm/settings/{non_existent_llm_name}")
    json = response.json()

    assert response.status_code == 400
    assert f"{non_existent_llm_name} not supported" in json["detail"]["error"]


def test_get_llm_settings(client):

    llm_name = "LLMDefaultConfig"
    response = client.get(f"/llm/settings/{llm_name}")
    json = response.json()

    assert response.status_code == 200
    assert json["status"] == "success"
    assert json["settings"] == {}
    assert json["schema"]["languageModelName"] == llm_name
    assert json["schema"]["type"] == "object"


def test_upsert_llm_settings_success(client):
    
    # set a different LLM
    invented_url = "https://example.com"
    payload = {
        "url": invented_url,
        "options": {}
    }
    response = client.put("/llm/settings/LLMCustomConfig", json=payload)
    json = response.json()

    # check immediate response
    assert response.status_code == 200
    assert json["status"] == "success"
    assert json["setting"]["value"]["url"] == invented_url

    # retrieve LLMs settings to check if it was saved in DB
    response = client.get("/llm/settings/")
    json = response.json()
    assert response.status_code == 200
    assert json["selected_configuration"] == 'LLMCustomConfig'
    assert json["settings"][0]["value"]["url"] == invented_url

    # check also specific LLM endpoint
    response = client.get("/llm/settings/LLMCustomConfig")
    json = response.json()
    assert response.status_code == 200
    assert json["settings"]["url"] == invented_url