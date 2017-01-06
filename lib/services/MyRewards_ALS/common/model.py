import os

from basic.model import MLModel
from utils.env import logger, sc
from pyspark.mllib.recommendation import MatrixFactorizationModel


class MyRewardsALSModel(MLModel):
    def load_model(self):
        # load model
        self.model = MatrixFactorizationModel.load(sc, os.path.join(self.model_path, "als_model"))
        self.feature_total = self.model.productFeatures().count()

        self.__load_data()

    def __load_data(self):
        logger.info("Loading mapping table...")

        customer_rdd = self.sc.textFile(os.path.join(self.model_path, "als_customer_map.csv"))
        self.customer_dict = customer_rdd.map(lambda x: x.split(",")) \
                                         .map(lambda x: (x[0], int(x[1]))) \
                                         .collectAsMap()
        product_rdd = self.sc.textFile(os.path.join(self.model_path, "als_feature_map.csv"))
        self.product_dict = product_rdd.map(lambda x: x.split(",")) \
                                       .filter(lambda x: x[0] == "product") \
                                       .map(lambda x : (int(x[2]), x[1])) \
                                       .collectAsMap()

    def get_top_ratings(self, params):
        """
            Recommends up to product_count top unrated product to user_id
        """
        user_id = params["user_id"]
        count = params["count"]

        bc_customer_dict = self.sc.broadcast(self.customer_dict)
        bc_product_dict = self.sc.broadcast(self.product_dict)

        if user_id in bc_customer_dict.value:
            customer_no = bc_customer_dict.value[user_id]
            predict_score = self.sc.parallelize(self.model.recommendProducts(user = customer_no, num = self.feature_total))
            product_score = predict_score.filter(lambda x: x[1] in bc_product_dict.value) \
                                         .sortBy(lambda x: -x[2]) \
                                         .map(lambda x: {bc_product_dict.value[x[1]]: x[2]})
            result = product_score.take(count)
        else:
            result = "Not Found, id: {}.".format(user_id)

        return result
