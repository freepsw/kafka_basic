from confluent_kafka.admin import AdminClient, NewTopic

a = AdminClient({'bootstrap.servers': 'localhost'})

# 새롭게 생성할 topic에 대한 상세 설정 및 생성할 topic 명을 입력한다.
new_topics = [NewTopic(topic, num_partitions=3, replication_factor=1) for topic in ["my_topic_new1", "my_topic_new2"]]


# Call create_topics to asynchronously create topics. A dict of <topic,future> is returned.
fs = a.create_topics(new_topics)

# Wait for each operation to finish.
for topic, f in fs.items():
    try:
        f.result()  # The result itself is None
        print("Topic {} created".format(topic))
    except Exception as e:
        print("Failed to create topic {}: {}".format(topic, e))