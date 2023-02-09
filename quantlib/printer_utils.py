#python3 -m pip install termcolor
import enum
from termcolor import colored, cprint

class Printer():

    @staticmethod
    def pretty(left="", centre="", right="", color=None, highlight=None):
        formatted = "{:<20}{:^10}{:>10}".format(left, centre, right)
        if color != None and highlight != None:
            color_format = colored(formatted, color=color.value, on_color=highlight.value)
        elif color != None:
            color_format = colored(formatted, color=color.value)
        elif highlight != None:
            color_format = colored(formatted, on_color=highlight.value)
        else:
            color_format = formatted
        cprint(color_format)


class _Colors(enum.Enum):
    GREY = "grey"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    BLUE = "cyan"
    WHITE = "white"

class _Highlights(enum.Enum):
    GREY = "on_grey"
    RED = "on_red"
    GREEN = "on_green"
    YELLOW = "on_yellow"
    PURPLE = "on_purple"
    BLUE = "on_cyan"
    WHITE = "on_white"