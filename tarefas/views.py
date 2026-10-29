
from rest_framework import filters, generics
from django.db.models import Count, Q
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Tarefa
from .serializers import TarefaSerializer
from .pagination import PaginacaoTarefas


class TarefaListCreateView(generics.ListCreateAPIView):
    serializer_class = TarefaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['data_limite']
    pagination_class = PaginacaoTarefas

    def get_queryset(self):
        # Isolamento: só as tarefas de quem fez a requisição.
        queryset = Tarefa.objects.filter(usuario=self.request.user)

        # Filtro opcional ?concluida=true|false
        concluida = self.request.query_params.get('concluida')
        if concluida is not None:
            queryset = queryset.filter(concluida=(concluida.lower() == 'true'))

        # Filtro opcional ?prioridade=alta|media|baixa
        prioridade = self.request.query_params.get('prioridade')
        if prioridade:
            queryset = queryset.filter(prioridade=prioridade.upper())

        return queryset

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class TarefaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TarefaSerializer

    def get_queryset(self):
        # Tarefa de outro usuário não está no queryset: a API responde 404.
        return Tarefa.objects.filter(usuario=self.request.user)

class TarefaEstatisticasView(APIView):
    def get(self, request):
        tarefas = Tarefa.objects.filter(usuario=request.user)

        estatisticas = tarefas.aggregate(
            total=Count('id'),
            concluidas=Count('id', filter=Q(concluida=True)),
            pendentes=Count('id', filter=Q(concluida=False)),
        )

        return Response(estatisticas)
