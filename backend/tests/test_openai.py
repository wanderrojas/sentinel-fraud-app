"""
Test rápido de OpenAI API
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("=" * 60)
print("🧪 TEST DE OPENAI API KEY")
print("=" * 60)
print(f"\n🔑 API Key encontrada: {api_key[:20]}..." if api_key else "❌ No se encontró API Key")

if api_key and api_key.startswith("sk-proj-"):
    print("✅ Formato de API Key correcto")
    
    # Intentar hacer una llamada de prueba
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        print("\n🚀 Probando conexión con OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Di solo 'Hola, funciono correctamente'"}
            ],
            max_tokens=50
        )
        
        print(f"✅ Respuesta recibida: {response.choices[0].message.content}")
        print("\n🎉 ¡Tu API Key funciona perfectamente!")
        
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        print("\n⚠️ Verifica que:")
        print("   1. Tu API Key es correcta")
        print("   2. Tienes créditos en tu cuenta OpenAI")
        print("   3. No hay problemas de red")
else:
    print("❌ API Key no válida o no encontrada")
    print("\n📝 Pasos para obtener tu API Key:")
    print("   1. Ve a https://platform.openai.com/api-keys")
    print("   2. Crea una nueva API Key")
    print("   3. Cópiala en tu archivo .env")

print("=" * 60)