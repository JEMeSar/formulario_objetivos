import streamlit as st
import pandas as pd
from datetime import datetime
import io
import uuid
import time
from gsheets_service import cargar_areas_agrupaciones, guardar_objetivo, guardar_nueva_agrupacion

# Configuración de la página
st.set_page_config(
    page_title="Objetivos de Productividad",
    page_icon="",
    layout="wide"
)

# --- UI ---
st.image("logo_ayuntamiento_azul.png", width=100)
st.title("Objetivos de Productividad")
st.markdown("---")

# Cargar áreas y agrupaciones
with st.spinner("Cargando áreas y agrupaciones..."):
    areas_df = cargar_areas_agrupaciones()

if areas_df.empty:
    st.error("No se pudieron cargar las áreas y agrupaciones. Verifica la conexión con Google Sheets.")
    st.stop()

# Selectores de área y agrupación
col1, col2 = st.columns(2)
with col1:
    area = st.selectbox("Área funcional", sorted(areas_df["Area"].unique()))

with col2:
    agrupaciones_filtradas = areas_df[areas_df["Area"] == area]["Agrupacion_Funcional"].unique()
    agrupar = st.selectbox("Agrupación funcional", sorted(agrupaciones_filtradas))

# Sección para agregar nueva agrupación
with st.expander("➕ Agregar nueva agrupación funcional"):
    nueva_agrupacion = st.text_input("Nueva agrupación funcional")
    if st.button("Guardar nueva agrupación funcional"):
        if nueva_agrupacion.strip():
            if guardar_nueva_agrupacion(area, nueva_agrupacion):
                st.rerun()  # Recargar para mostrar la nueva agrupación
        else:
            st.warning("Escribe un nombre para la nueva agrupación funcional")

st.markdown("---")
st.header("Objetivos")

# Inicializar estado de la sesión
if "objetivos" not in st.session_state:
    st.session_state.objetivos = [""]
    st.session_state.indicadores = [""]
    st.session_state.responsables = [""]

def render_objetivos():
    """Renderiza los campos de objetivos dinámicamente"""
    for i in range(len(st.session_state.objetivos)):
        with st.container():
            st.markdown(f"#### Objetivo {i+1}")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.session_state.objetivos[i] = st.text_area(
                    f"Descripción del objetivo {i+1}", 
                    value=st.session_state.objetivos[i], 
                    key=f"obj_{i}",
                    height=100,
                    help="Describe claramente el objetivo a alcanzar"
                )
            
            with col2:
                st.session_state.indicadores[i] = st.text_input(
                    f"Indicador {i+1}", 
                    value=st.session_state.indicadores[i], 
                    key=f"ind_{i}",
                    help="Métrica para medir el cumplimiento"
                )
                st.session_state.responsables[i] = st.text_input(
                    f"Responsable {i+1}", 
                    value=st.session_state.responsables[i], 
                    key=f"resp_{i}",
                    help="Persona responsable del objetivo"
                )
            
            st.markdown("---")

render_objetivos()

# Botones de control
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Nuevo objetivo", type="secondary"):
        st.session_state.objetivos.append("")
        st.session_state.indicadores.append("")
        st.session_state.responsables.append("")
        st.rerun()

with col2:
    if st.button("🗑️ Borrar último objetivo", type="secondary"):
        if len(st.session_state.objetivos) > 1:
            st.session_state.objetivos.pop()
            st.session_state.indicadores.pop()
            st.session_state.responsables.pop()
            st.rerun()
        else:
            st.warning("Debe mantener al menos un objetivo")

with col3:
    if st.button("♻️ Reiniciar", type="secondary"):
        st.session_state.objetivos = [""]
        st.session_state.indicadores = [""]
        st.session_state.responsables = [""]
        st.rerun()

with col4:
    if st.button("📤 Enviar objetivos", type="primary"):
        # Validar que hay al menos un objetivo completo
        objetivos_validos = []
        for i, (obj, ind, resp) in enumerate(zip(
            st.session_state.objetivos,
            st.session_state.indicadores,
            st.session_state.responsables
        )):
            if obj.strip() and ind.strip() and resp.strip():
                objetivos_validos.append((obj.strip(), ind.strip(), resp.strip()))
            elif obj.strip() or ind.strip() or resp.strip():
                st.warning(f"El objetivo {i+1} está incompleto. Complete todos los campos o déjelos vacíos.")
        
        if not objetivos_validos:
            st.error("No hay objetivos válidos para guardar. Complete al menos un objetivo con todos sus campos.")
        else:
            # Generar datos únicos para esta entrada
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            id_entrada = uuid.uuid4().hex[:8]
            
            # Guardar objetivos
            errores = []
            objetivos_guardados = 0
            
            with st.spinner(f"Guardando {len(objetivos_validos)} objetivos..."):
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
            
            # Mostrar resultados
            if objetivos_guardados > 0:
                st.success(f"✅ {objetivos_guardados} objetivos guardados correctamente (ID: {id_entrada})")
                
                # Limpiar formulario después de guardar exitosamente
                if not errores:  # Solo limpiar si no hubo errores
                    st.session_state.objetivos = [""]
                    st.session_state.indicadores = [""]
                    st.session_state.responsables = [""]
                    time.sleep(2)  # Pequeña pausa para que el usuario vea el mensaje
                    st.rerun()
            
            if errores:
                st.error("❌ Algunos objetivos no se pudieron guardar:")
                for error in errores:
                    st.error(f"• {error}")

st.markdown("---")

# Sección de descarga
if st.button("⬇️ Descargar en Excel", type="secondary"):
    # Filtrar solo objetivos con contenido
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No hay objetivos para descargar")

# Información adicional
with st.expander("ℹ️ Información"):
    st.info("""
    **Instrucciones de uso:**
    1. Selecciona el área y agrupación funcional
    2. Completa los objetivos con su indicador y responsable
    3. Usa los botones para agregar, eliminar o reiniciar objetivos
    4. Envía los objetivos cuando estén completos
    5. Descarga un Excel con los objetivos actuales si es necesario
    
    **Campos obligatorios:** Objetivo, Indicador y Responsable
    """)