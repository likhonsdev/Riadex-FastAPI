import docker
import asyncio
import uuid
from typing import Dict, Any, Optional
from infrastructure.config import get_settings
import structlog

logger = structlog.get_logger()
settings = get_settings()

class SandboxService:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.containers: Dict[str, Any] = {}
    
    async def create_sandbox(self, session_id: str) -> Dict[str, Any]:
        """Create a new sandbox container for the session"""
        try:
            container_name = f"riadex-sandbox-{session_id}"
            
            # Create container
            container = self.docker_client.containers.run(
                settings.docker_image,
                name=container_name,
                detach=True,
                tty=True,
                stdin_open=True,
                network=settings.docker_network,
                environment={
                    "DISPLAY": ":1",
                    "VNC_PORT": "5901"
                },
                ports={
                    "5901/tcp": None,  # VNC port
                    "22/tcp": None     # SSH port
                }
            )
            
            self.containers[session_id] = {
                "container": container,
                "container_id": container.id,
                "vnc_port": container.ports.get("5901/tcp", [{}])[0].get("HostPort"),
                "ssh_port": container.ports.get("22/tcp", [{}])[0].get("HostPort")
            }
            
            logger.info("Sandbox created", session_id=session_id, container_id=container.id)
            
            return {
                "container_id": container.id,
                "vnc_port": self.containers[session_id]["vnc_port"],
                "ssh_port": self.containers[session_id]["ssh_port"]
            }
            
        except Exception as e:
            logger.error("Failed to create sandbox", session_id=session_id, error=str(e))
            raise
    
    async def execute_shell_command(self, session_id: str, command: str) -> Dict[str, Any]:
        """Execute shell command in sandbox"""
        try:
            if session_id not in self.containers:
                await self.create_sandbox(session_id)
            
            container = self.containers[session_id]["container"]
            
            # Execute command
            result = container.exec_run(command, tty=True)
            
            return {
                "command": command,
                "output": result.output.decode("utf-8"),
                "exit_code": result.exit_code
            }
            
        except Exception as e:
            logger.error("Shell command execution failed", session_id=session_id, error=str(e))
            return {
                "command": command,
                "output": f"Error: {str(e)}",
                "exit_code": 1
            }
    
    async def read_file(self, session_id: str, file_path: str) -> Dict[str, Any]:
        """Read file content from sandbox"""
        try:
            if session_id not in self.containers:
                await self.create_sandbox(session_id)
            
            container = self.containers[session_id]["container"]
            
            # Read file using cat command
            result = container.exec_run(f"cat {file_path}")
            
            if result.exit_code == 0:
                return {
                    "file": file_path,
                    "content": result.output.decode("utf-8"),
                    "success": True
                }
            else:
                return {
                    "file": file_path,
                    "content": f"Error reading file: {result.output.decode('utf-8')}",
                    "success": False
                }
                
        except Exception as e:
            logger.error("File read failed", session_id=session_id, file_path=file_path, error=str(e))
            return {
                "file": file_path,
                "content": f"Error: {str(e)}",
                "success": False
            }
    
    async def write_file(self, session_id: str, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to file in sandbox"""
        try:
            if session_id not in self.containers:
                await self.create_sandbox(session_id)
            
            container = self.containers[session_id]["container"]
            
            # Write file using echo command
            escaped_content = content.replace("'", "'\"'\"'")
            result = container.exec_run(f"echo '{escaped_content}' > {file_path}")
            
            return {
                "file": file_path,
                "success": result.exit_code == 0,
                "message": "File written successfully" if result.exit_code == 0 else f"Error: {result.output.decode('utf-8')}"
            }
            
        except Exception as e:
            logger.error("File write failed", session_id=session_id, file_path=file_path, error=str(e))
            return {
                "file": file_path,
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    async def get_vnc_port(self, session_id: str) -> Optional[str]:
        """Get VNC port for session"""
        if session_id in self.containers:
            return self.containers[session_id].get("vnc_port")
        return None
    
    async def cleanup_sandbox(self, session_id: str) -> bool:
        """Clean up sandbox container"""
        try:
            if session_id in self.containers:
                container = self.containers[session_id]["container"]
                container.stop()
                container.remove()
                del self.containers[session_id]
                logger.info("Sandbox cleaned up", session_id=session_id)
                return True
        except Exception as e:
            logger.error("Sandbox cleanup failed", session_id=session_id, error=str(e))
        return False
