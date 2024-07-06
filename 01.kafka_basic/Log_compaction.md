# Log Cleansing 

## Delete Log Examples
- 삭제하기 이전의 sement 파일 확인 
```
> ls -alh /tmp/kafka-logs/kv_topic-0
-rw-r--r--.  1 freepsw18 freepsw18  10M Jul  6 07:16 00000000000000000000.index
-rw-r--r--.  1 freepsw18 freepsw18  405 Jul  2 12:23 00000000000000000000.log
-rw-r--r--.  1 freepsw18 freepsw18  10M Jul  6 07:16 00000000000000000000.timeindex
-rw-r--r--.  1 freepsw18 freepsw18  148 Jul  2 12:44 00000000000000000012.snapshot
-rw-r--r--.  1 freepsw18 freepsw18    8 Jul  6 07:16 leader-epoch-checkpoint
-rw-r--r--.  1 freepsw18 freepsw18   43 Jul  2 11:31 partition.metadata


> ls -alh /tmp/kafka-logs/kv_topic-1
-rw-r--r--.  1 freepsw18 freepsw18  10M Jul  6 07:16 00000000000000000000.index
-rw-r--r--.  1 freepsw18 freepsw18  438 Jul  2 11:52 00000000000000000000.log
-rw-r--r--.  1 freepsw18 freepsw18  10M Jul  6 07:16 00000000000000000000.timeindex
-rw-r--r--.  1 freepsw18 freepsw18  148 Jul  2 12:44 00000000000000000014.snapshot
-rw-r--r--.  1 freepsw18 freepsw18    8 Jul  6 07:16 leader-epoch-checkpoint
-rw-r--r--.  1 freepsw18 freepsw18   43 Jul  2 11:31 partition.metadata
```

- kv_topic 데이터 삭제 
    - 직접 삭제하는 것이 아니라, 데이터를 보유하는 기간을 0으로 조정하여, 
    - 그 이전 데이터는 broker가 자동으로 삭제
```
> cd ~/apps/kafka_2.12-3.6.2
> bin/kafka-configs.sh --bootstrap-server localhost:9092 --topic kv_topic --add-config retention.ms=0 --alter
Completed updating config for topic kv_topic.
```

- Kafaka broker 로그 확인
  - 위에서 업데이트한 정보가 반영되고 있고,
  - segment file을 순차적으로 삭제 하고 있다.
```
[2024-07-06 09:02:16,271] INFO [LocalLog partition=kv_topic-1, dir=/tmp/kafka-logs] Rolled new log segment at offset 14 in 4 ms. (kafka.log.LocalLog)
[2024-07-06 09:02:16,273] INFO [UnifiedLog partition=kv_topic-1, dir=/tmp/kafka-logs] Deleting segment LogSegment(baseOffset=0, size=438, lastModifiedTime=1719921124712, largestRecordTimestamp=Some(1719921123711)) due to log retention time 0ms breach based on the largest record timestamp in the segment (kafka.log.UnifiedLog)
[2024-07-06 09:02:16,276] INFO [UnifiedLog partition=kv_topic-1, dir=/tmp/kafka-logs] Incremented log start offset to 14 due to segment deletion (kafka.log.UnifiedLog)
[2024-07-06 09:02:16,281] INFO [LocalLog partition=kv_topic-0, dir=/tmp/kafka-logs] Rolled new log segment at offset 12 in 1 ms. (kafka.log.LocalLog)
[2024-07-06 09:02:16,281] INFO [UnifiedLog partition=kv_topic-0, dir=/tmp/kafka-logs] Deleting segment LogSegment(baseOffset=0, size=405, lastModifiedTime=1719923025594, largestRecordTimestamp=Some(1719923025015)) due to log retention time 0ms breach based on the largest record timestamp in the segment (kafka.log.UnifiedLog)
[2024-07-06 09:02:16,282] INFO [UnifiedLog partition=kv_topic-0, dir=/tmp/kafka-logs] Incremented log start offset to 12 due to segment deletion (kafka.log.UnifiedLog)

```


- 약 5분 정도 후에 다시 segment 파일을 조회하면 기존 segment 파일(00000.log)은 삭제되고
- partition 0는 00000000000000000012.log 파일이 새롭게 생성되고,
  - File size가 0으로 모든 데이터가 삭제되었음을 확인 
```
> /tmp/kafka-logs/kv_topic-0
-rw-r--r--.  1 freepsw18 freepsw18    0 Jul  6 09:02 00000000000000000012.log
-rw-r--r--.  1 freepsw18 freepsw18  148 Jul  2 12:44 00000000000000000012.snapshot
-rw-r--r--.  1 freepsw18 freepsw18    9 Jul  6 09:02 leader-epoch-checkpoint
-rw-r--r--.  1 freepsw18 freepsw18   43 Jul  2 11:31 partition.metadata
```

- partition 1는 00000000000000000014.log 파일이 새롭게 생성되고,
  - File size가 0으로 모든 데이터가 삭제되었음을 확인 
```
> ls /tmp/kafka-logs/kv_topic-1
-rw-r--r--.  1 freepsw18 freepsw18    0 Jul  6 09:02 00000000000000000014.log
-rw-r--r--.  1 freepsw18 freepsw18  148 Jul  2 12:44 00000000000000000014.snapshot
-rw-r--r--.  1 freepsw18 freepsw18    9 Jul  6 09:02 leader-epoch-checkpoint
-rw-r--r--.  1 freepsw18 freepsw18   43 Jul  2 11:31 partition.metadata
```

- 변경했던 옵션을 삭제
```
> bin/kafka-configs.sh --bootstrap-server localhost:9092 --topic kv_topic --delete-config retention.ms --alter
Completed updating config for topic kv_topic.

## Config에 retention.ms 옵션이 삭제됨
> bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic kv_topic --describe
Topic: kv_topic	TopicId: JuKdf41ASVKbZXEKru3iLA	PartitionCount: 2	ReplicationFactor: 1	Configs: segment.bytes=1073741824
	Topic: kv_topic	Partition: 0	Leader: 0	Replicas: 0	Isr: 0
	Topic: kv_topic	Partition: 1	Leader: 0	Replicas: 0	Isr: 0
```

## Log Compaction Examples 

```
> bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic log_compact_topic \
  --config "cleanup.policy=compact" \
  --config "delete.retention.ms=100"  \
  --config "segment.ms=100" \
  --config "min.cleanable.dirty.ratio=0.01"

> bin/kafka-topics.sh --list --bootstrap-server localhost:9092
log_compact_topic

> bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic log_compact_topic --describe
Topic: log_compact_topic	TopicId: 2jkGM9unTc6TiBz5aV74_g	PartitionCount: 1	ReplicationFactor: 1	Configs: cleanup.policy=compact,min.cleanable.dirty.ratio=0.01,delete.retention.ms=100,segment.ms=100
	Topic: log_compact_topic	Partition: 0	Leader: 0	Replicas: 0	Isr: 0



## Produce key-value message 
> bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic log_compact_topic \
--property "parse.key=true" \
--property "key.separator=:" \
--property "print.key=true"
k1:msg11
k2:msg21
k3:msg31
k1:msg12
k2:msg22
k3:msg32
k1:msg13
k2:msg23


# 2분 후에 다시 한번 새로운 메세지를 보낸다.
k4:msg445


## 약 5분 정도 후에 아래 consumer를 통해서 메세지를 확인해 본다. 
## 5분은 내부적으로 broker의 log cleaner가 동작하는 시간 고려
> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic log_compact_topic \
--property print.key=true \
--property key.separator=":" \
--from-beginning
k3:msg32
k1:msg13
k2:msg23
k4:msg445
```