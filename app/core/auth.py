import httpx
from fastapi import Depends, HTTPException, Request, status
from clerk_backend_api.security import AuthenticateRequestOptions
from app.core.config import settings
from app.core.clerk import clerk
import logging

logger = logging.getLogger(__name__)


class AuthUser:
    def __init__(self, user_id: str, org_id: str, org_role: list):
        self.user_id = user_id
        self.org_id = org_id
        self.org_role = org_role

    def has_role(self, role: str) -> bool:
        return role in self.org_role

    @property
    def can_view(self) -> bool:
        return (
            self.has_role("org:tasks:view") or
            self.has_role("org:admin") or
            self.has_role("org:member")
        )

    @property
    def can_edit(self) -> bool:
        # ✅ org:member can also edit (matches frontend canManage logic)
        return (
            self.has_role("org:tasks:edit") or
            self.has_role("org:admin") or
            self.has_role("org:member")
        )

    @property
    def can_delete(self) -> bool:
        # ✅ org:member can also delete
        return (
            self.has_role("org:tasks:delete") or
            self.has_role("org:admin") or
            self.has_role("org:member")
        )

    @property
    def can_create(self) -> bool:
        return (
            self.has_role("org:tasks:create") or
            self.has_role("org:admin") or
            self.has_role("org:member")
        )


def convert_to_httpx_request(fastapi_request: Request) -> httpx.Request:
    return httpx.Request(
        method=fastapi_request.method,
        url=str(fastapi_request.url),
        headers=dict(fastapi_request.headers),
    )


async def get_current_user(request: Request) -> AuthUser:
    httpx_request = convert_to_httpx_request(request)

    logger.debug(f"Authenticating request — authorized_parties: {[settings.FRONTEND_URL]}")

    request_state = clerk.authenticate_request(
        httpx_request,
        AuthenticateRequestOptions(authorized_parties=[settings.FRONTEND_URL])
    )

    if not request_state.is_signed_in:
        logger.warning(f"Auth failed — reason: {request_state.reason}, message: {request_state.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User is not signed in. Reason: {request_state.reason}"
        )

    claims = request_state.payload
    logger.debug(f"Token claims: {claims}")

    user_id = claims.get("sub")

    # ✅ Clerk puts org_id and org_role at the top level in custom JWT templates.
    # Also check the nested `o` object (Clerk's compact org claim) as fallback.
    org_id = claims.get("org_id") or (claims.get("o") or {}).get("id")

    # ✅ org_role comes as a single string from Clerk (e.g. "org:admin", "org:member")
    # Normalise into a list so has_role() works uniformly.
    raw_role = (
        claims.get("org_role") or
        (claims.get("o") or {}).get("rol") or
        claims.get("role") or
        ""
    )
    org_role: list[str] = [raw_role] if isinstance(raw_role, str) and raw_role else raw_role if isinstance(raw_role, list) else []

    logger.debug(f"user_id={user_id}, org_id={org_id}, org_role={org_role}")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token."
        )

    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No organization selected. Please select an organization to proceed."
        )

    return AuthUser(user_id=user_id, org_id=org_id, org_role=org_role)


def require_view(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to view tasks.")
    return user


def require_edit(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_edit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to edit tasks.")
    return user


def require_delete(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_delete:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete tasks.")
    return user


def require_create(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.can_create:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to create tasks.")
    return user