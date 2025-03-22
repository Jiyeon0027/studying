# SPARK

- 대규모 데이터 프로세싱을 위한 도구
- map, flatmap, filter, distinct, sample, union, intersection, subtract, cartesian
- collect, count, countByValue, take, top, reduce,…
- LAZY evaluation → 액션을 부르기 전까지 아무것도 하지 않음
  → 액션 요청하자마자 바로 원하는 결과를 얻기위한 최적화 경로를 계산

## spark3

- mllib 사라지기 시작함 →RDD 가 있는것들에 관해서 (dataframe)
- 훨씬 빨라짐 17배
- 딥러닝 시스템의 탑재? 클러스터에 걸쳐 딥러닝? GPU 인스턴스 사용을 원활하게
- Binary file support
- spark Graph
- Cypher

## spark Context

- 클러스터와 스파크 애플리케이션과의 연결을 관리하는 객체로 모든 스파크 애플리케이션은 반드시 SparkContext를 생성해야 함

- SparkContext는 생성할 때 스파크 동작에 필요한 설정들의 정보를 지정
- master 클러스터 마스터의 정보, appName은 애플리케이션의 이름은 필수적으로 지정해야하는 정보
- 간단한 예시 (conf 안에서 spark context의 설정값을 지정해줌)

```python
conf = new SparkConf().setMaster("local[2]").setAppName("My App")
sc = new SparkContext(conf)
```

- spark Context 를 만들었다면 이 객체를 통해 RDD 를 생성가능
  - RDD를 만들기 위해 sc.textFile()을 호출 → 연산 수행가능
  - 이러한 연산을 수행하기 위해서 Executer들을 관리함

```python
from pyspark import SparkConf, SparkContext
import collections

conf = SparkConf().setMaster("local").setAppName("RatingsHistogram")
sc = SparkContext(conf=conf)

lines = sc.textFile("./ml-100k/u.data")
ratings = lines.map(lambda x: x.split()[2])
result = ratings.countByValue()  # spark Code

sortedResults = collections.OrderedDict(sorted(result.items()))  # python codes
for key, value in sortedResults.items():
    print("%s %i" % (key, value))
```

## RDD’s can hold key/value pairs

- 키 단위로 집계가 가능
- 값에 복잡한것이 있더라도 원래값을 키를 유지하고 그 값에 대한 값을 만들 수 있음
- reduceByKey() , groupByKey() , sortByKey()
- keys(), values()
- join(), rightOuterJoin(), leftOuterJoin() … 과 같은 sql-style 조인을 사용가능
- mapValues(), flatmapValues() 이는 키에 영향을 주지 않음 → 효율

## sparkSQL

- RDD 를 Dataframe object로 확장하기
- DataFrames : 큰 데이터 프레임 테이블과 비슷함
  - Contain Row objects, SQL 쿼리로 접근 가능
  - Spark session 을 불러와서 spark sql을 사용할 수 있도록 함
  - MLlib 와 Spark Streaming 서비스도 DataFrame을 사용하는 것으로 이동중
- DataSet : can wrap Known, typed data를 같이 wrap 할 수 있도록 해줌

  - python 보다는 scala를 사용하도록 함

- SparkSession 은 스파크 컨텍스트에 세션 상태 정보를 추가로 담은것
- Spark 에서 사용자가 RDD와 같은 백엔드 서비스에 직접 접근 가능한 API를 사용하는 대신 RDD보다 한단계 추상화된 API 를 사용해 코드를 작성하게 하고 최적화 과정을 거쳐 실제 동작 가능한 RDD 기반 코드로 전환 → 데이터 프레임과 데이터 셋

```python
from pyspark.sql import SparkSession
from pyspark.sql import Row

# Create a SparkSession
spark = SparkSession.builder.appName("SparkSQL").getOrCreate()

def mapper(line):
    fields = line.split(',')
    return Row(ID=int(fields[0]), name=str(fields[1].encode("utf-8")), \
               age=int(fields[2]), numFriends=int(fields[3]))

lines = spark.sparkContext.textFile("fakefriends.csv")
people = lines.map(mapper)

# Infer the schema, and register the DataFrame as a table.
schemaPeople = spark.createDataFrame(people).cache()
schemaPeople.createOrReplaceTempView("people")

# SQL can be run over DataFrames that have been registered as a table.
# age field 는 위의 mapper 로 이름이 매핑되었음
teenagers = spark.sql("SELECT * FROM people WHERE age >= 13 AND age <= 19")

# The results of SQL queries are RDDs and support all the normal RDD operations.
for teen in teenagers.collect():
  print(teen)

# We can also use functions instead of SQL queries:
schemaPeople.groupBy("age").count().orderBy("age").show()

spark.stop()
```

- SparkSession 을 통해 불러와서 SQL을 사용할 수 있도록 함

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SparkSQL").getOrCreate()

people = spark.read.option("header", "true").option("inferSchema", "true")\
    .csv("file:///SparkCourse/fakefriends-header.csv")

print("Here is our inferred schema:")
people.printSchema()

print("Let's display the name column:")
people.select("name").show()

print("Filter out anyone over 21:")
people.filter(people.age < 21).show()

print("Group by age")
people.groupBy("age").count().show()

print("Make everyone 10 years older:")
people.select(people.name, people.age + 10).show()

spark.stop()

# printSchema(), select(), filter(), groupby(), show()…
# 위와 같이 csv 파일을 읽어서 Dataframe 으로 바로 가지고 올 수 있음
```

## Spark 안에서 BFS를 이용하는 예시

- 슈퍼 히어로들간의 관계 즉, 거리를 SPARK BFS로 구현하는 예시
- accumulator 가 많은 작업들을 공유 변수를 이용해 증가시키고 있음 (cluster 내부)
  - 관심이 있는 캐릭터가 나올때 까지 반복하고 있음
  - 실행이 완료되었는지 알기 위해서 accumulator를 사용
- mapper: hitcounter를 증가시키는 역할
- reducer : 두 데이터를 비교하여 하나의 최소 거리를 구하는 역할

```python
#Boilerplate stuff:
from pyspark import SparkConf, SparkContext

conf = SparkConf().setMaster("local").setAppName("DegreesOfSeparation")
sc = SparkContext(conf = conf)

# The characters we wish to find the degree of separation between:
startCharacterID = 5306 #SpiderMan
targetCharacterID = 14  #ADAM 3,031 (who?)

# Our accumulator, used to signal when we find the target character during
# our BFS traversal.
hitCounter = sc.accumulator(0) #누적값을 이용해 작업종료 확인

def convertToBFS(line):
    fields = line.split()
    heroID = int(fields[0])
    connections = []
    for connection in fields[1:]:
        connections.append(int(connection))

    color = 'WHITE'
    distance = 9999

    if (heroID == startCharacterID): #초기 스파이더맨 방문 시 distance =0
        color = 'GRAY'
        distance = 0

    return (heroID, (connections, distance, color))
```

## 추천 시스템에 Spark 를 적용하는 방법

- item - based collaberative filtering

  ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/1206d1c4-0281-421a-8d0e-ffc21959e876/c96fa9ab-c2f5-431e-81e9-1ed4ff542741/Untitled.png)

- 이 경우 userId, Movieid, rating columns 를 찾아서 self join을 시행함 → movie1, movie2, rating1, rating2 를 가지고 이 두 쌍을 가지고 필터링
- duplicate 쌍을 유사성을 구하여 집계 → Filter, sort, display result…
- caching datasets : 다시 유사성에 대한 데이터 셋을 사용하기 위해서는 cache 필요
  - 메모리에 cache dataset
  - cache(), persist() : 복구를 더 잘할 수 있음

---

## EMR (Elastic MapReduce)

- 완전 관리형 빅데이터 플랫폼
- EMR을 사용하는 이유 : 하둡이나 스파크 같이 널리 사용되는 오픈소스 프레임워크를 규모에 구애받지 않고 원하는 용량으로 쉽게 생성 (유연성과 확장성)
- EMR 이 생성한 클러스터는 EC2 인스턴스의 집합
- EMR Cluster = Master Node + Core Node(HDFS) + Task Node(Worker Node)

- 클러스터에서 실행중이기 때문에 스크립트를 수정해야함
  - 확대를 어떻게 할 것인가 → partitioning
  - executor 가 실패할 때 그 이유 추적하기 쉽지 않음
  - .partitionBy() 에서 실행자를 여러명을 나눌 수 있음
- 파티션 size의 선택

  - 너무 적은 파티션 : 클러스터의 큰 이득을 얻지 못함
  - 너무 큰 파티션 : shuffle data 시에 오버헤드 발생
  - 하나의 파티션에 적합한 값이 들어갈 수 있도록 변경하기

- 클러스터에 있는 스파크 트러블 슈팅
  - spark history server 안의 로그를 확인하여 트러블 슈팅이 가능(succeed 여부도 확인)
  - code depenency on spark
    → 하둡의 결함허용에 의존하지 말 것(보장되지 않음)
    → Recovery 불가능
  - 추가로 필요한 python package 는 각 worker에 설치(pip)해주거나 pyfiles로 스파크에 전달하여 실행자 노드에 전달하는 방식 (마스터에는 이미 있어야 함)
  - package 는 웬만하면 쓰지 말것 (종속성 문제에 쓰는 시간이 줄어야함)

---

## SPARK.ML

- 내장 ML라이브러리의 사용 (neural network를 제외)
- 기본적인 통계함수, 회귀모델, 클러스터링 모델,,,
- MLLib 라는 RDD 위에서 사용 가능한 모델이 있었지만 제거 예정 spark3.0 (Dataframe 기준)
- “advanced analytics wirht spark” 2판 추천

```python
names = loadMovieNames()

ratings = spark.read.option("sep", "\t").schema(moviesSchema) \
    .csv("file:///SparkCourse/ml-100k/u.data")

print("Training recommendation model...")

als = ALS().setMaxIter(5).setRegParam(0.01).setUserCol("userID").setItemCol("movieID") \
    .setRatingCol("rating")

model = als.fit(ratings)

# Manually construct a dataframe of the user ID's we want recs for
userID = int(sys.argv[1])
userSchema = StructType([StructField("userID", IntegerType(), True)])
users = spark.createDataFrame([[userID,]], userSchema)

recommendations = model.recommendForUserSubset(users, 10).collect()
#훈련된 모델에 적용하여 결과값을 가져오기
```

- ALS() 라는 추천시스템 모델이 만들어져 있어 이 모델안에 데이터를 넣어주기만 하면 됨

- 값이 정확하지 않을 수 있음
  - 하이퍼 파라미터 튜닝을 적합하게 하여야함 train/test 평가필요
  - 추천시스템에서 데이터가 부족하면 일어날 수 있음
  - 내부적으로 정확하지 않을 수 있음 (블랙박스 알고리즘)
