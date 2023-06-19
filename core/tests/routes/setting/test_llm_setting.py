def test_upsert_llm_settings_success(client):
    # prepare test data
    payload = {"model_name": "gpt-3.5-turbo",
               "openai_api_key": "your-key-here"}

    # act
    response = client.put("/settings/llm/LLMOpenAIChatConfig",
                          json=payload)

    # assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()[
        "setting"]["value"]["model_name"] == payload["model_name"]
