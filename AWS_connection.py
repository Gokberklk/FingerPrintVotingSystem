import psycopg2
import logging as Logger

ENDPOINT="postgres.chcecoomgfvf.eu-west-1.rds.amazonaws.com"
PORT="5432"
USER="postgres"
REGION="us-west-1"
DBNAME="postgres"




def establish_connection():
    try:
        conn = psycopg2.connect(host=ENDPOINT, port=PORT, dbname=DBNAME, user=USER, password="Bitirme123",
                                sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor()
        return cursor
    except (Exception, psycopg2.DatabaseError) as error:
        Logger.raise_error(f"Error while connecting to PostgreSQL: {error}")
        return None



if __name__ == "__main__":
    cursor = establish_connection()
    cursor.execute("Select * from citizen")
    test = cursor.fetchall()
    print(test)
