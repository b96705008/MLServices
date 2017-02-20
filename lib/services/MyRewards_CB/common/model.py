import os

from basic.model import MLModel
from utils.env import logger, sc

class MyRewardsCBModel(MLModel):
    def load_model(self):
        logger.info("Loading CB model...")

        def split_data(line):
            info = line.split(",")
            cust_id, prod_list = info[0], info[1:]

            result = [cust_id, prod_list]

            return(result)

        load_data = self.sc.textFile("file:" + os.path.join(self.model_path, "CB_model.csv"))
        cb_model = load_data.map(split_data)

        self.cb_dict = cb_model.collectAsMap()

    def get_top_ratings(self, params):
        """
            Recommends up to product_count top unrated product to user_id
        """
        user_id = params["user_id"]
        count = params["count"]

        bc_cb_dict = self.sc.broadcast(self.cb_dict)
        if user_id in bc_cb_dict.value:
            recommend_product = bc_cb_dict.value[user_id][0:count]
            result = []
            for i in range(len(recommend_product)):
                result.append({recommend_product[i]: int(count - i)})
        else:
            result = "Not Found, id: {}.".format(user_id)
        
        return result

