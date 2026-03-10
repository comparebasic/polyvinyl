BSTREAM_MAX = 2048
SALT_BYTES = 64
SESS_BYTES = 64

SEEK_START = 0
SEEK_CUR = 1
SEEK_END = 2
SESSION_DAYS = 14

from .utils.config import ParseConfig, ParseCli
from .utils.exception import DingerNotOk 
from .utils.log import GetLogger

from .auth.serve import DingerAuthServer
from .provider.serve import DingerProviderServer

__version__ = "0"
__author__ = "Compare Basic"

