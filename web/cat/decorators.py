

def tool(function):

    def wrapper():

        print('DECORATING', function.__name__)
        return function()

    return wrapper


def prompt(function):

    def wrapper():

        print('DECORATING', function.__name__)
        return function()

    return wrapper


def hook(function):

    def wrapper():

        print('DECORATING', function.__name__)
        return function()

    return wrapper