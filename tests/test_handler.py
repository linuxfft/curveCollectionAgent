from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from utils.app import create_web_app
import http
import json

class Test(AioHTTPTestCase):
    async def get_application(self):
        """
        Override the get_app method to return your application.
        """

        app = create_web_app()
        return app

    @unittest_run_loop
    async def test_healthz_check_handler(self):
        resp = await self.client.request("GET", "/healthz")
        assert resp.status == http.HTTPStatus.NO_CONTENT

    @unittest_run_loop
    async def test_post_curve_collectionhandle(self):
        # todo: mock data
        # mock_data = {
        #     "result": [
        #         {
        #             "name": "TimeMin_T",
        #             "i18n_name": "最小时间",
        #             "value": 0.0
        #         },
        #         {
        #             "name": "TimeMin_X",
        #             "i18n_name": "最小时间X",
        #             "value": 0.13123
        #         }
        #     ],
        #     "curve": {
        #         "force": [0.11, 0.12],
        #         "time": [0.005, 0.01],
        #         "distance": [0.2, 0.3]
        #     }
        # }
        mock_data = {}
        with open("demo_data.json", 'r') as load_f:
            mock_data = json.load(load_f)
        resp = await self.client.post("/curves", json=mock_data)
