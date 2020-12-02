from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import HttpResponseNotFound, JsonResponse
from .models import *
from logview.models import DnsLog,WebLog,UserSubDomain
from dnslog.settings import FAST_USERID, FAST_API_TOKEN
from django_redis import get_redis_connection
import pickle

cache = get_redis_connection('default')


# Create your views here.
def weblog(request, apikey, hashstr):
	user = ApiKey.objects.filter(key=apikey)
	if user:
		weblogs = WebLog.objects.filter(user=user[0].user).filter(path__contains=hashstr)
		data = []
		ret = {}
		if weblogs:
			for weblogi in weblogs:
				data.append({'path': weblogi.path, 'ip': weblogi.ip, 'header': weblogi.header, 'body': weblogi.body})
			ret = {'status': 1, 'msg': '', 'total': len(weblogs), 'data': data}
		else:
			ret = {'status': 1, 'msg': '', 'total': 0, 'data': []}
	else:
		ret = {'status': -1, 'msg': 'api key not found!'}
	return JsonResponse(ret)


def dnslog(request, apikey, hashstr):
	hashstr +='.'

	if apikey == FAST_API_TOKEN:
		dnslogs = cache.keys(f'{hashstr}_*')
		data = []
		if dnslogs:
			for dnslogi in dnslogs:
				dnslogi = cache.get(dnslogi)
				dnslogi = pickle.loads(dnslogi)
				data.append({'host':dnslogi.host, 'ip':dnslogi.ip, 'log_time':dnslogi.log_time})
				ret = {'status': 1, 'msg': '', 'total': len(data), 'data': data}
			return JsonResponse(ret)
		else:
			ret = {'status': 1, 'msg': '', 'total': 0, 'data': data}
			return JsonResponse(ret)

	else:
		user = ApiKey.objects.filter(key=apikey)
		if user:
			dnslogs = DnsLog.objects.filter(user=user[0].user).filter(host__contains=hashstr)
			# dnslogs = DnsLog.objects.filter(user=user_id).filter(host=hashstr+'.')
			data = []
			if dnslogs:
				for dnslogi in dnslogs:
					data.append({'host': dnslogi.host, 'log_time': dnslogi.log_time})
				ret = {'status': 1, 'msg': '', 'total': len(data), 'data': data}
			else:
				ret = {'status': 1, 'msg': '', 'total': 0, 'data': data}
		else:
			ret = {'status': -1, 'msg': 'api key not found!'}
		return JsonResponse(ret)



def clear(request, apikey):
	user = ApiKey.objects.filter(key=apikey)
	if user:
		DnsLog.objects.filter(user=user[0].user).delete()
		WebLog.objects.filter(user=user[0].user).delete()
		ret = {'status': 1, 'msg': ''}
	else:
		ret = {'status': -1, 'msg': 'api key not found!'}
	return JsonResponse(ret)




def notfound(request):
	return HttpResponseNotFound('<h1>Page not found</h1>')
