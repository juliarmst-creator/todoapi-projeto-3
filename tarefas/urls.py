
from django.urls import path

from . import views

urlpatterns = [
    path('tarefas/', views.TarefaListCreateView.as_view(), name='tarefa-lista'),
    path('tarefas/estatisticas/', views.TarefaEstatisticasView.as_view(), name='tarefa-estatisticas'),
    path('tarefas/<int:pk>/', views.TarefaDetailView.as_view(), name='tarefa-detalhe'),
]
