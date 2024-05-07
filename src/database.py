import os
import pyodbc
import struct
from msal import ConfidentialClientApplication
import pandas as pd

from sqlalchemy import create_engine
from urllib.parse import quote_plus

class AzureSQLDatabase:
    def __init__(self, server, database, client_id, client_secret, tenant_id):
        self.server = server
        self.database = database
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

    def get_access_token(self):
        authority_url = f"https://login.microsoftonline.com/{self.tenant_id}"
        scopes = ["https://database.windows.net//.default"]

        app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=authority_url
        )

        result = app.acquire_token_for_client(scopes)
        return result['access_token']

    def get_connection(self):
        access_token = self.get_access_token()
        token_bytes = access_token.encode('UTF-16-LE')
        token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
        SQL_COPT_SS_ACCESS_TOKEN = 1256

        connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={self.server};Database={self.database};"
        params = quote_plus(connection_string)
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", connect_args={'attrs_before': {SQL_COPT_SS_ACCESS_TOKEN: token_struct}})
        return engine

    def init_connection(self):
        # Initiate the connection
        self.engine = self.get_connection()

    def execute_query(self, sql_query):
        print('Please wait, authenticating your login and executing SQL query...')
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(sql_query, conn)
            error = None
        except Exception as e:
            df = pd.DataFrame()
            error = e

        print('SQL query executed.')
        return df, error


class SQLDatabase(AzureSQLDatabase):
    def __init__(self):
        super().__init__(
            server="<server name>",
            database="<db name>",
            client_id=os.getenv("<client id>"),
            client_secret=os.getenv("<client secret>"),
            tenant_id="<tenant id>"
        )

        self.init_connection()


# Factory Method
def get_database(db_name):
    if db_name.lower() == 'SQL':
        return SQLDatabase()
    else:
        raise ValueError(f"Unknown database type: {db_name}")
