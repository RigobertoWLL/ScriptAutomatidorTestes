import threading
import time
import logging
from Servicos.ConexaoFirebird import ConexaoFirebird
from Modelos.ConsultasSql import ConsultasSql


class ExecutorConsultaRotativa:
    def __init__(self, ip_porta, gerenciador_rotacao, nome_consulta, sql_consulta, thread_id, intervalo_consultas=None):
        self.ip_porta = ip_porta
        self.gerenciador_rotacao = gerenciador_rotacao
        self.nome_consulta = nome_consulta
        self.sql_consulta = sql_consulta
        self.thread_id = thread_id
        self.executando = False
        self.thread = None
        self.contador_consultas = 0
        self.contador_erros = 0
        self.contador_rotacoes = 0
        self.loja_atual = None
        self.conexao_atual = None
        self.intervalo_consultas = intervalo_consultas or 0.02
        self.logger = logging.getLogger(f'SimuladorCarga.ExecutorRotativo.{ip_porta}.{nome_consulta}.Thread{thread_id}')
        self.tempo_ultima_rotacao = time.time()

    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.contador_consultas = 0
            self.contador_erros = 0
            self.contador_rotacoes = 0
            self.thread = threading.Thread(
                target=self._executar_loop_rotativo,
                name=f"ExecutorRotativo-{self.ip_porta}-{self.nome_consulta}-{self.thread_id}"
            )
            self.thread.daemon = True
            self.thread.start()
            self.logger.info(
                f"Thread rotativa {self.thread_id} iniciada para {self.nome_consulta} no IP {self.ip_porta}")

    def parar_execucao(self):
        if self.executando:
            self.executando = False
            if self.thread:
                self.thread.join(timeout=10)

            if self.loja_atual:
                self.gerenciador_rotacao.liberar_loja(self.ip_porta, self.loja_atual)
                self.loja_atual = None

            if self.conexao_atual:
                self.conexao_atual.desconectar()
                self.conexao_atual = None

            self.logger.info(f"Thread rotativa {self.thread_id} parada - {self.nome_consulta} no IP {self.ip_porta}")
            self.logger.info(
                f"  Consultas: {self.contador_consultas} | Erros: {self.contador_erros} | Rotações: {self.contador_rotacoes}")

    def _executar_loop_rotativo(self):
        self.logger.info(
            f"Thread {self.thread_id} - Iniciando loop rotativo para {self.nome_consulta} no IP {self.ip_porta}")

        while self.executando:
            if not self.loja_atual or self._deve_rotacionar():
                if not self._rotacionar_loja():
                    time.sleep(1)
                    continue

            if self.conexao_atual and self.conexao_atual.executar_consulta(self.sql_consulta):
                self.contador_consultas += 1
            else:
                self.contador_erros += 1

            if self.contador_consultas % 100 == 0 and self.contador_consultas > 0:
                self.logger.info(
                    f"Thread {self.thread_id} - {self.nome_consulta}: {self.contador_consultas} consultas na loja {self.loja_atual.nome_banco if self.loja_atual else 'N/A'}")

            if self.intervalo_consultas > 0:
                time.sleep(self.intervalo_consultas)

        self.logger.info(
            f"Thread {self.thread_id} - Loop rotativo finalizado para {self.nome_consulta} no IP {self.ip_porta}")

    def _deve_rotacionar(self):
        tempo_atual = time.time()
        return (tempo_atual - self.tempo_ultima_rotacao) >= 300

    def _rotacionar_loja(self):
        if self.loja_atual:
            self.gerenciador_rotacao.liberar_loja(self.ip_porta, self.loja_atual)
            if self.conexao_atual:
                self.conexao_atual.desconectar()

        nova_loja = self.gerenciador_rotacao.obter_proxima_loja(self.ip_porta)
        if not nova_loja:
            self.logger.warning(f"Thread {self.thread_id} - Nenhuma loja disponível para IP {self.ip_porta}")
            return False

        self.loja_atual = nova_loja
        self.conexao_atual = ConexaoFirebird(nova_loja, f"{self.nome_consulta}-T{self.thread_id}")

        if self.conexao_atual.conectar():
            self.contador_rotacoes += 1
            self.tempo_ultima_rotacao = time.time()
            self.logger.info(
                f"Thread {self.thread_id} - Rotação {self.contador_rotacoes}: Conectado à loja {nova_loja.nome_banco}")
            return True
        else:
            self.logger.error(f"Thread {self.thread_id} - Falha ao conectar à loja {nova_loja.nome_banco}")
            self.gerenciador_rotacao.liberar_loja(self.ip_porta, nova_loja)
            self.loja_atual = None
            self.conexao_atual = None
            return False

    def obter_estatisticas(self):
        return {
            'consultas_executadas': self.contador_consultas,
            'erros': self.contador_erros,
            'rotacoes': self.contador_rotacoes,
            'loja_atual': self.loja_atual.nome_banco if self.loja_atual else None,
            'ativo': self.executando
        }