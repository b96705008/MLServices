from basic.dataset import MLDataset
from utils.env import logger, sc

def get_counts_and_averages(id_and_ratings_tuple):
    nratings = len(id_and_ratings_tuple[1])
    total_ratings = sum(x for x in id_and_ratings_tuple[1])

    return id_and_ratings_tuple[0], (nratings, float(total_ratings) / nratings)

class MovieLenRatings(MLDataset):
    def init(self):
        self.sc = sc

    def prepare_data(self):
        logger.info("Prepare MovieLens data from {}".format(self.dataset_path))

        ratings_raw_RDD = self.sc.textFile(self.dataset_path)
        ratings_raw_data_header = ratings_raw_RDD.take(1)[0]
        self.ratings_RDD = ratings_raw_RDD.filter(lambda line: line != ratings_raw_data_header) \
            .map(lambda line: line.split(",")) \
            .map(lambda tokens: (int(tokens[0]), int(tokens[1]), float(tokens[2]))) \
            .cache()

    def add_ratings(self, ratings):
        new_ratings_RDD = self.sc.parallelize(ratings)
        self.ratings_RDD = self.ratings_RDD.union(new_ratings_RDD)
