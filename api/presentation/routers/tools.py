from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Dict, Any

from domain.entities.tool import ShellRequest, ShellResponse, FileRequest, FileResponse
from application.services.sandbox_service import SandboxService
from application.services.session_service import SessionService
from presentation.schemas.response import APIResponse

router = APIRouter()

async def get_sandbox_service():
    return SandboxService()

async def get_session_service():
    return SessionService()

@router.post("/sessions/{session_id}/shell", response_model=APIResponse)
async def view_shell_session(
    session_id: str,
    request: ShellRequest,
    sandbox_service: SandboxService = Depends(get_sandbox_service),
    session_service: SessionService = Depends(get_session_service)
):
    """View shell session output in the sandbox environment"""
    try:
        # Verify session exists
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Execute shell command to get session output
        result = await sandbox_service.execute_shell_command(
            session_id, 
            f"history | tail -20"  # Get recent command history
        )
        
        # Parse console history (simplified)
        console_history = []
        if result.get("output"):
            lines = result["output"].strip().split("\n")
            for line in lines:
                if line.strip():
                    console_history.append({
                        "ps1": "$ ",
                        "command": line.strip(),
                        "output": ""
                    })
        
        response_data = ShellResponse(
            output=result.get("output", ""),
            session_id=request.session_id,
            console=console_history
        )
        
        return APIResponse(
            code=0,
            msg="success",
            data=response_data.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/file", response_model=APIResponse)
async def view_file_content(
    session_id: str,
    request: FileRequest,
    sandbox_service: SandboxService = Depends(get_sandbox_service),
    session_service: SessionService = Depends(get_session_service)
):
    """View file content in the sandbox environment"""
    try:
        # Verify session exists
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Read file from sandbox
        result = await sandbox_service.read_file(session_id, request.file)
        
        response_data = FileResponse(
            content=result.get("content", ""),
            file=request.file
        )
        
        return APIResponse(
            code=0,
            msg="success",
            data=response_data.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/sessions/{session_id}/vnc")
async def vnc_connection(
    websocket: WebSocket,
    session_id: str,
    sandbox_service: SandboxService = Depends(get_sandbox_service)
):
    """Establish a VNC WebSocket connection to the session's sandbox environment"""
    await websocket.accept()
    
    try:
        # Get VNC port for session
        vnc_port = await sandbox_service.get_vnc_port(session_id)
        if not vnc_port:
            # Create sandbox if it doesn't exist
            sandbox_info = await sandbox_service.create_sandbox(session_id)
            vnc_port = sandbox_info.get("vnc_port")
        
        if not vnc_port:
            await websocket.close(code=1000, reason="VNC not available")
            return
        
        # VNC WebSocket proxy implementation would go here
        # This is a simplified version - in production, you'd need a proper VNC proxy
        while True:
            try:
                data = await websocket.receive_bytes()
                # Forward data to VNC server and send response back
                # This requires implementing a VNC protocol proxy
                await websocket.send_bytes(b"VNC proxy not fully implemented")
                
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        await websocket.close(code=1000, reason=f"Error: {str(e)}")
