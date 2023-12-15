from django.contrib import admin
from parler.admin import TranslatableAdmin


from .models import Mixnet


admin.site.register(Mixnet)

class Mixnet(TranslatableAdmin):
    pass
