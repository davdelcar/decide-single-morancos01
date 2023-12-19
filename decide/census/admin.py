from django.contrib import admin
from parler.admin import TranslatableAdmin


from .models import Census


class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )


admin.site.register(Census, CensusAdmin)

class CensusAdmin(TranslatableAdmin):
    pass
