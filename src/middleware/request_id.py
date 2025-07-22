import uuid
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException
from src.logger.logger import request_id_context
from src.constants.constants import REQUEST_ID_HEADER

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate or get request ID (prefer from header if client provided it)
        request_id: str = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))
        
        # Set in context for logging
        token = request_id_context.set(request_id)
        
        # Add request_id to request state for access in route handlers
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            
            # Always add request_id to response header
            response.headers[REQUEST_ID_HEADER] = request_id
            
            return response
        except HTTPException as http_exc:
            # Handle HTTP exceptions (400, 401, 403, etc.)
            response = JSONResponse(
                status_code=http_exc.status_code,
                content={"detail": http_exc.detail},
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
            
        except Exception as e:
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            request_id_context.reset(token)