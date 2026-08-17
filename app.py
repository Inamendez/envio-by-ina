import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Envío by Ina", page_icon="✉️", layout="wide"
)

st.title("✉️ Envío by Ina")
st.write("Cruza tus bases contra el reporte exacto de Mailtrap.")

if "procesado" not in st.session_state:
    st.session_state.procesado = False

base_file = st.file_uploader("1. Carga tu Base Principal (Excel)", type=["xlsx", "xls"])

if base_file:
    xls = pd.ExcelFile(base_file)
    hoja_seleccionada = st.selectbox("Selecciona la pestaña a procesar:", xls.sheet_names)
    df_base = pd.read_excel(xls, sheet_name=hoja_seleccionada)

    reporte_file = st.file_uploader("2. Carga el Reporte de Mailtrap (CSV o Excel)", type=["csv", "xlsx"])

    if reporte_file:
        if reporte_file.name.endswith(".csv"):
            df_reporte = pd.read_csv(reporte_file)
        else:
            df_reporte = pd.read_excel(reporte_file)

        col_base = st.selectbox("Columna de correo en la Base Principal:", df_base.columns)
        col_reporte = st.selectbox("Columna de correo en el Reporte Mailtrap:", df_reporte.columns, index=0)

        if st.button("🚀 Procesar y Generar Consolidador Excel"):
            # Limpieza profunda de emails
            df_base["email_clean"] = df_base[col_base].astype(str).str.strip().str.rstrip(",.").str.lower()
            df_reporte["email_clean"] = df_reporte[col_reporte].astype(str).str.strip().str.rstrip(",.").str.lower()

            # 1. ABIERTOS (opens > 0 O state in ['opened', 'clicked'])
            cond_open = (pd.to_numeric(df_reporte["opens"], errors="coerce") > 0) | (df_reporte["state"].astype(str).str.lower().isin(["opened", "clicked"]))
            emails_abiertos = set(df_reporte[cond_open]["email_clean"])
            abiertos = df_base[df_base["email_clean"].isin(emails_abiertos)].drop(columns=["email_clean"]).drop_duplicates(subset=[col_base])

            # 2. CLICKS (clicks > 0 O state == 'clicked')
            cond_click = (pd.to_numeric(df_reporte["clicks"], errors="coerce") > 0) | (df_reporte["state"].astype(str).str.lower() == "clicked")
            emails_clicks = set(df_reporte[cond_click]["email_clean"])
            clicks = df_base[df_base["email_clean"].isin(emails_clicks)].drop(columns=["email_clean"]).drop_duplicates(subset=[col_base])

            # 3. ENTREGADOS SIN ABRIR (state == 'delivered' y sin opens)
            cond_delivered = (df_reporte["state"].astype(str).str.lower() == "delivered") & (~df_reporte["email_clean"].isin(emails_abiertos))
            emails_delivered_no_open = set(df_reporte[cond_delivered]["email_clean"])
            sin_abrir = df_base[df_base["email_clean"].isin(emails_delivered_no_open)].drop(columns=["email_clean"]).drop_duplicates(subset=[col_base])

            # 4. REBOTADOS / RECHAZADOS EN MAILTRAP (bounced o rejected)
            cond_bounced = df_reporte["state"].astype(str).str.lower().isin(["bounced", "rejected"])
            emails_bounced = set(df_reporte[cond_bounced]["email_clean"])
            rebotados = df_base[df_base["email_clean"].isin(emails_bounced)].drop(columns=["email_clean"]).drop_duplicates(subset=[col_base])

            # 5. NO CARGADOS (Correos de la base que no están en el CSV de Mailtrap)
            correos_en_reporte = set(df_reporte["email_clean"].dropna())
            no_cargados = df_base[~df_base["email_clean"].isin(correos_en_reporte)].drop(columns=["email_clean"]).drop_duplicates(subset=[col_base])

            # Crear el archivo Excel con 5 pestañas
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
                sin_abrir.to_excel(writer, sheet_name="Entregados Sin Abrir", index=False)
                abiertos.to_excel(writer, sheet_name="Correos Abiertos", index=False)
                clicks.to_excel(writer, sheet_name="Hicieron Clicks", index=False)
                rebotados.to_excel(writer, sheet_name="Rebotados (Mailtrap)", index=False)
                no_cargados.to_excel(writer, sheet_name="No Cargados en Mailtrap", index=False)

            output_excel.seek(0)

            # Guardar en sesión
            st.session_state.sin_abrir = sin_abrir
            st.session_state.abiertos = abiertos
            st.session_state.clicks = clicks
            st.session_state.rebotados = rebotados
            st.session_state.no_cargados = no_cargados
            st.session_state.excel_bytes = output_excel.getvalue()
            st.session_state.hoja_seleccionada = hoja_seleccionada
            st.session_state.procesado = True

if st.session_state.procesado:
    st.success("¡Procesamiento completado con éxito!")

    hoja = st.session_state.hoja_seleccionada
    sin_abrir = st.session_state.sin_abrir
    abiertos = st.session_state.abiertos
    clicks = st.session_state.clicks
    rebotados = st.session_state.rebotados
    no_cargados = st.session_state.no_cargados

    # Métricas alineadas con Mailtrap
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Entregados Sin Abrir", len(sin_abrir))
    with col2:
        st.metric("Correos Abiertos", len(abiertos))
    with col3:
        st.metric("Hicieron Clicks", len(clicks))
    with col4:
        st.metric("Rebotados (Mailtrap)", len(rebotados))
    with col5:
        st.metric("No Cargados (Base)", len(no_cargados))

    st.markdown("---")
    st.subheader("📊 Descargar Libro Consolidado de Excel")

    st.download_button(
        label="📥 Descargar Excel Completo (5 Pestañas)",
        data=st.session_state.excel_bytes,
        file_name=f"Resultado_Cruce_{hoja}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="btn_excel_consolidado",
    )
