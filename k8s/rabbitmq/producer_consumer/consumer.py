import pika
import json
import requests
import sys
from pathlib import Path
from vault_helper import vault_helper


def weather_callback(api_key, **params):
    resp = requests.get(
        url="http://api.weatherapi.com/v1/current.json",
        params={
            "key": api_key,
            **params
        }
    )

    return resp.json()

def food_callback(api_key, **params):
    resp = requests.get(
        url="https://api.spoonacular.com/recipes/complexSearch",
        params={
            "apiKey": api_key,
            **params
        }
    )

    return resp.json()

CALLBACK_DICT = {
    'weather': weather_callback,
    'food': food_callback
}

def message_callback(ch, method, properties, body):
    json_data = json.loads(body)
    alias = json_data.pop('alias')
    api_key = vault_helper.get_api_key(alias)
    api_callback = CALLBACK_DICT.get(alias, weather_callback)
    api_data = api_callback(api_key, **json_data)
    file_path = Path("data") / f"{alias}.json"
    with file_path.open('w') as f:
        json.dump(obj=api_data, fp=f, ensure_ascii=False, indent=2)
    ch.basic_ack(delivery_tag = method.delivery_tag)

def main():
    api_alias = sys.argv[1:][0]

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

    queue_name = f"{api_alias}-queue"
    channel.queue_declare(
        queue=queue_name,
        durable=True
    )
    channel.queue_bind(
        exchange='api',
        queue=queue_name,
        routing_key=api_alias
    )

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=message_callback
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()