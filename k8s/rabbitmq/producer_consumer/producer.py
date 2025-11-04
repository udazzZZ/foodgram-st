import json
import pika
from vault_helper import vault_helper

data_food = {
    'alias': 'food',
    'q': 'Pasta'
}

data_weather = {
    'alias': 'weather',
    'q': 'Paris'
}

def main():
    data = data_food

    json_data = json.dumps(data)

    vault_credentials = vault_helper.get_rabbitmq_credentials()

    credentials = pika.PlainCredentials(
        **vault_credentials
    )
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='rabbitmq.foodgram.localhost.ru',
            credentials=credentials
        )
    )

    channel = connection.channel()

    channel.exchange_declare(
        exchange='api',
        exchange_type='direct',
        durable=True
    )

    channel.basic_publish(
        exchange='api',
        routing_key=data.get('alias', ''),
        body=json_data,
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        )
    )

    connection.close()


if __name__ == "__main__":
    main()