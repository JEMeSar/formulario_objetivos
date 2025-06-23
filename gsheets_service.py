import gspread
import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import time

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

def cargar_credenciales():
    """Carga las credenciales desde los secretos de Streamlit"""
    try:
        info = st.secrets["gcp_service_account"]
        return Credentials.from_service_account_info(info, scopes=SCOPE)
    except Exception as e:
        st.error(f"Error cargando credenciales: {e}")
        return None

def inicializar_cliente():
    """Inicializa el cliente de Google Sheets"""
    try:
        creds = cargar_credenciales()
        if creds is None:
            return None
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error inicializando cliente: {e}")
        return None

def cargar_hoja_estado():
    """Carga la hoja 'estado' del Google Sheets, la crea si no existe"""
    try:
        client = inicializar_cliente()
        if client is None:
            return None
        
        sheet = client.open_by_key(st.secrets["sheet_id"])
        
        try:
            # Intentar cargar la hoja existente
            return sheet.worksheet("estado")
        except gspread.WorksheetNotFound:
            # Si no existe, crearla
            st.warning("La hoja 'estado' no existe. Creándola automáticamente...")
            worksheet = sheet.add_worksheet(title="estado", rows="1000", cols="10")
            
            # Agregar encabezados
            headers = [
                "id_entrada", "timestamp", "area", "agrupacion", 
                "objetivo", "indicador", "responsable", "estado", "fecha_cambio_estado"
            ]
            worksheet.append_row(headers)
            st.success("Hoja 'estado' creada correctamente con los encabezados necesarios.")
            return worksheet
            
    except Exception as e:
        st.error(f"Error conectando con Google Sheets (Objetivos): {e}")
        return None

def guardar_objetivo(id_entrada, timestamp, area, agrupacion, objetivo, indicador, responsable, estado):
    """Guarda un objetivo en la hoja de estado"""
    hoja = cargar_hoja_estado()
    if hoja is None:
        raise Exception("No se pudo conectar con la hoja de objetivos")
    
    try:
        # Validar que los campos obligatorios no estén vacíos
        if not all([objetivo.strip(), indicador.strip(), responsable.strip()]):
            raise Exception("Todos los campos (objetivo, indicador, responsable) son obligatorios")
        
        # Intentar guardar con reintentos en caso de error temporal
        max_intentos = 3
        for intento in range(max_intentos):
            try:
                hoja.append_row([
                    str(id_entrada),
                    str(timestamp),
                    str(area),
                    str(agrupacion),
                    str(objetivo),
                    str(indicador),
                    str(responsable),
                    str(estado),
                    str(timestamp)  # fecha_cambio_estado
                ])
                return True
            except Exception as e:
                if intento < max_intentos - 1:
                    time.sleep(1)  # Esperar un segundo antes del siguiente intento
                    continue
                else:
                    raise e
    except Exception as e:
        raise Exception(f"Error al guardar objetivo: {e}")

def cargar_areas_agrupaciones():
    """Carga las áreas y agrupaciones desde Google Sheets, crea la hoja si no existe"""
    try:
        client = inicializar_cliente()
        if client is None:
            return pd.DataFrame()
        
        sheet = client.open_by_key(st.secrets["sheet_id"])
        
        try:
            ws = sheet.worksheet("Areas_Agrupaciones")
        except gspread.WorksheetNotFound:
            # Crear la hoja si no existe
            st.warning("La hoja 'Areas_Agrupaciones' no existe. Creándola automáticamente...")
            ws = sheet.add_worksheet(title="Areas_Agrupaciones", rows="100", cols="5")
            
            # Agregar encabezados y algunos datos de ejemplo
            headers = ["Area", "Agrupacion_Funcional"]
            ws.append_row(headers)
            
            # Datos de ejemplo
            ejemplos = [
                ["ALCALDÍA - OMAC", "Alcaldía"],
                ["RECURSOS HUMANOS", "Personal"],
                ["HACIENDA", "Contabilidad"],
                ["URBANISMO", "Licencias"]
            ]
            for ejemplo in ejemplos:
                ws.append_row(ejemplo)
            
            st.success("Hoja 'Areas_Agrupaciones' creada con datos de ejemplo.")
        
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        
        # Limpiar datos y eliminar filas vacías
        if not df.empty:
            df = df.dropna(subset=['Area', 'Agrupacion_Funcional'])
            # Limpiar espacios en blanco
            df['Area'] = df['Area'].astype(str).str.strip()
            df['Agrupacion_Funcional'] = df['Agrupacion_Funcional'].astype(str).str.strip()
            # Eliminar filas donde Area o Agrupacion_Funcional estén vacíos
            df = df[(df['Area'] != '') & (df['Agrupacion_Funcional'] != '')]
        
        return df
    except Exception as e:
        st.error(f"Error conectando con Google Sheets (Áreas/Agrupaciones): {e}")
        return pd.DataFrame()

def guardar_nueva_agrupacion(area, nueva_agrupacion):
    """Guarda una nueva agrupación funcional"""
    try:
        if not area.strip() or not nueva_agrupacion.strip():
            st.error("Área y agrupación no pueden estar vacías")
            return False
        
        client = inicializar_cliente()
        if client is None:
            return False
        
        sheet = client.open_by_key(st.secrets["sheet_id"])
        ws = sheet.worksheet("Areas_Agrupaciones")
        
        # Verificar si la combinación ya existe
        existing_data = ws.get_all_records()
        for row in existing_data:
            if (str(row.get('Area', '')).strip().lower() == area.strip().lower() and 
                str(row.get('Agrupacion_Funcional', '')).strip().lower() == nueva_agrupacion.strip().lower()):
                st.warning("Esta combinación de área y agrupación ya existe")
                return False
        
        ws.append_row([area.strip(), nueva_agrupacion.strip()])
        st.success("Nueva agrupación funcional guardada correctamente.")
        return True
    except Exception as e:
        st.error(f"No se pudo guardar la nueva agrupación funcional: {e}")
        return False