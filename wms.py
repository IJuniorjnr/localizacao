import pymysql
from pymysql import OperationalError

# Configurações da conexão com o banco de dados
def conectar_banco():
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db="defaultdb",  # Substitua pelo nome do seu banco de dados
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
                    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
            print("Tabela 'etiquetas' criada ou já existe.")
        except OperationalError as e:
            print(f"Erro ao criar a tabela: {e}")
        finally:
            connection.close()

# Função para adicionar uma nova etiqueta
def adicionar_etiqueta(id_etiqueta, area_inicial):
    connection = conectar_banco()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO etiquetas (id_etiqueta, area) VALUES (%s, %s)", 
                           (id_etiqueta, area_inicial))
            connection.commit()
        except OperationalError as e:
            raise ValueError(f"Erro ao adicionar etiqueta: {e}")
        finally:
            connection.close()

# Função para atualizar a localização de uma etiqueta
def atualizar_localizacao(id_etiqueta, nova_area):
    connection = conectar_banco()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE etiquetas SET area = %s WHERE id_etiqueta = %s", 
                           (nova_area, id_etiqueta))
            connection.commit()
        except OperationalError as e:
            raise ValueError(f"Erro ao atualizar localização: {e}")
        finally:
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
            connection.close()

# Inicializar banco de dados ao iniciar o sistema
criar_tabela()
