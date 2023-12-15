from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered


all_models = apps.get_models()

for model in all_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
