# Sistema de Gestión de Taller

Sistema flexible de gestión de taller adaptable a varias soluciones de almacenamiento de datos, con capacidades mejoradas de integración con Excel y OneDrive.

## Características

- Framework web Flask con almacenamiento de datos flexible
- Soporte para gestión de datos en Excel y OneDrive
- Importación y sincronización dinámica de datos
- Interfaz multilingüe
- Control de acceso basado en roles
- Informes de mantenimiento imprimibles con diseños personalizables

## Requisitos

- Python 3.8+
- Postgres (para la versión de base de datos SQL)
- Microsoft Excel (para la versión de Excel)

## Instalación

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno
4. Ejecutar la aplicación: `gunicorn main:app`

## Configuración

La aplicación requiere las siguientes variables de entorno:

- `DATABASE_URL`: URL de conexión a la base de datos PostgreSQL
- `SESSION_SECRET`: Clave secreta para las sesiones de Flask

## Despliegue

Este proyecto está configurado para desplegarse automáticamente en Railway.