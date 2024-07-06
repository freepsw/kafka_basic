# Apache Kafka Producer & Consumer 구현 (Java)
- https://developer.confluent.io/tutorials/kafka-producer-callback-application/confluent.html

## Download java project
- Maven 설치 : https://tecadmin.net/install-apache-maven-on-centos/
```
# Git에서 실습에 사용할 파일 다운로드
> cd ~
> sudo dnf install -y git
> git clone https://github.com/freepsw/kafka_basic.git

# Java package 생성을 위한 maven 환경 설치
> cd ~
> wget https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz
> sudo tar xzf apache-maven-3.9.6-bin.tar.gz -C /opt
> ls /opt
apache-maven-3.9.6

> sudo vi /etc/profile.d/maven.sh
# 아래 내용 추가
export M2_HOME=/opt/apache-maven-3.9.6
export PATH=${M2_HOME}/bin:${PATH}

> sudo chmod +x /etc/profile.d/maven.sh
> source /etc/profile.d/maven.sh

# maven 정상 설치 확인
> mvn -version
Apache Maven 3.9.6 (bc0240f3c744dd6b6ec2920b3cd08dcc295161ae)
Maven home: /opt/apache-maven-3.9.6
```

## Compile and Run Java Producer & Consumer 
### kafka client configuration (pom.xml)
```xml
        <dependency>
            <groupId>org.apache.kafka</groupId>
            <artifactId>kafka-clients</artifactId>
            <version>3.0.0</version>
        </dependency>
```
### Compile java 
```
> cd  ~/kafka_basic/05.producer_consumer_code/java/my-kafka-java/
> mvn clean package
.....
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  11.961 s
[INFO] Finished at: 2024-07-06T02:01:04Z
[INFO] ------------------------------------------------------------------------
```

## Run kafka console consumer & producer 
```
## topic을 생성하지 않았다면, 아래와 같이 생성한다. 
> cd $KAFKA_HOME
> bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 2 --topic my_topic
> bin/kafka-topics.sh --list --bootstrap-server localhost:9092
__consumer_offsets
my_topic

```

## Java Producer 테스트 
### Run a consumer 
- 확인을 위한 consumer 먼저 실행
```
> cd ~/apps/kafka_org/kafka_2.12-3.6.2
> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic my_topic \
--property print.key=true \
--property key.separator="-" \
--group my-group \
--from-beginning
```
### simple producer 실행 테스트
```
> cd ~/kafka_basic/05.producer_consumer_code/java/my-kafka-java/

> mvn exec:java -Dexec.mainClass="Producer_Simple"
[kafka-producer-network-thread | producer-1] INFO org.apache.kafka.clients.Metadata - [Producer clientId=producer-1] Cluster ID: GSuXzFhKRdCTcJ47F6h1Kg
ProducerRecord(topic=my_topic, partition=null, headers=RecordHeaders(headers = [], isReadOnly = true), key=null, value=simple producer message, timestamp=null)
....
```

### Sync 방식으로 메세지를 전달하는 producer 실행 테스트
```
> mvn exec:java -Dexec.mainClass="Producer_Callback_Sync"
[kafka-producer-network-thread | producer-1] INFO org.apache.kafka.clients.Metadata - [Producer clientId=producer-1] Cluster ID: GSuXzFhKRdCTcJ47F6h1Kg
Record written to offset 15 timestamp 1720231653778
....
```

### ASync 방식으로 메세지를 전달하는 producer 실행 테스트
```
> mvn exec:java -Dexec.mainClass="Producer_Callback_Async"
[kafka-producer-network-thread | producer-1] INFO org.apache.kafka.clients.Metadata - [Producer clientId=producer-1] Cluster ID: GSuXzFhKRdCTcJ47F6h1Kg
Record written to offset 16 timestamp 1720231716066
....

```

## Java Consumer 테스트 
### Run Producer 
- Consumer로 데이터를 전송하기 위한 producer 실행 
```
> cd ~/apps/kafka_org/kafka_2.12-3.6.2
> bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic my_topic \
--property "parse.key=true" \
--property "key.separator=:" \
--property "print.key=true"

k1:simple msg
k2:commit_auto
k3:commit_sync
k4:commit_sync_offset
k5:commit_async
```

### 1. Simple Consumer 실행 테스트
```
> cd ~/kafka_basic/05.producer_consumer_code/java/my-kafka-java/
> mvn exec:java -Dexec.mainClass="Consumer_Simple"
.....
ConsumerRecord(topic = my_topic, partition = 1, leaderEpoch = 0, offset = 40, CreateTime = 1720232352626, serialized key size = 2, serialized value size = 10, headers = RecordHeaders(headers = [], isReadOnly = false), key = k1, value = simple msg)
```

### 2. Auto commit Consumer 실행 테스트
- consumer가 메세지를 읽어온 후 자동으로 마지막 offset을 commit
```
> mvn exec:java -Dexec.mainClass="Consumer_Commit_Auto"

ConsumerRecord(topic = my_topic, partition = 0, leaderEpoch = 0, offset = 20, CreateTime = 1720232462094, serialized key size = 2, serialized value size = 11, headers = RecordHeaders(headers = [], isReadOnly = false), key = k3, value = commit_sync)

```

### 3. 수동 commit Consumer 실행 테스트
- Consumer에서 메세지를 읽은 후, 직접 코드에서 commit을 실행
- Consumer를 새롭게 시작하면, Consumer rebalance가 발생하여 초기 메세지를 읽어오는데 시간이 수 초 이상 걸림.
```
> mvn exec:java -Dexec.mainClass="Consumer_Commit_Sync"

ConsumerRecord(topic = my_topic, partition = 0, leaderEpoch = 0, offset = 21, CreateTime = 1720232856375, serialized key size = 2, serialized value size = 18, headers = RecordHeaders(headers = [], isReadOnly = false), key = k4, value = commit_sync_offset)

```

### 4. 수동 commit + partition/offset 지정하는 Consumer 실행 테스트
- 사용자가 직접 partition별 offset 값을 지정하여 commit 하는 방식
```
> mvn exec:java -Dexec.mainClass="Consumer_Commit_Sync_Offset"

ConsumerRecord(topic = my_topic, partition = 0, leaderEpoch = 0, offset = 22, CreateTime = 1720233170376, serialized key size = 2, serialized value size = 18, headers = RecordHeaders(headers = [], isReadOnly = false), key = k4, value = commit_sync_offset)
```


### 5. Async CommitConsumer 실행 테스트
- Commit 후 결과를 기다리지 않고, 다음 메세지를 처리하는 방식
- Commit 결과를 기다리는 시간이 없기 때문에, 더 많은 메세지를 처리할 수 있음
- 다만, commit이 실패하는 경우, 이전 데이터를 다시 읽어오는 과정에서 중복이 발생할 수 있음
- https://hudi.blog/kafka-consumer/
```
> mvn exec:java -Dexec.mainClass="Consumer_Commit_Async"
....
Commit succeeded
Commit succeeded
ConsumerRecord(topic = my_topic, partition = 0, leaderEpoch = 0, offset = 23, CreateTime = 1720233469257, serialized key size = 2, serialized value size = 12, headers = RecordHeaders(headers = [], isReadOnly = false), key = k5, value = commit_async)
Commit succeeded
.....
```


## ETC 
### Java project using maven
- https://kafka.apache.org/25/javadoc/overview-summary.html

### Java project using gradle
- https://developer.confluent.io/tutorials/kafka-producer-callback-application/confluent.html#initialize-the-project