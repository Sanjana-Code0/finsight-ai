from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_async_client, AsyncClient
from .config import settings
from typing import Dict, Any

security = HTTPBearer()

async def get_supabase_client() -> AsyncClient:
    """Returns an async Supabase client instance."""
    # Note: For dependencies, we usually return a new client per request or a shared one.
    # The async client is safe to share, but for simplicity, we create it here.
    client = await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return client

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    # client: AsyncClient = Depends(get_supabase_client) # We can optionally inject the client
) -> Dict[str, Any]:
    """
    Validates the JWT token using Supabase Auth and fetches the user's profile.
    Raises 401 if the token is invalid or expired.
    """
    token = credentials.credentials
    
    # We need a client with the anon key to verify the user token
    # Actually, to verify the token and act on behalf of the user, we set the session.
    client = await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    
    try:
        # Validate token by getting the user
        auth_res = await client.auth.get_user(token)
        
        if not auth_res or not auth_res.user:
            raise ValueError("Invalid token")
            
        user = auth_res.user
        
        # Fetch profile data
        profile_res = await client.table("profiles").select("*").eq("id", user.id).single().execute()
        profile_data = profile_res.data if profile_res else {}
        
        # Construct combined user dict
        user_dict = {
            "id": user.id,
            "email": user.email,
            "financial_literacy_level": profile_data.get("financial_literacy_level", "beginner"),
            "full_name": profile_data.get("full_name")
        }
        
        return user_dict
        
    except Exception as e:
        # Supabase raises exceptions for invalid/expired tokens
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
