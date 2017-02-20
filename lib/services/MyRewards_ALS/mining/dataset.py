import os
from basic.dataset import MLDataset
from utils.env import logger, sc, sqlContext, root_dir

product_list = {"rec_mmo_click" : ("MMO_Click", 1.167),
                "rec_mmo_att"   : ("MMO_ATT", 2.417),
                "rec_mmo_fav_p" : ("MMO_FAV_P", 2.167)}

other_list = {"rec_mmo_fav_s" : ("MMO_FAV_S_", 1.667),
              "rec_cctxn" : ("CCTXN", 1.917),
              "rec_bpoint" : ("BPOINT", 2.417),
              "rec_cti" : ("CTI", 1.833),
              "rec_web" : ("WEB", 1)}

class MyRewardsALSDataset(MLDataset):
    def init(self):
        self.sc = sc
        self.sqlContext = sqlContext

    def prepare_data(self):
        logger.info("Prepare ALS data...")

        self.__load_data()
        self.__prepare_mapping()
        self.__prepare_rating()

    def __load_data(self):
        logger.info("Loading rating data...")

        basepath_driver = os.path.join(root_dir(), "driver")

        product_rdd = self.sc.parallelize([])
        for i in product_list.keys():
            product_df = self.sqlContext.read.format("jdbc") \
                                        .option("driver", "com.teradata.jdbc.TeraDriver") \
                                        .option("url", self.connect_td) \
                                        .option("dbtable", "myrewards_" + i) \
                                        .load()
            product_raw = product_df.rdd.map(lambda row: [r if isinstance(r, int) or isinstance(r, float) else r.strip().encode("utf8") if r else "None" for r in row])

            group = product_list[i][0]
            weight = product_list[i][1]

            product_data = product_raw.map(lambda x: (("product", x[1], x[3].replace(group + "_", "")), int(x[4]) * weight))

            product_rdd = product_rdd.union(product_data)

        rating_rdd = product_rdd.reduceByKey(lambda x, y: x + y) \
                                     .map(lambda x: ((x[0][0], x[0][2]), x[0][1], x[1]))

        for i in other_list:
            other_df = self.sqlContext.read.format("jdbc") \
                                      .option("driver", "com.teradata.jdbc.TeraDriver") \
                                      .option("url", self.connect_td) \
                                      .option("dbtable", "myrewards_" + i) \
                                      .load()
            other_raw = other_df.rdd.map(lambda row: [r if isinstance(r, int) or isinstance(r, float) else r.strip().encode("utf8") if r else "None" for r in row])

            group = other_list[i][0]
            weight = other_list[i][1]

            other_data = other_raw.map(lambda x: (("other", x[3]), x[1], int(x[4]) * weight))

            rating_rdd = rating_rdd.union(other_data)
            
        self.rating_rdd = rating_rdd

    def __prepare_mapping(self):
        logger.info("Preparing mapping table...")

        self.customer_map = self.rating_rdd.map(lambda x: x[1]).distinct().zipWithIndex().collectAsMap()
        self.feature_map = self.rating_rdd.map(lambda x: (x[0][0], x[0][1])).distinct().zipWithIndex().collectAsMap()

    def __prepare_rating(self):
        logger.info("Preparing rating data...")

        bc_customer_map = self.sc.broadcast(self.customer_map)
        bc_feature_map = self.sc.broadcast(self.feature_map)
        self.rating_data = self.rating_rdd.map(lambda x: (bc_customer_map.value[x[1]], bc_feature_map.value[x[0]], x[2]))
