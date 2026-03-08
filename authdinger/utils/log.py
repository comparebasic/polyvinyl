from . import colors
from datetime import datetime

class Log(object):
    def __init__(self, color=False):
        self.color = color

    def _log(self, level, message, obj, color):
        if self.color and color:
            print("\x1b[{}m".format(color), end="")

        if obj:
            print("{} {}: {} {}".format(level, datetime.now(), message, obj))
        else:
            print("{} {}: {}".format(level, datetime.now(), message))

        if self.color and color:
            print("\x1b[0m", end="")

    def log(self, message, obj=None):
        self._log("Log", message, obj, colors.CYAN)

    def warn(self, message, obj=None):
        self._log("Warn", message, obj, colors.YELLOW)

    def error(self, message, obj=None):
        self._log("Error", message, obj, colors.RED)

def GetLogger(config):
    return Log(config.get("log-color"))
    
