import os
from basic.dataset import MLDataset
from utils.env import logger, sc, sqlContext, root_dir
from pyspark.mllib.feature import StandardScaler
from pyspark.mllib.linalg import Vectors

class MyRewardsCBDataset(MLDataset):
    def init(self):
        self.sc = sc
        self.sqlContext = sqlContext

    def prepare_data(self):
        logger.info("Prepare CB data...")

        self.__load_data()
        self.__data_standardized()
        self.__data_separating()

    def __load_data(self):
        logger.info("Loading customer data...")
        
        def data_process(line):
            feature = line[2:6] + line[7:]
            result = [float(feature[i]) for i in range(len(feature))]

            return(Vectors.dense(result))

        def long_to_wide (line, total):
            info = [line[1], line[4], line[5], line[6]]
            mcc = line[9]

            result = [0] * total
            result[int(mcc) - 1] = 1
            result = [info, result]

            return(result)

        basepath_driver = os.path.join(root_dir(), "driver")

        customer_df = self.sqlContext.read.format("jdbc") \
                          .option("driver", "com.teradata.jdbc.TeraDriver") \
                          .option("url", self.connect_td) \
                          .option("dbtable", "myrewards_rec_cust_base") \
                          .load()
        customer_rdd = customer_df.rdd.map(lambda row: [r if isinstance(r, int) or isinstance(r, float) else r.strip().encode("utf8") if r else "None" for r in row]) \
                                      .filter(lambda x: x[6] != "None")

        mcc_total = len(customer_rdd.map(lambda x: x[7:]).first())

        self.customer_profile = customer_rdd.map(lambda x: (x[0], "customer"))
        self.customer_last_product = customer_rdd.map(lambda x: (x[0], x[6]))
        self.customer_feature = customer_rdd.map(data_process)

        logger.info("Loading product data...")

        product_df = self.sqlContext.read.format("jdbc") \
                          .option("driver", "com.teradata.jdbc.TeraDriver") \
                          .option("url", self.connect_td) \
                          .option("dbtable", "myrewards_rec_mmo_product") \
                          .load()
        product_rdd = product_df.rdd.map(lambda row: [r if isinstance(r, int) or isinstance(r, float) else r.strip().encode("utf8") if r else "None" for r in row])

        self.product_profile = product_rdd.map(lambda x: (x[8], "product"))
        self.product_feature = product_rdd.map(lambda x: long_to_wide(x, mcc_total)) \
                                          .map(lambda x: Vectors.dense(x[0] + x[1]))

    def __data_standardized(self):
        logger.info("Standardizing features...")

        all_profile = self.customer_profile.union(self.product_profile)
        all_feature = self.customer_feature.union(self.product_feature)
        scale_model = StandardScaler(withMean = True, withStd = True).fit(all_feature)
        scale_feature = scale_model.transform(all_feature)

        self.scale_data = all_profile.zip(scale_feature)

    def __data_separating(self):
        logger.info("Separpting customer and product data...")

        self.customer_data = self.scale_data.filter(lambda x: x[0][1] == "customer") \
                                            .map(lambda x: (x[0][0], list(x[1])))
        self.product_data = self.scale_data.filter(lambda x: x[0][1] == "product") \
                                           .map(lambda x: (x[0][0], list(x[1])))