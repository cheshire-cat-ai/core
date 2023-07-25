def gen_response(message: str):
    msg = {
        "error": False,
        "type": "chat",
        "content": message,
        "why": {
            "input": "a",
            #"intermediate_steps": cat_message.get("intermediate_steps"),
            "memory": {
                "episodic": "a",
                "declarative": "a",
                "procedural": "a",
            },
        },
    }
    return msg