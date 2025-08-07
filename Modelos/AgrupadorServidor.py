from collections import defaultdict
import logging


class AgrupadorServidor:
    def __init__(self):
        self.logger = logging.getLogger('SimuladorCarga.AgrupadorServidor')

    def agrupar_por_servidor(self, configuracoes):
        servidores = defaultdict(list)

        for config in configuracoes:
            chave_servidor = f"{config.ip}:{config.porta}"
            servidores[chave_servidor].append(config)

        self.logger.info(f"Agrupamento por servidor:")
        for servidor, bancos in servidores.items():
            self.logger.info(f"  Servidor {servidor}: {len(bancos)} bancos")

        self.logger.info(f"Total de servidores únicos: {len(servidores)}")
        return dict(servidores)

    def obter_distribuicao_threads(self, servidores_agrupados, threads_por_consulta):
        distribuicao = {}

        for servidor, bancos in servidores_agrupados.items():
            total_consultas = len(bancos) * 5
            threads_por_servidor = total_consultas * threads_por_consulta

            distribuicao[servidor] = {
                'bancos': bancos,
                'total_bancos': len(bancos),
                'total_consultas': total_consultas,
                'threads_por_servidor': threads_por_servidor
            }

        return distribuicao