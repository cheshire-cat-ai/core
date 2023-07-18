from threading import Lock
import copy

class SingletonMeta(type):

    _instances = {}

    _lock: Lock = Lock()


    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Shared_memory(metaclass=SingletonMeta):
    state: dict = None
    lock: Lock = None

    def __init__(self, state: state) -> None:
        self.state = state
        self.lock = Lock()
    
    def write_state(self, addr: str, value):
        with self.lock:
            self.state[addr] = value
    
    def add_conversation_element(self, text: str):
        with self.lock:
            self.state["conversation"].append(text)

    def add_info(self, key: str, info):
        with self.lock:
            self.state["answers"][key] = info

    def read_state_addr(self, addr: str):
        with self.lock:
            return copy.copy(self.state[addr])
        
    def read_state(self):
        with self.lock:
            return copy.copy(self.state)    
        
    def pass_to_next_question(self, topic):
        with self.lock:
            self.tags[topic]["current"] += 1
            return
        
    def reset_state(self):
        with self.lock:
            self.state = {"context": "", "conversation": [], "answers": {}}

        
def get_memory():
    value = {"context": "", "conversation": [], "answers": {}}

    return Shared_memory(value)

