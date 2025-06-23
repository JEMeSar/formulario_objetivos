import streamlit as st
import pandas as pd
from datetime import datetime
import io
import uuid
import time
from gsheets_service import cargar_areas_agrupaciones, guardar_objetivo, guardar_nueva_agrupacion

# Configuración de la página
st.set_page_config(
    page_title="Gestión de Objetivos de Productividad",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la interfaz
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e7bcf 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2e7bcf;
    }
    
    .objective-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    
    .data-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def render_header():
    """Renderiza el header principal de la aplicación"""
    # Intentar mostrar el logo
    try:
        st.image("logo_ayuntamiento_azul.png", width=150)
    except:
        # Si no encuentra el logo, mostrar solo texto
        pass
    
    st.markdown("""
    <div class='main-header'>
        <h1>Gestión de Objetivos de Productividad</h1>
        <p>Departamento de Recursos Humanos</p>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(title, value, icon="📊"):
    """Renderiza una tarjeta de métrica"""
    st.markdown(f"""
    <div class='metric-container'>
        <h3 style='margin: 0; color: #2e7bcf; font-size: 1.2rem;'>{icon} {title}</h3>
        <p style='margin: 0; font-size: 2rem; font-weight: bold; color: #1f4e79;'>{value}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header principal
    render_header()
    
    # Inicializar estado de la sesión
    if "objetivos" not in st.session_state:
        st.session_state.objetivos = [""]
        st.session_state.indicadores = [""]
        st.session_state.responsables = [""]
    
    # Crear pestañas
    tab1, tab2 = st.tabs(["📝 Crear Objetivos", "📊 Ver Objetivos"])
    
    with tab1:
        render_crear_objetivos()
    
    with tab2:
        render_ver_objetivos()

def render_crear_objetivos():
    """Renderiza la pestaña de creación de objetivos"""
    
    # Cargar áreas y agrupaciones
    with st.spinner("🔄 Cargando áreas y agrupaciones..."):
        areas_df = cargar_areas_agrupaciones()

    if areas_df.empty:
        st.error("No se pudieron cargar las áreas y agrupaciones. Verifica la conexión con Google Sheets.")
        st.stop()

    # Sección de configuración
    st.markdown("### ⚙️ Configuración")
    col1, col2 = st.columns(2)
    
    with col1:
        area = st.selectbox(
            "🏢 Área funcional", 
            sorted(areas_df["Area"].unique()),
            help="Selecciona el área funcional correspondiente"
        )

    with col2:
        agrupaciones_filtradas = areas_df[areas_df["Area"] == area]["Agrupacion_Funcional"].unique()
        agrupar = st.selectbox(
            "📋 Agrupación funcional", 
            sorted(agrupaciones_filtradas),
            help="Selecciona la agrupación funcional específica"
        )

    # Sección para agregar nueva agrupación
    with st.expander("➕ Agregar nueva agrupación funcional"):
        nueva_agrupacion = st.text_input("Nueva agrupación funcional", placeholder="Escribe el nombre de la nueva agrupación...")
        if st.button("💾 Guardar nueva agrupación funcional", type="primary"):
            if nueva_agrupacion.strip():
                if guardar_nueva_agrupacion(area, nueva_agrupacion):
                    st.rerun()
            else:
                st.warning("⚠️ Escribe un nombre para la nueva agrupación funcional")

    st.divider()
    
    # Sección de objetivos
    st.markdown("### 🎯 Objetivos")
    render_objetivos_form()
    
    # Botones de control
    render_control_buttons(area, agrupar)
    
    st.divider()
    
    # Sección de descarga
    render_download_section(area, agrupar)

def render_objetivos_form():
    """Renderiza el formulario de objetivos"""
    for i in range(len(st.session_state.objetivos)):
        with st.container():
            st.markdown(f"<div class='objective-card'>", unsafe_allow_html=True)
            st.markdown(f"#### 🎯 Objetivo {i+1}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.session_state.objetivos[i] = st.text_area(
                    f"Descripción del objetivo {i+1}", 
                    value=st.session_state.objetivos[i], 
                    key=f"obj_{i}",
                    height=100,
                    help="Describe claramente el objetivo a alcanzar",
                    placeholder="Ejemplo: Mejorar la eficiencia del proceso de atención ciudadana..."
                )
            
            with col2:
                st.session_state.indicadores[i] = st.text_input(
                    f"📊 Indicador {i+1}", 
                    value=st.session_state.indicadores[i], 
                    key=f"ind_{i}",
                    help="Métrica para medir el cumplimiento",
                    placeholder="Ejemplo: % de satisfacción"
                )
                st.session_state.responsables[i] = st.text_input(
                    f"👤 Responsable {i+1}", 
                    value=st.session_state.responsables[i], 
                    key=f"resp_{i}",
                    help="Persona responsable del objetivo",
                    placeholder="Nombre del responsable"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")

def render_control_buttons(area, agrupar):
    """Renderiza los botones de control"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("➕ Nuevo objetivo", type="secondary", use_container_width=True):
            st.session_state.objetivos.append("")
            st.session_state.indicadores.append("")
            st.session_state.responsables.append("")
            st.rerun()

    with col2:
        if st.button("🗑️ Borrar último", type="secondary", use_container_width=True):
            if len(st.session_state.objetivos) > 1:
                st.session_state.objetivos.pop()
                st.session_state.indicadores.pop()
                st.session_state.responsables.pop()
                st.rerun()
            else:
                st.warning("⚠️ Debe mantener al menos un objetivo")

    with col3:
        if st.button("♻️ Reiniciar", type="secondary", use_container_width=True):
            st.session_state.objetivos = [""]
            st.session_state.indicadores = [""]
            st.session_state.responsables = [""]
            st.rerun()

    with col4:
        if st.button("🚀 Enviar objetivos", type="primary", use_container_width=True):
            procesar_envio_objetivos(area, agrupar)

def procesar_envio_objetivos(area, agrupar):
    """Procesa el envío de objetivos"""
    objetivos_validos = []
    for i, (obj, ind, resp) in enumerate(zip(
        st.session_state.objetivos,
        st.session_state.indicadores,
        st.session_state.responsables
    )):
        if obj.strip() and ind.strip() and resp.strip():
            objetivos_validos.append((obj.strip(), ind.strip(), resp.strip()))
        elif obj.strip() or ind.strip() or resp.strip():
            st.warning(f"⚠️ El objetivo {i+1} está incompleto. Complete todos los campos o déjelos vacíos.")
    
    if not objetivos_validos:
        st.error("❌ No hay objetivos válidos para guardar. Complete al menos un objetivo con todos sus campos.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        id_entrada = uuid.uuid4().hex[:8]
        
        errores = []
        objetivos_guardados = 0
        
        with st.spinner(f"💾 Guardando {len(objetivos_validos)} objetivos..."):
            for obj, ind, resp in objetivos_validos:
                try:
                    guardar_objetivo(
                        id_entrada=id_entrada,
                        timestamp=timestamp,
                        area=area,
                        agrupacion=agrupar,
                        objetivo=obj,
                        indicador=ind,
                        responsable=resp,
                        estado="ACTIVO"
                    )
                    objetivos_guardados += 1
                except Exception as e:
                    errores.append(f"Error guardando objetivo: {e}")
        
        if objetivos_guardados > 0:
            st.success(f"✅ {objetivos_guardados} objetivos guardados correctamente (ID: {id_entrada})")
            
            if not errores:
                st.session_state.objetivos = [""]
                st.session_state.indicadores = [""]
                st.session_state.responsables = [""]
                time.sleep(2)
                st.rerun()
        
        if errores:
            st.error("❌ Algunos objetivos no se pudieron guardar:")
            for error in errores:
                st.error(f"• {error}")

def render_download_section(area, agrupar):
    """Renderiza la sección de descarga"""
    st.markdown("### 📥 Descarga")
    
    if st.button("⬇️ Descargar en Excel", type="secondary", use_container_width=True):
        objetivos_con_contenido = []
        for obj, ind, resp in zip(
            st.session_state.objetivos,
            st.session_state.indicadores,
            st.session_state.responsables
        ):
            if obj.strip() or ind.strip() or resp.strip():
                objetivos_con_contenido.append({
                    "Área": area,
                    "Agrupación": agrupar,
                    "Objetivo": obj.strip(),
                    "Indicador": ind.strip(),
                    "Responsable": resp.strip()
                })
        
        if objetivos_con_contenido:
            df_descarga = pd.DataFrame(objetivos_con_contenido)
            
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df_descarga.to_excel(writer, index=False, sheet_name="Objetivos")
            
            st.download_button(
                label="📥 Descargar Excel",
                data=excel_buffer.getvalue(),
                file_name=f"objetivos_productividad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.warning("⚠️ No hay objetivos para descargar")
    
    # Información adicional
    with st.expander("ℹ️ Información"):
        st.info("""
        **Instrucciones de uso:**
        
        **📝 Crear Objetivos:**
        1. Selecciona el área y agrupación funcional
        2. Completa los objetivos con su indicador y responsable
        3. Usa los botones para agregar, eliminar o reiniciar objetivos
        4. Envía los objetivos cuando estén completos
        5. Descarga un Excel con los objetivos actuales si es necesario
        
        **Campos obligatorios:** Objetivo, Indicador y Responsable
        """)

def cargar_todos_objetivos_simple():
    """Función simplificada para cargar objetivos (fallback)"""
    try:
        from gsheets_service import cargar_hoja_estado
        hoja = cargar_hoja_estado()
        if hoja is None:
            return pd.DataFrame()
        
        data = hoja.get_all_records()
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.dropna(how='all')
            string_columns = ['area', 'agrupacion', 'objetivo', 'indicador', 'responsable', 'estado']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
            
            df = df[
                (df['objetivo'].notna()) & 
                (df['objetivo'] != '') & 
                (df['objetivo'] != 'nan')
            ]
            
            if 'timestamp' in df.columns:
                df = df.sort_values('timestamp', ascending=False)
        
        return df
    except Exception as e:
        st.error(f"Error cargando objetivos: {e}")
        return pd.DataFrame()

def render_ver_objetivos():
    """Renderiza la pestaña de visualización de objetivos"""
    st.markdown("### 📊 Todos los Objetivos")
    
    # Cargar datos
    with st.spinner("🔄 Cargando objetivos..."):
        try:
            # Intentar importar la función actualizada
            from gsheets_service import cargar_todos_objetivos
            df_objetivos = cargar_todos_objetivos()
        except ImportError:
            # Si no existe, usar la función simplificada
            df_objetivos = cargar_todos_objetivos_simple()
    
    if df_objetivos.empty:
        st.info("ℹ️ No hay objetivos guardados. Crea algunos objetivos en la pestaña 'Crear Objetivos' para verlos aquí.")
        return
    
    # Mostrar métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Total Objetivos", len(df_objetivos), "🎯")
    
    with col2:
        areas_unicas = df_objetivos['area'].nunique() if 'area' in df_objetivos.columns else 0
        render_metric_card("Áreas", areas_unicas, "🏢")
    
    with col3:
        responsables_unicos = df_objetivos['responsable'].nunique() if 'responsable' in df_objetivos.columns else 0
        render_metric_card("Responsables", responsables_unicos, "👤")
    
    with col4:
        if 'estado' in df_objetivos.columns:
            objetivos_activos = len(df_objetivos[df_objetivos['estado'] == 'ACTIVO'])
        else:
            objetivos_activos = len(df_objetivos)
        render_metric_card("Activos", objetivos_activos, "✅")
    
    st.divider()
    
    # Filtros
    st.markdown("### 🔍 Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'area' in df_objetivos.columns:
            areas_disponibles = ['Todas'] + sorted(df_objetivos['area'].unique().tolist())
            area_filtro = st.selectbox("🏢 Filtrar por Área", areas_disponibles)
        else:
            area_filtro = 'Todas'
    
    with col2:
        if 'estado' in df_objetivos.columns:
            estados_disponibles = ['Todos'] + sorted(df_objetivos['estado'].unique().tolist())
            estado_filtro = st.selectbox("📊 Filtrar por Estado", estados_disponibles)
        else:
            estado_filtro = 'Todos'
    
    with col3:
        if 'responsable' in df_objetivos.columns:
            responsables_disponibles = ['Todos'] + sorted(df_objetivos['responsable'].unique().tolist())
            responsable_filtro = st.selectbox("👤 Filtrar por Responsable", responsables_disponibles)
        else:
            responsable_filtro = 'Todos'
    
    # Aplicar filtros
    df_filtrado = df_objetivos.copy()
    
    if area_filtro != 'Todas' and 'area' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['area'] == area_filtro]
    
    if estado_filtro != 'Todos' and 'estado' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['estado'] == estado_filtro]
    
    if responsable_filtro != 'Todos' and 'responsable' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['responsable'] == responsable_filtro]
    
    st.divider()
    
    # Mostrar tabla
    if df_filtrado.empty:
        st.info("🔍 No se encontraron objetivos con los filtros aplicados.")
    else:
        st.markdown(f"### 📋 Objetivos Encontrados ({len(df_filtrado)})")
        
        # Preparar datos para mostrar
        columnas_mostrar = []
        nombres_columnas = []
        
        if 'timestamp' in df_filtrado.columns:
            columnas_mostrar.append('timestamp')
            nombres_columnas.append('Fecha')
        if 'area' in df_filtrado.columns:
            columnas_mostrar.append('area')
            nombres_columnas.append('Área')
        if 'agrupacion' in df_filtrado.columns:
            columnas_mostrar.append('agrupacion')
            nombres_columnas.append('Agrupación')
        if 'objetivo' in df_filtrado.columns:
            columnas_mostrar.append('objetivo')
            nombres_columnas.append('Objetivo')
        if 'indicador' in df_filtrado.columns:
            columnas_mostrar.append('indicador')
            nombres_columnas.append('Indicador')
        if 'responsable' in df_filtrado.columns:
            columnas_mostrar.append('responsable')
            nombres_columnas.append('Responsable')
        if 'estado' in df_filtrado.columns:
            columnas_mostrar.append('estado')
            nombres_columnas.append('Estado')
        
        df_display = df_filtrado[columnas_mostrar].copy()
        df_display.columns = nombres_columnas
        
        if 'Fecha' in df_display.columns:
            try:
                df_display['Fecha'] = pd.to_datetime(df_display['Fecha']).dt.strftime('%d/%m/%Y %H:%M')
            except:
                pass
        
        # Mostrar tabla con estilo
        st.markdown("<div class='data-table'>", unsafe_allow_html=True)
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Botón de descarga para datos filtrados
        if st.button("📥 Descargar datos filtrados", type="secondary"):
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df_display.to_excel(writer, index=False, sheet_name="Objetivos_Filtrados")
            
            st.download_button(
                label="💾 Descargar Excel Filtrado",
                data=excel_buffer.getvalue(),
                file_name=f"objetivos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()