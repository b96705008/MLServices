import os
from pyspark import SparkContext, SparkConf
from movie_len_recommender.engine import MovieRCEngine

def init_spark_context():
    conf = SparkConf().setAppName("ALS Service").setMaster("local[*]")
    sc = SparkContext(conf=conf)
    return sc

if __name__ == '__main__':
    sc = init_spark_context()
    dataset_path = os.path.join('datasets', 'ml-latest-small')
    model_path = os.path.join('models', 'movie_lens_als')

    # build engine
    engine = MovieRCEngine(sc, dataset_path, model_path)

    # buil init service
    service1 = engine.build_service()
    mRatings = service1.get_top_ratings(1, 10)
    print('===initial ratings===')
    for m in mRatings:
        print(m)

    # add ratings
    engine.add_ratings([(2, 7502, 5), (3, 7502, 2), (1, 1, 3)])

    # build new service
    service2 = engine.build_service()
    mRatings = service2.get_top_ratings(1, 10)
    print('===new ratings===')
    for m in mRatings:
        print(m)
