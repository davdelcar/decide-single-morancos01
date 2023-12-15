from django.contrib import admin
from parler.admin import TranslatableAdmin


from .models import Vote


admin.site.register(Vote)

class Vote(TranslatableAdmin):
    pass
