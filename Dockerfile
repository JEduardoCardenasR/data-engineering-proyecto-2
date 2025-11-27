# ============================================================================
# Dockerfile para el Proyecto de Data Engineering - E-commerce
# ============================================================================
# 
# Este Dockerfile crea un contenedor con:
# - Python 3.10
# - dbt y dbt-postgres
# - Dependencias del proyecto (requirements.txt)
# - Jupyter para notebooks
# ============================================================================

FROM python:3.10-slim

# Metadatos
LABEL maintainer="Data Engineering Team"
LABEL description="Contenedor para proyecto de Data Engineering con dbt, Python y Jupyter"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements.txt e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Instalar dbt y adaptador para PostgreSQL
RUN pip install dbt-core dbt-postgres dbt-utils

# Instalar Jupyter y extensiones
RUN pip install jupyter jupyterlab ipykernel && \
    python -m ipykernel install --user --name=python3

# Copiar el proyecto completo
COPY . .

# Crear directorio para perfiles de dbt
RUN mkdir -p /root/.dbt

# Exponer puerto para Jupyter (opcional)
EXPOSE 8888

# Comando por defecto (mantener contenedor corriendo)
CMD ["tail", "-f", "/dev/null"]

