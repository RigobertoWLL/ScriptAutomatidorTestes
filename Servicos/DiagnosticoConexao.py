import fdb
import logging
import threading
import time

class DiagnosticoConexao:
    def __init__(self):
        self.logger = logging.getLogger('SimuladorCarga.DiagnosticoConexao')
    
    def testar_conexao_ip(self, ip, porta, nome_banco):
        try:
            self.logger.info(f"Testando conexão: {ip}:{porta}/{nome_banco}")
            
            conexao = fdb.connect(
                host=ip,
                port=int(porta),
                database=nome_banco,
                user='CCL',
                password='w_0rR-HbMomsH7vO917',
                role='R_CCL',
                connection_timeout=10
            )
            
            cursor = conexao.cursor()
            cursor.execute("SELECT FIRST 1 * FROM RDB$DATABASE")
            resultado = cursor.fetchone()
            cursor.close()
            conexao.close()
            
            self.logger.info(f"✅ Conexão OK: {ip}:{porta}/{nome_banco}")
            return True, "Conexão bem-sucedida"
            
        except Exception as e:
            erro_msg = str(e)
            self.logger.error(f"❌ Erro conexão {ip}:{porta}/{nome_banco}: {erro_msg}")
            return False, erro_msg
    
    def diagnosticar_ips_problematicos(self, configuracoes, max_testes=5):
        self.logger.info("Iniciando diagnóstico de conectividade")
        
        ips_testados = set()
        resultados = {}
        contador = 0
        
        for config in configuracoes:
            if contador >= max_testes:
                break
                
            ip_porta = f"{config.ip}:{config.porta}"
            if ip_porta not in ips_testados:
                ips_testados.add(ip_porta)
                sucesso, mensagem = self.testar_conexao_ip(config.ip, config.porta, config.nome_banco)
                resultados[ip_porta] = {
                    'sucesso': sucesso,
                    'mensagem': mensagem,
                    'banco_teste': config.nome_banco
                }
                contador += 1
        
        return resultados