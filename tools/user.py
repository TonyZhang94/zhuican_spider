# -*- coding: utf-8 -*-
# 验证用户名密码
import psycopg2
import db_params
import time


pg_conn = psycopg2.connect(host=db_params.PG_SERVER_HOST, port=db_params.PG_SERVER_PORT,user=db_params.PG_SERVER_USER,
	password=db_params.PG_SERVER_PASS, database='chu')
cur = pg_conn.cursor()


def val_user(username, password):
	table = 'public.user'
	try:
		sql = "select password from %s where username='%s'" %(table, username)
		cur.execute(sql)
		pwd = cur.fetchall()[0][0]
		print pwd, type(pwd)
		print password
		if pwd == password:
			return '0'
		else:
			return '1'
	except Exception as e:
		print e
		return '2'
	

def insert_user(username, password):
	table = 'public.user'
	datamonth = time.strftime('%Y%m%d%H%M%S', time.localtime())
	try:
		sql = "select password from %s where username='%s'" % (table, username)
		cur.execute(sql)
		if cur.fetchall()!=[]:
			return '1'
	except Exception as e:
		print e
	i = 0
	while i < 5:
		try:
			sql = "INSERT INTO {} (username, password, datamonth) VALUES (%s, %s, %s);".format(table)
			data = (username, password, datamonth)
			cur.execute(sql, data)
			pg_conn.commit()
			return '0'
		except Exception as e:
			i += 1
			print e
			cur.execute('rollback;')
		return '2'
