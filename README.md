# 🔥 Simulador de Carga Firebird

Sistema multithreaded Python para simulação de carga em servidores Firebird, com controle inteligente de distribuição por IP e diagnóstico automático de conectividade.

## 📋 Funcionalidades

- ✅ **Controle por IP**: Máximo de 8 consultas simultâneas por IP
- 🔄 **Sistema de Fila**: Todas as lojas são processadas automaticamente
- 🔍 **Diagnóstico Automático**: Detecta problemas de conectividade
- 📊 **Múltiplas Consultas**: 5 tipos de consultas simultâneas por loja
- 🔗 **Multithreading**: Sistema de threads independentes por consulta
- 📈 **Monitoramento em Tempo Real**: Estatísticas detalhadas e monitor ao vivo
- 📝 **Logs Detalhados**: Sistema completo de logging

## 🎯 Consultas Executadas

O sistema executa simultaneamente as seguintes consultas:

1. **SP_GERENCIAL**: `SELECT * FROM sp_gerencial_pg1 ('2025-07-01','2025-07-31',0)`
2. **SP_DRE**: `SELECT * FROM sp_dre (3, '2025-07-01', '2025-07-31', 0)`
3. **EMPRESA**: `SELECT * FROM EMPRESA`
4. **PRODUTOS**: `SELECT * FROM PRODUTOS`
5. **CLIENTES**: `SELECT * FROM CLIENTES`

## 🚀 Instalação

### Pré-requisitos

- Python 3.7+
- Firebird Client
- Conexão com servidores Firebird

### Passos de Instalação

1. **Clone ou baixe os arquivos**
   ```bash
   mkdir simulador-firebird
   cd simulador-firebird
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o arquivo ListaBanco.ini**
   ```ini
   IP:PORTA:NOME_BANCO
   18.231.89.147:3050:CCL_029
   177.71.192.87:3050:CCL_036
   # Adicione mais bancos conforme necessário
   ```

## 🏗️ Estrutura do Projeto

```
simulador-firebird/
├── Modelos/
│   ├── ConfiguracaoBanco.py
│   ├── ConsultasSql.py
│   ├── ConfiguracaoExecucao.py
│   └── GerenciadorFilaLojas.py
├── Servicos/
│   ├── ConfiguradorLog.py
│   ├── LeitorArquivoIni.py
│   ├── ConexaoFirebird.py
│   ├── DiagnosticoConexao.py
│   ├── ExecutorConsultasComDiagnostico.py
│   └── ExecutorLojaComDiagnostico.py
├── Controladores/
│   └── GerenciadorCargaComDiagnostico.py
├── InterfaceUsuario/
│   └── MenuConsoleComDiagnostico.py
├── Logs/
│   └── (arquivos de log são criados automaticamente)
├── Principal.py
├── ListaBanco.ini
├── requirements.txt
└── README.md
```

## 🎮 Como Usar

### Execução Básica

```bash
python Principal.py
```

### Menu Principal

```
🔥 SIMULADOR DE CARGA FIREBIRD - COM DIAGNÓSTICO 🔥
🔍 SISTEMA COM DETECÇÃO DE PROBLEMAS DE CONECTIVIDADE
📊 MÁXIMO 8 CONSULTAS SIMULTÂNEAS POR IP

1 - Iniciar simulação (Modo Normal)
2 - Iniciar simulação (Modo Alta Carga)
3 - Parar simulação
4 - Status da simulação
5 - Estatísticas com diagnóstico
6 - Resumo de IPs e conexões
7 - Monitor em tempo real
8 - Sair
```

### Modos de Operação

#### Modo Normal
- **5 threads por loja**
- Intervalo entre consultas: 0.02s
- Ideal para testes regulares

#### Modo Alta Carga
- **10 threads por loja**
- Intervalo entre consultas: 0.005s
- Para testes de stress intensivo

## ⚙️ Configuração

### Arquivo ListaBanco.ini

Formato: `IP:PORTA:NOME_BANCO`

```ini
# Servidor 1
18.231.89.147:3050:CCL_029
18.231.89.147:3050:CCL_030

# Servidor 2
177.71.192.87:3050:CCL_036
177.71.192.87:3050:CCL_037
```

### Credenciais de Banco

O sistema está configurado para usar:
- **Usuário**: CCL
- **Senha**: w_0rR-HbMomsH7vO917
- **Role**: R_CCL

Para alterar, edite o arquivo `Servicos/ConexaoFirebird.py`

### Parâmetros de Configuração

Arquivo: `Modelos/ConfiguracaoExecucao.py`

```python
MAX_CONSULTAS_POR_IP = 8          # Máximo de consultas por IP
THREADS_POR_LOJA_NORMAL = 5       # Threads modo normal
THREADS_POR_LOJA_ALTA_CARGA = 10  # Threads modo alta carga
TIMEOUT_CONEXAO = 30              # Timeout de conexão
TENTATIVAS_RECONEXAO = 3          # Tentativas de reconexão
```

## 📊 Monitoramento

### Logs

Os logs são salvos automaticamente em `Logs/simulador_carga_YYYY-MM-DD.log`

Níveis de log:
- **INFO**: Informações gerais de execução
- **ERROR**: Erros de conexão e execução
- **DEBUG**: Informações detalhadas (threads, consultas)

### Estatísticas em Tempo Real

O monitor mostra:
- 🔥 Total de consultas executadas
- ❌ Número de erros
- 🔗 Threads ativas
- 🔌 Conexões ativas
- 🖥️ IPs ativos/total

### Diagnóstico Automático

O sistema testa automaticamente:
- ✅ Conectividade com cada IP
- 🔌 Status das conexões ativas
- ⚠️ Detecção de problemas
- 🔄 Recuperação automática

## 🔧 Resolução de Problemas

### Problemas Comuns

#### Erro: "No module named 'fdb'"
```bash
pip install fdb
```

#### Erro de Conexão
1. Verifique se o Firebird Client está instalado
2. Confirme as credenciais no código
3. Teste conectividade manual com o servidor

#### Threads não executam consultas
1. Verifique o diagnóstico inicial nos logs
2. Confirme se as tabelas/procedures existem
3. Verifique permissões do usuário no banco

#### Performance baixa
1. Ajuste `INTERVALO_ENTRE_CONSULTAS`
2. Reduza `THREADS_POR_LOJA`
3. Monitore recursos do servidor

### Logs de Diagnóstico

Exemplo de log de sucesso:
```
2025-08-07 20:08:01 - SimuladorCarga.DiagnosticoConexao - INFO - ✅ Conexão OK: 18.231.89.147:3050/CCL_029
```

Exemplo de log de erro:
```
2025-08-07 20:08:01 - SimuladorCarga.DiagnosticoConexao - ERROR - ❌ Erro conexão 18.231.89.147:3050/CCL_029: Connection refused
```

## 🎯 Características Técnicas

### Arquitetura

- **Padrão MVC**: Separação clara de responsabilidades
- **Threading Seguro**: Uso de