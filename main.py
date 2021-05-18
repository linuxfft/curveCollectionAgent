import aiohttp
import os
import sys
import traceback
import asyncio
from typing import Dict
import pprint
import http
import logging
from urllib import parse
from aiohttp import web
from aiojobs.aiohttp import setup, spawn
from loguru import logger

logger.add("logs/curve_collection_agent.log", rotation="1 days", level="INFO", encoding='utf-8')  # 文件日誌

DEFAULT_LOG_FORMAT = '%a %t "%r" %s %b "%{Referer}i" "%{User-Agent}i" %D'  # 最后是耗时(微秒)

ENV_AIRFLOW_BASE_URL = os.getenv('ENV_AIRFLOW_BASE_URL', 'http://localhost:8080')

METHOD_DICT = {
    'post_curve': {
        'method': 'post',
        'url': 'dag_run'
    }
}

schema = {
    "result": [
        {
            "name": "TimeMin_T",  # 字段数值
            "i18n_name": "最小时间",  # 中文翻译
            "value": 0.0  # 数据，以实际类型显示,
        },
        {
            "name": "TimeMin_X",  # 字段数值
            "i18n_name": "最小时间X",  # 中文翻译
            "value": 0.13123  # 数据，以实际类型显示,
        },
    ],
    "curve": {
        "force": [0.11, 0.12],  # 力
        "time": [0.005, 0.01],  # 时间
        "distance": [0.2, 0.3],  # 行程
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


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error(tb)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = web.Application()
    app.add_routes([web.get('/', curveCollectionhandle),
                    web.post('/curves', postCurveCollectionhandle),
                    web.get('/healthz', healthzCheckHandler)])

    sys.excepthook = excepthook

    web.run_app(app, host='0.0.0.0', port=8080, access_log=logger)
