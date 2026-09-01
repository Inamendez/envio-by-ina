import io
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Envío by Ina", page_icon="✉️", layout="wide"
)

st.title("✉️ Envío by Ina - Generador de Diapositivas")
st.write(
    "Cruza tus bases de morosidad contra Mailtrap y genera automáticamente la **diapositiva completa en SVG** adaptada al color de morosidad."
)

if "procesado" not in st.session_state:
    st.session_state.procesado = False


def obtener_estilo_morosidad(nombre_hoja):
    """Devuelve el color primario del título según la pestaña/morosidad."""
    nombre_lower = nombre_hoja.lower()

    if "rojo" in nombre_lower:
        return {"titulo": f"Morosidad {nombre_lower}", "color_sub": "#D92D20"}
    elif "amarillo" in nombre_lower:
        return {"titulo": f"Morosidad {nombre_lower}", "color_sub": "#E08A00"}
    elif "verde" in nombre_lower:
        return {"titulo": f"Morosidad {nombre_lower}", "color_sub": "#1B9E48"}
    else:
        # Estilo por defecto si la pestaña tiene otro nombre
        return {"titulo": f"Morosidad {nombre_lower}", "color_sub": "#1B9E48"}


def generar_diapositiva_svg_completa(
    hoja, total_base, dup, bad, vac, sa, ab, cl, reb, nc
):
    """Genera el SVG completo de la lámina de presentación (1920x1080) adaptando títulos y colores."""
    estilo = obtener_estilo_morosidad(hoja)
    color_subtitulo = estilo["color_sub"]
    titulo_sub = estilo["titulo"]

    p_dup = (dup / total_base * 100) if total_base else 0
    p_bad = (bad / total_base * 100) if total_base else 0
    p_vac = (vac / total_base * 100) if total_base else 0

    p_sa = (sa / total_base * 100) if total_base else 0
    p_ab = (ab / total_base * 100) if total_base else 0
    p_cl = (cl / total_base * 100) if total_base else 0
    p_reb = (reb / total_base * 100) if total_base else 0
    p_nc = (nc / total_base * 100) if total_base else 0

    bar_w = 734
    h_bar = 20.18
    rx_bar = 10.09

    w_sa = max(0, min(bar_w, bar_w * (p_sa / 100.0)))
    w_ab = max(0, min(bar_w, bar_w * (p_ab / 100.0)))
    w_cl = max(0, min(bar_w, bar_w * (p_cl / 100.0)))
    w_reb = max(0, min(bar_w, bar_w * (p_reb / 100.0)))
    w_nc = max(0, min(bar_w, bar_w * (p_nc / 100.0)))

    svg = f"""<svg width="1920" height="1080" viewBox="0 0 1920 1080" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .tit-main {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 800; font-size: 72px; fill: #2B2D32; letter-spacing: -1.5px; }}
    .tit-sub {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 700; font-size: 52px; fill: {color_subtitulo}; letter-spacing: -1px; }}
    .capsula-bg {{ fill: #EFEFEF; rx: 32px; }}
    .capsula-txt {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 500; font-size: 32px; fill: #4A4D55; }}
    .card-bg {{ fill: #FFFFFF; stroke: #F0F0F0; stroke-width: 2px; rx: 32px; }}
    .card-tit {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 700; font-size: 40px; fill: #3A3D44; letter-spacing: -0.5px; }}
    .row-bg {{ fill: #F9F9F9; rx: 16px; }}
    .lbl-cuali {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 500; font-size: 30px; fill: #7E828D; }}
    .num-cuali {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 700; font-size: 36px; fill: #3B3E46; }}
    .pct-cuali {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 400; font-size: 24px; fill: #9BA0AB; }}
    .lbl-cuanti {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 500; font-size: 30px; fill: #7E828D; }}
    .val-cuanti {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 500; font-size: 24px; fill: #8E939E; }}
    .footer-txt {{ font-family: 'Inter', system-ui, sans-serif; font-weight: 500; font-style: italic; font-size: 28px; fill: #A5A9B4; }}
  </style>

  <rect width="1920" height="1080" fill="#FFFFFF"/>

  <text x="100" y="130" class="tit-main">Resultados</text>
  <text x="100" y="195" class="tit-sub">{titulo_sub.capitalize()}</text>

  <g transform="translate(100, 235)">
    <rect width="780" height="72" class="capsula-bg"/>
    <text x="50" y="47" class="capsula-txt">Se recibió una base de {total_base:,} contactos (100%)</text>
  </g>

  <g transform="translate(100, 350)">
    <rect width="820" height="580" class="card-bg"/>
    <text x="50" y="70" class="card-tit">Resultado cualitativo de la base</text>

    <g transform="translate(50, 120)">
      <rect width="720" height="110" class="row-bg"/>
      <text x="30" y="65" class="lbl-cuali">Registros duplicados</text>
      <text x="690" y="52" text-anchor="end" class="num-cuali">{dup:,}</text>
      <text x="690" y="85" text-anchor="end" class="pct-cuali">{p_dup:.1f}%</text>
    </g>

    <g transform="translate(50, 260)">
      <rect width="720" height="110" class="row-bg"/>
      <text x="30" y="65" class="lbl-cuali">Correos mal escritos/sintaxis</text>
      <text x="690" y="52" text-anchor="end" class="num-cuali">{bad:,}</text>
      <text x="690" y="85" text-anchor="end" class="pct-cuali">{p_bad:.1f}%</text>
    </g>

    <g transform="translate(50, 400)">
      <rect width="720" height="110" class="row-bg"/>
      <text x="30" y="65" class="lbl-cuali">Registros sin correos</text>
      <text x="690" y="52" text-anchor="end" class="num-cuali">{vac:,}</text>
      <text x="690" y="85" text-anchor="end" class="pct-cuali">{p_vac:.1f}%</text>
    </g>
  </g>

  <g transform="translate(960, 350)">
    <rect width="860" height="580" class="card-bg"/>
    <text x="50" y="70" class="card-tit">Resultado cuantitativo del envío</text>

    <g transform="translate(50, 120)">
      <circle cx="10" cy="18" r="8" fill="#FF5100"/>
      <text x="30" y="24" class="lbl-cuanti">Entregados sin abrir</text>
      <text x="784" y="24" text-anchor="end" class="val-cuanti">{p_sa:.1f}% ({sa:,})</text>
      <rect x="50" y="42" width="{bar_w}" height="{h_bar}" rx="{rx_bar}" fill="#EAEAEA"/>
      {'<rect x="50" y="42" width="' + f'{w_sa:.2f}' + '" height="' + f'{h_bar}' + '" rx="' + f'{rx_bar}' + '" fill="#FF5100"/>' if p_sa > 0 else ''}
    </g>

    <g transform="translate(50, 205)">
      <circle cx="10" cy="18" r="8" fill="#FF5100"/>
      <text x="30" y="24" class="lbl-cuanti">Correos Abiertos</text>
      <text x="784" y="24" text-anchor="end" class="val-cuanti">{p_ab:.1f}% ({ab:,})</text>
      <rect x="50" y="42" width="{bar_w}" height="{h_bar}" rx="{rx_bar}" fill="#EAEAEA"/>
      {'<rect x="50" y="42" width="' + f'{w_ab:.2f}' + '" height="' + f'{h_bar}' + '" rx="' + f'{rx_bar}' + '" fill="#FF5100"/>' if p_ab > 0 else ''}
    </g>

    <g transform="translate(50, 290)">
      <circle cx="10" cy="18" r="8" fill="#FF5100"/>
      <text x="30" y="24" class="lbl-cuanti">Hicieron click</text>
      <text x="784" y="24" text-anchor="end" class="val-cuanti">{p_cl:.1f}% ({cl:,})</text>
      <rect x="50" y="42" width="{bar_w}" height="{h_bar}" rx="{rx_bar}" fill="#EAEAEA"/>
      {'<rect x="50" y="42" width="' + f'{w_cl:.2f}' + '" height="' + f'{h_bar}' + '" rx="' + f'{rx_bar}' + '" fill="#FF5100"/>' if p_cl > 0 else ''}
    </g>

    <g transform="translate(50, 375)">
      <circle cx="10" cy="18" r="8" fill="#FF5100"/>
      <text x="30" y="24" class="lbl-cuanti">Rebotados (Mailtrap)</text>
      <text x="784" y="24" text-anchor="end" class="val-cuanti">{p_reb:.1f}% ({reb:,})</text>
      <rect x="50" y="42" width="{bar_w}" height="{h_bar}" rx="{rx_bar}" fill="#EAEAEA"/>
      {'<rect x="50" y="42" width="' + f'{w_reb:.2f}' + '" height="' + f'{h_bar}' + '" rx="' + f'{rx_bar}' + '" fill="#FF5100"/>' if p_reb > 0 else ''}
    </g>

    <g transform="translate(50, 460)">
      <circle cx="10" cy="18" r="8" fill="#FF5100"/>
      <text x="30" y="24" class="lbl-cuanti">No Cargados en Mailtrap</text>
      <text x="784" y="24" text-anchor="end" class="val-cuanti">{p_nc:.1f}% ({nc:,})</text>
      <rect x="50" y="42" width="{bar_w}" height="{h_bar}" rx="{rx_bar}" fill="#EAEAEA"/>
      {'<rect x="50" y="42" width="' + f'{w_nc:.2f}' + '" height="' + f'{h_bar}' + '" rx="' + f'{rx_bar}' + '" fill="#FF5100"/>' if p_nc > 0 else ''}
    </g>
  </g>

  <line x1="100" y1="1000" x2="1820" y2="1000" stroke="#E0E0E0" stroke-width="1.5"/>
  <text x="100" y="1035" class="footer-txt">Invierte en soluciones</text>
</svg>"""
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

        if st.button("🚀 Procesar y Generar Diapositiva Completa"):
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

            # --- FILTRADO DE PESTAÑAS ---
            cond_open = (
                pd.to_numeric(df_reporte["opens"], errors="coerce") > 0
            ) | (
                df_reporte["state"]
                .astype(str)
                .str.lower()
                .isin(["opened", "clicked"])
            )
            emails_abiertos = set(df_reporte[cond_open]["email_clean"])
            abiertos = df_base[df_base["email_clean"].isin(emails_abiertos)]

            cond_click = (
                pd.to_numeric(df_reporte["clicks"], errors="coerce") > 0
            ) | (df_reporte["state"].astype(str).str.lower() == "clicked")
            emails_clicks = set(df_reporte[cond_click]["email_clean"])
            clicks = df_base[df_base["email_clean"].isin(emails_clicks)]

            cond_delivered = (
                df_reporte["state"].astype(str).str.lower() == "delivered"
            ) & (~df_reporte["email_clean"].isin(emails_abiertos))
            emails_delivered_no_open = set(
                df_reporte[cond_delivered]["email_clean"]
            )
            sin_abrir = df_base[
                df_base["email_clean"].isin(emails_delivered_no_open)
            ]

            cond_bounced = (
                df_reporte["state"]
                .astype(str)
                .str.lower()
                .isin(["bounced", "rejected"])
            )
            emails_bounced = set(df_reporte[cond_bounced]["email_clean"])
            rebotados = df_base[df_base["email_clean"].isin(emails_bounced)]

            correos_en_reporte = set(df_reporte["email_clean"].dropna())
            no_cargados = df_base[
                ~df_base["email_clean"].isin(correos_en_reporte)
            ]

            # --- GENERAR LIBRO EXCEL CONSOLIDADOR ---
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

            # Generar SVG Completo con Colores según Pestaña
            svg_diapositiva = generar_diapositiva_svg_completa(
                hoja_seleccionada,
                total_base,
                duplicados,
                mal_escritos,
                vacios,
                len(sin_abrir),
                len(abiertos),
                len(clicks),
                len(rebotados),
                len(no_cargados),
            )

            st.session_state.svg_diapositiva = svg_diapositiva
            st.session_state.excel_bytes = output_excel.getvalue()
            st.session_state.hoja_seleccionada = hoja_seleccionada
            st.session_state.procesado = True

if st.session_state.procesado:
    st.success("¡Diapositiva armada con éxito!")

    hoja = st.session_state.hoja_seleccionada
    svg_code = st.session_state.svg_diapositiva

    st.markdown(
        f"## 🖼️ Vista Previa de tu Diapositiva ({hoja})"
    )

    components.html(
        f'<div style="transform: scale(0.65); transform-origin: top left; width: 1920px; height: 1080px;">{svg_code}</div>',
        height=720,
    )

    st.markdown("---")
    col_dl, col_code = st.columns([1, 2])

    with col_dl:
        st.subheader("⬇️ Descargar Archivos")
        st.download_button(
            label="🖼️ Descargar Diapositiva SVG",
            data=svg_code.encode("utf-8"),
            file_name=f"Diapositiva_{hoja}.svg",
            mime="image/svg+xml",
        )
        st.download_button(
            label="📊 Descargar Excel Consolidado (5 Pestañas)",
            data=st.session_state.excel_bytes,
            file_name=f"Resultado_Cruce_{hoja}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with col_code:
        st.subheader("📋 Código SVG para Figma")
        st.caption(
            "Haz clic en el botón de copiar y presiona **Cmd + V** en Figma."
        )
        st.code(svg_code, language="xml")
