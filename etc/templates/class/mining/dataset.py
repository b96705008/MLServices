from basic.dataset import MLDataset
from utils.env import logger, sc

#######################################
# 修改 init()
# 修改 prepare_data()
#######################################
class #SERVICE#Dataset(MLDataset):
    def init(self):
        raise NotImplementedError

    def prepare_data(self):
        raise NotImplementedError
