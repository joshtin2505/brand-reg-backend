# Brand Reg Backend (FastAPI)

API backend para la aplicación Brand Register, desarrollada con FastAPI y SQLite/Turso. Proporciona endpoints para la gestión completa del registro de marcas.

## Características

- API RESTful completa para gestionar registros de marcas (CRUD)
- Base de datos SQLite remota con Turso/libSQL
- Validación de datos con Pydantic
- Documentación automática con Swagger/OpenAPI
- CORS configurado para frontend Next.js
- Script de seed para datos de prueba
- Paginación para grandes conjuntos de datos
- Manejo de errores consistente

## Requisitos

- Python 3.13+
- Cuenta en Turso Database (o SQLite local para desarrollo)

## Estructura del Proyecto

```shell
brand-reg-backend/
├── .env                # Variables de entorno (no comitear)
├── .env.example        # Plantilla para variables de entorno
├── .gitignore          # Archivos ignorados por Git
├── README.md           # Documentación del proyecto
├── requirements.txt    # Dependencias Python
├── app/                # Código fuente principal
│   ├── __init__.py
│   ├── main.py         # Punto de entrada de FastAPI
│   ├── db.py           # Configuración de la base de datos
│   ├── seed.py         # Script para poblar la DB con datos de prueba
│   ├── core/           # Configuración central
│   │   ├── __init__.py
│   │   └── config.py   # Configuraciones de la aplicación
│   ├── routers/        # Definición de endpoints API
│   │   ├── __init__.py
│   │   └── brands.py   # Rutas para gestión de marcas
│   └── schemas/        # Modelos Pydantic
│       ├── __init__.py
│       └── brand.py    # Esquemas para marcas
└── .vscode/            # Configuración de VS Code
    └── tasks.json      # Tareas para ejecutar el servidor
```

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/joshtin2505/brand-reg-backend.git
cd brand-reg-backend
```

1. Crea y activa un entorno virtual (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

1. Instala las dependencias:

```powershell
pip install -r requirements.txt
```

1. Copia el archivo de ejemplo de variables de entorno y configúralo:

```powershell
cp .env.example .env
# Edita .env con tu URL y token de Turso
```

## Configuración de la Base de Datos

Este proyecto utiliza [Turso](https://turso.tech/) (basado en libSQL/SQLite) como base de datos. Necesitarás:

1. [Crear una cuenta en Turso](https://turso.tech/)
1. Instalar la CLI de Turso:

```bash
curl -sSfL https://get.tur.so/install.sh | bash
```

1. Iniciar sesión y crear una base de datos:

```bash
turso auth login
turso db create brand-register
```

1. Obtener la URL y token de autenticación:

```bash
turso db show brand-register --url
turso db tokens create brand-register
```

1. Actualiza estos valores en tu archivo `.env`

## Desarrollo

1. Ejecutar el servidor en modo desarrollo:

```powershell
# Método 1: Directamente con uvicorn
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Método 2: Usando la tarea de VS Code
# Terminal > Run Task > "Run FastAPI (dev)"
```

1. Poblar la base de datos con datos de prueba:

```powershell
python app/seed.py --reset  # --reset borra datos existentes
```

1. Acceder a los endpoints:
   - API: <http://localhost:8000/>
   - Documentación OpenAPI: <http://localhost:8000/docs>
   - Verificación de salud: <http://localhost:8000/health>

## API Endpoints

### Brands

- `GET /brands` - Obtener todas las marcas con paginación
  - Parámetros de consulta:
    - `page`: Número de página (por defecto: 1)
    - `page_size`: Tamaño de página (por defecto: 5)
- `GET /brands/{id}` - Obtener una marca por ID
- `POST /brands` - Crear una nueva marca
- `PUT /brands/{id}` - Actualizar una marca existente
- `DELETE /brands/{id}` - Eliminar una marca

## Modelos de Datos

### Brand

```python
class Brand(BaseModel):
    id: int
    brand: str
    holder: str
    status: str
    created_at: Optional[datetime] = None
```

### PaginatedResponse

```python
class PaginatedResponse(BaseModel):
    items: List[Brand]
    total: int
    page: int
    page_size: int
    total_pages: int
```

## Documentación

La documentación completa de la API está disponible en:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Frontend

Este backend está diseñado para funcionar con una aplicación frontend en Next.js. El repositorio del frontend está disponible en:
[brand-register](https://github.com/joshtin2505/brand-register)

## Desarrollo Futuro

- Autenticación con JWT
- Migraciones de base de datos
- Pruebas unitarias e integración
- Filtros y ordenación avanzados
- Búsqueda de texto completo
- Logging detallado
- Caché para mejorar rendimiento
- Despliegue con Docker
