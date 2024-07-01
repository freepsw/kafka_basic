from confluent_kafka import Producer

p = Producer({'bootstrap.servers': 'localhost'})

# Call back function (어떤 partition에 할당 되었는지 확인)
def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

# Producer가 데이터를 전송한 후 callback 함수가 호출되기까지 대기하는 시간
p.poll(0)
p.produce('my_topic', "test-msg".encode('utf-8'), callback=delivery_report)

p.flush()