# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from tools import user
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required


def index(request):
	username = request.COOKIES.get('name')
	print username
	# print user
	return render(request, 'index.html', {'username': username})


def login(request):
	if request.method == 'GET':
		return render(request, 'login.html')
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('pwd')
		res = user.val_user(username, password)
		jsonresp = JsonResponse({'status': res})
		print res
		jsonresp.set_cookie('name', value=username, max_age=60*60*24*2)
		return jsonresp


def register(request):
	if request.method == 'GET':
		return render(request, 'login.html')
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('pwd')
		res = user.insert_user(username, password)
		print res
		return JsonResponse({'status': res})


def test1(request):
	return render(request, 'test.html')
