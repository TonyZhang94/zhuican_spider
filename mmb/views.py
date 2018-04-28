# -*- coding: utf-8 -*-
import time
import json
import psycopg2
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from mmb_customized.mmb_api_parse import mmb_api_parse
from tools.write_log import OperationLog, ErrorLog, RunLog
from .tasks import words_run
from .tasks import models_run
from tools import db_params
from tools.websocket import websocket


operation_log = OperationLog()

search_keys_models = list()
mmb_api_parse = mmb_api_parse()
now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def index(request):  # 慢慢买主页
	cookie = request.COOKIES.get('name')
	if cookie:
		return render(request, 'mmb_index.html')
	else:
		return redirect('login/')


def mmb_round(request):  # 慢慢买循环跑
	# return render(request, 'mmb_round.html')
	cookie = request.COOKIES.get('name')
	if cookie:
		return HttpResponse('mmb_round')
	else:
		return redirect('login/')


def mmb_model4(request):  # 慢慢买模式4页面
	cookie = request.COOKIES.get('name')
	print 'model4', cookie
	if cookie:
		return render(request, 'mmb_model4.html')
	else:
		return redirect('login/')


def mmb_model5(request):  # 慢慢买模式5页面
	cookie = request.COOKIES.get('name')
	if cookie:
		return render(request, 'mmb_model5.html')
	else:
		return redirect('login/')


def designed_words(request):  # 处理定制words
	username = request.COOKIES.get('name')
	text = request.POST.get('text')
	version = request.POST.get('version')
	table = request.POST.get('table')
	print 'version', version
	key_type = 'words'
	# operation_log.operation_log('=' * 30 + '指定{}:'.format(key_type) + '=' * 30)
	operation_log.operation_log(data=(username, text, version))
	search_keys_words = list()
	for t in text.split('\n'):
		search_keys_words.append(t)
	search_key_sum = len(search_keys_words)
	try:
		
		words_run.delay(search_keys_words, version, table, username)
		search_keys_words = list()
		return JsonResponse({'search_key_sum': search_key_sum, 'status': '0'})
	except Exception as e:
		
		print e
		return JsonResponse({'search_key_sum': '0', 'status': '1'})


def designed_models(request):  # 处理定制models
	username = request.COOKIES.get('name')
	text = request.POST.get('text')
	version = request.POST.get('version')
	table = request.POST.get('table')
	key_type = 'models'
	operation_log.operation_log('=' * 30 + '指定{}:'.format(key_type) + '=' * 30)
	operation_log.operation_log(data=(username, text, version))
	# print 'text', text
	search_keys_models = list()
	for t in text.split('\n'):
		search_keys_models.append(t)
	search_key_sum = len(search_keys_models)
	print 'models', search_keys_models
	try:
		
		models_run.delay(search_keys_models, version, table, username)
		search_keys_words = list()
		return JsonResponse({'search_key_sum': search_key_sum, 'status': '0'})
	except Exception as e:
		
		print e
		return JsonResponse({'search_key_sum': '0', 'status': '1'})


# 查询数据库 返回数据库中数据显示在前端页面中
def show_pro(request):
	table = request.GET.get('table')
	version = request.GET.get('version')
	print 'show_pro type', (version, type(version))
	db_conn = psycopg2.connect(host=db_params.PG_SERVER_HOST, port=db_params.PG_SERVER_PORT, password=
	db_params.PG_SERVER_PASS, user=db_params.PG_SERVER_USER, database='chu')
	print 'conn success'
	cur = db_conn.cursor()
	while 1:
		
		sql = "select result from {table} where version='{version}'".format(table=table, version=version)
		cur.execute(sql)
		res = cur.fetchall()
		print res
		break
	res_list = list()
	for r in res:
		res_list.append(r[0])
	i = len(res_list)
	print 'i', i
	return JsonResponse({'res_list': res_list, 'i': i})
