import io
import json
from os import PathLike
from typing import Optional

from litellm.types.llms.openai import FileTypes, OpenAIFilesPurpose


class InMemoryFile(io.BytesIO):
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


def should_replace_model_in_jsonl(
    purpose: OpenAIFilesPurpose,
) -> bool:
    """
    Check if the model name should be replaced in the JSONL file for the deployment model name.

    Azure raises an error on create batch if the model name for deployment is not in the .jsonl.
    """
    # Accept enums, strings, or objects with name/value attributes. Normalize to string
    try:
        if hasattr(purpose, "value"):
            val = purpose.value
        elif hasattr(purpose, "name"):
            val = purpose.name
        else:
            val = str(purpose)
        return str(val).lower() == "batch"
    except Exception:
        return False


def replace_model_in_jsonl(file_content: FileTypes, new_model_name: str) -> FileTypes:
    try:
        original_name: str | None = None

        # If given a path (str or PathLike), read the file bytes
        if isinstance(file_content, PathLike) or isinstance(file_content, str):
            path_str = str(file_content)
            # derive a file name without importing os
            original_name = path_str.replace("\\", "/").split("/")[-1] or "modified_file.jsonl"
            with open(path_str, "rb") as f:
                file_content_bytes = f.read()

        # If file-like object, read bytes and try to preserve the original name
        elif hasattr(file_content, "read"):
            original_name = getattr(file_content, "name", None)
            # read and then reset stream position if possible
            file_content_bytes = file_content.read()  # type: ignore
            try:
                if hasattr(file_content, "seek"):
                    file_content.seek(0)
            except Exception:
                pass

        # If tuple, expect (name, bytes_or_fileobj)
        elif isinstance(file_content, tuple):
            if len(file_content) >= 2:
                original_name = str(file_content[0])
                payload = file_content[1]
                if hasattr(payload, "read"):
                    file_content_bytes = payload.read()
                else:
                    file_content_bytes = payload
            else:
                return file_content

        else:
            file_content_bytes = file_content

        # Decode the bytes to a string
        if isinstance(file_content_bytes, bytes):
            file_content_str = file_content_bytes.decode("utf-8")
        elif isinstance(file_content_bytes, str):
            file_content_str = file_content_bytes
        else:
            # Unknown type: don't attempt to modify
            return file_content

        lines = file_content_str.splitlines()
        modified_lines = []
        for line in lines:
            # Parse each line as a JSON object
            if not line.strip():
                continue
            json_object = json.loads(line.strip())

            # Replace the model name if it exists
            if "body" in json_object and isinstance(json_object["body"], dict):
                json_object["body"]["model"] = new_model_name

            # Convert the modified JSON object back to a string
            modified_lines.append(json.dumps(json_object))

        # Reassemble the modified lines and return as bytes
        modified_file_content = "\n".join(modified_lines).encode("utf-8")

        # Preserve return shape: if input was a tuple, return (name, bytes)
        if isinstance(file_content, tuple):
            return (original_name or "modified_file.jsonl", modified_file_content)

        # For path/str/file-like inputs, return an InMemoryFile with the original name if available
        return InMemoryFile(modified_file_content, name=(original_name or "modified_file.jsonl"))  # type: ignore

    except (json.JSONDecodeError, UnicodeDecodeError):
        # return the original file content if there is an error replacing the model name
        return file_content


def _get_router_metadata_variable_name(function_name: Optional[str]) -> str:
    """
    Helper to return what the "metadata" field should be called in the request data

    For all /thread or /assistant endpoints we need to call this "litellm_metadata"

    For ALL other endpoints we call this "metadata
    """
    ROUTER_METHODS_USING_LITELLM_METADATA = set(
        ["batch", "generic_api_call", "_acreate_batch", "file"]
    )
    if function_name and any(
        method in function_name for method in ROUTER_METHODS_USING_LITELLM_METADATA
    ):
        return "litellm_metadata"
    else:
        return "metadata"
