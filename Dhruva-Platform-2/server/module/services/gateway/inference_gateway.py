import traceback
from typing import Any
import os
from urllib.parse import urlparse

import gevent.ssl
import requests
import tritonclient.http as http_client
from exception.base_error import BaseError
from fastapi.logger import logger
from numpy import block

from ..error import Errors
from ..model import Service


class InferenceGateway:
    def __init__(self):
        # Get Triton endpoint from environment variable or use default
        triton_endpoint_raw = os.getenv("TRITON_ENDPOINT", "http://localhost:8000")
        # Store the raw endpoint for logging, but we'll parse it when needed
        self.triton_endpoint = triton_endpoint_raw
        self.use_aws_triton = os.getenv("USE_AWS_TRITON", "false").lower() == "true"
        logger.info(f"Initialized InferenceGateway with Triton endpoint: {self.triton_endpoint}")

    def send_inference_request(
        self,
        request_body: Any,
        service: Service,
    ) -> dict:
        try:
            response = requests.post(service.endpoint, json=request_body.dict())
        except:
            raise BaseError(Errors.DHRUVA101.value, traceback.format_exc())

        if response.status_code >= 400:
            raise BaseError(Errors.DHRUVA102.value)

        return response.json()

    def send_inference_request_dict(
        self,
        request_body: dict,
        service: Service,
    ) -> dict:
        try:
            response = requests.post(service.endpoint, json=request_body)
        except:
            raise BaseError(Errors.DHRUVA101.value, traceback.format_exc())

        if response.status_code >= 400:
            raise BaseError(Errors.DHRUVA102.value)

        return response.json()

    def send_triton_request(
        self,
        url: str,
        headers: dict,
        model_name: str,
        input_list: list,
        output_list: list,
    ):
        try:
            # Use AWS Triton endpoint if configured
            endpoint = self.triton_endpoint if self.use_aws_triton else url
            
            # Triton client requires URL without scheme (e.g., "host:port" not "http://host:port")
            # Parse and extract host:port if URL contains scheme
            if endpoint.startswith(("http://", "https://")):
                parsed = urlparse(endpoint)
                if parsed.port:
                    endpoint = f"{parsed.hostname}:{parsed.port}"
                elif parsed.hostname:
                    # Use hostname only if no port specified (Triton will use default)
                    endpoint = parsed.hostname
                else:
                    endpoint = endpoint.split("://", 1)[1]  # Fallback: just remove scheme
            elif "://" in endpoint:
                # Handle other schemes by removing them
                endpoint = endpoint.split("://", 1)[1]
            
            logger.info(f"Using Triton endpoint: {endpoint} for model: {model_name}")

            triton_client = http_client.InferenceServerClient(
                url=endpoint,
                ssl=False,
                ssl_context_factory=gevent.ssl._create_default_https_context,  # type: ignore
                concurrency=20,
            )

            # Check server health
            try:
                health_ctx = triton_client.is_server_ready(headers=headers)
                logger.info(f"Triton server health check: {health_ctx}")
                if not health_ctx:
                    raise BaseError(Errors.DHRUVA107.value, "Triton server is not ready")
            except Exception as e:
                logger.error(f"Failed to check Triton server health: {str(e)}")
                # Continue anyway as the server might still be usable

            response = triton_client.async_infer(
                model_name,
                model_version="1",
                inputs=input_list,
                outputs=output_list,
                headers=headers,
            )
            response = response.get_result(block=True, timeout=20)

        except Exception as e:
            logger.error(f"Triton inference failed: {str(e)}")
            raise BaseError(Errors.DHRUVA101.value, traceback.format_exc())

        return response
