from django.urls import path
from . import views  # Импортируем views из текущего приложения
from .views import predictions_view

urlpatterns = [
    path('', views.home, name='home'),
    # path('graph/', views.graph_view, name='graph'),  # Удалил дубликат
    path("graph/", views.graph_view, name="exchange_rate_graph"),  #  Путь для графика
    path('predikcia/', predictions_view, name='predikcia'),

]

