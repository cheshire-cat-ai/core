
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
    
    # prepare test config
    invented_key = "some-key"
    payload = {
        "model_name": "gpt-3.5-turbo",
        "openai_api_key": invented_key
    }

    # act
    response = client.put("/settings/llm/LLMOpenAIChatConfig", json=payload)
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["status"] == "success"
    assert json["setting"]["value"]["openai_api_key"] == invented_key


    # retrieve data to check if it was saved in DB
    response = client.get("/settings/llm/")
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["selected_configuration"] == 'LLMOpenAIChatConfig'
    assert json["settings"][0]["value"]["openai_api_key"] == invented_key