import psycopg2
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()
# PostgreSQL Connection Parameters
pg_connection_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
}

# MQTT Connection Parameters
mqtt_broker_address = os.getenv('MQTT_BROKER')
mqtt_topic = os.getenv('MQTT_TOPIC')

def on_message(client, userdata, message):
    # Handle MQTT message reception here
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

def main():
    # Connect to PostgreSQL
    conn = psycopg2.connect(**pg_connection_params)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    # Connect to MQTT Broker
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.connect(mqtt_broker_address)
    mqtt_client.subscribe(mqtt_topic)
    mqtt_client.loop_start()

    # Listen for PostgreSQL notifications
    with conn.cursor() as cursor:
        cursor.execute("LISTEN transaction_created;")
        while True:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop()
                print(f"Received PostgreSQL notification: {notify.payload}")
                # Publish MQTT message when a transaction is created
                mqtt_client.publish(mqtt_topic, f"Transaction Created: {notify.payload}")

if __name__ == "__main__":
    main()
