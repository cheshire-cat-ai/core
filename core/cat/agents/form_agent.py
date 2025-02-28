from cat.experimental.form import CatFormState
from cat.agents import BaseAgent, AgentOutput
from cat.log import log

class FormAgent(BaseAgent):

    def execute(self, cat) -> AgentOutput:

        # get active form from working memory
        active_form = cat.working_memory.active_form
        
        if not active_form:
            # no active form
            return AgentOutput()
        elif active_form._state == CatFormState.CLOSED:
            # form is closed, delete it from working memory
            cat.working_memory.active_form = None
            return AgentOutput()
        else:
            # continue form
            try:
                form_output = active_form.next() # form should be async and should be awaited
                return AgentOutput(
                    output=form_output["output"],
                    return_direct=True, # we assume forms always do a return_direct
                    intermediate_steps=[
                        ((active_form.name, ""), form_output["output"])
                    ]
                )

            except Exception:
                log.error("Error while executing form")
                return AgentOutput()
    
        
    
