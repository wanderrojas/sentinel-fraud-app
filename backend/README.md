uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Explicación del comando:**
- `app.main:app` → Archivo `app/main.py`, variable `app`
- `--reload` → Auto-recarga cuando cambies código
- `--host 0.0.0.0` → Escucha en todas las interfaces
- `--port 8000` → Puerto 8000

---

## 🎉 PASO 4: VERIFICAR QUE FUNCIONA

Deberías ver algo como esto en tu consola:
```
INFO:     Will watch for changes in these directories: ['C:\\...\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
============================================================
🚀 Fraud Detection Multi-Agent System
📌 Version: 1.0.0
🌐 API docs: http://localhost:8000/docs
📚 ReDoc: http://localhost:8000/redoc
============================================================
INFO:     Application startup complete.
```

---

## 🧪 PASO 5: PROBAR LA API

Abre tu navegador y visita:

### 1. **Ruta raíz**
```
http://localhost:8000/