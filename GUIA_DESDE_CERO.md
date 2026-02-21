# Guia completa para ejecutar el proyecto desde cero

Esta guia explica, paso a paso, como instalar todo y ejecutar el pipeline de artefactos de software, con lenguaje simple para personas no tecnicas.

## 1) Que hace este proyecto (explicado simple)

Este sistema toma una descripcion inicial de una idea de producto ("brief") y la transforma automaticamente en documentos estructurados de analisis.

Trabaja como si fueran 4 especialistas colaborando en cadena:

1. **Requirements Agent (Analista de Requerimientos)**  
   Convierte la idea en requisitos funcionales y no funcionales.
2. **Inception Agent (Incepcion de Producto)**  
   Resume el producto, define alcance del MVP y enumera riesgos.
3. **User Stories Agent (Analista Agile)**  
   Genera historias de usuario y criterios de aceptacion.
4. **ER Design Agent (Disenador de Datos)**  
   Propone el modelo entidad-relacion de la base de datos.

Al final, todo queda en archivos JSON listos para revisar o usar en otras herramientas.

## 2) Requisitos previos

Antes de empezar, necesitas tener instalado:

- **Git** (para descargar el proyecto)
- **Python 3.9 o superior**
- **pip** (gestor de paquetes de Python)
- **Una API Key de Groq** (clave para usar el modelo de IA)

## 3) Instalacion desde cero

### Paso 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd agents
```

Si ya lo tienes descargado, solo entra a la carpeta del proyecto:

```bash
cd agents
```

### Paso 2. Crear entorno virtual

```bash
python3 -m venv .venv
```

### Paso 3. Activar entorno virtual

En macOS/Linux:

```bash
source .venv/bin/activate
```

En Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### Paso 4. Instalar dependencias del proyecto

```bash
pip install -e .
```

Este comando instala:

- `groq` (conexion con el proveedor de IA)
- `pydantic` (validacion de estructura de datos)
- `streamlit` (interfaz web)

## 4) Configurar API Key de Groq

Configura la variable de entorno antes de ejecutar:

En macOS/Linux:

```bash
export GROQ_API_KEY="TU_API_KEY_AQUI"
```

En Windows (PowerShell):

```powershell
$env:GROQ_API_KEY="TU_API_KEY_AQUI"
```

## 5) Ejecutar por linea de comandos (CLI)

Este modo procesa un archivo de entrada y genera los artefactos automaticamente.

### Paso 1. Preparar archivo de entrada

Puedes usar el ejemplo existente:

- `examples/input_brief.json`

Formato esperado:

```json
{
  "brief_text": "Descripcion narrativa del problema, usuarios, metas y restricciones..."
}
```

### Paso 2. Ejecutar pipeline

```bash
se-pipeline \
  --input-file examples/input_brief.json \
  --output-file final_artifacts.json \
  --model llama-3.1-8b-instant
```

### Paso 3. Revisar resultados

Se generan estos archivos:

- `requirements.json`
- `inception.json`
- `user_stories.json`
- `er_design.json`
- `final_artifacts.json` (todo consolidado)

## 6) Ejecutar con interfaz visual (Streamlit)

Si prefieres una vista grafica:

```bash
streamlit run src/multi_agent_pipeline/streamlit_app.py
```

Luego abre en navegador la URL local que muestra Streamlit (normalmente `http://localhost:8501`).

En esta pantalla puedes:

- Escribir el brief
- Lanzar el pipeline
- Ver la salida de cada agente en vivo
- Descargar el resultado final en JSON

## 7) Explicacion de componentes (no tecnico)

- `src/multi_agent_pipeline/streamlit_app.py`  
  Es la pantalla web para usar el sistema de forma visual.

- `src/multi_agent_pipeline/cli.py`  
  Es la version por comandos (sin interfaz web).

- `src/multi_agent_pipeline/orchestrator.py`  
  Es el "coordinador": decide el orden de trabajo de los 4 agentes.

- `src/multi_agent_pipeline/agents.py`  
  Contiene la logica de cada agente (que produce cada uno).

- `src/multi_agent_pipeline/llm.py`  
  Es el conector que envia/recibe informacion del modelo de IA (Groq).

- `src/multi_agent_pipeline/schemas.py`  
  Define la forma exacta que deben tener los resultados (estructura esperada).

- `examples/input_brief.json`  
  Ejemplo de entrada para ejecutar rapido.

- `final_artifacts.json` y archivos intermedios  
  Son los resultados producidos por el pipeline.

## 8) Flujo completo recomendado (resumen rapido)

```bash
cd /Users/camilo/agents
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
export GROQ_API_KEY="TU_API_KEY_AQUI"
se-pipeline --input-file examples/input_brief.json --output-file final_artifacts.json --model llama-3.1-8b-instant
```

## 9) Problemas comunes y solucion

### Error: `api key is not set`

- Verifica que exportaste `GROQ_API_KEY` en la misma terminal donde ejecutas el programa.
- Repite:

```bash
export GROQ_API_KEY="TU_API_KEY_AQUI"
```

### Error: `brief_text` invalido o muy corto

- El texto de entrada debe tener contenido suficiente (minimo 50 caracteres).
- Revisa `examples/input_brief.json`.

### Error: comando no encontrado (`se-pipeline` o `streamlit`)

- Asegurate de tener el entorno virtual activado.
- Reinstala dependencias:

```bash
pip install -e .
```

---

