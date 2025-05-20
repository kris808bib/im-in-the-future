import requests
import json
import time
from config import API_CONFIG

class ApiHandler:
    def __init__(self):
        self.API_URL = API_CONFIG["API_URL"]
        self.API_KEY = API_CONFIG["API_KEY"]
        self.SECRET_KEY = API_CONFIG["SECRET_KEY"]
        self.pipeline_id = None
        self.cancel_flag = False
        self.connect_to_api()

    def connect_to_api(self):
        try:
            headers = self._get_auth_headers()
            response = requests.get(f"{self.API_URL}key/api/v1/pipelines", headers=headers)
            self.pipeline_id = response.json()[0]['id']
        except Exception as e:
            raise ConnectionError(f"API connection failed: {str(e)}")

    def generate_image(self, prompt):
        if not self.pipeline_id:
            raise ValueError("API not connected")
        try:
            params = {
                "type": "GENERATE",
                "numImages": 1,
                "style": "ANIME",
                "width": 1024,
                "height": 1024,
                "generateParams": {"query": prompt}
            }
            
            data = {
                'pipeline_id': (None, self.pipeline_id),
                'params': (None, json.dumps(params), 'application/json'), 
            }
            
            response = requests.post(
                f"{self.API_URL}key/api/v1/pipeline/run",
                headers=self._get_auth_headers(),
                files=data
            )
            # print(response)
            task_id = response.json()['uuid']
            # print(task_id)
            for _ in range(15):
                if self.cancel_flag:
                    raise InterruptedError("Generation cancelled")
                
                status = self._check_status(task_id)
                # print(status['status'])
                if status['status'] == 'DONE':
                    return status['result']['files'][0]
                elif status['status'] == 'FAIL':
                    raise RuntimeError("Image generation failed")
                
                time.sleep(10)
            
            raise TimeoutError("Generation timeout (150 seconds)")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error: {str(e)}")

    def _check_status(self, task_id):
        response = requests.get(
            f"{self.API_URL}key/api/v1/pipeline/status/{task_id}",
            headers=self._get_auth_headers()
        )
        return response.json()

    def _get_auth_headers(self):
        return {
            'X-Key': f'Key {self.API_KEY}',
            'X-Secret': f'Secret {self.SECRET_KEY}',
        } 
