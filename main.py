import os
import sys
import traceback
from aiohttp import web
from utils.app import create_web_app
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


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error(tb)


if __name__ == '__main__':
    app = create_web_app()
    sys.excepthook = excepthook

    web.run_app(app, host='0.0.0.0', port=8080, access_log=logger)
