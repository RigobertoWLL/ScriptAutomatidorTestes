from Servicos.ConfiguradorLog import ConfiguradorLog
from InterfaceUsuario.MenuConsoleComDiagnostico import MenuConsoleComDiagnostico
import logging

if __name__ == "__main__":
    try:
        logger = ConfiguradorLog.configurar_log()
        logger.info("=== SIMULADOR DE CARGA FIREBIRD COM DIAGNÓSTICO ===")
        logger.info("Usuário: RigobertoWLL")
        logger.info("Data/Hora: 2025-08-07 20:08:01 UTC")
        logger.info("Sistema de diagnóstico de conectividade ativo")
        
        menu = MenuConsoleComDiagnostico()
        menu.exibir_menu_principal()
        
    except Exception as e:
        logger = logging.getLogger('SimuladorCarga')
        logger.error(f"Erro crítico na aplicação: {e}")
        print(f"❌ Erro crítico: {e}")
        input("Pressione Enter para sair...")
    finally:
        logger = logging.getLogger('SimuladorCarga')
        logger.info("=== SIMULADOR DE CARGA FIREBIRD FINALIZADO ===")