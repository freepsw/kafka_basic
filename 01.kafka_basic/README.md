# Apache Kafka 기본 명령어 활용 예시

## 1. Basic Command 

### 1-1. Key/Value 전송
```
> cd ~/apps/kafka_2.12-3.6.2
> bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 2 --topic kv_topic

> bin/kafka-topics.sh --list --bootstrap-server localhost:9092
__consumer_offsets
kv_topic
mytopic


> bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic kv_topic \
--property "parse.key=true" \
--property "key.separator=:" \
--property "print.key=true"
k1:msg1
k2:msg2
k3:msg3
k4:msg4
k5:msg5
k6:msg6
k7:msg7

> cd ~/apps/kafka_2.12-3.6.2
> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic kv_topic --from-beginning

msg1
msg2
msg3
msg4
msg5
msg6
msg7

> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic kv_topic \
--property print.key=true \
--property key.separator="-" \
--group my-group \
--from-beginning

k1-msg1
k2-msg2
k6-msg6
k3-msg3
k4-msg4
k5-msg5
k7-msg7


```

### 1-2. Consumer Group 확인하기
```
> cd ~/apps/kafka_2.12-3.6.2
> bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
my-group
console-consumer-64400


> bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group my-group --describe
GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID                                           HOST            CLIENT-ID
my-group        kv_topic        0          4               4               0               console-consumer-00714fae-a38e-4c52-9b7b-83e431210802 /10.178.0.4     console-consumer
my-group        kv_topic        1          3               3               0               console-consumer-00714fae-a38e-4c52-9b7b-83e431210802 /10.178.0.4     console-consumer
```

### 1-3. Multi Consumer 실행
- my-group 내에 2개의 consumer를 실행한다. 
```
## Consumer 0 (my-group)
> cd ~/apps/kafka_2.12-3.6.2

> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic kv_topic \
--property print.key=true \
--property key.separator="-" \
--group my-group \
--from-beginning

## Consumer 1 (my-group)
> cd ~/apps/kafka_2.12-3.6.2

> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic kv_topic \
--property print.key=true \
--property key.separator="-" \
--group my-group \
--from-beginning

## Consumer group 확인 
## 2개의 consumer에 각 partition 1개씩 할당되어 처리하고 있음.  
> cd ~/apps/kafka_2.12-3.6.2
> bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group my-group --describe

GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID                                           HOST            CLIENT-ID
my-group        kv_topic        0          4               4               0               console-consumer-49fe00c1-4f0e-4fe4-b33f-489165b540de /10.178.0.4     console-consumer
my-group        kv_topic        1          3               3               0               console-consumer-49fe00c1-4f0e-4fe4-b33f-489165b540de /10.178.0.4     console-consumer

## Key/Value 데이터 전송 
## 동일한 Key 데이터가 항상 동일한 consumer로 전달 되는지 확인 가능 
> cd ~/apps/kafka_2.12-3.6.2

> bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic kv_topic \
--property "parse.key=true" \
--property "key.separator=:" \
--property "print.key=true"
k1:msg1
k2:msg2
k3:msg3
k4:msg4
k5:msg5
k1:msg1
k2:msg2
k3:msg3
k4:msg4
k5:msg5
k1:msg1
k2:msg2

## Consumer 0의 출력 결과
k3-msg3
k4-msg4
k5-msg5
k3-msg3
k4-msg4
k5-msg5

## Consumer 1의 출력 결과
k1-msg1
k2-msg2
k1-msg1
k2-msg2
k1-msg1
k2-msg2

# Consumer 중지
```


### 1-4. Consumer에서 특정 partition 데이터만 읽어오기
- partition 옵션을 통해서 특정 partition만 읽도록 조정 가능 
```
> cd ~/apps/kafka_2.12-3.6.2
> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic kv_topic \
  --partition 1 \
  --from-beginning

msg1
msg2
msg6
msg1
msg2
msg1
msg2
msg1
msg2

```

### Consumer에서 특정 partition의 특정 offset 이후의 데이터만 읽어오기
- offset 0는 from-beginning과 동일한 효과 
```
> cd ~/apps/kafka_2.12-3.6.2

> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic kv_topic \
  --partition 1 \
  --offset 0

msg1
msg2
msg6
msg1
msg2
msg1
msg2
msg1
msg2

```


## Idempotence Producer
- 기본 producer은 데이터만 전달하는거에 비해 멱등성 producer은 데이터를 전달할 때 producer PID와 시퀀스 넘버를 함께 전달하여 중복 데이터 적재를 방지한다. 
- 시퀀스 넘버는 데이터를 전달할 때마다 시퀀스 넘버를 1씩 증가하여 보내며, broker는 데이터를 전달받을 때 PID와 시퀀스 넘버를 이용해 같은 데이터인지를 확인하고 같은 데이터인 경우 데이터를 저장하지 않는다.
```
> cd ~/apps/kafka_2.12-3.6.2

> vi producer.conf
enable.idempotence=true
max.in.flight.request.per.connection=5
retries=3
acks=all

> bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic kv_topic --producer.config producer.conf
k8:msg8
k9:msg9
k10:msg10
k11:msg11
k12:msg12
```


### Delete messages in topic
- topic 내의 지정한 partition의 시작점에서 특정 offset 까지의 범위를 삭제한다. 
#### delete_offset.json
```json
{
    "partitions": [
    {"topic": "kv_topic", "partition":0, "offset": 2}
    ], 
    "version":1
}
```
- 중간의 특정 데이터만 삭제할 수는 없음
```
# partition 0번의 offset 0~2 까지의 데이터를 삭제한다. 
> cd ~/apps/kafka_2.12-3.6.2

# 삭제하기 이전의 데이터 확인
> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic kv_topic   --partition 0   --from-beginning
msg3
msg4
msg5
msg7
msg3
msg4
msg5
msg3
msg4
msg5


# 데이터 삭제를 위한 설정 파일 생성
> vi delete_offset.json

> bin/kafka-delete-records.sh --bootstrap-server localhost:9092 --offset-json-file ./delete_offset.json
Executing records delete operation
Records delete operation completed:
partition: kv_topic-0	low_watermark: 2

> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic kv_topic   --partition 0   --from-beginning
## msg3, msg4 데이터가 삭제됨
msg5
msg7
msg3
msg4
msg5
msg3
msg4
msg5
...
```


## 2. 운영관련 Command 
### Dump kafka log file(segment)
```
> bin/kafka-dump-log.sh --print-data-log --files /tmp/kafka-logs/kv_topic-0/00000000000000000000.log

Dumping /tmp/kafka-logs/kv_topic-0/00000000000000000000.log
Starting offset: 0   <-- offset 시작점

## offset 0 번째 데이터 정보 출력  
baseOffset: 0 lastOffset: 0 count: 1 baseSequence: -1 lastSequence: -1 producerId: -1 producerEpoch: -1 partitionLeaderEpoch: 0 isTransactional: false isControl: false position: 0 CreateTime: 1648305071780 size: 74 magic: 2 compresscodec: none crc: 585719343 isvalid: true
| offset: 0 CreateTime: 1648305071780 keySize: 2 valueSize: 4 sequence: -1 headerKeys: [] key: k3 payload: msg3


## offset 0~2 번째 데이터 정보 출력 
baseOffset: 0 lastOffset: 2 count: 3 baseSequence: 0 lastSequence: 2 producerId: 1000 producerEpoch: 0 partitionLeaderEpoch: 0 isTransactional: false isControl: false deleteHorizonMs: OptionalLong.empty position: 0 CreateTime: 1719919955151 size: 100 magic: 2 compresscodec: none crc: 2553173963 isvalid: true
| offset: 0 CreateTime: 1719919955151 keySize: 2 valueSize: 4 sequence: 0 headerKeys: [] key: k3 payload: msg3
| offset: 1 CreateTime: 1719919955151 keySize: 2 valueSize: 4 sequence: 1 headerKeys: [] key: k4 payload: msg4
| offset: 2 CreateTime: 1719919955151 keySize: 2 valueSize: 4 sequence: 2 headerKeys: [] key: k5 payload: msg5

## offset 3 번째 데이터 정보 출력 
baseOffset: 3 lastOffset: 3 count: 1 baseSequence: 3 lastSequence: 3 producerId: 1000 producerEpoch: 0 partitionLeaderEpoch: 0 isTransactional: false isControl: false deleteHorizonMs: OptionalLong.empty position: 100 CreateTime: 1719919956175 size: 74 magic: 2 compresscodec: none crc: 3724116375 isvalid: true
| offset: 3 CreateTime: 1719919956175 keySize: 2 valueSize: 4 sequence: 3 headerKeys: [] key: k7 payload: msg7

## offset 4 ~ 9 번째 데이터 정보 출력 
baseOffset: 4 lastOffset: 9 count: 6 baseSequence: 0 lastSequence: 5 producerId: 1001 producerEpoch: 0 partitionLeaderEpoch: 0 isTransactional: false isControl: false deleteHorizonMs: OptionalLong.empty position: 174 CreateTime: 1719920692528 size: 139 magic: 2 compresscodec: none crc: 1245378216 isvalid: true
| offset: 4 CreateTime: 1719920692527 keySize: 2 valueSize: 4 sequence: 0 headerKeys: [] key: k3 payload: msg3
| offset: 5 CreateTime: 1719920692528 keySize: 2 valueSize: 4 sequence: 1 headerKeys: [] key: k4 payload: msg4
| offset: 6 CreateTime: 1719920692528 keySize: 2 valueSize: 4 sequence: 2 headerKeys: [] key: k5 payload: msg5
| offset: 7 CreateTime: 1719920692528 keySize: 2 valueSize: 4 sequence: 3 headerKeys: [] key: k3 payload: msg3
| offset: 8 CreateTime: 1719920692528 keySize: 2 valueSize: 4 sequence: 4 headerKeys: [] key: k4 payload: msg4
| offset: 9 CreateTime: 1719920692528 keySize: 2 valueSize: 4 sequence: 5 headerKeys: [] key: k5 payload: msg5


## partition 0의 offset이 2번 부터 시작함. (이전에 삭제한 0,1 offet은 제외)
> bin/kafka-run-class.sh kafka.tools.DumpLogSegments --deep-iteration --print-data-log --files /tmp/kafka-logs/kv_topic-0/00000000000000000000.timeindex
Dumping /tmp/kafka-logs/kv_topic-0/00000000000000000000.timeindex
timestamp: 0 offset: 0
The following indexed offsets are not found in the log.
Indexed offset: 0, found log offset: 2

```

### Topic의 partition 별로 마지막 commit 된 위치 확인
```
> cat /tmp/kafka-logs/replication-offset-checkpoint
kv_topic 0 10 <-- partition 0은 마지막 commit offset이 10 (현재 9번 offset까지 존재)
kv_topic 1 14 <-- partition 0은 마지막 commit offset이 14 (현재 13번 offset까지 존재)
```

#### 다시 데이터를 전송한 후, commit 값이 증가했는지 확인 
```
> bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic kv_topic \
 --property "parse.key=true" \
 --property "key.separator=:" \
 --property "print.key=true"
k20:msg20
k21:msg21

> cat /tmp/kafka-logs/replication-offset-checkpoint
kv_topic 0 12 <-- partition 0에만 위 2건이 추가된 commit 확인 가능
kv_topic 1 14
``` 

## 현재 Broker 설정 확인 
- 현재 운영중인 Kafka broker에 적용된 모든 설정 값을 확인 가능
```
> bin/kafka-configs.sh --bootstrap-server localhost:9092 --broker 0 --describe --all
All configs for broker 0 are:
  advertised.listeners=null sensitive=false synonyms={}
  alter.config.policy.class.name=null sensitive=false synonyms={}
  alter.log.dirs.replication.quota.window.num=11 sensitive=false synonyms={DEFAULT_CONFIG:alter.log.dirs.replication.quota.window.num=11}
  alter.log.dirs.replication.quota.window.size.seconds=1 sensitive=false synonyms={DEFAULT_CONFIG:alter.log.dirs.replication.quota.window.size.seconds=1}
  authorizer.class.name= sensitive=false synonyms={DEFAULT_CONFIG:authorizer.class.name=}
  auto.create.topics.enable=true sensitive=false synonyms={DEFAULT_CONFIG:auto.create.topics.enable=true}
  auto.include.jmx.reporter=true sensitive=false synonyms={DEFAULT_CONFIG:auto.include.jmx.reporter=true}
  auto.leader.rebalance.enable=true sensitive=false synonyms={DEFAULT_CONFIG:auto.leader.rebalance.enable=true}
  background.threads=10 sensitive=false synonyms={DEFAULT_CONFIG:background.threads=10}
  broker.heartbeat.interval.ms=2000 sensitive=false synonyms={DEFAULT_CONFIG:broker.heartbeat.interval.ms=2000}

.....
```



### 관련 github repository

- https://github.com/onlybooks/kafka2 실전 카프카 개발부터 운영까지

- https://github.com/bjpublic/apache-kafka-with-java 아파치 카프카 애플리케이션 프로그래밍 with 자바

- https://github.com/bstashchuk/apache-kafka-course The Complete Apache Kafka Practical Guide

### Fastcampus kafka 강의 자료
- https://github.com/jingene/fastcampus_kafka_handson Part 2. 실무에서 쉽게 써보는 Kafka

- https://github.com/fast-campus-lecture Part 3. Spring for Apache Kafka

- https://github.com/freepsw/kafka-metrics-monitoring Part 4. 실시간 모니터링을 위한 Kafka 매트릭 이해