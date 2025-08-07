import threading
import time
import logging
from Servicos.ConexaoFirebird import ConexaoFirebird
from Modelos.ConsultasSql import ConsultasSql
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao


class ExecutorConsultasThread:
    def __init__(self, configuracao_banco, thread_id, intervalo_consultas=None, intervalo_ciclos=None):
        self.configuracao = configuracao_banco
        self.thread_id = thread_id
        self.executando = False
        self.thread = None
        self.contador_consultas = 0
        self.contador_erros = 0
        self.contador_ciclos = 0
        self.intervalo_consultas = intervalo_consultas or ConfiguracaoExecucao.INTERVALO_ENTRE_CONSULTAS
        self.intervalo_ciclos = intervalo_ciclos or ConfiguracaoExecucao.INTERVALO_ENTRE_CICLOS
        self.logger = logging.getLogger(f'SimuladorCarga.ExecutorThread.{configuracao_banco.nome_banco}.{thread_id}')

    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.contador_consultas = 0
            self.contador_erros = 0
            self.contador_ciclos = 0
            self.thread = threading.Thread(target=self._executar_loop,
                                           name=f"Executor-{self.configuracao.nome_banco}-{self.thread_id}")
            self.thread.daemon = True
            self.thread.start()
            self.logger.info(f"Thread {self.thread_id} iniciada para: {self.configuracao.nome_banco}")

    def parar_execucao(self):
        if self.executando:
            self.executando = False
            if self.thread:
                self.thread.join(timeout=10)
            self.logger.info(
                f"Thread {self.thread_id} parada para {self.configuracao.nome_banco} - Consultas: {self.contador_consultas} - Erros: {self.contador_erros} - Ciclos: {self.contador_ciclos}")

    def _executar_loop(self):
        conexao = ConexaoFirebird(self.configuracao, self.thread_id)

        if not conexao.conectar():
            self.logger.error(
                f"Thread {self.thread_id} - Falha ao conectar {self.configuracao.nome_banco} - Thread será encerrada")
            return

        consultas = ConsultasSql.obter_todas_consultas()
        self.logger.info(
            f"Thread {self.thread_id} - Iniciando loop de execução intensiva para {self.configuracao.nome_banco}")

        while self.executando:
            self.contador_ciclos += 1

            for consulta in consultas:
                if not self.executando:
                    break

                if conexao.executar_consulta(consulta):
                    self.contador_consultas += 1
                else:
                    self.contador_erros += 1

                if self.intervalo_consultas > 0:
                    time.sleep(self.intervalo_consultas)

            if self.contador_consultas % 500 == 0 and self.contador_consultas > 0:
                self.logger.info(
                    f"Thread {self.thread_id} - Progresso {self.configuracao.nome_banco}: {self.contador_consultas} consultas, {self.contador_ciclos} ciclos")

            if self.intervalo_ciclos > 0:
                time.sleep(self.intervalo_ciclos)

        conexao.desconectar()
        self.logger.info(f"Thread {self.thread_id} - Loop finalizado para {self.configuracao.nome_banco}")