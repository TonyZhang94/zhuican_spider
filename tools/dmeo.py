import psycopg2
import db_params
db_conn = psycopg2.connect(host=db_params.PG_SERVER_HOST, port=db_params.PG_SERVER_PORT, password=
db_params.PG_SERVER_PASS, user=db_params.PG_SERVER_USER, database='raw_mj_category')
print 'conn success'
cur = db_conn.cursor()
version = '20180426111357'
while 1:
    sql = "select result from hotwords.person where version='{}'".format("20180426113235")
    cur.execute(sql)
    res = cur.fetchall()
    print res
    break