from aiohttp import web
import aiohttp
from typing import Dict
import pprint
import http
import os
from urllib import parse
from loguru import logger

ENV_AIRFLOW_BASE_URL = os.getenv('ENV_AIRFLOW_BASE_URL', 'http://localhost:8080')

METHOD_DICT = {
    'post_curve': {
        'method': 'post',
        'url': 'dag_run'
    }
}


async def doPushCurve2Airflow():
    async with aiohttp.ClientSession() as session:
        dt: Dict = METHOD_DICT.get('post_curve', {})
        mm = dt.get('method')
        m = getattr(session, mm)
        post_curve_url = parse.urljoin(ENV_AIRFLOW_BASE_URL, dt.get('url', ''))
        async with m(post_curve_url) as resp:
            txt = await resp.text(encoding='utf-8')
            logger.info("推送曲线: {}, payload: {}".format(resp.status, txt))
            return txt


async def postCurveCollectionhandle(request):
    data = await curveCollectionhandle(request)
    return data


async def healthzCheckHandler(request):
    return web.Response(status=http.HTTPStatus.NO_CONTENT)


async def curveCollectionhandle(request):
    data: Dict = await request.json()
    result_content = data.get('result', '')
    curve_content = data.get('curve', '')
    logger.debug("收到曲线数据: {}".format(pprint.pformat(data, indent=4)))
    resp = await doPushCurve2Airflow()
    return web.Response(text=resp)
