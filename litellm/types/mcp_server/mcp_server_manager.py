from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from litellm.proxy._types import MCPAuthType, MCPTransportType

# MCPInfo now allows arbitrary additional fields for custom metadata
MCPInfo = Dict[str, Any]

class MCPOAuthMetadata(BaseModel):
    scopes: List[str] = []
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    registration_url: Optional[str] = None

class MCPServer(BaseModel):
    server_id: str
    name: str
    alias: Optional[str] = None
    server_name: Optional[str] = None
    url: Optional[str] = None
    transport: MCPTransportType
    spec_path: Optional[str] = None
    auth_type: Optional[MCPAuthType] = None
    authentication_token: Optional[str] = None
    mcp_info: Optional[MCPInfo] = None
    extra_headers: Optional[
        List[str]
    ] = None  # allow admin to specify which headers to forward from client to the MCP server
    allowed_tools: List[str] = []
    disallowed_tools: List[str] = []
    allowed_params: Dict[str, List[str]] = {}
    static_headers: Dict[str, str] = {}
    # OAuth-specific fields
    client_id: str = ""
    client_secret: str = ""
    scopes: Optional[List[str]] = None
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    registration_url: Optional[str] = None
    # Stdio-specific fields
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    access_groups: Optional[List[str]] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)
