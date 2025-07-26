# 📊 Creación de un Pipeline de Datos y API con Caché Inteligente

Este proyecto demuestra cómo construir una solución completa de backend capaz de migrar datos a gran escala, exponerlos mediante una API segura y optimizada, y desplegarla en la nube con una estrategia de caché inteligente.

## 🚀 Características Principales

- **Pipeline ETL con Azure Data Factory**: Migración y transformación de un dataset desde Azure Blob Storage hacia una base de datos en Azure.
- **API REST con FastAPI**: Backend implementado en Python con endpoints para consulta y gestión de datos.
- **Autenticación con Firebase**: Protección de endpoints mediante JWT con roles y permisos definidos (usuarios activos y administradores).
- **Caché con Redis**: Implementación de caching dinámico para consultas con invalidación automática.
- **Monitoreo con Azure Application Insights**: Análisis de desempeño, trazas y métricas de la API bajo carga.
- **Despliegue en la nube con Docker**: Contenedor desplegado usando Azure App Service o Azure Container Apps.

## 🔑 Endpoints Principales

- `POST /signup`: Registro de nuevos usuarios.
- `POST /login`: Autenticación y emisión de JWT.
- `GET /catalog`: Consulta de todos los registros del modelo de datos (cacheable)
- `POST /catalog`: Creación de nuevos registros con lógica de invalidación de caché.
- `GET/catalong?category=A`: Consulta de datos con filtros (cacheable)

## 📦 Tecnologías Usadas

- Python + FastAPI
- Azure Data Factory, Blob Storage, SQL
- Firebase Authentication
- Redis
- Azure Application Insights
- Docker + Azure App Service

## ▶️ Ejecución Local
1. Clona el repositorio
2. Crear un archivo `.env` con las variables de entorno necesarias
3. Crear un ambiente ambiente de python `python -m venv env`
4. Habilitar el ambiente virtual `source ./env/bin/activate`
5. Instalar dependencias: `pip install -r requirements.txt`
6. Ejecuta el servidor: `main main.py`
