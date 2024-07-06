import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.apache.kafka.common.serialization.StringSerializer;
import java.util.Properties;

public class Producer_Callback_Sync {
    public static void main(String[] args) {
        Properties configs = new Properties();
        configs.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        configs.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        configs.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        KafkaProducer<String, String> producer = new KafkaProducer<>(configs);

        String msg = "Sync producer message";
        ProducerRecord<String, String> record = new ProducerRecord<>("my_topic", msg);

        try {
            // 메세지 전달결과를 기다렸다가 결과를 출력하는 Sync 방식
            RecordMetadata metadata = producer.send(record).get();
            System.out.println("Record written to offset " +
                    metadata.offset() + " timestamp " +
                    metadata.timestamp());
        } catch (Exception e) {
            System.out.println(e.getMessage());
        } finally {
            producer.flush();
            producer.close();
        }
    }
}
