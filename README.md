# Multi-Agent Software Engineering Artifacts Pipeline

Pipeline de 4 agentes que transforma un brief narrativo en artefactos de ingenieria de software en formato JSON.

## Tabla de contenido

1. Vision general
2. Flujo de extremo a extremo
3. Estructura del repositorio
4. Explicacion detallada de cada archivo en `src/`
5. Requisitos
6. Instalacion
7. Ejecucion por CLI
8. Ejecucion con UI (Streamlit)
9. Archivos de salida
10. Dependencias utilizadas
11. Notas operativas y limitaciones

## 1. Vision general

Este proyecto automatiza una parte del analisis inicial de producto/software.
A partir de un texto libre (`brief_text`), genera:

- Requerimientos
- Documento de inception de producto
- Historias de usuario
- Diseno ER (entidad-relacion)

Todo el proceso esta modelado como una cadena de agentes: la salida de uno alimenta al siguiente.

## 2. Flujo de extremo a extremo

1. Se recibe un brief narrativo.
2. Se valida el input minimo con Pydantic.
3. El agente de requerimientos produce estructura funcional/no funcional.
4. El agente de inception define propuesta, alcance MVP y riesgos.
5. El agente agile crea epicas e historias de usuario.
6. El agente de datos genera entidades, atributos y relaciones.
7. Se valida la estructura final y se escribe JSON de salida.

## 3. Estructura del repositorio

```text
.
|-- README.md
|-- pyproject.toml
|-- setup.py
|-- examples/
|   `-- input_brief.json
`-- src/
    |-- multi_agent_pipeline/
    |   |-- __init__.py
    |   |-- agents.py
    |   |-- cli.py
    |   |-- llm.py
    |   |-- orchestrator.py
    |   |-- schemas.py
    |   `-- streamlit_app.py
    `-- multi_agent_se_artifacts.egg-info/
```

## 4. Explicacion detallada de cada archivo en `src/`

### `src/multi_agent_pipeline/__init__.py`

**Para que sirve:**
- Expone la funcion principal del paquete para importar facilmente desde afuera.

**Que contiene:**
- `__all__ = ["run_pipeline"]`: define la API publica del paquete.
- `from .orchestrator import run_pipeline`: reexporta la funcion orquestadora.

**Uso tipico:**
- Permite usar `from multi_agent_pipeline import run_pipeline`.

---

### `src/multi_agent_pipeline/schemas.py`

**Para que sirve:**
- Define el contrato de datos de entrada/salida con modelos Pydantic.
- Evita que los agentes devuelvan estructuras inconsistentes.

**Tecnologias usadas:**
- `pydantic.BaseModel`
- `typing.Literal` para restringir valores validos.

**Modelos y para que sirve cada uno:**

- `InitialBriefInput`
  - Campo: `brief_text` (minimo 50 caracteres).
  - Valida el input inicial.

- `RequirementItem`
  - Estructura de un requerimiento funcional.
  - Incluye `id`, `title`, `description`, `priority`, `rationale`.

- `NonFunctionalRequirement`
  - Estructura de requerimiento no funcional.
  - Incluye categoria y objetivo medible.

- `RequirementsOutput`
  - Salida completa del agente de requerimientos.
  - Contiene stakeholders, goals, requerimientos y preguntas abiertas.

- `RiskItem`
  - Estructura de riesgo con impacto/probabilidad controlados por `Literal`.

- `InceptionOutput`
  - Salida del agente de inception: resumen, problema, propuesta, alcance y riesgos.

- `UserStory`
  - Formato estandar de historia de usuario.

- `UserStoriesOutput`
  - Conjunto de epicas, historias y dependencias.

- `EntityAttribute`
  - Describe un atributo de entidad de datos.
  - Incluye flags de PK/FK/null/unique.

- `Relationship`
  - Define relacion entre entidades, cardinalidad y FK.

- `EntityDefinition`
  - Estructura de cada entidad con atributos y relaciones.

- `EROutput`
  - Salida final del agente de diseno de datos.

- `FinalArtifactsPackage`
  - Contenedor de todo el pipeline (brief + 4 artefactos).

---

### `src/multi_agent_pipeline/llm.py`

**Para que sirve:**
- Encapsula la comunicacion con Groq para pedir respuestas en JSON.

**Tecnologias usadas:**
- SDK de `groq`
- `json` para serializar/deserializar payloads

**Clase principal:**
- `GroqJSONClient`

**Metodos:**
- `__init__(model="llama-3.1-8b-instant")`
  - Inicializa cliente Groq y modelo por defecto.
  - Prepara `self.client` y `self.model`.

- `complete_json(system_prompt, user_payload)`
  - Envia un prompt de sistema + payload usuario.
  - Fuerza `response_format={"type": "json_object"}`.
  - Convierte la respuesta textual del modelo en `dict` Python.
  - Lanza error si la respuesta viene vacia.

**Nota importante del estado actual del codigo:**
- El archivo tiene una API key hardcodeada en la variable `api_key`.
- Aunque se importa `os`, actualmente no se esta leyendo `GROQ_API_KEY` desde variable de entorno.

---

### `src/multi_agent_pipeline/agents.py`

**Para que sirve:**
- Implementa la logica de cada agente y la capa de robustez para normalizar/validar salida del LLM.

**Que usa internamente:**
- `dataclass` para definir agentes livianos
- `pydantic` para validacion
- `GroqJSONClient` para inferencia
- Modelos de `schemas.py` como contrato de salida

**Funciones utilitarias de normalizacion:**

- `_obj_list(value)`
  - Asegura que un valor termine como lista de diccionarios.

- `_str_list(value)`
  - Convierte distintos tipos a lista de strings limpios.

- `_str_scalar(value)`
  - Convierte estructuras complejas a texto simple.

- `_normalize_item_ids(items)`
  - Convierte `id` a string consistentemente.

- `_normalize_requirements(raw)`
  - Normaliza salida del agente de requerimientos.

- `_normalize_inception(raw)`
  - Normaliza salida de inception.

- `_normalize_stories(raw)`
  - Normaliza epicas/historias/criterios.

- `_normalize_er(raw)`
  - Normaliza entidades, atributos y relaciones.

**Funcion de validacion y reparacion:**

- `_validate_with_repair(llm, system_prompt, payload, model_type, normalize)`
  - Paso 1: pide JSON al modelo.
  - Paso 2: normaliza.
  - Paso 3: valida con Pydantic.
  - Si falla validacion:
    - Reintenta con un prompt de reparacion que incluye errores de validacion.
    - Vuelve a normalizar y validar.

**Agentes concretos:**

- `RequirementsAgent`
  - Metodo: `run(payload)`
  - Genera requerimientos funcionales/no funcionales.

- `InceptionAgent`
  - Metodo: `run(payload)`
  - Genera resumen de producto, alcance MVP y riesgos.

- `UserStoriesAgent`
  - Metodo: `run(payload)`
  - Genera epicas e historias con criterios de aceptacion.

- `ERDesignAgent`
  - Metodo: `run(payload)`
  - Genera modelo ER conceptual/logico.

Cada `run(...)` define un `system_prompt` con schema esperado y devuelve un modelo validado.

---

### `src/multi_agent_pipeline/orchestrator.py`

**Para que sirve:**
- Coordina el orden de ejecucion de agentes y compone el resultado final.

**Funcion principal:**
- `run_pipeline(brief_text, model="llama-3.1-8b-instant", on_agent_complete=None)`

**Que hace paso a paso:**
1. Crea y valida `InitialBriefInput`.
2. Instancia `GroqJSONClient`.
3. Crea instancias de los 4 agentes.
4. Ejecuta agentes secuencialmente.
5. Pasa la salida de cada etapa como contexto de la siguiente.
6. Si existe callback `on_agent_complete`, reporta cada salida parcial.
7. Devuelve `FinalArtifactsPackage`.

**Por que es importante:**
- Centraliza el flujo para que CLI y Streamlit reutilicen exactamente la misma logica.

---

### `src/multi_agent_pipeline/cli.py`

**Para que sirve:**
- Permite correr el pipeline desde terminal (`se-pipeline`).

**Funciones:**
- `_parse_args()`
  - Define argumentos de linea de comandos:
    - `--input-file` (obligatorio)
    - `--output-file` (default: `final_artifacts.json`)
    - `--model` (default: `llama-3.1-8b-instant`)

- `main()`
  - Lee JSON de entrada.
  - Verifica que exista `brief_text` string.
  - Define callback `_print_agent_output(...)` para:
    - imprimir salida por agente,
    - guardar archivos parciales (`requirements.json`, etc.),
    - ir actualizando el JSON agregado de progreso.
  - Ejecuta `run_pipeline(...)`.
  - Escribe JSON final consolidado.

**Comportamiento relevante:**
- Persiste resultados parciales por agente incluso antes del resultado final.

---

### `src/multi_agent_pipeline/streamlit_app.py`

**Para que sirve:**
- Interfaz visual para correr el pipeline sin usar comandos.

**Elementos clave del archivo:**

- `AGENT_ORDER`
  - Orden canonico de etapas visualizadas.

- `AGENT_LABELS`
  - Etiquetas amigables para mostrar en UI.

- `_run_pipeline_worker(brief_text, model, events)`
  - Corre el pipeline en un thread separado.
  - Envia eventos a una cola (`Queue`):
    - `agent` por cada agente terminado,
    - `final` al finalizar,
    - `error` si algo falla.

- `main()`
  - Configura pagina y formulario.
  - Valida longitud minima del brief.
  - Lanza thread worker.
  - Consume cola de eventos para refrescar la interfaz en tiempo real.
  - Muestra JSON por agente y JSON final.
  - Habilita descarga de `final_artifacts.json`.
  - Guarda resultados en `st.session_state` para mostrar "Most Recent Run".

**Diseno tecnico importante:**
- Uso de `Thread + Queue` evita bloquear la UI durante ejecucion del pipeline.

## 5. Requisitos

- Python 3.9+
- pip
- Acceso a Groq API

## 6. Instalacion

```bash
cd /Users/camilo/agents
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 7. Ejecucion por CLI

```bash
se-pipeline \
  --input-file examples/input_brief.json \
  --output-file final_artifacts.json \
  --model llama-3.1-8b-instant
```

### Formato de input

`examples/input_brief.json`

```json
{
  "brief_text": "Narrative business brief text..."
}
```

## 8. Ejecucion con UI (Streamlit)

```bash
streamlit run src/multi_agent_pipeline/streamlit_app.py
```

Abre la URL local que imprime Streamlit (normalmente `http://localhost:8501`).

## 9. Archivos de salida

Durante ejecucion por CLI se generan:

- `requirements.json`
- `inception.json`
- `user_stories.json`
- `er_design.json`
- `final_artifacts.json`

`final_artifacts.json` consolida todo bajo estas claves:

- `initial_brief`
- `requirements`
- `inception`
- `user_stories`
- `er_design`

## 10. Dependencias utilizadas

Definidas en `pyproject.toml`:

- `groq>=0.18.0`: cliente API LLM
- `pydantic>=2.7.0`: validacion de contratos
- `streamlit>=1.32.0`: interfaz web

Script de entrada CLI:

- `se-pipeline = multi_agent_pipeline.cli:main`

## 11. Notas operativas y limitaciones

- El input exige `brief_text` con minimo 50 caracteres (`InitialBriefInput`).
- El pipeline depende de que el modelo responda JSON valido o reparable.
- Existe una doble capa de robustez: normalizacion + validacion + intento de reparacion.
- Actualmente `llm.py` usa una API key hardcodeada; para produccion se recomienda leerla desde variable de entorno.
