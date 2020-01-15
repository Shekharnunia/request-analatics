import json

from .models import WebRequest

from celery.decorators import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)



def dumps(value):
    return json.dumps(value,default=lambda o:None)


@task(name="save_request")
def save_request(method, content_length, content_type, headers, user_id, user_agent, cookies, host, status_code, path, uri, get, client_ip):
    WebRequest(
            method = method,
            content_length = content_length,
            content_type = content_type,
            headers = headers,
            get = get,
            user_id = user_id,
            user_agent = user_agent,
            cookies = cookies,
            host = host,
            status_code = status_code,
            path = path,
            uri = uri,
            client_ip = client_ip
        ).save()

    logger.info("Request Successfully saved")
    return 1