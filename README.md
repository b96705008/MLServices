# MLServices
* reference from http://predictionio.incubator.apache.org/system/

## Module structure (services)

### Builder service
#### dataset
* prepare training data
* prepare entity id map

#### algorithm
* train model
* save model or just dump result

#### builder
* coordinate dataset to algorithm
* subscribe for BUILD_MODEL command
* publish NEW_MODEL for engine
* builder service app

### API service
#### model
* load model or/and using dataset
* predict, recommend, or serve function

#### engine
* coordinate model for API service(serving)
* subscribe NEW_MODEL command

#### serving
* Flask API route
* API service app

### App entry point
* app.py for builder or api

## Example
### Required
* pyspark (1.6 or 2.0)
* keras (tensorflow & theano) - contribute from RC

### Services
* Iris classifier
* MoviesLens recommender

### Run Microservice
* Start iris service on port 5001, movielens service on port 5002
```
  # should be execute the bin/start.sh firstly
  # 1. it will export the enviornment python path
  # 2. it will start the redis-server

  # == IRIS DNN classifier ==
  python services/iris_classifier/app.py --service builder --channel iris_builder
  python services/iris_classifier/app.py --service api --channel iris_api
  # redis-cli: PUBLISH iris_builder BUILD_MODEL
  # redis-cli: PUBLISH iris_api KILL

  # == MovieLens recommender ==
  python services/movielens_recommender/app.py --service builder --channel movielens_builder
  python services/movielens_recommender/app.py --service api --channel movielens_api
  # redis-cli: PUBLISH movie_rc_builder BUILD_MODEL
  # redis-cli: PUBLISH movie_rc_api KILL
```
* Routes
1. http://localhost:5001/features/2,3,4,1/class
2. http://localhost:5001/features/2,3,4,1/probs
3. http://localhost:5002/users/1/top/10
