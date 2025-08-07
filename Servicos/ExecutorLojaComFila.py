import threading
import time
import logging
from Servicos.ExecutorConsultas import ExecutorConsultas
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao


class ExecutorLojaComFila:
    def __init__(self, ip_porta, gerenciador_fila, modo_alta_carga=False):
        self.ip_porta = ip_porta
        self.gerenciador_fila = gerenciador_fila
        self.modo_alta_carga = modo_alta_carga
        self.executores_ativos = {}
        self.executando = False
        self.thread_gerenciador = None
        self.config = ConfiguracaoExecucao.obter_configuracao_alta_carga() if modo_alta_carga else ConfiguracaoExecucao.obter_configuracao_normal()
        self.logger = logging.getLogger(f'SimuladorCarga.ExecutorLojaComFila.{ip_porta}')

    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.executores_ativos = {}
            self.thread_gerenciador = threading.Thread(target=self._gerenciar_fila_lojas,
                                                       name=f"GerenciadorFila-{self.ip_porta}")
            self.thread_gerenciador.daemon = True
            self.thread_gerenciador.start()
            self.logger.info(f"Gerenciador de fila iniciado para IP {self.ip_porta}")

    def parar_execucao(self):
        if self.executando:
            self.executando = False

            for nome_loja, executor in self.executores_ativos.items():
                executor.parar_execucao()
                self.gerenciador_fila.liberar_loja(self.ip_porta, nome_loja)

            if self.thread_gerenciador:
                self.thread_gerenciador.join(timeout=10)

            self.executores_ativos.clear()
            self.logger.info(f"Gerenciador de fila parado para IP {self.ip_porta}")

    def _gerenciar_fila_lojas(self):
        self.logger.info(f"Iniciando gerenciamento de fila para IP {self.ip_porta}")

        while self.executando:
            try:
                self._processar_fila()
                self._remover_executores_finalizados()
                time.sleep(self.config['intervalo_verificacao'])
            except Exception as e:
                self.logger.error(f"Erro no gerenciamento da fila para IP {self.ip_porta}: {e}")

        self.logger.info(f"Gerenciamento de fila finalizado para IP {self.ip_porta}")

    def _processar_fila(self):
        slots_disponiveis = ConfiguracaoExecucao.MAX_CONSULTAS_POR_IP - len(self.executores_ativos)

        for _ in range(slots_disponiveis):
            if not self.executando:
                break

            loja = self.gerenciador_fila.obter_proxima_loja(self.ip_porta)
            if loja:
                self._iniciar_executor_loja(loja)
            else:
                break

    def _iniciar_executor_loja(self, loja):
        if loja.nome_banco not in self.executores_ativos:
            executor = ExecutorConsultas(loja, self.modo_alta_carga)
            self.executores_ativos[loja.nome_banco] = executor
            executor.iniciar_execucao()
            self.logger.info(
                f"Executor iniciado para loja {loja.nome_banco} no IP {self.ip_porta} ({len(self.executores_ativos)}/{ConfiguracaoExecucao.MAX_CONSULTAS_POR_IP})")

    def _remover_executores_finalizados(self):
        lojas_finalizadas = []

        for nome_loja, executor in self.executores_ativos.items():
            if not executor.executando:
                lojas_finalizadas.append(nome_loja)

        for nome_loja in lojas_finalizadas:
            if nome_loja in self.executores_ativos:
                self.executores_ativos[nome_loja].parar_execucao()
                del self.executores_ativos[nome_loja]
                self.gerenciador_fila.liberar_loja(self.ip_porta, nome_loja)
                self.logger.info(f"Executor removido para loja {nome_loja} no IP {self.ip_porta}")

    def obter_estatisticas(self):
        if not self.executando:
            return None

        stats_lojas = {}
        total_consultas = 0
        total_erros = 0
        total_threads_ativas = 0
        total_threads = 0

        for nome_loja, executor in self.executores_ativos.items():
            stats = executor.obter_estatisticas()
            if stats:
                stats_lojas[nome_loja] = stats
                total_consultas += stats['total_consultas']
                total_erros += stats['total_erros']
                total_threads_ativas += stats['threads_ativas']
                total_threads += stats['threads_total']

        status_fila = self.gerenciador_fila.obter_status_filas().get(self.ip_porta, {})

        return {
            'ip_porta': self.ip_porta,
            'lojas_ativas': stats_lojas,
            'total_lojas_ativas': len(self.executores_ativos),
            'total_consultas': total_consultas,
            'total_erros': total_erros,
            'threads_ativas': total_threads_ativas,
            'threads_total': total_threads,
            'fila_aguardando': status_fila.get('fila_aguardando', 0),
            'lojas_processadas': status_fila.get('processadas', 0),
            'limite_maximo': ConfiguracaoExecucao.MAX_CONSULTAS_POR_IP
        }