
from langchain.callbacks.base import BaseCallbackHandler


class NewTokenHandler(BaseCallbackHandler):

    def __init__(self, stray):
        # cat could be an instance of CheshireCat or StrayCat
        self.stray = stray
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.stray.send_ws_message(token, msg_type="chat_token")
