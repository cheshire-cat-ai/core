# class to represent a @plugin override
class CatPluginDecorator:
    def __init__(self, function):
        self.function = function
        self.name = function.__name__


# @plugin decorator. Any function in a plugin decorated by @plugin and named properly (among list of available overrides)
#   is used to override plugin behaviour. These are not hooks because they are not piped, they are specific for every plugin
def plugin(func):
    return CatPluginDecorator(func)
