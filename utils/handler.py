import json
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
        'url': 'dag_runs'
    }
}


async def doPushCurve2Airflow(data):
    async with aiohttp.ClientSession() as session:
        dt: Dict = METHOD_DICT.get('post_curve', {})
        mm = dt.get('method')
        m = getattr(session, mm)
        post_curve_url = parse.urljoin(ENV_AIRFLOW_BASE_URL, dt.get('url', ''))
        async with m(post_curve_url, data=data) as resp:
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

    measure_result = ""
    entity_id = ""
    for item_result in result_content:
        if item_result.get("name") == "IsPass":
            measure_result = "OK" if item_result.get("value") else "NOK"
        if item_result.get("name") == "BarCade":
            entity_id = item_result.get("value")

    cur_m = curve_content.get("force")
    cur_w = curve_content.get("distance")
    cur_t = curve_content.get("time")
    measure_torque = cur_m[-1]
    measure_angle = cur_w[-1]
    measure_time = cur_t[-1]

    airflow_data = {
      "replace_microseconds": 'false',
      "conf": {
        "entity_id": entity_id,
        "result": {
          "measure_result": measure_result,
          "measure_torque": measure_torque,
          "measure_angle": measure_angle,
          "measure_time": measure_time,
          "batch": '',
          "count": 1,
          "job": 1,
          "controller_sn": "",
          "controller_name": "CA-09R4",
          "pset": 1,
          "program": 1
        },
        "curve": {
          "cur_m": cur_m,
          "cur_w": cur_w,
          "cur_t": cur_t
        },
      }
    }
    # logger.debug("收到曲线数据: {}".format(pprint.pformat(data, indent=4)))
    resp = await doPushCurve2Airflow(json.dumps(airflow_data, ensure_ascii=False))
    return web.Response(text=resp)
