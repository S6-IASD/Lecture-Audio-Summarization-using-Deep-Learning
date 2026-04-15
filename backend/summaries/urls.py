from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.SummaryCreateView.as_view(), name='summary-create'),
    path('', views.SummaryListView.as_view(), name='summary-list'),
    path('<int:pk>/', views.SummaryDetailView.as_view(), name='summary-detail'),
    path('<int:summary_id>/download/<str:file_type>/',
         views.SummaryDownloadView.as_view(), name='summary-download'),
    path('health/', views.HealthView.as_view(), name='health'),
]
