import logging
from collections import deque, defaultdict
import threading

class GerenciadorFilaLojas:
    def __init__(self):
        self.filas_por_ip = defaultdict(deque)
        self.lojas_ativas = defaultdict(set)
        self.lojas_processadas = defaultdict(set)
        self.max_consultas_por_ip = 8
        self.lock = threading.Lock()
        self.logger = logging.getLogger('SimuladorCarga.GerenciadorFilaLojas')
    
    def inicializar_filas(self, configuracoes):
        with self.lock:
            self.filas_por_ip.clear()
            self.lojas_ativas.clear()
            self.lojas_processadas.clear()
            
            agrupamento_por_ip = defaultdict(list)
            
            for config in configuracoes:
                ip_porta = f"{config.ip}:{config.porta}"
                agrupamento_por_ip[ip_porta].append(config)
            
            for ip_porta, bancos in agrupamento_por_ip.items():
                self.filas_por_ip[ip_porta] = deque(bancos)
                self.logger.info(f"IP {ip_porta}: {len(bancos)} lojas na fila")
            
            self.logger.info(f"Total de IPs únicos: {len(self.filas_por_ip)}")
            self.logger.info(f"Limite de {self.max_consultas_por_ip} consultas simultâneas por IP")
    
    def obter_proxima_loja(self, ip_porta):
        with self.lock:
            if len(self.lojas_ativas[ip_porta]) >= self.max_consultas_por_ip:
                return None
            
            if self.filas_por_ip[ip_porta]:
                loja = self.filas_por_ip[ip_porta].popleft()
                self.lojas_ativas[ip_porta].add(loja.nome_banco)
                self.logger.debug(f"Loja {loja.nome_banco} ativada no IP {ip_porta} ({len(self.lojas_ativas[ip_porta])}/{self.max_consultas_por_ip})")
                return loja
            
            return None
    
    def liberar_loja(self, ip_porta, nome_loja):
        with self.lock:
            if nome_loja in self.lojas_ativas[ip_porta]:
                self.lojas_ativas[ip_porta].remove(nome_loja)
                self.lojas_processadas[ip_porta].add(nome_loja)
                self.logger.debug(f"Loja {nome_loja} liberada do IP {ip_porta}")
                
                if not self.filas_por_ip[ip_porta] and not self.lojas_ativas[ip_porta]:
                    self._reiniciar_fila_ip(ip_porta)
    
    def _reiniciar_fila_ip(self, ip_porta):
        if self.lojas_processadas[ip_porta]:
            configuracoes_reiniciar = []
            for nome_loja in self.lojas_processadas[ip_porta]:
                ip, porta = ip_porta.split(':')
                from Modelos.ConfiguracaoBanco import ConfiguracaoBanco
                config = ConfiguracaoBanco(ip, porta, nome_loja)
                configuracoes_reiniciar.append(config)
            
            self.filas_por_ip[ip_porta] = deque(configuracoes_reiniciar)
            self.lojas_processadas[ip_porta].clear()
            self.logger.info(f"Fila reiniciada para IP {ip_porta} com {len(configuracoes_reiniciar)} lojas")
    
    def obter_status_filas(self):
        with self.lock:
            status = {}
            for ip_porta in self.filas_por_ip:
                status[ip_porta] = {
                    'fila_aguardando': len(self.filas_por_ip[ip_porta]),
                    'ativas': len(self.lojas_ativas[ip_porta]),
                    'processadas': len(self.lojas_processadas[ip_porta]),
                    'limite_maximo': self.max_consultas_por_ip
                }
            return status