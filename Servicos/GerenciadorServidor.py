import threading
import logging
from Servicos.ExecutorConsultas import ExecutorConsultas
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao


class GerenciadorServidor:
    def __init__(self, servidor_ip_porta, bancos_servidor, modo_alta_carga=False):
        self.servidor_ip_porta = servidor_ip_porta
        self.bancos_servidor = bancos_servidor
        self.modo_alta_carga = modo_alta_carga
        self.executores = []
        self.executando = False
        self.logger = logging.getLogger(f'SimuladorCarga.GerenciadorServidor.{servidor_ip_porta}')

        self.config = ConfiguracaoExecucao.obter_configuracao_alta_carga() if modo_alta_carga else ConfiguracaoExecucao.obter_configuracao_normal()

    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.executores = []

            threads_por_consulta = self.config['threads_por_consulta']
            total_threads_servidor = ConfiguracaoExecucao.calcular_threads_por_servidor(len(self.bancos_servidor),
                                                                                        threads_por_consulta)

            self.logger.info(f"Iniciando servidor {self.servidor_ip_porta}:")
            self.logger.info(f"  Bancos: {len(self.bancos_servidor)}")
            self.logger.info(f"  Threads por consulta: {threads_por_consulta}")
            self.logger.info(f"  Total threads servidor: {total_threads_servidor}")

            for banco in self.bancos_servidor:
                executor = ExecutorConsultas(banco, self.modo_alta_carga)
                self.executores.append(executor)
                executor.iniciar_execucao()

            self.logger.info(f"Servidor {self.servidor_ip_porta} iniciado com {len(self.executores)} executores")

    def parar_execucao(self):
        if self.executando:
            self.executando = False
            self.logger.info(f"Parando servidor {self.servidor_ip_porta}")

            for executor in self.executores:
                executor.parar_execucao()

            self._log_estatisticas_finais()
            self.executores = []

    def _log_estatisticas_finais(self):
        total_consultas = 0
        total_erros = 0
        total_threads = 0

        for executor in self.executores:
            stats = executor.obter_estatisticas()
            if stats:
                total_consultas += stats['total_consultas']
                total_erros += stats['total_erros']
                total_threads += stats['threads_total']

        self.logger.info(f"Estatísticas finais servidor {self.servidor_ip_porta}:")
        self.logger.info(f"  Total consultas: {total_consultas}")
        self.logger.info(f"  Total erros: {total_erros}")
        self.logger.info(f"  Total threads: {total_threads}")

    def obter_estatisticas(self):
        if not self.executando:
            return None

        stats_bancos = {}
        total_consultas = 0
        total_erros = 0
        total_threads_ativas = 0
        total_threads = 0

        for executor in self.executores:
            stats = executor.obter_estatisticas()
            if stats:
                nome_banco = executor.configuracao.nome_banco
                stats_bancos[nome_banco] = stats
                total_consultas += stats['total_consultas']
                total_erros += stats['total_erros']
                total_threads_ativas += stats['threads_ativas']
                total_threads += stats['threads_total']

        return {
            'servidor_ip_porta': self.servidor_ip_porta,
            'bancos': stats_bancos,
            'total_bancos': len(self.bancos_servidor),
            'total_consultas': total_consultas,
            'total_erros': total_erros,
            'threads_ativas': total_threads_ativas,
            'threads_total': total_threads,
            'percentual_uso': (total_threads_ativas / total_threads * 100) if total_threads > 0 else 0
        }