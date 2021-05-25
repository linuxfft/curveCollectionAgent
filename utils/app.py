from aiohttp import web
from utils.handler import curveCollectionhandle, postCurveCollectionhandle, healthzCheckHandler


def create_web_app() -> web.Application:
    # loop = asyncio.get_event_loop()
    ret: web.Application = web.Application(client_max_size=1024 * 1024 * 10)
    ret.add_routes([web.get('/', curveCollectionhandle),
                    web.post('/curves', postCurveCollectionhandle),
                    web.get('/healthz', healthzCheckHandler)])

    return ret
