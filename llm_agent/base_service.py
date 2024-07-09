import os
import json
import requests
import uuid
from linkinpark.lib.common.logger import getLogger
from linkinpark.lib.common.secret_accessor import SecretAccessor
from langchain_community.llms import HuggingFaceEndpoint

APP_ENV = os.environ.get("APP_ENV", "dev")
SERVICE_LOGGER = getLogger(name="ai-llm-service", labels={"env": APP_ENV})

class BaseService:
    def __init__(self, service_name: str, llm_source: str = 'local', **kwargs):
        self.llm_source = llm_source
        self.generation_params = kwargs
        self.service_name = service_name
        self.service_id = uuid.uuid4().hex
        self.llm = HuggingFaceEndpoint(**self.generation_params)
        self.auth_token = self._get_token()
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.llm.client.headers = self.auth_headers
        self._log_service()

    def _get_token(self):
        url = "https://ai-model-dev.jubo.health/api/v1/get-token"
        username = SecretAccessor().access_secret('local-gpu-username')
        password = SecretAccessor().access_secret('local-gpu-password')
        data = {"username": username, "password": password}
        response = requests.post(url, data=json.dumps(data))
        return response.json()['token']

    def _log_service(self):
        llm_info_request = requests.get(
            url=self.generation_params['endpoint_url'] + '/info',
            headers=self.auth_headers
        )
        llm_info = llm_info_request.json()
        SERVICE_LOGGER.info({
            "message": f"initialized new local service: {self.service_name}",
            "metrics": {"called": 1},
            "labels": {
                'service_id': self.service_id,
                'service_name': self.service_name,
                'llm_source': self.llm_source,
                'llm_info': json.dumps(llm_info),
                'generation_params': json.dumps(self.generation_params)
            }
        })
