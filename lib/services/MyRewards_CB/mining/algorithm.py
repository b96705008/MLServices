import shutil, os, csv
import numpy as np

from basic.algorithm import MLAlgorithm
from utils.env import logger

class MyRewardsCBTrain(MLAlgorithm):
    def train_model(self):
        logger.info("Training the CB model...")

        def calculate_score(line, dict):
            customer_id, customer_info = line[0], line[1]

            result = []
            for product_id, product_info in dict.items():
                result.append((product_id, np.corrcoef([np.array(customer_info), np.array(product_info)])[0][1]))
            result = [customer_id, result]

            return(result)

        def sort_product_score(line):
            customer_id, score_info = line[0], list(line[1])

            score_info1 = dict(score_info[0])
            score_info2 = dict(score_info[1])

            avg_score = [(key, (value + score_info2.get(key)) / 2) for key, value in score_info1.items()]
            sort_score = sorted(avg_score, key = lambda x: -x[1])

            result = [customer_id] + [x[0] for x in sort_score]

            return(result)

        product_dict = self.dataset.product_data.collectAsMap()
        bc_product_dict = self.sc.broadcast(product_dict)

        customer_score1 = self.dataset.customer_data.map(lambda x: calculate_score(x, product_dict))
        customer_score2 = self.dataset.customer_last_product.map(lambda x: (x[0], bc_product_dict.value[x[1]])) \
                                                            .map(lambda x: calculate_score(x, product_dict))
        all_score = customer_score1.union(customer_score2)

        self.cb_model = all_score.groupByKey().map(sort_product_score)

    def save_model(self):
        logger.info("Saving the CB model...")

        try:
            shutil.rmtree(self.model_path)
        except Exception:
            pass

        with open(os.path.join(self.model_path, "CB_model.csv"), "w") as f:
            output = csv.writer(f)
            output.writerows(self.cb_model.collect())
