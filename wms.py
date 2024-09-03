import pymysql
from pymysql import OperationalError
from datetime import datetime
import pytz
from openpyxl import Workbook
from io import BytesIO

# Configurações da conexão com o banco de dados
def conectar_banco():
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db="defaultdb",
            host="mysql-loc-project-166.l.aivencloud.com",
            password="AVNS_CS4hASi4h2FxmmE0Vsy",
            read_timeout=10,
            port=27550,
            user="avnadmin",
            write_timeout=10,
        )
        return connection
    except OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Criar a tabela se não existir
def criar_tabela():
    connection = conectar_banco()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS etiquetas (
                    id_etiqueta VARCHAR(50) PRIMARY KEY,
                    area VARCHAR(100) NOT NULL,
                    data_hora TIMESTAMP NOT NULL,
                    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
            print("Tabela 'etiquetas' criada ou já existe.")
        except OperationalError as e:
            print(f"Erro ao criar a tabela: {e}")
        finally:
            cursor.close()
            connection.close()

# Função para obter o horário atual de São Paulo
def horario_sao_paulo():
    timezone = pytz.timezone('America/Sao_Paulo')
    return datetime.now(timezone)

# Função para adicionar uma nova etiqueta
def adicionar_etiqueta(id_etiqueta, area_inicial):
    connection = conectar_banco()
    if connection:
        try:
            cursor = connection.cursor()
            data_hora_atual = horario_sao_paulo()
            cursor.execute("""
                INSERT INTO etiquetas (id_etiqueta, area, data_hora, data_criacao) 
                VALUES (%s, %s, %s, %s)
            """, (id_etiqueta, area_inicial, data_hora_atual, data_hora_atual))
            connection.commit()
        except OperationalError as e:
            raise ValueError(f"Erro ao adicionar etiqueta: {e}")
        finally:
            cursor.close()
            connection.close()


# Função para atualizar a localização de uma etiqueta
def atualizar_localizacao(id_etiqueta, nova_area):
    connection = conectar_banco()
    if connection:
        try:
            cursor = connection.cursor()
            data_hora_atual = horario_sao_paulo()
            cursor.execute("UPDATE etiquetas SET area = %s, data_hora = %s WHERE id_etiqueta = %s", 
                           (nova_area, data_hora_atual, id_etiqueta))
            connection.commit()
        except OperationalError as e:
            raise ValueError(f"Erro ao atualizar localização: {e}")
        finally:
            cursor.close()
            connection.close()

# Função para consultar a localização de uma etiqueta
def consultar_localizacao(id_etiqueta):
    connection = conectar_banco()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT area, data_hora FROM etiquetas WHERE id_etiqueta = %s", 
                           (id_etiqueta,))
            result = cursor.fetchone()
            if result:
                return {"area": result["area"], "data_hora": result["data_hora"]}
            else:
                raise ValueError(f"Etiqueta {id_etiqueta} não encontrada.")
        except OperationalError as e:
            raise ValueError(f"Erro ao consultar localização: {e}")
        finally:
            cursor.close()
            connection.close()
    
def gerar_relatorio_excel(data_inicio, data_fim):
    connection = conectar_banco()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id_etiqueta, area, data_hora, data_criacao
                FROM etiquetas 
                WHERE data_hora BETWEEN %s AND %s
                ORDER BY data_hora
            """, (data_inicio, data_fim))
            
            results = cursor.fetchall()
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Relatório de Etiquetas"
            
            # Adicionar cabeçalhos
            ws.append(["ID da Etiqueta", "Área", "Data e Hora da Última Atualização", "Data e Hora de Criação"])
            
            # Adicionar dados
            for row in results:
                ws.append([row['id_etiqueta'], row['area'], row['data_hora'], row['data_criacao']])
            
            # Salvar o arquivo em um buffer de memória
            excel_file = BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)
            
            return excel_file
        except OperationalError as e:
            raise ValueError(f"Erro ao gerar relatório: {e}")
        finally:
            cursor.close()
            connection.close()

# Inicializar banco de dados ao iniciar o sistema
criar_tabela()
