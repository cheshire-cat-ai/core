"""Various utiles used from the projects."""

from datetime import timedelta


def to_camel_case(text):
    """Take in a string of words separated by either hyphens or underscores and returns a string of words in camel case."""
    s = text.replace("-", " ").replace("_", " ").capitalize()
    s = s.split()
    if len(text) == 0:
        return text
    return s[0] + "".join(i.capitalize() for i in s[1:])


def verbal_timedelta(td):
    """Convert a timedelta in human form."""
    if td.days != 0:
        abs_days = abs(td.days)
        if abs_days > 7:
            abs_delta = "{} weeks".format(td.days // 7)
        else:
            abs_delta = "{} days".format(td.days)
    else:
        abs_minutes = abs(td.seconds) // 60
        if abs_minutes > 60:
            abs_delta = "{} hours".format(abs_minutes // 60)
        else:
            abs_delta = "{} minutes".format(abs_minutes)
    if td < timedelta(0):
        return "{} ago".format(abs_delta)
    else:
        return "{} ago".format(abs_delta)
