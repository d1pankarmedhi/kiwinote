import psycopg2
from psycopg2 import sql
import urllib.parse as up
from logger import get_logger

logger = get_logger(__name__)

class Database:
    def __init__(self, database_url: str) -> None:
        self.cursor = None
        self.database_url = database_url

    def connect(self):
        try:
            up.uses_netloc.append("postgres")
            url = up.urlparse(self.database_url)
            conn = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
            conn.autocommit = True
            self.cursor = conn.cursor()
        except Exception as e:
            logger.error(e)

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
        except Exception as e:
            logger.error(f"Error: {e}")

    def fetch_all(self, table_name):
        try:
            query = sql.SQL(f"SELECT * FROM {table_name}")
            self.execute_query(query)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(e)

    def fetch_by_id(self, table_name, id):
        try:
            query = sql.SQL(f"SELECT * FROM {table_name} WHERE id = %s")
            self.execute_query(query, (id,))
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(e)

    def insert_data(self, table_name, data):
        try:
            columns = data.keys()
            values = [data[column] for column in columns]
            
            columns_sql = sql.SQL(', ').join(map(sql.Identifier, columns))
            values_sql = sql.SQL(', ').join([sql.Placeholder()] * len(values))

            query = sql.SQL("INSERT INTO {0} ({1}) VALUES ({2})").format(
                sql.Identifier(table_name), columns_sql, values_sql
            )

            self.execute_query(query, values)
        except Exception as e:
            logger.error(e)

    def update_data(self, table_name: str, id:int, data: dict):
        try:
            # set_values = [sql.SQL("{0} = %s".format(sql.Identifier(column))) for column in data.keys()]
            
            query = sql.SQL(f"UPDATE {table_name} SET title='{data['title']}', body='{data['body']}' WHERE id = {id}")

            self.execute_query(query)
        except Exception as e:
            logger.error(e)



    def delete_data(self, table_name, id):
        try:
            query = sql.SQL(f"DELETE FROM {table_name} WHERE id = %s")
            self.execute_query(query, (id,))
 
        except Exception as e:
            logger.error(e)

    def search_by_keywords(self, table_name, keywords):
        try:
            # Construct a tsquery using OR to match any of the keywords
            tsquery = ' | '.join(f'{keyword}' for keyword in keywords.split(" "))
            logger.info(f"keywords: {tsquery}")
            search_query = sql.SQL(
                f"SELECT * FROM {table_name} WHERE to_tsvector('english', body) @@ to_tsquery('english', %s)"
            )
            self.execute_query(search_query, (tsquery,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(e)


    def get_counts(self, table_name):
        count_query = sql.SQL(f"SELECT count(*) as cnt FROM {table_name}")
        self.execute_query(count_query)
        return self.cursor.fetchall()

    def fetch_relevant_docs(self, region: str, language: str, embedding):
        try:
            fetch_query = sql.SQL(
                f"SELECT title, description, examples, 1 - (embedding <=> '{embedding}' ) AS cosine_similarity FROM documents WHERE language='{language}' AND region='{region}' ORDER BY 2 DESC LIMIT 10;"
            )
            self.execute_query(fetch_query)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(e)

    def close_connection(self):
        self.cursor.close()
