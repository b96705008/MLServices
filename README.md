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
* keras

### Services
* MoviesLens recommender
* Iris classifier

### Run Global
*  Start server on port 8000
```
  python app.py
```
* Routes
1. http://localhost:8000/iris/features/2,3,4,1/class
2. http://localhost:8000/iris/features/2,3,4,1/probs
3. http://localhost:8000/movielens/users/1/top/10

### Microservice
* Start movielens service on port 5003, iris service on port 5001
```
  # redis-server should start
  python iris_classifier/builder.py
  python iris_classifier/serving.py
  # PUBLISH iris_builder BUILD_MODEL
  # PUBLISH iris_api KILL

  # recommender
  python movielens_recommender/serving.py
```
* Routes
1. http://localhost:5001/features/2,3,4,1/class
2. http://localhost:5001/features/2,3,4,1/probs
3. http://localhost:5003/users/1/top/10
