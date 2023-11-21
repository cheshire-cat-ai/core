
from langchain.callbacks.base import BaseCallbackHandler


class NewTokenHandler(BaseCallbackHandler):

    def __init__(self, cat):
        # cat could be an instance of CheshireCat or StrayCat
        self.cat = cat
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.cat.send_ws_message(token, msg_type="chat_token")
