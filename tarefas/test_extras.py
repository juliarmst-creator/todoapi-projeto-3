from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from .models import Tarefa


class DesafiosExtrasTest(APITestCase):
    def setUp(self):
        self.ana = User.objects.create_user(
            username='ana_extra', password='senha123'
        )
        self.beto = User.objects.create_user(
            username='beto_extra', password='senha123'
        )

        self.token_ana = Token.objects.create(user=self.ana)
        self.token_beto = Token.objects.create(user=self.beto)

        self.cliente_ana = APIClient()
        self.cliente_ana.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token_ana.key}'
        )

        self.cliente_beto = APIClient()
        self.cliente_beto.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token_beto.key}'
        )

        self.tarefas = []
        for dia in range(1, 7):
            tarefa = Tarefa.objects.create(
                titulo=f'Tarefa {dia}',
                usuario=self.ana,
                data_limite=date(2026, 11, dia),
                concluida=(dia % 2 == 0),
            )
            self.tarefas.append(tarefa)

        self.tarefa_beto = Tarefa.objects.create(
            titulo='Tarefa particular do Beto',
            usuario=self.beto,
        )

    def test_paginacao(self):
        url = reverse('tarefa-lista') + '?page=1'
        resposta = self.cliente_ana.get(url)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data['count'], 6)
        self.assertEqual(len(resposta.data['results']), 5)

    def test_ordenacao(self):
        url = reverse('tarefa-lista') + '?ordering=data_limite'
        resposta = self.cliente_ana.get(url)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.data[0]['titulo'],
            'Tarefa 1'
        )

    def test_subtarefa_mesmo_usuario(self):
        url = reverse('tarefa-lista')

        resposta = self.cliente_ana.post(
            url,
            {
                'titulo': 'Subtarefa da Ana',
                'tarefa_pai': self.tarefas[0].id,
            },
        )

        self.assertEqual(resposta.status_code, 201)

        subtarefa = Tarefa.objects.get(
            titulo='Subtarefa da Ana'
        )
        self.assertEqual(
            subtarefa.tarefa_pai_id,
            self.tarefas[0].id
        )

    def test_bloqueia_tarefa_pai_de_outro_usuario(self):
        url = reverse('tarefa-lista')

        resposta = self.cliente_ana.post(
            url,
            {
                'titulo': 'Subtarefa indevida',
                'tarefa_pai': self.tarefa_beto.id,
            },
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertFalse(
            Tarefa.objects.filter(
                titulo='Subtarefa indevida'
            ).exists()
        )

    def test_estatisticas_por_usuario(self):
        url = reverse('tarefa-estatisticas')

        resposta = self.cliente_ana.get(url)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data['total'], 6)
        self.assertEqual(resposta.data['concluidas'], 3)
        self.assertEqual(resposta.data['pendentes'], 3)

        resposta_beto = self.cliente_beto.get(url)
        self.assertEqual(resposta_beto.data['total'], 1)

    def test_estatisticas_exigem_token(self):
        url = reverse('tarefa-estatisticas')
        resposta = self.client.get(url)

        self.assertEqual(resposta.status_code, 401)
