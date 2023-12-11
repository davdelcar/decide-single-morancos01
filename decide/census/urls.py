from django.urls import path, include
from . import views

urlpatterns = [
    path('export/', views.export_csv),
    path('import/', views.import_csv),
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
]
