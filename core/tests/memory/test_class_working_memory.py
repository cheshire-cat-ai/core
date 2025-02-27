from langchain_core.messages import AIMessage, HumanMessage

from cat.convo.messages import Role, UserMessage, CatMessage
from cat.memory.working_memory import WorkingMemory

def create_working_memory_with_convo_history(turns=1):
    """Utility to create a working memory and populate its convo history."""

    working_memory = WorkingMemory()
    
    for i in range(turns):
        human_message = UserMessage(user_id="123", who="Human", text="Hi")
        working_memory.update_history(human_message)
        cat_message = CatMessage(user_id="123", who="AI", text="Meow")
        working_memory.update_history(cat_message)
    
    return working_memory

def test_create_working_memory():

    wm = WorkingMemory()
    assert wm.history == []
    assert wm.user_message_json is None
    assert wm.active_form is None
    assert wm.recall_query == ""
    assert wm.episodic_memories == []
    assert wm.declarative_memories == []
    assert wm.procedural_memories == []
    assert wm.model_interactions == []


def test_update_history():

    wm = create_working_memory_with_convo_history()

    assert len(wm.history) == 2

    assert isinstance(wm.history[0], UserMessage)
    assert wm.history[0].who == "Human"
    assert wm.history[0].role == Role.Human
    assert wm.history[0].text == "Hi"

    assert isinstance(wm.history[1], CatMessage)
    assert wm.history[1].who == "AI"
    assert wm.history[1].role == Role.AI
    assert wm.history[1].text == "Meow"


def test_history_max_length():

    wm = create_working_memory_with_convo_history(turns=50)

    # TODO: make it configurable
    assert len(wm.history) == 20 # current max history length


def test_stringify_chat_history():

    wm = create_working_memory_with_convo_history()
    assert wm.stringify_chat_history() == "\n - Human: Hi\n - AI: Meow"


def test_langchainfy_chat_history():

    wm = create_working_memory_with_convo_history()
    langchain_convo = wm.langchainfy_chat_history()

    assert len(langchain_convo) == len(wm.history)

    assert isinstance(langchain_convo[0], HumanMessage)
    assert langchain_convo[0].name == "Human"
    assert isinstance(langchain_convo[0].content, list)
    assert langchain_convo[0].content[0] == {"type": "text", "text": "Hi"}

    assert isinstance(langchain_convo[1], AIMessage)
    assert langchain_convo[1].name == "AI"
    assert langchain_convo[1].content == "Meow"


def test_working_memory_as_dictionary_object():

    wm = WorkingMemory()
    wm.a = "a"
    wm["b"] = "b"
    assert wm.a == "a"
    assert wm["a"] == "a"
    assert wm.b == "b"
    assert wm["b"] == "b"
    # assert wm.c is None # too dangerous

# TODOV2: add tests for multimodal messages!
