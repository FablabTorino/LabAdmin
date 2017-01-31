from django.conf import settings

from paho.mqtt.client import MQTTv311


BASE_MQTT_CONFIG = {
    'HOSTNAME': 'localhost',
    'PORT': 1883,
    'AUTH': None,
    'TLS': None,
    'PROTOCOL': MQTTv311,
    'TRANSPORT': 'tcp',
}
MQTT_CONFIG = {}


USER_MQTT_CONFIG = getattr(settings, 'LABADMIN_MQTT_CONFIG', {})
MQTT_ENTRANCE_NOTIFICATION = getattr(settings, 'LABADMIN_NOTIFY_MQTT_ENTRANCE', False)
MQTT_ENTRANCE_TOPIC = getattr(settings, 'LABADMIN_MQTT_ENTRANCE_TOPIC', 'labadmin/entrance')

MQTT_CONFIG = BASE_MQTT_CONFIG.copy()
MQTT_CONFIG.update(USER_MQTT_CONFIG)
