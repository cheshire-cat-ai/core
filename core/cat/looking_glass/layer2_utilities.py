from cat.plugins.DbInteraction import Db


class prompt_utils():
    def __init__(self):
        pass
    def make_prompt_from_json(self, json):
        return "The menù of the restaurant is: \n" + self.dfs_dictionary(json)
    def get_initial_info(self):
        settings = Db.get_settings()
        suffix = "\n\nYou already have these informations"
        if "address" in settings:
            suffix += "\nHome address: " + settings["address"]
        if "card" in settings:
            suffix += "\nCard: " + settings["card"]
        return suffix



    def dfs_dictionary(self, input, depth: int):
        if(type(input) is dict):
            answer = ""
            for el in input.keys():
                answer += "\n"
                for int in range(depth):
                    answer = answer + "    "
                answer += el + ": " + self.dfs_dictionary(input[el], depth + 1)
        else:
            if(type(input) is list):
                answer = "\n"
                for int in range(depth):
                    answer += "    "
                for el in input:
                    answer += el + " - "
            else:
                answer = "\n"
                for int in range(depth):
                    answer += "    "
                answer += str(input)
        return answer