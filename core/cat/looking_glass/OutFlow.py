import asyncio
import nest_asyncio
import cat.plugins.test.openai_test as chatgpt
# from cat.plugins.Layer2LLM import delivery_agent
from cat.plugins.layer2_plugins.restaurant_agent import restaurant_agent

class AbnormalF():
    def __init__(self):
        self.msg = None
        self.manager = None
        self.cur_agent = None
        self.is_first = True

    def execute(self):
        nest_asyncio.apply()
        self.loop = asyncio.new_event_loop()
        from cat.routes.websocket import manager
        self.manager = manager
        self.manager.normal_flow = False
        print(self.manager)
        print(self.manager.plugin_id)
        print("\n\n\n chat gpt~~~~~~~~~~~~~~~~")

        self.msg = self.manager.msg_queue.get()
        match self.manager.plugin_id:
            case 1:
                cur_agent = restaurant_agent
        if(self.is_first is True):
            cur_agent.initialize(self.msg["text"])
            # print(cur_agent)
            # reply = cur_agent.predict(self.msg["text"])
            # print("\n\n\n")
            # print(reply)
            # print("\n\n\n") 
            self.is_first = False

        reply = cur_agent.predict(self.msg["text"])

        
        final_output = self.gen_msg(reply)
        print("\n\n\n")
        print(reply)
        print("\n\n\n")        
        # print(self.msg)
        # print(f"Plugin ID: {self.manager.plugin_id}")
        self.loop.run_until_complete(manager.send_via_ws(final_output))

        if(cur_agent.is_completed()):
            self.close()
            self.is_first = True

        #loop.close()
        # self.manager.normal_flow = False
        #return self.msg 
        # 
    
    def gen_msg(self, reply):
        msg = {
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

        return msg

    def close(self):
        self.loop.close()
        self.manager.normal_flow = True
        self.manager.plugin_id = -1
    

abnormal = AbnormalF()        
        #    

