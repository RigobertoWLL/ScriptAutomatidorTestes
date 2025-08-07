class ConsultasSql:
    CONSULTA_SP_GERENCIAL = "SELECT * FROM sp_gerencial_pg1 ('2025-07-01','2025-07-31',0)"
    CONSULTA_SP_DRE = "SELECT * FROM sp_dre (3, '2025-07-01', '2025-07-31', 0)"
    CONSULTA_EMPRESA = "SELECT * FROM EMPRESA"
    CONSULTA_PRODUTOS = "SELECT * FROM PRODUTOS"
    CONSULTA_CLIENTES = "SELECT * FROM CLIENTES"

    @staticmethod
    def obter_todas_consultas():
        return [
            ConsultasSql.CONSULTA_SP_GERENCIAL,
            ConsultasSql.CONSULTA_SP_DRE,
            ConsultasSql.CONSULTA_EMPRESA,
            ConsultasSql.CONSULTA_PRODUTOS,
            ConsultasSql.CONSULTA_CLIENTES
        ]

    @staticmethod
    def obter_consultas_com_nome():
        return {
            'SP_GERENCIAL': ConsultasSql.CONSULTA_SP_GERENCIAL,
            'SP_DRE': ConsultasSql.CONSULTA_SP_DRE,
            'EMPRESA': ConsultasSql.CONSULTA_EMPRESA,
            'PRODUTOS': ConsultasSql.CONSULTA_PRODUTOS,
            'CLIENTES': ConsultasSql.CONSULTA_CLIENTES
        }