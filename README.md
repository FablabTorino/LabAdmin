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
