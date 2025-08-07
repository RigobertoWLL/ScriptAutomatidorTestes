import threading
import time
import logging
from Servicos.ExecutorConsultas import ExecutorConsultas
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao


class GerenciadorIP:
    def __init__(self, ip_porta, bancos_ativos, modo_alta_carga=False):
        self.ip_porta = ip_porta
        self.bancos_ativos = bancos_ativos
        self.modo_alta_carga = modo_alta_carga
        self.executores = []
        self.executando = False
        self.logger = logging.getLogger(f'SimuladorCarga.GerenciadorIP.{ip_porta}')

        self.config = ConfiguracaoExecucao.obter_configuracao_alta_carga() if modo_alta_carga else ConfiguracaoExecucao.obter_configuracao_normal()

    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.executores = []

            threads_por_loja = self.config['threads_por_loja']
            total_threads_ip = len(self.bancos_ativos) * 5 * threads_por_loja

            lojas_ativas = [banco.nome_banco for banco in self.bancos_ativos]

            self.logger.info(f"Iniciando IP {self.ip_porta}:")
            self.logger.info(f"  Lojas ativas: {len(self.bancos_ativos)} (máx: {self.config['max_consultas_por_ip']})")
            self.logger.info(f"  Threads por loja: {threads_por_loja}")
            self.logger.info(f"  Total threads IP: {total_threads_ip}")
            self.logger.info(f"  Lojas: {', '.join(lojas_ativas)}")

            for banco in self.bancos_ativos:
                executor = ExecutorConsultas(banco, self.modo_alta_carga)
                self.executores.append(executor)
                executor.iniciar_execucao()

            self.logger.info(f"IP {self.ip_porta} iniciado com {len(self.executores)} lojas ativas")

    def atualizar_bancos_ativos(self, novos_bancos):
        if self.executando:
            self.logger.info(f"Atualizando lojas ativas do IP {self.ip_porta}")

            for executor in self.executores:
                executor.parar_execucao()

            self.bancos_ativos = novos_bancos
            self.executores = []

            lojas_novas = [banco.nome_banco for banco in novos_bancos]
            self.logger.info(f"Novas lojas ativas: {', '.join(lojas_novas)}")

            for banco in self.bancos_ativos:
                executor = ExecutorConsultas(banco, self.modo_alta_carga)
                self.executores.append(executor)
                executor.iniciar_execucao()

    def parar_execucao(self):
        if self.executando:
            self.executando = False
            self.logger.info(f"Parando IP {self.ip_porta}")

            for executor in self.executores:
                executor.parar_execucao()

            self._log_estatisticas_finais()
            self.executores = []

    def _log_estatisticas_finais(self):
        total_consultas = 0
        total_erros = 0
        lojas_consultadas = []

        for executor in self.executores:
            stats = executor.obter_estatisticas()
            if stats:
                total_consultas += stats['total_consultas']
                total_erros += stats['total_erros']
                lojas_consultadas.append(executor.configuracao.nome_banco)

        self.logger.info(f"Estatísticas finais IP {self.ip_porta}:")
        self.logger.info(f"  Lojas consultadas: {', '.join(lojas_consultadas)}")
        self.logger.info(f"  Total consultas: {total_consultas}")
        self.logger.info(f"  Total erros: {total_erros}")

    def obter_estatisticas(self):
        if not self.executando:
            return None

        stats_lojas = {}
        total_consultas = 0
        total_erros = 0
        total_threads_ativas = 0
        total_threads = 0

        for executor in self.executores:
            stats = executor.obter_estatisticas()
            if stats:
                nome_loja = executor.configuracao.nome_banco
                stats_lojas[nome_loja] = stats
                total_consultas += stats['total_consultas']
                total_erros += stats['total_erros']
                total_threads_ativas += stats['threads_ativas']
                total_threads += stats['threads_total']

        return {
            'ip_porta': self.ip_porta,
            'lojas_ativas': list(stats_lojas.keys()),
            'lojas': stats_lojas,
            'total_lojas_ativas': len(self.bancos_ativos),
            'total_consultas': total_consultas,
            'total_erros': total_erros,
            'threads_ativas': total_threads_ativas,
            'threads_total': total_threads,
            'percentual_uso': (total_threads_ativas / total_threads * 100) if total_threads > 0 else 0
        }