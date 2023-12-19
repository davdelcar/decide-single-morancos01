from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Auth, Key


admin.site.register(Auth)
admin.site.register(Key)

class Auth(TranslatableAdmin):
    pass