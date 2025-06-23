import streamlit as st
from datetime import datetime

def render_header():
    """Renderiza el header principal de la aplicación"""
    st.markdown("""
    <div class='main-header'>
        <h1>🎯 Gestión de Objetivos de Productividad</h1>
        <p>Sistema integral para la definición, seguimiento y gestión de objetivos organizacionales</p>
    </div>
    """, unsafe_allow_html=True)

def render_success_message(message, details=None):
    """Renderiza un mensaje de éxito con estilo personalizado"""
    st.success(message)
    if details:
        with st.expander("Ver detalles"):
            st.write(details)

def render_error_message(message, details=None):
    """Renderiza un mensaje de error con estilo personalizado"""
    st.error(message)
    if details:
        with st.expander("Ver detalles del error"):
            st.write(details)

def render_warning_message(message, details=None):
    """Renderiza un mensaje de advertencia con estilo personalizado"""
    st.warning(message)
    if details:
        with st.expander("Ver detalles"):
            st.write(details)

def render_info_card(title="ℹ️ Información", content=None):
    """Renderiza una tarjeta de información"""
    if content is None:
        content = """
        **Instrucciones de uso:**
        
        **📝 Crear Objetivos:**
        1. Selecciona el área y agrupación funcional
        2. Completa los objetivos con su indicador y responsable
        3. Usa los botones para agregar, eliminar o reiniciar objetivos
        4. Envía los objetivos cuando estén completos
        5. Descarga un Excel con los objetivos actuales si es necesario
        
        **📊 Ver Objetivos:**
        1. Visualiza todos los objetivos creados
        2. Usa los filtros para encontrar objetivos específicos
        3. Descarga los datos filtrados en Excel
        
        **Campos obligatorios:** Objetivo, Indicador y Responsable
        """
    
    with st.expander(title):
        st.info(content)

def render_metric_card(title, value, icon="📊"):
    """Renderiza una tarjeta de métrica"""
    st.markdown(f"""
    <div class='metric-container'>
        <h3 style='margin: 0; color: #2e7bcf; font-size: 1.2rem;'>{icon} {title}</h3>
        <p style='margin: 0; font-size: 2rem; font-weight: bold; color: #1f4e79;'>{value}</p>
    </div>
    """, unsafe_allow_html=True)

def render_objective_summary_card(objetivo_data):
    """Renderiza una tarjeta resumen de objetivo"""
    estado_color = "#28a745" if objetivo_data['estado'] == 'ACTIVO' else "#6c757d"
    estado_icon = "✅" if objetivo_data['estado'] == 'ACTIVO' else "⏸️"
    
    st.markdown(f"""
    <div style='
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid {estado_color};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    '>
        <div style='display: flex; justify-content: between; align-items: start; margin-bottom: 1rem;'>
            <h4 style='margin: 0; color: #1f4e79;'>{objetivo_data['objetivo'][:100]}{'...' if len(objetivo_data['objetivo']) > 100 else ''}</h4>
            <span style='color: {estado_color}; font-weight: bold;'>{estado_icon} {objetivo_data['estado']}</span>
        </div>
        
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;'>
            <div>
                <strong>📊 Indicador:</strong><br>
                <span style='color: #6c757d;'>{objetivo_data['indicador']}</span>
            </div>
            <div>
                <strong>👤 Responsable:</strong><br>
                <span style='color: #6c757d;'>{objetivo_data['responsable']}</span>
            </div>
        </div>
        
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.9rem; color: #6c757d;'>
            <div>
                <strong>🏢 Área:</strong> {objetivo_data['area']}
            </div>
            <div>
                <strong>📋 Agrupación:</strong> {objetivo_data['agrupacion']}
            </div>
        </div>
        
        <div style='margin-top: 1rem; font-size: 0.8rem; color: #adb5bd;'>
            <strong>📅 Creado:</strong> {objetivo_data['timestamp']}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_filter_section():
    """Renderiza la sección de filtros con estilo"""
    st.markdown("""
    <div class='filter-section'>
        <h4 style='margin-top: 0; color: #1f4e79;'>🔍 Filtros de Búsqueda</h4>
        <p style='margin-bottom: 1rem; color: #6c757d;'>Utiliza los filtros para encontrar objetivos específicos</p>
    </div>
    """, unsafe_allow_html=True)

def render_stats_dashboard(df):
    """Renderiza un dashboard de estadísticas"""
    if df.empty:
        return
    
    st.markdown("### 📈 Estadísticas Generales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_objetivos = len(df)
        render_metric_card("Total Objetivos", total_objetivos, "🎯")
    
    with col2:
        areas_unicas = df['area'].nunique()
        render_metric_card("Áreas Diferentes", areas_unicas, "🏢")
    
    with col3:
        responsables_unicos = df['responsable'].nunique()
        render_metric_card("Responsables", responsables_unicos, "👤")
    
    with col4:
        if 'estado' in df.columns:
            objetivos_activos = len(df[df['estado'] == 'ACTIVO'])
            render_metric_card("Objetivos Activos", objetivos_activos, "✅")
        else:
            render_metric_card("Agrupaciones", df['agrupacion'].nunique(), "📋")

def render_loading_spinner(message="Cargando..."):
    """Renderiza un spinner de carga personalizado"""
    return st.spinner(f"🔄 {message}")

def render_empty_state(title="Sin datos", message="No hay información para mostrar", icon="📭"):
    """Renderiza un estado vacío con estilo"""
    st.markdown(f"""
    <div style='
        text-align: center;
        padding: 3rem 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        border: 2px dashed #dee2e6;
        margin: 2rem 0;
    '>
        <div style='font-size: 4rem; margin-bottom: 1rem;'>{icon}</div>
        <h3 style='color: #6c757d; margin-bottom: 0.5rem;'>{title}</h3>
        <p style='color: #adb5bd; margin: 0;'>{message}</p>
    </div>
    """, unsafe_allow_html=True)

def render_action_buttons():
    """Renderiza botones de acción con estilo consistente"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nuevo = st.button("➕ Nuevo", type="secondary", use_container_width=True)
    
    with col2:
        editar = st.button("✏️ Editar", type="secondary", use_container_width=True)
    
    with col3:
        eliminar = st.button("🗑️ Eliminar", type="secondary", use_container_width=True)
    
    return nuevo, editar, eliminar

def render_breadcrumb(items):
    """Renderiza un breadcrumb de navegación"""
    breadcrumb_html = " > ".join([f"<span style='color: #6c757d;'>{item}</span>" for item in items])
    st.markdown(f"<div style='margin-bottom: 1rem; font-size: 0.9rem;'>{breadcrumb_html}</div>", unsafe_allow_html=True)

def render_page_footer():
    """Renderiza el footer de la página"""
    st.markdown("---")
    st.markdown(f"""
    <div style='
        text-align: center;
        padding: 1rem;
        color: #6c757d;
        font-size: 0.9rem;
        background: #f8f9fa;
        border-radius: 8px;
        margin-top: 2rem;
    '>
        Sistema de Gestión de Objetivos • Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)