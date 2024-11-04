import sqlalchemy as sa
import pyodbc

# Defina a string de conexão
connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=GCL5L9GV53\LOCALDB;DATABASE=actionplanner;Trusted_Connection=yes"

# Crie o engine
engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")

# Função para conectar ao banco de dados
def connect_to_db():
    return engine.connect()