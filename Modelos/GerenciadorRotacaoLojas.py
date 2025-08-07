import logging
from collections import deque, defaultdict
import threading


class GerenciadorRotacaoLojas:
    def __init__(self):
        self.lojas_por_ip = defaultdict(deque)
        self.lojas_em_uso = defaultdict(set)
        self.lojas_processadas = defaultdict(set)
        self.lock = threading.Lock()
        self.logger = logging.getLogger('SimuladorCarga.GerenciadorRotacaoLojas')

    def inicializar_lojas(self, configuracoes):
        with self.lock:
            self.lojas_por_ip.clear()
            self.lojas_em_uso.clear()
            self.lojas_processadas.clear()

            for config in configuracoes:
                ip_porta = f"{config.ip}:{config.porta}"
                self.lojas_por_ip[ip_porta].append(config)

            for ip_porta, lojas in self.lojas_por_ip.items():
                self.logger.info(f"IP {ip_porta}: {len(lojas)} lojas disponíveis")
                lojas_nomes = [loja.nome_banco for loja in lojas]
                self.logger.info(f"  Lojas: {', '.join(lojas_nomes[:10])}{'...' if len(lojas_nomes) > 10 else ''}")

    def obter_proxima_loja(self, ip_porta):
        with self.lock:
            if ip_porta not in self.lojas_por_ip:
                return None

            lojas_disponiveis = self.lojas_por_ip[ip_porta]

            if not lojas_disponiveis:
                todas_processadas = len(self.lojas_processadas[ip_porta])
                self.logger.info(f"Reiniciando rotação para IP {ip_porta} - {todas_processadas} lojas já processadas")

                for loja_config in list(self.lojas_processadas[ip_porta]):
                    if loja_config not in self.lojas_em_uso[ip_porta]:
                        lojas_disponiveis.append(loja_config)

                self.lojas_processadas[ip_porta].clear()

            if lojas_disponiveis:
                loja_config = lojas_disponiveis.popleft()
                self.lojas_em_uso[ip_porta].add(loja_config)
                self.logger.debug(f"Loja {loja_config.nome_banco} atribuída ao IP {ip_porta}")
                return loja_config

            return None

    def liberar_loja(self, ip_porta, loja_config):
        with self.lock:
            if loja_config in self.lojas_em_uso[ip_porta]:
                self.lojas_em_uso[ip_porta].remove(loja_config)
                self.lojas_processadas[ip_porta].add(loja_config)
                self.logger.debug(f"Loja {loja_config.nome_banco} liberada do IP {ip_porta}")

    def obter_estatisticas_rotacao(self):
        with self.lock:
            estatisticas = {}
            for ip_porta in self.lojas_por_ip.keys():
                total_lojas = len(self.lojas_por_ip[ip_porta]) + len(self.lojas_processadas[ip_porta]) + len(
                    self.lojas_em_uso[ip_porta])
                lojas_em_uso = len(self.lojas_em_uso[ip_porta])
                lojas_processadas = len(self.lojas_processadas[ip_porta])
                lojas_pendentes = len(self.lojas_por_ip[ip_porta])

                estatisticas[ip_porta] = {
                    'total_lojas': total_lojas,
                    'em_uso': lojas_em_uso,
                    'processadas': lojas_processadas,
                    'pendentes': lojas_pendentes
                }

            return estatisticas