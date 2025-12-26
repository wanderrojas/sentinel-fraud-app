"""
Servicio para interactuar con LLMs (OpenAI o Azure OpenAI)
"""
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from app.config import get_settings

settings = get_settings()


def get_llm(temperature: float = None, model: str = None):
    """
    Obtener instancia del LLM configurado (OpenAI o Azure)
    
    Args:
        temperature: Temperatura para la generación (0.0 - 1.0)
        model: Modelo a usar (solo aplica para OpenAI directo)
    
    Returns:
        ChatOpenAI o AzureChatOpenAI: Instancia del modelo
    """
    temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
    
    # ============================================
    # OPCIÓN 1: AZURE OPENAI
    # ============================================
    if settings.LLM_PROVIDER == "azure":
        print(f"🔵 Usando Azure OpenAI - Deployment: {settings.AZURE_OPENAI_DEPLOYMENT_NAME}")
        return AzureChatOpenAI(
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            temperature=temp,
            max_tokens=settings.MAX_TOKENS,
        )
    
    # ============================================
    # OPCIÓN 2: OPENAI DIRECTO
    # ============================================
    else:
        print(f"🟢 Usando OpenAI directo - Model: {model or settings.LLM_MODEL}")
        return ChatOpenAI(
            model=model or settings.LLM_MODEL,
            temperature=temp,
            max_tokens=settings.MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
        )


def invoke_llm(prompt: str, temperature: float = None) -> str:
    """
    Invocar el LLM con un prompt simple
    
    Args:
        prompt: El prompt a enviar
        temperature: Temperatura para la generación
    
    Returns:
        str: Respuesta del LLM
    """
    llm = get_llm(temperature=temperature)
    response = llm.invoke(prompt)
    return response.content


def get_provider_info() -> dict:
    """
    Obtener información del proveedor LLM configurado
    
    Returns:
        dict: Información del proveedor
    """
    if settings.LLM_PROVIDER == "azure":
        return {
            "provider": "Azure OpenAI",
            "endpoint": settings.AZURE_OPENAI_ENDPOINT,
            "deployment": settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            "api_version": settings.AZURE_OPENAI_API_VERSION,
        }
    else:
        return {
            "provider": "OpenAI",
            "model": settings.LLM_MODEL,
        }