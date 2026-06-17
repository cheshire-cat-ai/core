
from cat.memory.working_memory import WorkingMemory

# TODOV2: tests for new WorkingMemory, ChatResponse and ChatReply


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
