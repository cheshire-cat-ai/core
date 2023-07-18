import asyncio
import nest_asyncio
import cat.plugins.test.openai_test as chatgpt

class AbnormalF():
    def __init__(self):
        self.msg = None
        self.manager = None

    def execute(self):
        nest_asyncio.apply()
        loop = asyncio.new_event_loop()
        from cat.routes.websocket import manager
        self.manager = manager
        self.manager.normal_flow = False
        print("\n\n\n chat gpt~~~~~~~~~~~~~~~~")

        self.msg = self.manager.msg_queue.get()
        reply = chatgpt.run_chatgpt(self.msg["text"])
        final_output = {
            "error": False,
            "type": "chat",
            "content": reply,
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
        print(self.msg)
        loop.run_until_complete(manager.send_via_ws(final_output))
        loop.close()
        manager.normal_flow = False
        #return self.msg 
        # 
abnormal = AbnormalF()        
        #    

