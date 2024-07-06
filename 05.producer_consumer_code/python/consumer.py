from confluent_kafka import Consumer

c = Consumer({
    'bootstrap.servers': 'localhost',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})

# Subscribe to topics
c.subscribe(['my_topic'])

# Read messages from Kafka, print to stdout
# timeout : 메세지가 없는 경우 대기하는 최대 시간(second), -1인 경우 무한 대기
while True:
    msg = c.poll(timeout=1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))

c.close()