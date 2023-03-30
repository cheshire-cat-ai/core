import json
import logging
from pprint import pprint


def log(msg):

    color_code = "38;5;200"

    msg_header = '----------------  ^._.^  ----------------'
    msg_footer = '-----------------------------------------'

    print(f"\n\n\u001b[{color_code}m\033[1;3m{msg_header}\u001b[0m")
    pprint(msg)
    print(f"\u001b[{color_code}m\033[1;3m{msg_footer}\u001b[0m\n")