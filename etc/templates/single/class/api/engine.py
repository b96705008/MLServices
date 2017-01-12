import uuid

from utils.env import logger, sc
from basic.engine import MLEngine

######################################
# 修改 load_model()
######################################

class #SERVICE#Engine(MLEngine):
    def refresh_model(self):
        raise NotImplementedError
