import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Envío by Ina", page_icon="✉️", layout="wide"
)

st.title("✉️ Envío by Ina")
st.write("Cruza tus bases de morosidad contra el reporte de Mailtrap.")

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

        if st.button("🚀 Procesar y Separar"):
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

            # 1. NO PROCESADOS
            correos_en_reporte = set(df_reporte["email_clean"].dropna())
            no_procesados = (
                df_base[~df_base["email_clean"].isin(correos_en_reporte)]
                .drop(columns=["email_clean"])
                .drop_duplicates(subset=[col_base])
            )

            # 2. ENTREGADOS SIN ABRIR
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

            # 3. ABIERTOS
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

            # 4. CLICKS
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

            # Guardar en memoria de sesión
            st.session_state.no_procesados = no_procesados
            st.session_state.sin_abrir = sin_abrir
            st.session_state.abiertos = abiertos
            st.session_state.clicks = clicks
            st.session_state.hoja_seleccionada = hoja_seleccionada
            st.session_state.procesado = True

# Mostrar resultados y botones de descarga
if st.session_state.procesado:
    st.success("¡Procesamiento completado con éxito!")
    st.subheader("📥 Descargar Resultados")

    col1, col2, col3, col4 = st.columns(4)

    hoja = st.session_state.hoja_seleccionada
    no_proc = st.session_state.no_procesados
    sin_abrir = st.session_state.sin_abrir
    abiertos = st.session_state.abiertos
    clicks = st.session_state.clicks

    with col1:
        st.metric("No Procesados (Errores)", len(no_proc))
        st.download_button(
            label="Descargar No Procesados",
            data=no_proc.to_csv(index=False).encode("utf-8"),
            file_name=f"No_Procesados_{hoja}.csv",
            mime="text/csv",
            key="btn_no_proc",
        )

    with col2:
        st.metric("Entregados Sin Abrir", len(sin_abrir))
        st.download_button(
            label="Descargar Sin Abrir",
            data=sin_abrir.to_csv(index=False).encode("utf-8"),
            file_name=f"Entregados_Sin_Abrir_{hoja}.csv",
            mime="text/csv",
            key="btn_sin_abrir",
        )

    with col3:
        st.metric("Correos Abiertos", len(abiertos))
        st.download_button(
            label="Descargar Abiertos",
            data=abiertos.to_csv(index=False).encode("utf-8"),
            file_name=f"Abiertos_{hoja}.csv",
            mime="text/csv",
            key="btn_abiertos",
        )

    with col4:
        st.metric("Hicieron Clicks", len(clicks))
        st.download_button(
            label="Descargar Clicks",
            data=clicks.to_csv(index=False).encode("utf-8"),
            file_name=f"Clicks_{hoja}.csv",
            mime="text/csv",
            key="btn_clicks",
        )
