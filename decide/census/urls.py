from django.urls import path, include
from . import views

urlpatterns = [
    path('export/', views.export_csv, name='export'),
    path('', views.CensusList.as_view(), name='census_list'),
    path('create/', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path("import/", views.CensusImportView.as_view(), name="import"),
]
