import fdb
import time
from Modelos.ConsultasSql import ConsultasSql

class ConexaoFirebird:
    def __init__(self, configuracao_banco):
        self.configuracao = configuracao_banco
        self.conexao = None
    
    def conectar(self):
        try:
            string_conexao = f"{self.configuracao.ip}:{self.configuracao.porta}/{self.configuracao.nome_banco}"
            self.conexao = fdb.connect(
                host=self.configuracao.ip,
                port=int(self.configuracao.porta),
                database=self.configuracao.nome_banco,
                user='SYSDBA',
                password='masterkey'
            )
            return True
        except Exception:
            return False
    
    def executar_consulta(self, sql):
        if not self.conexao:
            return False
        
        try:
            cursor = self.conexao.cursor()
            cursor.execute(sql)
            cursor.fetchall()
            cursor.close()
            return True
        except Exception:
            return False
    
    def desconectar(self):
        if self.conexao:
            self.conexao.close()
            self.conexao = None