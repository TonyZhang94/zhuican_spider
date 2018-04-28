# -*- coding: utf-8 -*-
from __future__ import absolute_import

import time
import psycopg2
from celery import task
from zcspider.celery import app

from django.http import JsonResponse
from tools.write_log import OperationLog, ErrorLog, RunLog
from .mmb_customized.mmb_api_parse import mmb_api_parse
from tools.websocket import websocket
from tools import db_params

mmb_api_parse = mmb_api_parse()
db_conn = psycopg2.connect(host=db_params.PG_SERVER_HOST, port=db_params.PG_SERVER_PORT,password=db_params.PG_SERVER_PASS,user=db_params.PG_SERVER_USER, database='chu')
cur = db_conn.cursor()


class NoneError(Exception):
	def __init__(self, err='search_key不能为空'):
		Exception.__init__(self, err)


def generate_version():  # 生成version
	return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


@app.task()
def words_run(search_keys, version, table, username):
	
	print 'search_keys', search_keys
	key_type = "words"
	# print 'search_keys', search_keys
	# search_keys: ['50010808;唇膏/口红;赵石爱凤定|||1255', '50010808;唇膏/口红;无色限唇膏|||1255', \
	# '50010808;唇膏/口红;防裂唇膏|||1255']
	# 初始化日志 书写对象
	run_log = RunLog(search_keys[0].split(';')[0])  # search_keys[0].split(';')[0]:cid
	for search_key in search_keys:  # search_key:50010808;唇膏 / 口红;防裂唇膏 | | | 1255
		run_log.write_title(search_key)
		search_key = search_key.split(';')
		
		res = mmb_api_parse.start(search_key, key_type, version, run_log)
		try:
			while True:
				try:
					sql = 'insert into {} (username, result,version) values(%s,%s,%s)'.format(table)
					data = (username, res, version)
					cur.execute(sql, data)
					db_conn.commit()
					break
				except Exception as e:
					print e
					cur.execute('rollback;')
		except Exception as e:
			error_log = ErrorLog(search_key[0])
			
			error_log.error_log('run logdb insert errro: ' + e)
		time.sleep(2)



@task
def models_run(search_keys, version, table, username):
	print 'search_keys', search_keys
	key_type = "models"
	# print 'search_keys', search_keys
	# search_keys: ['50010808;唇膏/口红;赵石爱凤定|||1255', '50010808;唇膏/口红;无色限唇膏|||1255', \
	# '50010808;唇膏/口红;防裂唇膏|||1255']
	# 初始化日志 书写对象
	run_log = RunLog(search_keys[0].split(';')[0])  # search_keys[0].split(';')[0]:cid
	for search_key in search_keys:  # search_key:50010808;唇膏 / 口红;防裂唇膏 | | | 1255
		run_log.write_title(search_key)
		search_key = search_key.split(';')
		
		res = mmb_api_parse.start(search_key, key_type, version, run_log)
		try:
			while True:
				try:
					sql = 'insert into {} (username, result,version) values(%s,%s,%s)'.format(table)
					data = (username, res, version)
					cur.execute(sql, data)
					db_conn.commit()
					break
				except Exception as e:
					print e
					cur.execute('rollback;')
		except Exception as e:
			error_log = ErrorLog(search_key[0])
			
			error_log.error_log('run logdb insert errro: ' + e)
		time.sleep(2)