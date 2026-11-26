"""
Helper functions to handle images passed in messages
"""

import base64

from httpx import Response

import litellm
from litellm import verbose_logger
from litellm.caching.caching import InMemoryCache

MAX_IMGS_IN_MEMORY = 10

in_memory_cache = InMemoryCache(max_size_in_memory=MAX_IMGS_IN_MEMORY)


def _process_image_response(response: Response, url: str) -> str:
    # Accept a range of successful status codes and be tolerant of different client response attributes
    status = getattr(response, "status_code", None)
    if status is None:
        status = getattr(response, "status", None)

    if status is not None and not (200 <= int(status) < 300):
        raise Exception(
            f"Error: Unable to fetch image from URL. Status code: {status}, url={url}"
        )

    image_bytes = response.content
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    image_type = response.headers.get("Content-Type")
    if image_type is None:
        img_type = url.split(".")[-1].lower()
        _img_type = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }.get(img_type)
        if _img_type is None:
            raise Exception(
                f"Error: Unsupported image format. Format={img_type}. Supported types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']"
            )
        img_type = _img_type
    else:
        img_type = image_type

    result = f"data:{img_type};base64,{base64_image}"
    in_memory_cache.set_cache(url, result)
    return result


async def async_convert_url_to_base64(url: str) -> str:
    cached_result = in_memory_cache.get_cache(url)
    if cached_result:
        return cached_result

    # Be robust to a few possible module-level attribute names for the async client
    client = (
        getattr(litellm, "module_level_async_client", None)
        or getattr(litellm, "module_level_acclient", None)
        or getattr(litellm, "module_level_ac_client", None)
        or getattr(litellm, "module_level_aclient", None)
        or getattr(litellm, "module_level_client", None)
    )
    if client is None:
        raise Exception("Error: No module-level async client available to fetch the URL.")

    for _ in range(3):
        try:
            response = await client.get(url, follow_redirects=True)
            return _process_image_response(response, url)
        except Exception:
            pass
    raise Exception(
        f"Error: Unable to fetch image from URL after 3 attempts. url={url}"
    )


def convert_url_to_base64(url: str) -> str:
    cached_result = in_memory_cache.get_cache(url)
    if cached_result:
        return cached_result

    client = getattr(litellm, "module_level_client", None) or getattr(litellm, "module_level_sync_client", None)
    if client is None:
        raise Exception("Error: No module-level client available to fetch the URL.")

    for _ in range(3):
        try:
            response = client.get(url, follow_redirects=True)
            return _process_image_response(response, url)
        except Exception as e:
            try:
                # Guard against logging errors (e.g., closed handlers) during tests
                verbose_logger.exception(e)
            except Exception:
                pass
            # print(e)
            pass
    raise Exception(
        f"Error: Unable to fetch image from URL after 3 attempts. url={url}"
    )
