
from rest_framework import serializers

from .models import Tarefa


class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'
        # O dono vem sempre do token (request.user), nunca do corpo da requisição.
        extra_kwargs = {'usuario': {'read_only': True}}

    def validate_tarefa_pai(self, tarefa_pai):
        if tarefa_pai is None:
            return tarefa_pai

        request = self.context.get('request')

        if request is None or tarefa_pai.usuario_id != request.user.id:
            raise serializers.ValidationError(
                'A tarefa principal deve pertencer ao usuário autenticado.'
            )

        if self.instance and tarefa_pai.pk == self.instance.pk:
            raise serializers.ValidationError(
                'Uma tarefa não pode ser sua própria tarefa principal.'
            )

        if self.instance:
            ancestral = tarefa_pai
            visitados = set()

            while ancestral is not None and ancestral.pk not in visitados:
                if ancestral.pk == self.instance.pk:
                    raise serializers.ValidationError(
                        'Não é permitido criar uma referência circular entre tarefas.'
                    )

                visitados.add(ancestral.pk)
                ancestral = ancestral.tarefa_pai

        return tarefa_pai