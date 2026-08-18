import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Envío by Ina", page_icon="✉️", layout="wide"
)

st.title("✉️ Envío by Ina - Informe de Resultados")
st.write(
    "Cruza tus bases de morosidad contra Mailtrap, obtiene las métricas exactas para la presentación y descarga las barras SVG y el Excel consolidado."
)

if "procesado" not in st.session_state:
    st.session_state.procesado = False


def crear_barras_svg(pct, color="#FF5500", width=734, height=20.18):
    """Genera una barra horizontal en SVG vectorial con dimensiones exactas: 734px x 20.18px."""
    fill_w = max(0, min(width, width * (pct / 100.0)))
    rx = height / 2.0  # Esquinas redondeadas suaves (10.09px)
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" rx="{rx}" fill="#EAEAEA"/>
  <rect width="{fill_w:.2f}" height="{height}" rx="{rx}" fill="{color}"/>
</svg>'''
    return svg


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

        if st.button("🚀 Procesar y Generar Informe Completo"):
            total_base = len(df_base)

            # Limpieza y estandarización
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

            # --- ANÁLISIS CUALITATIVO DE LA BASE ---
            vacios = df_base[col_base].isna().sum() + (
                df_base["email_clean"].isin(["nan", "", "none", "null"])
            ).sum()
            duplicados = df_base.duplicated(subset=["email_clean"]).sum()

            valid_syntax = df_base["email_clean"].str.contains("@") & df_base[
                "email_clean"
            ].apply(
                lambda x: "." in x.split("@")[-1] if "@" in str(x) else False
            )
            mal_escritos = (
                ~valid_syntax
                & ~df_base["email_clean"].isin(["nan", "", "none", "null"])
            ).sum()

            # --- FILTRADO DE PESTAÑAS (CUANTITATIVO) ---
            # 1. ABIERTOS
            cond_open = (
                pd.to_numeric(df_reporte["opens"], errors="coerce") > 0
            ) | (
                df_reporte["state"]
                .astype(str)
                .str.lower()
                .isin(["opened", "clicked"])
            )
            emails_abiertos = set(df_reporte[cond_open]["email_clean"])
            abiertos = df_base[
                df_base["email_clean"].isin(emails_abiertos)
            ].drop_duplicates(subset=[col_base])

            # 2. CLICKS
            cond_click = (
                pd.to_numeric(df_reporte["clicks"], errors="coerce") > 0
            ) | (df_reporte["state"].astype(str).str.lower() == "clicked")
            emails_clicks = set(df_reporte[cond_click]["email_clean"])
            clicks = df_base[
                df_base["email_clean"].isin(emails_clicks)
            ].drop_duplicates(subset=[col_base])

            # 3. ENTREGADOS SIN ABRIR
            cond_delivered = (
                df_reporte["state"].astype(str).str.lower() == "delivered"
            ) & (~df_reporte["email_clean"].isin(emails_abiertos))
            emails_delivered_no_open = set(
                df_reporte[cond_delivered]["email_clean"]
            )
            sin_abrir = df_base[
                df_base["email_clean"].isin(emails_delivered_no_open)
            ].drop_duplicates(subset=[col_base])

            # 4. REBOTADOS / RECHAZADOS EN MAILTRAP
            cond_bounced = (
                df_reporte["state"]
                .astype(str)
                .str.lower()
                .isin(["bounced", "rejected"])
            )
            emails_bounced = set(df_reporte[cond_bounced]["email_clean"])
            rebotados = df_base[
                df_base["email_clean"].isin(emails_bounced)
            ].drop_duplicates(subset=[col_base])

            # 5. NO CARGADOS EN MAILTRAP
            correos_en_reporte = set(df_reporte["email_clean"].dropna())
            no_cargados = df_base[
                ~df_base["email_clean"].isin(correos_en_reporte)
            ].drop_duplicates(subset=[col_base])

            # --- GENERAR LIBRO EXCEL CONSOLIDADOR (5 PESTAÑAS) ---
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
                sin_abrir.drop(columns=["email_clean"]).to_excel(
                    writer, sheet_name="Entregados Sin Abrir", index=False
                )
                abiertos.drop(columns=["email_clean"]).to_excel(
                    writer, sheet_name="Correos Abiertos", index=False
                )
                clicks.drop(columns=["email_clean"]).to_excel(
                    writer, sheet_name="Hicieron Clicks", index=False
                )
                rebotados.drop(columns=["email_clean"]).to_excel(
                    writer, sheet_name="Rebotados (Mailtrap)", index=False
                )
                no_cargados.drop(columns=["email_clean"]).to_excel(
                    writer, sheet_name="No Cargados en Mailtrap", index=False
                )
            output_excel.seek(0)

            # Guardar en sesión
            st.session_state.total_base = total_base
            st.session_state.duplicados = duplicados
            st.session_state.mal_escritos = mal_escritos
            st.session_state.vacios = vacios
            st.session_state.sin_abrir = len(sin_abrir)
            st.session_state.abiertos = len(abiertos)
            st.session_state.clicks = len(clicks)
            st.session_state.rebotados = len(rebotados)
            st.session_state.no_cargados = len(no_cargados)
            st.session_state.excel_bytes = output_excel.getvalue()
            st.session_state.hoja_seleccionada = hoja_seleccionada
            st.session_state.procesado = True

if st.session_state.procesado:
    st.success("¡Cruce completado con éxito!")

    tot = st.session_state.total_base
    hoja = st.session_state.hoja_seleccionada

    st.markdown(f"## 📊 Datos para la Presentación ({hoja})")
    st.info(f"**Total de contactos recibidos en la base:** {tot:,} (100.0%)")

    col_cuali, col_cuanti = st.columns(2)

    with col_cuali:
        st.subheader("🔍 Diagnóstico Cualitativo de la Base")
        dup = st.session_state.duplicados
        bad = st.session_state.mal_escritos
        vac = st.session_state.vacios
        st.write(
            f"• **Registros duplicados (mismo correo):** {dup} ({dup/tot*100:.1f}%)"
        )
        st.write(
            f"• **Correos mal escritos / sintaxis:** {bad} ({bad/tot*100:.1f}%)"
        )
        st.write(
            f"• **Registros sin correo / vacíos:** {vac} ({vac/tot*100:.1f}%)"
        )

    with col_cuanti:
        st.subheader("📈 Resultados Cuantitativos del Envío")
        sa = st.session_state.sin_abrir
        ab = st.session_state.abiertos
        cl = st.session_state.clicks
        reb = st.session_state.rebotados
        nc = st.session_state.no_cargados

        st.write(f"• **Entregados Sin Abrir:** {sa} ({sa/tot*100:.1f}%)")
        st.write(f"• **Correos Abiertos:** {ab} ({ab/tot*100:.1f}%)")
        st.write(f"• **Hicieron Clicks:** {cl} ({cl/tot*100:.1f}%)")
        st.write(f"• **Rebotados (Mailtrap):** {reb} ({reb/tot*100:.1f}%)")
        st.write(f"• **No Cargados en Mailtrap:** {nc} ({nc/tot*100:.1f}%)")

    st.markdown("---")
    st.subheader("📥 Descargar Archivo Excel Detallado (5 Pestañas)")

    st.download_button(
        label="📥 Descargar Libro Consolidado (.xlsx)",
        data=st.session_state.excel_bytes,
        file_name=f"Resultado_Cruce_{hoja}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="btn_excel_consolidado",
    )

    # --- BARRAS SVG CON MEDIDAS EXACTAS (734 x 20.18) ---
    st.markdown("---")
    st.subheader("🎨 Barras Vectoriales SVG (734px x 20.18px)")
    st.write(
        "A continuación puedes visualizar, copiar o descargar cada barra vectorial con las medidas exactas requeridas para tu diseño:"
    )

    categorias = [
        ("Entregados Sin Abrir", sa, "#FF5500"),  # Naranja
        ("Correos Abiertos", ab, "#2E7D32"),  # Verde
        ("Hicieron Clicks", cl, "#1565C0"),  # Azul
        ("Rebotados (Mailtrap)", reb, "#D32F2F"),  # Rojo
        ("No Cargados en Mailtrap", nc, "#757575"),  # Gris
    ]

    for nombre, cantidad, color in categorias:
        pct = (cantidad / tot) * 100 if tot > 0 else 0
        svg_code = crear_barras_svg(
            pct, color=color, width=734, height=20.18
        )

        st.markdown(f"**{nombre}:** {pct:.1f}% ({cantidad:,} de {tot:,})")
        st.components.v1.html(svg_code, height=35)

        c1, c2 = st.columns([1, 4])
        with c1:
            st.download_button(
                label=f"⬇️ Descargar SVG ({nombre})",
                data=svg_code.encode("utf-8"),
                file_name=f"barra_{nombre.lower().replace(' ', '_')}.svg",
                mime="image/svg+xml",
                key=f"svg_dl_{nombre}",
            )
        with c2:
            st.text_input(
                "Código SVG exacto:",
                value=svg_code,
                key=f"svg_txt_{nombre}",
            )
