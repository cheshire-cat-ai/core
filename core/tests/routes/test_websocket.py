
from tests.utils import send_websocket_message

def test_websocket(client):
        
        # use fake LLM
        response = client.put("/settings/llm/LLMFakeConfig", json={})
    
        res = send_websocket_message({
            "text": "Your bald aunt with a wooden leg"
        }, client)

        for k in ["error", "content", "why"]:
            assert k in res.keys()

        assert not res["error"]
        assert type(res["content"]) == str
        assert "You did not configure" in res["content"]
        assert len(res["why"].keys()) > 0