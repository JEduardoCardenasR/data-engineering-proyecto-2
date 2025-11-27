#!/bin/bash
# ============================================================================
# Script de Inicialización de Base de Datos
# ============================================================================
# 
# Este script ejecuta los scripts DDL para crear el modelo físico
# de la base de datos después de que PostgreSQL esté listo.
# 
# Uso:
#   docker-compose exec db bash /docker-entrypoint-initdb.d/init-db.sh
# ============================================================================

set -e

echo "Iniciando creación del modelo físico del data warehouse..."

# Esperar a que PostgreSQL esté completamente listo
until pg_isready -U ${POSTGRES_USER:-usuario} -d ${POSTGRES_DB:-avance_1_db}; do
  echo "Esperando a que PostgreSQL esté listo..."
  sleep 2
done

# Ejecutar scripts DDL en orden
if [ -d "/docker-entrypoint-initdb.d/init-scripts" ]; then
    echo "Ejecutando scripts DDL..."
    psql -U ${POSTGRES_USER:-usuario} -d ${POSTGRES_DB:-avance_1_db} -f /docker-entrypoint-initdb.d/init-scripts/00_create_all_tables.sql
    echo "Modelo físico creado exitosamente!"
else
    echo "Directorio de scripts no encontrado. Saltando inicialización automática."
    echo "Puedes ejecutar los scripts manualmente desde dbt/sql/"
fi

