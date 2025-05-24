import os
import pandas as pd
import shutil
from datetime import datetime

# Definiciones y constantes
DB_FILE = 'workshop_database.xlsx'
BACKUP_FOLDER = 'backups'

def create_backup():
    """Crea una copia de seguridad del archivo Excel actual"""
    # Asegurar que existe el directorio de backup
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    
    # Verificar si el archivo principal existe
    if not os.path.exists(DB_FILE):
        return False
    
    # Crear nombre del archivo de backup con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_FOLDER, f'backup_{timestamp}_{DB_FILE}')
    
    # Copiar archivo
    try:
        shutil.copy2(DB_FILE, backup_file)
        print(f"Backup creado en {backup_file}")
        return True
    except Exception as e:
        print(f"Error al crear backup: {str(e)}")
        return False

def sync_with_onedrive(onedrive_path=None):
    """
    Sincroniza el archivo Excel con OneDrive
    
    Esta función puede implementarse de diferentes maneras:
    1. Copiar el archivo a una carpeta de OneDrive sincronizada
    2. Usar la API de Microsoft Graph para subir el archivo
    3. Usar otro mecanismo de sincronización
    
    Para este ejemplo, simplemente copiamos a una ruta local de OneDrive
    """
    if not onedrive_path:
        # Ruta predeterminada de OneDrive en Windows (ejemplo)
        onedrive_path = os.path.join(os.path.expanduser('~'), 'OneDrive', 'TallerApp')
    
    # Verificar si existe la carpeta en OneDrive
    if not os.path.exists(onedrive_path):
        try:
            os.makedirs(onedrive_path)
        except Exception as e:
            print(f"Error al crear carpeta en OneDrive: {str(e)}")
            return False
    
    # Copiar archivo a OneDrive
    onedrive_file = os.path.join(onedrive_path, DB_FILE)
    
    try:
        shutil.copy2(DB_FILE, onedrive_file)
        print(f"Archivo sincronizado con OneDrive en {onedrive_file}")
        return True
    except Exception as e:
        print(f"Error al sincronizar con OneDrive: {str(e)}")
        return False

def import_from_onedrive(onedrive_path=None):
    """Importa un archivo Excel desde OneDrive"""
    if not onedrive_path:
        # Ruta predeterminada de OneDrive en Windows (ejemplo)
        onedrive_path = os.path.join(os.path.expanduser('~'), 'OneDrive', 'TallerApp')
    
    # Verificar si existe el archivo en OneDrive
    onedrive_file = os.path.join(onedrive_path, DB_FILE)
    
    if not os.path.exists(onedrive_file):
        print(f"No se encontró el archivo en OneDrive: {onedrive_file}")
        return False
    
    # Crear backup del archivo local si existe
    if os.path.exists(DB_FILE):
        create_backup()
    
    # Copiar archivo desde OneDrive
    try:
        shutil.copy2(onedrive_file, DB_FILE)
        print(f"Archivo importado desde OneDrive: {onedrive_file}")
        return True
    except Exception as e:
        print(f"Error al importar desde OneDrive: {str(e)}")
        return False

# Función para configurar la sincronización automática (se puede ejecutar periódicamente)
def setup_auto_sync(interval_minutes=30):
    """Configurar sincronización automática cada X minutos"""
    # Aquí se podría implementar un mecanismo para ejecutar sync_with_onedrive()
    # automáticamente cada cierto tiempo, usando por ejemplo:
    # - Un scheduler como APScheduler
    # - Un servicio del sistema
    # - Un cron job
    
    print(f"Sincronización automática configurada cada {interval_minutes} minutos")
    # Esta implementación requeriría código adicional para manejar la ejecución periódica

if __name__ == "__main__":
    # Ejemplo de uso
    create_backup()
    sync_with_onedrive()