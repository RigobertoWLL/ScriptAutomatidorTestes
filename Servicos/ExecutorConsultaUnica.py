import threading
import time
import logging
from Servicos.ConexaoFirebird import ConexaoFirebird


class ExecutorConsultaUnica:
    def __init__(self, configuracao_banco, nome_consulta, sql_consulta, thread_id, intervalo_consultas=None):
        self.configuracao = configuracao_banco
        self.nome_consulta = nome_consulta
        self.sql_consulta = sql_consulta
        self.thread_id = thread_id
        self.executando = False
        self.thread = None
        self.contador_consultas = 0
        self.contador_erros = 0
        self.contador_ciclos = 0
        self.intervalo_consultas = intervalo_consultas or 0.01
        self.logger = logging.getLogger(
            f'SimuladorCarga.{configuracao_banco.nome_banco}.{nome_consulta}.Thread{thread_id}')

    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.contador_consultas = 0
            self.contador_erros = 0
            self.contador_ciclos = 0
            self.thread = threading.Thread(
                target=self._executar_loop,
                name=f"Executor-{self.configuracao.nome_banco}-{self.nome_consulta}-{self.thread_id}"
            )
            self.thread.daemon = True
            self.thread.start()
            self.logger.info(
                f"Thread {self.thread_id} iniciada para consulta {self.nome_consulta} em {self.configuracao.nome_banco}")

    def parar_execucao(self):
        if self.executando:
            self.executando = False
            if self.thread:
                self.thread.join(timeout=10)
            self.logger.info(
                f"Thread {self.thread_id} parada - {self.nome_consulta} em {self.configuracao.nome_banco} - Consultas: {self.contador_consultas} - Erros: {self.contador_erros}")

    def _executar_loop(self):
        conexao = ConexaoFirebird(self.configuracao, f"{self.nome_consulta}-{self.thread_id}")

        if not conexao.conectar():
            self.logger.error(
                f"Thread {self.thread_id} - Falha ao conectar para {self.nome_consulta} em {self.configuracao.nome_banco}")
            return

        self.logger.info(
            f"Thread {self.thread_id} - Iniciando execução contínua de {self.nome_consulta} em {self.configuracao.nome_banco}")

        while self.executando:
            self.contador_ciclos += 1

            if conexao.executar_consulta(self.sql_consulta):
                self.contador_consultas += 1
            else:
                self.contador_erros += 1

            if self.contador_consultas % 200 == 0 and self.contador_consultas > 0:
                self.logger.info(
                    f"Thread {self.thread_id} - {self.nome_consulta}: {self.contador_consultas} consultas executadas")

            if self.intervalo_consultas > 0:
                time.sleep(self.intervalo_consultas)

        conexao.desconectar()
        self.logger.info(
            f"Thread {self.thread_id} - Loop finalizado para {self.nome_consulta} em {self.configuracao.nome_banco}")

    def obter_estatisticas(self):
        return {
            'consultas_executadas': self.contador_consultas,
            'erros': self.contador_erros,
            'ciclos_completados': self.contador_ciclos,
            'ativo': self.executando
        }