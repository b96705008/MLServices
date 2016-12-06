import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_counts_and_averages(id_and_ratings_tuple):
    nratings = len(id_and_ratings_tuple[1])
    total_ratings = sum(x for x in id_and_ratings_tuple[1])
    return id_and_ratings_tuple[0], (nratings, float(total_ratings) / nratings)

class MovieLenDataset:
    def __init__(self, sc, dataset_path):
        logger.info("Starting up the Data preparator...")
        self.sc = sc
        self.dataset_path = dataset_path
        self.prepare_data()
        # self.ratings_RDD
        # self.movies_RDD -> movieId, title, genres
        # self.movies_titles_RDD
        # self.movies_rating_counts_RDD

    def prepare_data(self):
        self.__load_ratings(self.dataset_path)
        self.__load_movies(self.dataset_path)
        self.__count_and_average_ratings()

    def add_ratings(self, ratings):
        new_ratings_RDD = self.sc.parallelize(ratings)
        self.ratings_RDD = self.ratings_RDD.union(new_ratings_RDD)
        self.__count_and_average_ratings()

    def __load_ratings(self, dataset_path):
        logger.info("Loading Ratings data...")
        ratings_file_path = os.path.join(dataset_path, 'ratings.csv')
        ratings_raw_RDD = self.sc.textFile(ratings_file_path)
        ratings_raw_data_header = ratings_raw_RDD.take(1)[0]
        self.ratings_RDD = ratings_raw_RDD.filter(lambda line: line != ratings_raw_data_header) \
            .map(lambda line: line.split(",")) \
            .map(lambda tokens: (int(tokens[0]), int(tokens[1]), float(tokens[2]))) \
            .cache()

    def __load_movies(self, dataset_path):
        logger.info("Loading Movies data...")
        movies_file_path = os.path.join(dataset_path, 'movies.csv')
        movies_raw_RDD = self.sc.textFile(movies_file_path)
        movies_raw_data_header = movies_raw_RDD.take(1)[0]
        self.movies_RDD = movies_raw_RDD \
            .filter(lambda line: line != movies_raw_data_header) \
            .map(lambda line: line.split(",")) \
            .map(lambda tokens: (int(tokens[0]), tokens[1], tokens[2])) \
            .cache()
        self.movies_titles_RDD = self.movies_RDD.map(lambda x: (int(x[0]), x[1])).cache()

    def __count_and_average_ratings(self):
        logger.info('Counting movie ratings...')
        movie_ID_with_ratings_RDD = self.ratings_RDD.map(lambda x: (x[1], x[2])).groupByKey()
        movie_ID_with_avg_ratings_RDD = movie_ID_with_ratings_RDD.map(get_counts_and_averages)
        self.movies_rating_counts_RDD = movie_ID_with_avg_ratings_RDD.map(lambda x: (x[0], x[1][0]))
