# -*- coding: utf-8 -*-
# 写日志
import time
import os
import sys
import db_params
import psycopg2
reload(sys)
sys.setdefaultencoding('utf-8')

now_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
h_time = time.strftime('%Y%m%d%H', time.localtime(time.time()))
DIR = "C:\\Users\\null\\Desktop\\zcspider\\log\\"
pg_conn = psycopg2.connect(host=db_params.PG_SERVER_HOST, port=db_params.PG_SERVER_PORT, user=db_params.PG_SERVER_USER,
                           password=db_params.PG_SERVER_PASS, database='chu')
cur = pg_conn.cursor()
# FILE_NAME = '{}'+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


class OperationLog(object):
	"""操作日志 以操作时间为文件名"""
	def __init__(self):
		self.file_dir = ''
	
	def operation_log(self, data):
		self.file_dir = DIR + 'operation_log'
		file_name = h_time
		with open(os.path.join(self.file_dir, file_name + '.txt'), 'ab') as f:
			f.write(now_time)
			f.write('\n')
			f.write(data)
			f.write('\n')
		i = 0
		while 1:
			try:
				sql = 'insert into {} (username, work, datamonth) values(%s, %s, %s)'.format('public.operation_log')
				cur.execute(sql, data)
				pg_conn.commit()
				break
			except Exception as e:
				i += 1
				if i > 5:
					err = ErrorLog('oprro')
					err.error_log('死活存不进去:'+data)
					break

				print e
				print 'operation log insert error'
				cur.execute('rollback;')
			
			

class RunLog(object):
	"""运行日志"""
	def __init__(self, cid):
		self.file_dir = ''
		self.file_dir = DIR + 'run_log'
		file_name = str(cid)
		self.f = open(os.path.join(self.file_dir, file_name + '.txt'), 'ab')
		
	def write_title(self, title):
		self.f.write('='*30+title+'='*30)
		self.f.write('\n')
		
	def run_log(self, string):
		
		self.f.write(now_time)
		self.f.write(string)
		self.f.write('\n')
		
		
class ErrorLog(object):
	"""错误日志"""
	def __init__(self, title):
		self.file_dir = ''
		self.file_dir = DIR + 'error_log'
		file_name = str(title)
		self.f = open(os.path.join(self.file_dir, file_name + '.txt'), 'ab')

	def error_log(self, string):
		
		self.f.write(now_time)
		self.f.write(string)
		self.f.write('\n')