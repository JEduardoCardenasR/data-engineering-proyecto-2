# Avance 2: Análisis de Preguntas de Negocio y Modelo Dimensional Kimball

## 📋 Descripción General

Este avance se enfoca en el análisis de negocio y el diseño del modelo dimensional para el Data Warehouse. Se han desarrollado notebooks de análisis que responden a preguntas de negocio específicas y se ha diseñado un modelo dimensional completo siguiendo la metodología de Kimball.

### Objetivos del Avance 2

1. **Análisis de Preguntas de Negocio**: Desarrollo de notebooks que responden a 20 preguntas de negocio organizadas en 4 categorías
2. **Diseño del Modelo Dimensional**: Creación de un modelo dimensional completo siguiendo la metodología de Kimball
3. **Documentación del Modelo**: Diagrama ER y documentación completa del modelo propuesto

### Características Principales

- **4 Notebooks de Análisis**: Cubren preguntas de negocio sobre ventas, pagos, usuarios y productos
- **Modelo Dimensional Kimball**: Diseño completo con hechos, dimensiones y estrategias SCD
- **Diagrama ER**: Representación visual del modelo dimensional propuesto
- **Documentación Completa**: Explicación detallada de decisiones de diseño y justificaciones

---

## 📊 Fase 1: Análisis de Preguntas de Negocio

### Objetivo

Desarrollar notebooks de análisis que respondan a preguntas de negocio específicas utilizando los datos cargados en PostgreSQL, proporcionando insights accionables para la toma de decisiones.

### Notebooks Implementados

#### 1. **preguntas_ventas.ipynb**

**Ubicación**: `preguntas_negocio/preguntas_ventas.ipynb`

**Preguntas Respondidas**:

1. ¿Cuáles son los productos más vendidos por volumen?
2. ¿Cuál es el ticket promedio por orden?
3. ¿Cuáles son las categorías con mayor número de productos vendidos?
4. ¿Qué día de la semana se generan más ventas?
5. ¿Cuántas órdenes se generan cada mes y cuál es su variación?

**Análisis Incluidos**:
- Top 10 productos más vendidos con visualizaciones
- Análisis estadístico del ticket promedio (promedio, mediana, desviación estándar)
- Distribución de ventas por categoría
- Análisis temporal de ventas (día de semana, mensual)
- Variación mes a mes de órdenes

**Visualizaciones**:
- Gráficos de barras horizontales para productos más vendidos
- Histogramas y box plots para distribución de tickets
- Gráficos de barras para categorías
- Gráficos de línea temporal para análisis mensual
- Gráficos de barras para días de la semana

#### 2. **preguntas_pagos_transacciones.ipynb**

**Ubicación**: `preguntas_negocio/preguntas_pagos_transacciones.ipynb`

**Preguntas Respondidas**:

1. ¿Cuáles son los métodos de pago más utilizados?
2. ¿Cuál es el monto promedio pagado por método de pago?
3. ¿Cuántas órdenes se pagaron usando más de un método de pago?
4. ¿Cuántos pagos están en estado 'Procesando' o 'Fallido'?
5. ¿Cuál es el monto total recaudado por mes?

**Análisis Incluidos**:
- Ranking de métodos de pago por frecuencia de uso
- Análisis comparativo de montos promedio por método
- Identificación de órdenes con múltiples métodos de pago
- Análisis de estados de pago problemáticos
- Evolución mensual de recaudación
- Heatmap de recaudación por método y mes

**Visualizaciones**:
- Gráficos de barras y pastel para métodos de pago
- Box plots para distribución de montos
- Gráficos de línea temporal para recaudación mensual
- Heatmaps para análisis multidimensional

#### 3. **preguntas_usuarios.ipynb**

**Ubicación**: `preguntas_negocio/preguntas_usuarios.ipynb`

**Preguntas Respondidas**:

1. ¿Cuántos usuarios se registran por mes?
2. ¿Cuántos usuarios han realizado más de una orden?
3. ¿Cuántos usuarios registrados no han hecho ninguna compra?
4. ¿Qué usuarios han gastado más en total?
5. ¿Cuántos usuarios han dejado reseñas?

**Análisis Incluidos**:
- Tendencias de registro de usuarios por mes
- Análisis de usuarios recurrentes (múltiples órdenes)
- Identificación de usuarios inactivos (sin compras)
- Ranking de usuarios por gasto total
- Análisis de participación en reseñas
- Distribución de número de órdenes por usuario

**Visualizaciones**:
- Gráficos de barras y línea para registros mensuales
- Gráficos de barras horizontales para top usuarios
- Gráficos de pastel para distribución de usuarios
- Scatter plots para relaciones entre variables
- Gráficos de distribución

#### 4. **preguntas_productos_stock.ipynb**

**Ubicación**: `preguntas_negocio/preguntas_productos_stock.ipynb`

**Preguntas Respondidas**:

1. ¿Qué productos tienen alto stock pero bajas ventas?
2. ¿Cuántos productos están actualmente fuera de stock?
3. ¿Cuáles son los productos peor calificados?
4. ¿Qué productos tienen mayor cantidad de reseñas?
5. ¿Qué categoría tiene el mayor valor económico vendido (no solo volumen)?

**Análisis Incluidos**:
- Identificación de productos con desequilibrio stock-ventas
- Análisis de estado de stock (fuera de stock, stock bajo, stock OK)
- Ranking de productos por calificación promedio
- Análisis de productos más reseñados
- Comparación de categorías por valor económico vs volumen
- Distribución de calificaciones

**Visualizaciones**:
- Scatter plots para stock vs ventas
- Gráficos de barras para estados de stock
- Gráficos de barras horizontales para rankings
- Gráficos de distribución de calificaciones
- Gráficos de pastel para distribución porcentual

### Características Comunes de los Notebooks

Todos los notebooks comparten las siguientes características:

- **Configuración Inicial**: Importación de bibliotecas y conexión a base de datos
- **Conexión a BD**: Uso de `DBConnector` (patrón Singleton) para conexión única
- **Consultas SQL**: Consultas optimizadas para cada pregunta de negocio
- **Visualizaciones**: Gráficos profesionales usando matplotlib y seaborn
- **Análisis Estadístico**: Resúmenes estadísticos y métricas clave
- **Documentación**: Explicaciones claras de cada análisis

### Bibliotecas Utilizadas

- `pandas`: Manipulación y análisis de datos
- `numpy`: Operaciones numéricas
- `matplotlib`: Visualizaciones básicas
- `seaborn`: Visualizaciones estadísticas avanzadas
- `sqlalchemy`: Conexión a base de datos
- `database.db_connector`: Conexión única a PostgreSQL

### Estado de la Fase 1

- [x] Notebook de preguntas de ventas implementado
- [x] Notebook de preguntas de pagos y transacciones implementado
- [x] Notebook de preguntas de usuarios implementado
- [x] Notebook de preguntas de productos y stock implementado
- [x] Visualizaciones y análisis completos para todas las preguntas
- [x] Documentación y explicaciones incluidas

---

## 🎯 Fase 2: Diseño del Modelo Dimensional Kimball

### Objetivo

Diseñar un modelo dimensional completo siguiendo la metodología de Kimball que permita responder a todas las preguntas de negocio identificadas, con un diseño optimizado para análisis y consultas analíticas.

### Notebook Implementado

#### **modelo_dimensional_kimball.ipynb**

**Ubicación**: `modelo_dimensional_kimball.ipynb` (raíz del proyecto)

**Contenido Completo**:

1. **Revisión de Preguntas de Negocio**
   - Compilación de las 20 preguntas de negocio identificadas
   - Organización por categorías (Ventas, Pagos, Usuarios, Productos)

2. **Identificación de Medidas y Dimensiones**
   - Análisis de información necesaria
   - Identificación de medidas cuantitativas (hechos)
   - Identificación de dimensiones descriptivas

3. **Esquema Conceptual del Modelo**
   - Entidades principales identificadas
   - Relaciones y cardinalidades
   - Diagrama conceptual simplificado

4. **Modelo Lógico - Hechos y Dimensiones**
   - **4 Tablas de Hechos**:
     - `Fact_Ventas`: Hecho principal para análisis de ventas
     - `Fact_Pagos`: Hecho para análisis de transacciones de pago
     - `Fact_Resenas`: Hecho para análisis de satisfacción del cliente
     - `Fact_Usuarios`: Tabla acumulativa para métricas de usuarios
   
   - **8 Dimensiones**:
     - `Dim_Tiempo`: Dimensión de tiempo (estática)
     - `Dim_Producto`: Dimensión de productos (SCD Tipo 2)
     - `Dim_Cliente`: Dimensión de clientes (SCD Tipo 2)
     - `Dim_Categoria`: Dimensión de categorías (SCD Tipo 1)
     - `Dim_Metodo_Pago`: Dimensión de métodos de pago (SCD Tipo 1)
     - `Dim_Estado_Orden`: Dimensión de estados de orden
     - `Dim_Estado_Pago`: Dimensión de estados de pago
     - `Dim_Geografia`: Dimensión geográfica

5. **Análisis de Dimensiones que Requieren Historial (SCD)**
   - **SCD Tipo 2** (Historial completo):
     - `Dim_Producto`: Para historial de precios y stock
     - `Dim_Cliente`: Para historial de segmentación
   
   - **SCD Tipo 1** (Sin historial):
     - `Dim_Categoria`: Cambios raros
     - `Dim_Metodo_Pago`: Cambios raros
     - `Dim_Estado_Orden`: Valores fijos
     - `Dim_Estado_Pago`: Valores fijos
   
   - **Estática**:
     - `Dim_Tiempo`: Pre-poblada

6. **Estructura del Diagrama ER del Modelo Lógico**
   - Definición completa de tablas de hechos con medidas
   - Definición completa de tablas de dimensiones con atributos
   - Diagrama ER visual del modelo dimensional
   - Relaciones clave entre hechos y dimensiones

7. **Explicación de Decisiones de Diseño**
   - Justificación de elección de hechos centrales
   - Justificación de estrategias SCD
   - Decisiones sobre granularidad
   - Decisiones sobre claves (surrogate keys vs natural keys)
   - Consideraciones de performance (índices, particionamiento)

8. **Mapeo de Preguntas de Negocio a Hechos y Dimensiones**
   - Tabla completa que relaciona cada pregunta con:
     - Hecho utilizado
     - Dimensiones necesarias
     - Medidas requeridas

9. **Ejemplos de Consultas SQL**
   - 7 consultas SQL de ejemplo para el modelo propuesto
   - Consultas para productos más vendidos
   - Consultas para ticket promedio
   - Consultas para métodos de pago
   - Consultas para análisis histórico

10. **Consideraciones Adicionales y Mejoras Futuras**
    - Optimizaciones adicionales (vistas materializadas, índices)
    - Extensiones futuras (hechos y dimensiones adicionales)
    - Proceso ETL propuesto
    - Métricas de calidad
    - Documentación recomendada

11. **Resumen Ejecutivo**
    - Resumen del modelo propuesto
    - Capacidades del modelo
    - Ventajas del diseño
    - Próximos pasos

### Características del Modelo Dimensional

#### Hechos Centrales

**Fact_Ventas**:
- **Granularidad**: Una fila por línea de detalle de orden
- **Medidas**: `cantidad_vendida`, `precio_unitario`, `subtotal`, `descuento`, `total_linea`
- **Dimensiones**: Tiempo, Producto, Cliente, Categoría, Estado Orden, Geografía

**Fact_Pagos**:
- **Granularidad**: Una fila por transacción de pago
- **Medidas**: `monto_pagado`
- **Dimensiones**: Tiempo, Cliente, Método Pago, Estado Pago

**Fact_Resenas**:
- **Granularidad**: Una fila por reseña
- **Medidas**: `calificacion`, `tiene_comentario`, `longitud_comentario`
- **Dimensiones**: Tiempo, Producto, Cliente, Categoría

**Fact_Usuarios**:
- **Granularidad**: Una fila por usuario (tabla acumulativa)
- **Medidas**: `total_ordenes`, `total_gastado`, `total_resenas`, `ticket_promedio`
- **Dimensiones**: Cliente, Tiempo (registro, primera compra, última compra)

#### Estrategias SCD Implementadas

| Dimensión | Tipo SCD | Justificación |
|-----------|----------|--------------|
| Dim_Tiempo | Estática | No cambia |
| Dim_Producto | Tipo 2 | Precio y stock cambian frecuentemente |
| Dim_Cliente | Tipo 2 | Segmento y datos pueden cambiar |
| Dim_Categoria | Tipo 1 | Cambios raros, no requieren historial |
| Dim_Metodo_Pago | Tipo 1 | Cambios raros |
| Dim_Estado_Orden | Tipo 1 | Valores fijos |
| Dim_Estado_Pago | Tipo 1 | Valores fijos |
| Dim_Geografia | Tipo 1/2 | Depende de necesidad de historial |

### Estado de la Fase 2

- [x] Revisión completa de preguntas de negocio
- [x] Identificación de medidas y dimensiones
- [x] Esquema conceptual del modelo
- [x] Modelo lógico con hechos y dimensiones
- [x] Análisis de dimensiones que requieren historial
- [x] Estrategias SCD propuestas con justificación
- [x] Estructura completa del diagrama ER
- [x] Explicación detallada de decisiones de diseño
- [x] Mapeo de preguntas a hechos y dimensiones
- [x] Ejemplos de consultas SQL
- [x] Consideraciones adicionales y mejoras futuras
- [x] Resumen ejecutivo

---

## 📐 Diagrama Entidad-Relación (DER)

### Ubicación

**Archivo**: `assets/DER.png`

**Ubicación**: `assets/DER.png` (carpeta en la raíz del proyecto)

### Descripción

El diagrama ER representa visualmente el modelo dimensional propuesto, mostrando:

- **Tablas de Hechos**: Fact_Ventas, Fact_Pagos, Fact_Resenas, Fact_Usuarios
- **Tablas de Dimensiones**: Dim_Tiempo, Dim_Producto, Dim_Cliente, Dim_Categoria, Dim_Metodo_Pago, Dim_Estado_Orden, Dim_Estado_Pago, Dim_Geografia
- **Relaciones**: Conexiones entre hechos y dimensiones (muchos a uno)
- **Claves**: Identificación de claves primarias y foráneas
- **Estrategias SCD**: Indicación de dimensiones con SCD Tipo 2

### Visualización en el Notebook

El diagrama puede ser visualizado en el notebook `modelo_dimensional_kimball.ipynb` usando el siguiente código:

```python
from IPython.display import Image, display
import os

# Obtener la ruta del archivo
ruta_der = os.path.join('assets', 'DER.png')

# Verificar que el archivo existe
if os.path.exists(ruta_der):
    display(Image(filename=ruta_der, width=1200))
else:
    print(f"Error: No se encontró el archivo en {ruta_der}")
```

### Estado del DER

- [x] Diagrama ER creado
- [x] Diagrama incluido en carpeta `assets/`
- [x] Código para visualización en notebook proporcionado

---

## 📁 Estructura del Proyecto Actualizada

```
Proyecto Integrador/
├── assets/                          # Recursos del proyecto
│   └── DER.png                     # Diagrama Entidad-Relación del modelo dimensional
│
├── preguntas_negocio/               # Notebooks de análisis de negocio
│   ├── preguntas_ventas.ipynb       # Análisis de ventas (5 preguntas)
│   ├── preguntas_pagos_transacciones.ipynb  # Análisis de pagos (5 preguntas)
│   ├── preguntas_usuarios.ipynb     # Análisis de usuarios (5 preguntas)
│   └── preguntas_productos_stock.ipynb      # Análisis de productos (5 preguntas)
│
├── modelo_dimensional_kimball.ipynb # Diseño del modelo dimensional completo
│
├── pipeline/                        # Módulo principal del ETL (Avance 1)
│   ├── models/                      # Modelos ORM y creación de tablas
│   ├── etl/                         # Módulo ETL
│   ├── utils/                       # Módulo de utilidades
│   ├── scripts/                     # Scripts ejecutables
│   └── notebooks/                   # Notebooks de análisis EDA
│
├── database/                        # Conexión a base de datos
│   └── db_connector.py             # DBConnector (Singleton)
│
├── data/                           # Datos del proyecto
│   ├── CSV/                        # Archivos CSV originales
│   └── sql/                        # Scripts SQL
│
├── Readme_Avance_1.md             # Documentación del Avance 1
└── Readme_Avance_2.md             # Este archivo
```

---

## 🎯 Resumen de Entregables

### Notebooks de Análisis de Negocio

| Notebook | Preguntas | Categoría |
|----------|-----------|-----------|
| `preguntas_ventas.ipynb` | 5 | Ventas |
| `preguntas_pagos_transacciones.ipynb` | 5 | Pagos y Transacciones |
| `preguntas_usuarios.ipynb` | 5 | Usuarios |
| `preguntas_productos_stock.ipynb` | 5 | Productos y Stock |
| **Total** | **20** | **4 categorías** |

### Modelo Dimensional

| Componente | Cantidad | Descripción |
|------------|----------|-------------|
| **Tablas de Hechos** | 4 | Fact_Ventas, Fact_Pagos, Fact_Resenas, Fact_Usuarios |
| **Dimensiones** | 8 | Dim_Tiempo, Dim_Producto, Dim_Cliente, Dim_Categoria, Dim_Metodo_Pago, Dim_Estado_Orden, Dim_Estado_Pago, Dim_Geografia |
| **Estrategias SCD** | 3 tipos | Tipo 1, Tipo 2, Estática |
| **Ejemplos SQL** | 7 | Consultas de ejemplo para el modelo |

### Documentación

- ✅ README completo del Avance 2
- ✅ Notebook de modelo dimensional con documentación completa
- ✅ Diagrama ER visual (DER.png)
- ✅ Explicación de decisiones de diseño
- ✅ Mapeo de preguntas a hechos y dimensiones

---

## 🔍 Capacidades del Modelo Dimensional

El modelo dimensional propuesto permite responder a **todas las 20 preguntas de negocio** identificadas:

### ✅ Ventas (5 preguntas)
- Productos más vendidos por volumen
- Ticket promedio por orden
- Categorías con mayor número de productos vendidos
- Día de la semana con más ventas
- Órdenes por mes y variación

### ✅ Pagos y Transacciones (5 preguntas)
- Métodos de pago más utilizados
- Monto promedio por método de pago
- Órdenes con múltiples métodos de pago
- Pagos en estado Procesando/Fallido
- Monto total recaudado por mes

### ✅ Usuarios (5 preguntas)
- Usuarios registrados por mes
- Usuarios con más de una orden
- Usuarios sin compras
- Usuarios que más han gastado
- Usuarios que han dejado reseñas

### ✅ Productos y Stock (5 preguntas)
- Productos con alto stock y bajas ventas
- Productos fuera de stock
- Productos peor calificados
- Productos con más reseñas
- Categoría con mayor valor económico

---

## 📚 Referencias

- [The Data Warehouse Toolkit - Ralph Kimball](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Matplotlib Documentation](https://matplotlib.org/)
- [Seaborn Documentation](https://seaborn.pydata.org/)

---

## 📝 Notas Técnicas

### Requisitos para Ejecutar los Notebooks

1. **Entorno Virtual Activado**: Asegúrate de tener el entorno virtual activado
2. **Dependencias Instaladas**: Todas las dependencias del `requirements.txt` deben estar instaladas
3. **Base de Datos Configurada**: La base de datos PostgreSQL debe estar configurada y accesible
4. **Archivo .env**: Debe contener las credenciales de conexión a la base de datos

### Ejecución de Notebooks

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# o
source venv/bin/activate      # Linux/Mac

# Iniciar Jupyter
jupyter notebook

# O usar JupyterLab
jupyter lab
```

### Orden Recomendado de Ejecución

1. Primero ejecutar los notebooks de preguntas de negocio para entender los datos
2. Luego revisar el notebook de modelo dimensional para entender el diseño propuesto
3. Finalmente, visualizar el DER para tener una vista completa del modelo

---

**Fecha de Documentación**: Enero 2025  
**Versión**: 1.0 - Avance 2 Completado  
**Autor**: Proyecto Integrador - Módulo 2

