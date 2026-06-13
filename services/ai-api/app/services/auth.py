from __future__ import annotations

import hashlib
import hmac
from typing import Optional

from fastapi import Header, HTTPException

from app.config import settings
from app.services import persistence


def hash_api_key(api_key: str) -> str:
    return hmac.new(
        settings.api_key_hash_secret.encode("utf-8"),
        api_key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def get_tenant_from_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header.")

    tenant = persistence.get_tenant_by_api_key_hash(hash_api_key(x_api_key))
    if tenant is None:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    if tenant.status != "active":
        raise HTTPException(status_code=403, detail="Tenant is inactive.")
    return tenant
