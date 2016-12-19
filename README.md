# MLServices
* reference from http://predictionio.incubator.apache.org/system/

## Module structure (movie_len_recommender)
### dataset
* prepare training data
* prepare entity id map

### algorithm
* train model
* save model or just dump result

### model
* load model or/and using dataset
* predict, recommend, or serve function

### engine
* coordinate dataset, algorithm and service
* build new service by changing dataset, algorithm
* support luigi or any scheduler in the future
* https://github.com/spotify/luigi

### serving
* Flask API route
* Can be merge to app.py (global) or microservice

## Example
### Required
* pyspark (1.6 or 2.0)
* keras (tensorflow & theano) - contribute from RC

### Services
* MoviesLens recommender
* Iris classifier

### Run Microservice
* Start iris service on port 5001, movielens service on port 5002
```
  # redis-server should start (pubsub server)

  # == IRIS DNN classifier ==
  python services/iris_classifier/builder.py
  python services/iris_classifier/serving.py
  # redis-cli: PUBLISH iris_builder BUILD_MODEL
  # redis-cli: PUBLISH iris_api KILL

  # == MovieLens recommender ==
  python services/movielens_recommender/builder.py
  python services/movielens_recommender/serving.py
  # redis-cli: PUBLISH movie_rc_builder BUILD_MODEL
  # redis-cli: PUBLISH movie_rc_api KILL
```
* Routes
1. http://localhost:5001/features/2,3,4,1/class
2. http://localhost:5001/features/2,3,4,1/probs
3. http://localhost:5002/users/1/top/10
