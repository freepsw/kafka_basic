# Real-time data pipeline using apache kafka 

## [STEP 0] Prerequisite
### Java 설치 및 JAVA_HOME 설정
- kafka_basic/README.md에 명시된 가이드에 따라서
- java 설치 및 JAVA_HOME 설정


## [STEP 1] Install ELK Stack (Elasticsearch + Logstash + Kibana)
- Elasticsearch를 비즈니에서 활용시 주의사항 (OSS버전 vs Default)
    - OSS는 elasticsearch를 이용하여 별도의 제품/솔루션으로 판매할 목적인 경우에 활용
    - Basic은 기업 내부에서는 무료로 사용가능 
        - 즉 OSS 버전을 기반으로 elastic사에서 추가기능(ML, SIEM등)을 무료로 제공하는 것
    - 정리하면, OSS는 누구나 활용 가능한 오픈소스
        - 이를 이용해 별도의 제품을 만들어도 가능함.
        - elastic사도 OSS를 이용해서 basic 제품을 개발하고, 이를 무료로 제공함. 
        - 하지만, basic 버전의 소유권은 elastic사에 귀속됨(무로지만, 이를 이용해 비즈니스/사업을 하면 안됨)
    - http://kimjmin.net/2020/06/2020-06-elastic-devrel/
- Elastic stack 설치
  - - https://www.elastic.co/guide/en/elastic-stack/current/installing-elastic-stack.html 참고

### 1) Install an Elasticsearch 
- config 설정 
    - 외부 접속 허용(network.host) : server와 client가 다른 ip가 있을 경우, 외부에서 접속할 수 있도록 설정을 추가해야함.
```
> cd ~/apps
> wget wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.14.1-linux-x86_64.tar.gz
> tar -xzf elasticsearch-8.14.1-linux-x86_64.tar.gz
> cd ~/apps/elasticsearch-8.14.1
> vi config/elasticsearch.yml
# bind ip to connect from client  (lan이 여러개 있을 경우 외부에서 접속할 ip를 지정할 수 있음.)
# bind all ip server have "0.0.0.0"
network.host: 0.0.0.0   #(":" 다음에 스페이스를 추가해야 함.)

# kibana에서 보안정책 없이 접근 가능하도록 "false"로 변경
xpack.security.enabled: false

```

#### 오류 해결 : virtual memory error
- 시스템의 nmap count를 증가기켜야 한다.
- 에러 : [2]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
- https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html
```
# 0) 현재 설정 값 확인
> cat /proc/sys/vm/max_map_count
65530

# 아래 3가지 방법 중 1가지를 선택하여 적용 가능
# 1-1) 현재 서버상태에서만 적용하는 방식
> sudo sysctl -w vm.max_map_count=262144

# 1-2) 영구적으로 적용 (서버 재부팅시 자동 적용)
> sudo vi /etc/sysctl.conf

# 아래 내용 추가
vm.max_map_count = 262144

# 1-3) 또는 아래 명령어 실행 
> echo vm.max_map_count=262144 | sudo tee -a /etc/sysctl.conf


# 3) 시스템에 적용하여 변경된 값을 확인
> sudo sysctl -p
vm.max_map_count = 262144
```


#### Run elasticsearch
```
> ./bin/elasticsearch
....................
[2024-07-02T12:41:39,687][INFO ][o.e.l.ClusterStateLicenseService] [instance-20240701-162846] license [2ce86f9d-ae5b-47c0-815a-35e4ad0d9ae2] mode [basic] - valid
[2024-07-02T12:41:46,485][INFO ][o.e.x.s.InitialNodeSecurityAutoConfiguration] [instance-20240701-162846] HTTPS has been configured with automatically generated certificates, and the CA's hex-encoded SHA-256 fingerprint is [6500b8c8df356e4965da2f1692d8569a4e3058f04522f945fd699b76d5c81c64]
[2024-07-02T12:41:46,489][INFO ][o.e.x.s.s.SecurityIndexManager] [instance-20240701-162846] security index does not exist, creating [.security-7] with alias [.security]
[2024-07-02T12:41:46,506][INFO ][o.e.x.s.e.InternalEnrollmentTokenGenerator] [instance-20240701-162846] Will not generate node enrollment token because node is only bound on localhost for transport and cannot connect to nodes from other hosts
[2024-07-02T12:41:46,559][INFO ][o.e.c.m.MetadataCreateIndexService] [instance-20240701-162846] [.security-7] creating index, cause [api], templates [], shards [1]/[0]
[2024-07-02T12:41:46,617][INFO ][o.e.x.s.s.SecurityIndexManager] [instance-20240701-162846] security index does not exist, creating [.security-7] with alias [.security]
[2024-07-02T12:41:46,839][INFO ][o.e.c.r.a.AllocationService] [instance-20240701-162846] current.health="GREEN" message="Cluster health status changed from [YELLOW] to [GREEN] (reason: [shards started [[.security-7][0]]])." previous.health="YELLOW" reason="shards started [[.security-7][0]]"


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Elasticsearch security features have been automatically configured!
✅ Authentication is enabled and cluster connections are encrypted.

ℹ️  Password for the elastic user (reset with `bin/elasticsearch-reset-password -u elastic`):
  ZG73I6D*OjUTT06oqZ4h

ℹ️  HTTP CA certificate SHA-256 fingerprint:
  6500b8c8df356e4965da2f1692d8569a4e3058f04522f945fd699b76d5c81c64

ℹ️  Configure Kibana to use this cluster:
• Run Kibana and click the configuration link in the terminal when Kibana starts.
• Copy the following enrollment token and paste it into Kibana in your browser (valid for the next 30 minutes):
  eyJ2ZXIiOiI4LjE0LjAiLCJhZHIiOlsiMTAuMTc4LjAuNDo5MjAwIl0sImZnciI6IjY1MDBiOGM4ZGYzNTZlNDk2NWRhMmYxNjkyZDg1NjlhNGUzMDU4ZjA0NTIyZjk0NWZkNjk5Yjc2ZDVjODFjNjQiLCJrZXkiOiJSc1YzYzVBQk5JX1ppY3hPSlk5RjpjdGtUUWcwc1NidWpxX2wxTU5uVlBBIn0=

ℹ️  Configure other nodes to join this cluster:
• On this node:
  ⁃ Create an enrollment token with `bin/elasticsearch-create-enrollment-token -s node`.
  ⁃ Uncomment the transport.host setting at the end of config/elasticsearch.yml.
  ⁃ Restart Elasticsearch.
• On other nodes:
  ⁃ Start Elasticsearch with `bin/elasticsearch --enrollment-token <token>`, using the enrollment token that you generated.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```

#### Check elasticsearch is running
- Console을 이용한 접근
```
> export ELASTIC_PASSWORD="ZG73I6D*OjUTT06oqZ4h"

> curl --cacert ~/apps/elasticsearch-8.14.1/config/certs/http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200 
{
  "name" : "instance-20240701-162846",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "BjsJfIIxSQySPV90paP3TQ",
  "version" : {
    "number" : "8.14.1",
    "build_flavor" : "default",
    "build_type" : "tar",
    "build_hash" : "93a57a1a76f556d8aee6a90d1a95b06187501310",
    "build_date" : "2024-06-10T23:35:17.114581191Z",
    "build_snapshot" : false,
    "lucene_version" : "9.10.0",
    "minimum_wire_compatibility_version" : "7.17.0",
    "minimum_index_compatibility_version" : "7.0.0"
  },
  "tagline" : "You Know, for Search"
}

## 아래와 같은 방법으로 접근도 가능함
> curl -k -v -u elastic https://34.64.166.195:9200
Enter host password for user 'elastic': ZG73I6D*OjUTT06oqZ4h
```

- Web Browser를 이용한 접근
  - Web brower 주소 창에서 "https://Elastic-server-ip:9200/" 입력
  - 팝업 창에서 user/password를 elastid/위에서 저장한 password 로 입력
  - web에서 elasticsearch 정보 확인



### 2) Install and run a kibana 
```
> cd ~/apps
> curl -O https://artifacts.elastic.co/downloads/kibana/kibana-8.14.1-linux-x86_64.tar.gz
> tar -xzf kibana-8.14.1-linux-x86_64.tar.gz
> cd ~/apps/kibana-8.14.1/
```

#### Kibana 설정 변경
- 외부 접속 가능하도록 설정 값 변경 
  - 외부의 어떤 IP에서도 접속 가능하도록 0.0.0.0으로 변경 (운영환경에서는 특정 ip대역만 지정하여 보안강화)
- elasticsearch 접속을 위한 user/password 설정
```
>  
# 외부에서 접근 가능하도록 설정 
server.host: "0.0.0.0"

```

#### Run kibana
```
> cd ~/apps/kibana-8.14.1/ 
> bin/kibana
.....
  log   [10:40:10.296] [info][server][Kibana][http] http server running at http://localhost:5601
  log   [10:40:12.690] [warning][plugins][reporting] Enabling the Chromium sandbox provides an additional layer of protection
```

#### Kibana 에러 시 기존 index 삭제 후 재시작
```
curl -XDELETE http://localhost:9200/.kibana
curl -XDELETE 'http://localhost:9200/.kibana*'
curl -XDELETE http://localhost:9200/.kibana_2
curl -XDELETE http://localhost:9200/.kibana_1
```


### 3) Install a logstash 
```
> cd ~/apps
> wget https://artifacts.elastic.co/downloads/logstash/logstash-8.14.1-linux-x86_64.tar.gz
> tar xvf logstash-8.14.1-linux-x86_64.tar.gz
> cd ~/apps/logstash-8.14.1
```

#### Test a logstash 
```
> bin/logstash -e 'input { stdin { } } output { stdout {} }'
# 실행까지 시간이 소요된다. (아래 메세지가 출력되면 정상 실행된 것으로 확인)
.........
[2024-07-02T15:42:37,938][INFO ][logstash.javapipeline    ][main] Pipeline started {"pipeline.id"=>"main"}
The stdin plugin is now waiting for input:
[2024-07-02T15:42:37,953][INFO ][logstash.agent           ] Pipelines running {:count=>1, :running_pipelines=>[:main], :non_running_pipelines=>[]}

mytest  <-- 메세지 입력 후 아래와 같이 출력되면 정상적으로 설치된 것
{
    "host" => {
        "hostname" => "instance-20240701-162846"
    },
    "event" => {
        "original" => "mytest"
    },
    "@version" => "1",
    "message" => "mytest",
    "@timestamp" => 2024-07-02T15:44:03.085998069Z
}
```



## [STEP 2] Configure kafka topic 

### Step 1: Create a topic (realtime)
- 실습에 사용할 topic을 생성한다. 
```
> cd ~/apps/kafka_2.12-3.6.2

> bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic realtime

# check created topic "realtime"
> bin/kafka-topics.sh --list --bootstrap-server localhost:9092
__consumer_offsets
kv_topic
mytopic
realtime
```


### Step 2: Send some messages
```
> bin/kafka-console-producer.sh --broker-list localhost:9092 --topic realtime
This is a message
This is another message
```

### Step 3: Start a consumer
```
> cd ~/apps/kafka_2.12-3.6.2
> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic realtime --from-beginning

This is a message
This is another message
```


## [STEP 3] Run the Kakfka Producer using logstash 

### download the sample file
```
> cd ~/apps
> wget https://github.com/freepsw/demo-spark-analytics/raw/master/00.stage1/tracks.csv
> touch tracks_live.csv
```
### Run logstash 
- kafka topic을 realtime로 변경
```
> vi ~/apps/producer.conf
```
- 아래 path의 경로를 다운로드 받은 파일의 경로로 변경
```yaml
input {
  file {
    path => "/home/freepsw/apps/tracks_live.csv"
  }
}

output {
  stdout {
    codec => rubydebug{ }
  }

  kafka {
    codec => plain {
      format => "%{message}"
    }
    bootstrap_servers => "localhost:9092"
    topic_id => "realtime"
  }
}

```

- run logstash 
```
> cd ~/apps/
> ~/apps/logstash-8.14.1/bin/logstash -f ~/apps/producer.conf
.....
[2024-07-02T16:06:52,012][INFO ][logstash.agent           ] Pipelines running {:count=>1, :running_pipelines=>[:main], :non_running_pipelines=>[]}
```


## [STEP 4] Generate steaming data using data-generator.py
```
> cd ~/apps
> vi data_generator.py
```
### data_generator.py
```python
#-*- coding: utf-8 -*-
import time
import random

r_fname = "tracks.csv"
w_fname = "tracks_live.csv"

rf = open(r_fname)
wf = open(w_fname, "a+")

try:
	num_lines = sum(1 for line in rf)
	print(num_lines)
	#num_lines = 10

	rf.seek(0)
	lines = 0
	while (1):
		line = rf.readline()
		wf.write(line)
		wf.flush()

		# sleep for weighted time period
		stime = random.choice([1, 1, 1, 0.5, 0.5, 0.8, 0.3, 2, 0.1, 3])
		print(stime)
		time.sleep(stime)
		lines += 1

		# exit if read all lines
		if(lines == num_lines):
			break
		# if(lines == num_lines):
		# 	rf.seek(0)
finally:
	rf.close()
	wf.close()
	print("close file")
```

### run generator 
```
> cd ~/apps
> python data_generator.py
```

### Check kafka message
- logstash에서 kafka로 정상적으로 메세지가 전송되고 있는지 모니터링
- 아래의 kafka-console-consumer 명령어를 통해 전송되는 메세지를 확인
```
> cd ~/apps/kafka_2.12-3.6.2
> bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic realtime
# logstash에서 정상적으로 메세지를 보내면, 아래와 같은 메세지가 출력될 것임.
0,48,453,"2014-10-23 03:26:20",0,"72132"
1,1081,19,"2014-10-15 18:32:14",1,"17307"
2,532,36,"2014-12-10 15:33:16",1,"66216
```


## [STEP 5] Run the Kakfka Consumer using logstash
```
> cd ~/apps
> vi ~/apps/consumer.conf
```
```yaml
input {
  kafka{
    topics => ["realtime"]
    bootstrap_servers => "localhost:9092"
  }
}

filter {
  csv {
    columns => ["event_id","customer_id","track_id","datetime","ismobile","listening_zip_code"]
    separator => ","
  }

  date {
    match => [ "datetime", "YYYY-MM-dd HH:mm:ss"]
    target => "datetime"
  }

  mutate {
    convert => { "ismobile" => "integer" }
  }
}

output {
  stdout { codec => rubydebug }

  elasticsearch {
    hosts => "http://localhost:9200"
    index => "ba_realtime"
  }
} 
```

### run logstash consumer 
```
> cd ~/apps
> ~/apps/logstash-8.14.1/bin/logstash --path.data ~/apps/consumer-data -f ~/apps/consumer.conf
```

## [STEP 6] Kibana로 실시간 유입 데이터 확인
### Kibana Web Browser에서 접속하여 데이터 확인
- http://vm-instance-ip:5601 

