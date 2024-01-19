
from json import dumps
from fastapi.encoders import jsonable_encoder
from cat.factory.llm import get_llms_schemas


def test_get_all_llm_settings(client):

    llms_schemas = get_llms_schemas()
    
    response = client.get("/llm/settings")
    json = response.json()

    assert response.status_code == 200
    assert type(json["settings"]) == list
    assert len(json["settings"]) == len(llms_schemas)

    for setting in json["settings"]:
        assert setting["name"] in llms_schemas.keys()
        assert setting["value"] == {}
        expected_schema = llms_schemas[setting["name"]]
        assert dumps(jsonable_encoder(expected_schema)) == dumps(setting["schema"])

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
    assert json["name"] == llm_name
    assert json["value"] == {}
    assert json["schema"]["languageModelName"] == llm_name
    assert json["schema"]["type"] == "object"


def test_upsert_llm_settings_success(client):
    
    # set a different LLM
    new_llm = "LLMCustomConfig"
    invented_url = "https://example.com"
    payload = {
        "url": invented_url,
        "options": {}
    }
    response = client.put(f"/llm/settings/{new_llm}", json=payload)

    # check immediate response
    json = response.json()
    assert response.status_code == 200
    assert json["name"] == new_llm
    assert json["value"]["url"] == invented_url

    # retrieve all LLMs settings to check if it was saved in DB
    response = client.get("/llm/settings")
    json = response.json()
    assert response.status_code == 200
    assert json["selected_configuration"] == new_llm
    saved_config = [ c for c in json["settings"] if c["name"] == new_llm ]
    assert saved_config[0]["value"]["url"] == invented_url

    # check also specific LLM endpoint
    response = client.get(f"/llm/settings/{new_llm}")
    assert response.status_code == 200
    json = response.json()
    assert json["name"] == new_llm
    assert json["value"]["url"] == invented_url
    assert json["schema"]["languageModelName"] == new_llm
