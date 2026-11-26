"""
Mistral chat completion handler

For handling Mistral chat completions using the newer llm_http_handler pattern.
"""

from typing import Optional
from litellm.llms.custom_httpx.llm_http_handler import BaseLLMHTTPHandler
from litellm.llms.mistral.mistral_chat_transformation import MistralConfig
from litellm.types.utils import ModelResponse

base_llm_http_handler = BaseLLMHTTPHandler()


def completion(
    model: str,
    messages: list,
    api_base: str,
    custom_llm_provider: str,
    model_response: ModelResponse,
    encoding,
    logging_obj,
    optional_params: dict,
    timeout,
    litellm_params: dict,
    acompletion: bool,
    stream: Optional[bool] = False,
    fake_stream: bool = False,
    api_key: Optional[str] = None,
    headers: Optional[dict] = None,
    client=None,
    **kwargs,
):
    """
    Handle Mistral chat completions using the newer llm_http_handler pattern.
    """
    # Create Mistral config for transformations
    provider_config = MistralConfig()
    
    # Get the API base and key from the config. The provider helper may return
    # either a tuple (api_base, api_key) or a single api_base value depending
    # on its implementation/annotations, so handle both cases safely.
    result = provider_config._get_openai_compatible_provider_info(
        api_base=api_base, api_key=api_key
    )
    if isinstance(result, (tuple, list)) and len(result) >= 2:
        api_base, api_key = result[0], result[1]
    else:
        # If only api_base was returned, keep/override api_base and leave api_key
        # as provided (or None). Use the returned value as api_base.
        api_base = result
    
    # Use the base handler for the actual HTTP calls
    return base_llm_http_handler.completion(
        model=model,
        messages=messages,
        api_base=api_base,
        custom_llm_provider=custom_llm_provider,
        model_response=model_response,
        encoding=encoding,
        logging_obj=logging_obj,
        optional_params=optional_params,
        timeout=timeout,
        litellm_params=litellm_params,
        acompletion=acompletion,
        stream=stream,
        fake_stream=fake_stream,
        api_key=api_key,
        headers=headers,
        client=client,
        provider_config=provider_config,  # Pass the Mistral config for transformations
        **kwargs,
    )


async def acompletion(
    model: str,
    messages: list,
    api_base: str,
    custom_llm_provider: str,
    model_response: ModelResponse,
    encoding,
    logging_obj,
    optional_params: dict,
    timeout,
    litellm_params: dict,
    stream: Optional[bool] = False,
    fake_stream: bool = False,
    api_key: Optional[str] = None,
    headers: Optional[dict] = None,
    client=None,
    provider_config: Optional[MistralConfig] = None,
):
    """
    Async Mistral completion using the newer llm_http_handler pattern.
    """
    if provider_config is None:
        provider_config = MistralConfig()
    
    # Ensure headers is a dict (avoid mutable default and satisfy Optional type)
    headers = headers or {}

    return await base_llm_http_handler.async_completion(
        custom_llm_provider=custom_llm_provider,
        provider_config=provider_config,
        api_base=api_base,
        headers=headers,
        data={},  # Will be set by transform_request
        timeout=timeout,
        model=model,
        model_response=model_response,
        logging_obj=logging_obj,
        messages=messages,
        optional_params=optional_params,
        litellm_params=litellm_params,
        encoding=encoding,
        api_key=api_key,
        client=client,
    ) 
