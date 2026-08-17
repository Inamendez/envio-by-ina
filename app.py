import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Envío by Ina", page_icon="✉️", layout="wide"
)

st.title("✉️ Envío by Ina")
st.write(
    "Cruza tus bases de morosidad contra el reporte de Mailtrap y descarga un solo Excel con todas las pestañas organizadas."
)

# Inicializar memoria de sesión
if "procesado" not in st.session_state:
    st.session_state.procesado = False

base_file = st.file_uploader(
    "1. Carga tu Base Principal (Excel)", type=["xlsx", "xls"]
)

if base_file:
    xls = pd.ExcelFile(base_file)
    hoja_seleccionada = st.selectbox(
        "Selecciona la pestaña a procesar:", xls.sheet_names
    )
    df_base = pd.read_excel(xls, sheet_name=hoja_seleccionada)

    reporte_file = st.file_uploader(
        "2. Carga el Reporte de Mailtrap (CSV o Excel)", type=["csv", "xlsx"]
    )

    if reporte_file:
        if reporte_file.name.endswith(".csv"):
            df_reporte = pd.read_csv(reporte_file)
        else:
            df_reporte = pd.read_excel(reporte_file)

        col_base = st.selectbox(
            "Columna de correo en la Base Principal:", df_base.columns
        )
        col_reporte = st.selectbox(
            "Columna de correo en el Reporte Mailtrap:",
            df_reporte.columns,
            index=0,
        )

        if st.button("🚀 Procesar y Generar Consolidador Excel"):
            # Limpieza profunda de emails (comas, puntos finales y espacios)
            df_base["email_clean"] = (
                df_base[col_base]
                .astype(str)
                .str.strip()
                .str.rstrip(",.")
                .str.lower()
            )
            df_reporte["email_clean"] = (
                df_reporte[col_reporte]
                .astype(str)
                .str.strip()
                .str.rstrip(",.")
                .str.lower()
            )

            # 1. NO PROCESADOS (No están en Mailtrap)
            correos_en_reporte = set(df_reporte["email_clean"].dropna())
            no_procesados = (
                df_base[~df_base["email_clean"].isin(correos_en_reporte)]
                .drop(columns=["email_clean"])
                .drop_duplicates(subset=[col_base])
            )

            # 2. ENTREGADOS SIN ABRIR (opens == 0 o vacío AND state == 'delivered')
            cond_no_opens = df_reporte["opens"].isna() | (
                pd.to_numeric(df_reporte["opens"], errors="coerce") == 0
            )
            cond_delivered = (
                df_reporte["state"].astype(str).str.lower() == "delivered"
            )
            emails_entregados_sin_abrir = set(
                df_reporte[cond_no_opens & cond_delivered]["email_clean"]
            )

            sin_abrir = (
                df_base[df_base["email_clean"].isin(emails_entregados_sin_abrir)]
                .drop(columns=["email_clean"])
                .drop_duplicates(subset=[col_base])
            )

            # 3. ABIERTOS (opens > 0)
            emails_abiertos = set(
                df_reporte[
                    pd.to_numeric(df_reporte["opens"], errors="coerce") > 0
                ]["email_clean"]
            )
            abiertos = (
                df_base[df_base["email_clean"].isin(emails_abiertos)]
                .drop(columns=["email_clean"])
                .drop_duplicates(subset=[col_base])
            )

            # 4. CLICKS (clicks > 0)
            emails_clicks = set(
                df_reporte[
                    pd.to_numeric(df_reporte["clicks"], errors="coerce") > 0
                ]["email_clean"]
            )
            clicks = (
                df_base[df_base["email_clean"].isin(emails_clicks)]
                .drop(columns=["email_clean"])
                .drop_duplicates(subset=[col_base])
            )

            # Generar Excel multipestaña en memoria
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
                no_procesados.to_excel(
                    writer, sheet_name="No Procesados (Errores)", index=False
                )
                sin_abrir.to_excel(
                    writer, sheet_name="Entregados Sin Abrir", index=False
                )
                abiertos.to_excel(
                    writer, sheet_name="Correos Abiertos", index=False
                )
                clicks.to_excel(
                    writer, sheet_name="Hicieron Clicks", index=False
                )

            output_excel.seek(0)

            # Guardar en la memoria de la sesión
            st.session_state.no_procesados = no_procesados
            st.session_state.sin_abrir = sin_abrir
            st.session_state.abiertos = abiertos
            st.session_state.clicks = clicks
            st.session_state.excel_bytes = output_excel.getvalue()
            st.session_state.hoja_seleccionada = hoja_seleccionada
            st.session_state.procesado = True

# Mostrar resultados y botón principal de descarga
if st.session_state.procesado:
    st.success("¡Procesamiento completado con éxito!")

    hoja = st.session_state.hoja_seleccionada
    no_proc = st.session_state.no_procesados
    sin_abrir = st.session_state.sin_abrir
    abiertos = st.session_state.abiertos
    clicks = st.session_state.clicks

    # Resumen de Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("No Procesados (Errores)", len(no_proc))
    with col2:
        st.metric("Entregados Sin Abrir", len(sin_abrir))
    with col3:
        st.metric("Correos Abiertos", len(abiertos))
    with col4:
        st.metric("Hicieron Clicks", len(clicks))

    st.markdown("---")
    st.subheader("📊 Descargar Libro Consolidado de Excel")

    st.download_button(
        label="📥 Descargar Excel Completo (4 Pestañas)",
        data=st.session_state.excel_bytes,
        file_name=f"Resultado_Cruce_{hoja}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="btn_excel_consolidado",
    )
