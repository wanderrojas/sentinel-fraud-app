"""
Streaming Service - SSE para logs en tiempo real
"""
from typing import Literal, Optional
from pydantic import BaseModel


class SSEEvent(BaseModel):
    """Evento SSE"""
    event: Literal[
        "phase",        # Nueva fase iniciada
        "agent",        # Agente ejecutándose
        "success",      # Operación exitosa
        "info",         # Información general
        "warning",      # Advertencia
        "error",        # Error
        "complete"      # Análisis completado
    ]
    phase: Optional[str] = None
    agent: Optional[str] = None
    message: str
    data: Optional[dict] = None


class StreamingService:
    """Servicio para streaming de eventos SSE"""
    
    @staticmethod
    def format_sse(event: SSEEvent) -> str:
        """
        Formatear evento como SSE
        
        Returns:
            String en formato SSE
        """
        data = event.model_dump_json()
        return f"data: {data}\n\n"
    
    @staticmethod
    async def emit_event(event: SSEEvent) -> str:
        """
        Emitir evento SSE
        
        Returns:
            Evento formateado
        """
        return StreamingService.format_sse(event)
    
    @staticmethod
    async def emit_phase(phase: str, message: str) -> str:
        """Emitir inicio de fase"""
        event = SSEEvent(
            event="phase",
            phase=phase,
            message=message
        )
        return StreamingService.format_sse(event)
    
    @staticmethod
    async def emit_agent(agent: str, message: str, data: dict = None) -> str:
        """Emitir actividad de agente"""
        event = SSEEvent(
            event="agent",
            agent=agent,
            message=message,
            data=data
        )
        return StreamingService.format_sse(event)
    
    @staticmethod
    async def emit_success(message: str, data: dict = None) -> str:
        """Emitir éxito"""
        event = SSEEvent(
            event="success",
            message=message,
            data=data
        )
        return StreamingService.format_sse(event)
    
    @staticmethod
    async def emit_info(message: str) -> str:
        """Emitir información"""
        event = SSEEvent(
            event="info",
            message=message
        )
        return StreamingService.format_sse(event)
    
    @staticmethod
    async def emit_warning(message: str) -> str:
        """Emitir advertencia"""
        event = SSEEvent(
            event="warning",
            message=message
        )
        return StreamingService.format_sse(event)
    
    @staticmethod
    async def emit_error(message: str) -> str:
        """Emitir error"""
        event = SSEEvent(
            event="error",
            message=message
        )
        return StreamingService.format_sse(event)
    
    @staticmethod
    async def emit_complete(message: str, data: dict) -> str:
        """Emitir completado"""
        event = SSEEvent(
            event="complete",
            message=message,
            data=data
        )
        return StreamingService.format_sse(event)