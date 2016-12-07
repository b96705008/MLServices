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
* required pyspark (1.6 or 2.0)
```
  export PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH
  export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.xx.x-src.zip:$PYTHONPATH
```
*  Start global server on port 5003
```
  python app.py
```
* Start microservice on port 5003 (only movie service)
```
  python movie_len_recommender/serving.py
```
