import asyncio
import nest_asyncio

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
        self.msg = self.manager.msg_queue.get()
        final_output = {
            "error": False,
            "type": "chat",
            "content": self.msg["text"],
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
        manager.normal_flow = True
        #return self.msg 
        # 
abnormal = AbnormalF()        
        #    

