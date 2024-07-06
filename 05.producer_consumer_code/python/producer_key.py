from confluent_kafka import Producer
from random import choice

p = Producer({'bootstrap.servers': 'localhost'})

# Call back function (어떤 partition에 할당 되었는지 확인)
def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition(), msg.key()))

# Producer가 데이터를 전송한 후 callback 함수가 호출되기까지 대기하는 시간
user_ids = ['eabara', 'jsmith', 'sgarcia', 'jbernard', 'htanaka', 'awalther']
products = ['book', 'alarm clock', 't-shirts', 'gift card', 'batteries']

for _ in range(10):
    p.poll(0)
    # Key 값 설정
    user_id = choice(user_ids)
    # Value 값 설정
    product = choice(products)
    p.produce('my_topic', product, user_id, callback=delivery_report)
    # topic (str)
    # value (str|bytes) – Message payload
    # key (str|bytes) – Message key
    # partition (int) – Partition to produce to, else uses the configured built-in partitioner.
    # on_delivery(err,msg) (func) – Delivery report callback to call (from poll() or flush()) on successful or failed delivery
    # timestamp (int) – Message timestamp (CreateTime) in milliseconds since epoch UTC (requires librdkafka >= v0.9.4, api.version.request=true, and broker >= 0.10.0.0). Default value is current time.
    # headers (dict|list) – Message headers to set on the message. The header key must be a string while the value must be binary, unicode or None. Accepts a list of (key,value) or a dict. (Requires librdkafka >= v0.11.4 and broker version >= 0.11.0.0)
    # https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#producer


p.flush()