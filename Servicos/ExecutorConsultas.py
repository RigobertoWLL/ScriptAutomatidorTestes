import threading
import logging
from Servicos.ExecutorConsultaUnica import ExecutorConsultaUnica
from Modelos.ConsultasSql import ConsultasSql
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao


class ExecutorConsultas:
    def __init__(self, configuracao_banco, modo_alta_carga=False):
        self.configuracao = configuracao_banco
        self.modo_alta_carga = modo_alta_carga
        self.executores_consultas = []
        self.executando = False
        self.logger = logging.getLogger(f'SimuladorCarga.ExecutorConsultas.{configuracao_banco.nome_banco}')

        if modo_alta_carga:
            self.config = ConfiguracaoExecucao.obter_configuracao_alta_carga()
        else:
            self.config = ConfiguracaoExecucao.obter_configuracao_normal()

    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.executores_consultas = []

            consultas_com_nome = ConsultasSql.obter_consultas_com_nome()
            threads_por_consulta = self.config['threads_por_consulta']
            total_threads = len(consultas_com_nome) * threads_por_consulta

            self.logger.info(
                f"Iniciando {total_threads} threads ({threads_por_consulta} por consulta) para {self.configuracao.nome_banco}")

            for nome_consulta, sql_consulta in consultas_com_nome.items():
                for thread_id in range(threads_por_consulta):
                    executor = ExecutorConsultaUnica(
                        self.configuracao,
                        nome_consulta,
                        sql_consulta,
                        thread_id,
                        self.config['intervalo_consultas']
                    )
                    self.executores_consultas.append(executor)
                    executor.iniciar_execucao()

            self.logger.info(
                f"Todas as {total_threads} threads iniciadas para {self.configuracao.nome_banco} - Simulando múltiplas conexões simultâneas")

    def parar_execucao(self):
        if self.executando:
            self.executando = False
            self.logger.info(f"Parando {len(self.executores_consultas)} threads para {self.configuracao.nome_banco}")

            for executor in self.executores_consultas:
                executor.parar_execucao()

            self._log_estatisticas_finais()
            self.executores_consultas = []

    def _log_estatisticas_finais(self):
        stats_por_consulta = {}
        total_consultas = 0
        total_erros = 0

        for executor in self.executores_consultas:
            nome_consulta = executor.nome_consulta
            if nome_consulta not in stats_por_consulta:
                stats_por_consulta[nome_consulta] = {'consultas': 0, 'erros': 0, 'threads': 0}

            stats = executor.obter_estatisticas()
            stats_por_consulta[nome_consulta]['consultas'] += stats['consultas_executadas']
            stats_por_consulta[nome_consulta]['erros'] += stats['erros']
            stats_por_consulta[nome_consulta]['threads'] += 1

            total_consultas += stats['consultas_executadas']
            total_erros += stats['erros']

        self.logger.info(f"Estatísticas finais para {self.configuracao.nome_banco}:")
        for nome_consulta, stats in stats_por_consulta.items():
            self.logger.info(
                f"  {nome_consulta}: {stats['consultas']} consultas, {stats['erros']} erros, {stats['threads']} threads")
        self.logger.info(f"  TOTAL: {total_consultas} consultas, {total_erros} erros")

    def obter_estatisticas(self):
        if not self.executando:
            return None

        stats_por_consulta = {}
        total_consultas = 0
        total_erros = 0
        threads_ativas = 0

        for executor in self.executores_consultas:
            nome_consulta = executor.nome_consulta
            if nome_consulta not in stats_por_consulta:
                stats_por_consulta[nome_consulta] = {'consultas': 0, 'erros': 0, 'threads_ativas': 0,
                                                     'threads_total': 0}

            stats = executor.obter_estatisticas()
            stats_por_consulta[nome_consulta]['consultas'] += stats['consultas_executadas']
            stats_por_consulta[nome_consulta]['erros'] += stats['erros']
            stats_por_consulta[nome_consulta]['threads_total'] += 1

            if stats['ativo']:
                stats_por_consulta[nome_consulta]['threads_ativas'] += 1
                threads_ativas += 1

            total_consultas += stats['consultas_executadas']
            total_erros += stats['erros']

        return {
            'consultas_por_tipo': stats_por_consulta,
            'total_consultas': total_consultas,
            'total_erros': total_erros,
            'threads_ativas': threads_ativas,
            'threads_total': len(self.executores_consultas)
        }