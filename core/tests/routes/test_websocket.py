
from tests.utils import send_websocket_message


# TODO: ws endpoint still talks with the prod cat configuration 
def test_websocket(client):
        
        # use fake LLM
        response = client.put("/settings/llm/LLMDefaultConfig", json={})
        assert response.status_code == 200

        # send websocket message
        res = send_websocket_message({
            "text": "Your bald aunt with a wooden leg"
        }, client)

        for k in ["error", "content", "why"]:
            assert k in res.keys()

        assert not res["error"]
        assert type(res["content"]) == str
        assert "You did not configure" in res["content"]
        assert len(res["why"].keys()) > 0
