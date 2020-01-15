import sys
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse

from .models import WebRequest
from .tasks import save_request


def dumps(value):
    return json.dumps(value,default=lambda o:None)


def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)
    return headers
    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class CustomDebugMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        setattr(request,'hide_post',view_kwargs.pop('hide_post',False))

    # def process_view(self, request, callback, callback_args, callback_kwargs):
    #     webrequest = WebRequest(title=request.headers)
        # webrequest.save()

    def process_template_response(self, request, response):
        user_agent = request.META.get("HTTP_USER_AGENT", None)
        cookies = request.META.get("HTTP_COOKIE", None)
        host = request.META.get("HTTP_HOST", None)
        status_code = response.status_code
        path = request.path
        uri = request.build_absolute_uri()
        client_ip = get_client_ip(request)


        method =  '{method} HTTP/1.1\n'.format(method=request.method)
        content_length = 'Content-Length: {content_length}\n'.format(content_length=request.META['CONTENT_LENGTH'])
        content_type = 'Content-Type: {content_type}\n'.format(content_type=request.META['CONTENT_TYPE'])
        headers = '{headers}\n\n'.format(headers=pretty_request(request))
        get = request.GET
        user = request.user.id if request.user.is_authenticated else None

        save_request.delay(method, content_length, content_type, headers, user, user_agent, cookies, host, status_code, path, uri, get, client_ip)
        return response

    #     if request.path.endswith('/favicon.ico'):
    #         return response

    #     if type(response) == HttpResponsePermanentRedirect and settings.APPEND_SLASH:
    #         new_location = response.get('location',None)
    #         content_length = response.get('content-length',None)

    #         if new_location and content_length is '0':
    #             new_parsed = urlparse(new_location)

    #             old = (('http','https')[request.is_secure()], request.get_host(), '{0}/'.format(request.path), request.META['QUERY_STRING'])
    #             new = (new_parsed.scheme, new_parsed.netloc, new_parsed.path, new_parsed.query)

    #             if old == new:
    #                 #dont log - it's just adding a /
    #                 return response
    #     try:
    #         self.save(request, response)
    #     except Exception as e:
    #         print(sys.stderr, "Error saving request log", e)

    #     return response

    # def save(self, request, response):
    #     if hasattr(request, 'user'):
    #         user = request.user if request.user.is_authenticated else None
    #     else:
    #         user = None

    #     meta = request.META.copy()
    #     meta.pop('QUERY_STRING',None)
    #     meta.pop('HTTP_COOKIE',None)
    #     remote_addr_fwd = None

    #     if 'HTTP_X_FORWARDED_FOR' in meta:
    #         remote_addr_fwd = meta['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()
    #         if remote_addr_fwd == meta['HTTP_X_FORWARDED_FOR']:
    #             meta.pop('HTTP_X_FORWARDED_FOR')

    #     post = None
    #     uri = request.build_absolute_uri()
    #     ignore_urls = (reverse("login"), reverse('logout'), reverse('password_change'), reverse('password_change_done'), reverse('password_reset'), reverse('password_reset_done'), reverse('password_reset_complete'))
    #     if request.POST and not uri.endswith(ignore_urls):
    #         post = dumps(request.POST)
    #     user_agent = meta.pop('HTTP_USER_AGENT',None),
    #     remote_addr = meta.pop('REMOTE_ADDR',None),

    #     transaction.on_commit(lambda: save_request.delay(
    #         host = request.get_host(),
    #         path = request.path,
    #         method = request.method,
    #         uri = request.build_absolute_uri(),
    #         status_code = response.status_code,
    #         user_agent = user_agent,
    #         remote_addr = remote_addr,
    #         remote_addr_fwd = remote_addr_fwd,
    #         get = request.GET,
    #         is_secure = request.is_secure(),
    #         is_ajax = request.is_ajax(),
    #         user = user.id
    #     ))
