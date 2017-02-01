# LabAdmin

Manage user rights to access the lab and the machines

## Quickstart

Install the labAdmin:

```
python setup.py install
```

Add it to the installed apps:

```
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'oauth2_provider',
    'labAdmin',
]
```

Add labAdmin urls to your project urls:

```
urlpatterns = [
    # ...
    include(r'^labAdmin/', include('labAdmin.urls')),
]
```

Profit!

### Settings

The optional MQTT integration has the following settings:

```
LABADMIN_MQTT_CONFIG = {
    'HOSTNAME': 'localhost',
    'PORT': 1883,
    'AUTH': None,
    'TLS': None,
    'PROTOCOL': MQTTv311,
    'TRANSPORT': 'tcp',
}

# Should we publish on MQTT each entrance
LABADMIN_NOTIFY_MQTT_ENTRANCE = False

# The MQTT topic where to publish
LABADMIN_MQTT_ENTRANCE_TOPIC = 'labadmin/entrance'
```

See [Paho MQTT documentation](https://github.com/eclipse/paho.mqtt.python#single) for `LABADMIN_MQTT_CONFIG` values.
