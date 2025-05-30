import streamlit as st
import pulp
import pandas as pd

st.set_page_config(page_title="American Steel company", layout="centered")
st.title("American Steel Company - analisis de sensibilidad")

# =======================
# DATOS POR DEFECTO
# =======================

# Minas con tipo, costo y límites

with open("Manual_Usuario.pdf.pdf", "rb") as f:
    st.download_button("📖 Abrir Manual de Usuario", f, file_name="Manual_Usuario.pdf.pdf")
minas = {
    "Butte": {"tipo": "A", "compra": 130, "envio": {"Pittsburg": 10, "Youngstown": 13}, "limite": 1000},
    "Cheyenne": {"tipo": "B", "compra": 110, "envio": {"Pittsburg": 14, "Youngstown": 17}, "limite": 2000}
}

# Plantas con capacidad y costos
plantas = {
    "Pittsburg": {"capacidad": 700, "proceso": {"alto": 32, "bajo": 27}},
    "Youngstown": {"capacidad": 1500, "proceso": {"alto": 39, "bajo": 32}}
}

# Mezclas para tipos de acero
mezclas = {
    "alto": {"A": 1, "B": 2},
    "bajo": {"A": 1, "B": 3}
}

# Demanda y costos de envío del producto terminado
paises = {
    "Japón":    {"alto": 400, "bajo": 200, "envio": {"Pittsburg": {"alto": 110, "bajo": 100}, "Youngstown": {"alto": 115, "bajo": 110}}},
    "Corea":    {"alto": 200, "bajo": 100, "envio": {"Pittsburg": {"alto": 140, "bajo": 130}, "Youngstown": {"alto": 150, "bajo": 145}}},
    "Taiwán":   {"alto": 200, "bajo": 100, "envio": {"Pittsburg": {"alto": 130, "bajo": 125}, "Youngstown": {"alto": 135, "bajo": 127}}},
    "México":   {"alto": 150, "bajo": 50,  "envio": {"Pittsburg": {"alto": 80, "bajo": 80},   "Youngstown": {"alto": 90, "bajo": 85}}}
}

# =======================
# ENTRADAS DINÁMICAS
# =======================

def init_session_state():
    if "minas" not in st.session_state:
        st.session_state["minas"] = {
            "Butte": {"tipo": "A", "compra": 130, "envio": {"Pittsburg": 10, "Youngstown": 13}, "limite": 1000},
            "Cheyenne": {"tipo": "B", "compra": 110, "envio": {"Pittsburg": 14, "Youngstown": 17}, "limite": 2000}
        }
    if "plantas" not in st.session_state:
        st.session_state["plantas"] = {
            "Pittsburg": {"capacidad": 700, "proceso": {"alto": 32, "bajo": 27}},
            "Youngstown": {"capacidad": 1500, "proceso": {"alto": 39, "bajo": 32}}
        }
    if "mezclas" not in st.session_state:
        st.session_state["mezclas"] = {
            "alto": {"A": 1, "B": 2},
            "bajo": {"A": 1, "B": 3}
        }
    if "paises" not in st.session_state:
        st.session_state["paises"] = {
            "Japón":    {"alto": 400, "bajo": 200, "envio": {"Pittsburg": {"alto": 110, "bajo": 100}, "Youngstown": {"alto": 115, "bajo": 110}}},
            "Corea":    {"alto": 200, "bajo": 100, "envio": {"Pittsburg": {"alto": 140, "bajo": 130}, "Youngstown": {"alto": 150, "bajo": 145}}},
            "Taiwán":   {"alto": 200, "bajo": 100, "envio": {"Pittsburg": {"alto": 130, "bajo": 125}, "Youngstown": {"alto": 135, "bajo": 127}}},
            "México":   {"alto": 150, "bajo": 50,  "envio": {"Pittsburg": {"alto": 80, "bajo": 80},   "Youngstown": {"alto": 90, "bajo": 85}}}
        }

init_session_state()

# Formulario para editar minas
def minas_form():
    st.subheader("Minas")
    minas = st.session_state["minas"]
    to_delete = []
    for nombre, datos in minas.items():
        with st.expander(f"{nombre}"):
            new_nombre = st.text_input(f"Nombre mina", value=nombre, key=f"minaname_{nombre}")
            tipo = st.selectbox(f"Tipo", ["A", "B"], index=["A", "B"].index(datos["tipo"]), key=f"minatipo_{nombre}")
            compra = st.number_input(f"Costo compra", value=datos["compra"], key=f"minacompra_{nombre}")
            limite = st.number_input(f"Límite", value=datos["limite"], key=f"minalimite_{nombre}")
            envio = {}
            for planta in st.session_state["plantas"]:
                envio[planta] = st.number_input(f"Envío a {planta}", value=datos["envio"].get(planta, 0), key=f"minaenvio_{nombre}_{planta}")
            if st.button(f"Eliminar mina {nombre}"):
                to_delete.append(nombre)
            # Actualizar datos
            minas[new_nombre] = {"tipo": tipo, "compra": compra, "envio": envio, "limite": limite}
            if new_nombre != nombre:
                to_delete.append(nombre)
    for nombre in to_delete:
        if nombre in minas:
            del minas[nombre]
    if st.button("Agregar mina"):
        minas[f"Mina{len(minas)+1}"] = {"tipo": "A", "compra": 0, "envio": {pl: 0 for pl in st.session_state["plantas"]}, "limite": 0}
    st.session_state["minas"] = minas

# Formulario para editar plantas
def plantas_form():
    st.subheader("Plantas")
    plantas = st.session_state["plantas"]
    to_delete = []
    for nombre, datos in plantas.items():
        with st.expander(f"{nombre}"):
            new_nombre = st.text_input(f"Nombre planta", value=nombre, key=f"plantaname_{nombre}")
            capacidad = st.number_input(f"Capacidad", value=datos["capacidad"], key=f"plantacap_{nombre}")
            proceso = {}
            for t in ["alto", "bajo"]:
                proceso[t] = st.number_input(f"Costo proceso {t}", value=datos["proceso"].get(t, 0), key=f"plantaproc_{nombre}_{t}")
            if st.button(f"Eliminar planta {nombre}"):
                to_delete.append(nombre)
            plantas[new_nombre] = {"capacidad": capacidad, "proceso": proceso}
            if new_nombre != nombre:
                to_delete.append(nombre)
    for nombre in to_delete:
        if nombre in plantas:
            del plantas[nombre]
    if st.button("Agregar planta"):
        plantas[f"Planta{len(plantas)+1}"] = {"capacidad": 0, "proceso": {"alto": 0, "bajo": 0}}
    st.session_state["plantas"] = plantas

# Formulario para editar mezclas
def mezclas_form():
    st.subheader("Mezclas de acero")
    mezclas = st.session_state["mezclas"]
    for t in ["alto", "bajo"]:
        with st.expander(f"Mezcla {t}"):
            for tipo in ["A", "B"]:
                mezclas[t][tipo] = st.number_input(f"{t} - {tipo}", value=mezclas[t][tipo], key=f"mezcla_{t}_{tipo}")
    st.session_state["mezclas"] = mezclas

# Formulario para editar países
def paises_form():
    st.subheader("Países destino")
    paises = st.session_state["paises"]
    to_delete = []
    for nombre, datos in paises.items():
        with st.expander(f"{nombre}"):
            new_nombre = st.text_input(f"Nombre país", value=nombre, key=f"paisname_{nombre}")
            alto = st.number_input(f"Demanda alto", value=datos["alto"], key=f"paisalto_{nombre}")
            bajo = st.number_input(f"Demanda bajo", value=datos["bajo"], key=f"paisbajo_{nombre}")
            envio = {}
            for planta in st.session_state["plantas"]:
                envio[planta] = {}
                for t in ["alto", "bajo"]:
                    envio[planta][t] = st.number_input(f"Envío {planta} {t}", value=datos["envio"].get(planta, {}).get(t, 0), key=f"paisenvio_{nombre}_{planta}_{t}")
            if st.button(f"Eliminar país {nombre}"):
                to_delete.append(nombre)
            paises[new_nombre] = {"alto": alto, "bajo": bajo, "envio": envio}
            if new_nombre != nombre:
                to_delete.append(nombre)
    for nombre in to_delete:
        if nombre in paises:
            del paises[nombre]
    if st.button("Agregar país"):
        paises[f"País{len(paises)+1}"] = {"alto": 0, "bajo": 0, "envio": {pl: {"alto": 0, "bajo": 0} for pl in st.session_state["plantas"]}}
    st.session_state["paises"] = paises

# Mostrar formularios
# Quitar el expander externo para evitar anidación
minas_form()
plantas_form()
mezclas_form()
paises_form()

# Usar los datos editados
minas = st.session_state["minas"]
plantas = st.session_state["plantas"]
mezclas = st.session_state["mezclas"]
paises = st.session_state["paises"]

# =======================
# SUMAR/RESTAR VARIABLES ANTES DE RESOLVER
# =======================

st.sidebar.header("➕➖ Sumar/Restar variables")

# Minas
if st.sidebar.button("+ Agregar mina"):
    minas[f"Mina{len(minas)+1}"] = {"tipo": "A", "compra": 0, "envio": {0 for pl in plantas}, "limite": 0}
if st.sidebar.button("- Quitar mina") and len(minas) > 1:
    minas.pop(list(minas.keys())[-1])

# Plantas
if st.sidebar.button("+ Agregar planta"):
    plantas[f"Planta{len(plantas)+1}"] = {"capacidad": 0, "proceso": {"alto": 0, "bajo": 0}}
if st.sidebar.button("- Quitar planta") and len(plantas) > 1:
    plantas.pop(list(plantas.keys())[-1])

# Países
if st.sidebar.button("+ Agregar país"):
    paises[f"País{len(paises)+1}"] = {"alto": 0, "bajo": 0, "envio": {pl: {"alto": 0, "bajo": 0} for pl in plantas}}
if st.sidebar.button("- Quitar país") and len(paises) > 1:
    paises.pop(list(paises.keys())[-1])

# Mezclas (solo sumar/restar tipos si lo deseas, pero normalmente son fijos)

st.session_state["minas"] = minas
st.session_state["plantas"] = plantas
st.session_state["paises"] = paises

# =======================
# RESOLUCIÓN Y TABLAS BONITAS
# =======================

# =======================
# SELECCIÓN DE OBJETIVO
# =======================

objetivo = st.radio(
    "¿Qué desea hacer?",
    ("Minimizar costo total", "Maximizar producción total"),
    index=0
)

if st.button("🔍 Resolver modelo"):
    with st.spinner("Calculando solución óptima..."):
        modelo = pulp.LpProblem("Modelo_American_Steel", pulp.LpMinimize if objetivo == "Minimizar costo total" else pulp.LpMaximize)

        # VARIABLES CORRECTAS
        envio_mineral = pulp.LpVariable.dicts("envioMineral", [(m, p) for m in minas for p in plantas], lowBound=0)
        procesado = pulp.LpVariable.dicts("procesado", [(p, t) for p in plantas for t in ["alto", "bajo"]], lowBound=0)
        distribucion = pulp.LpVariable.dicts("distribucion", [(p, c, t) for p in plantas for c in paises for t in ["alto", "bajo"]], lowBound=0)
        uso_mineral = pulp.LpVariable.dicts("usoMineral", [(m, p, t) for m in minas for p in plantas for t in ["alto", "bajo"]], lowBound=0)

        # OBJETIVO CORRECTO
        if objetivo == "Minimizar costo total":
            modelo += (
                pulp.lpSum(envio_mineral[m, p] * (minas[m]["compra"] + minas[m]["envio"][p]) for m in minas for p in plantas) +
                pulp.lpSum(procesado[p, t] * plantas[p]["proceso"][t] for p in plantas for t in ["alto", "bajo"]) +
                pulp.lpSum(distribucion[p, c, t] * paises[c]["envio"][p][t] for p in plantas for c in paises for t in ["alto", "bajo"])
            )
        else:
            modelo += pulp.lpSum(procesado[p, t] for p in plantas for t in ["alto", "bajo"])

        # RESTRICCIONES
        for m in minas:
            modelo += pulp.lpSum(envio_mineral[m, p] for p in plantas) <= minas[m]["limite"]
        for p in plantas:
            modelo += pulp.lpSum(envio_mineral[m, p] for m in minas) <= plantas[p]["capacidad"]
        # Relación entre uso de mineral y procesado (mezcla)
        for p in plantas:
            for t in ["alto", "bajo"]:
                suma_mezcla = mezclas[t]["A"] + mezclas[t]["B"]
                for m in minas:
                    tipo = minas[m]["tipo"]
                    modelo += uso_mineral[m, p, t] == procesado[p, t] * (mezclas[t][tipo] / suma_mezcla)
        # Balance de mineral enviado y usado en cada planta
        for m in minas:
            for p in plantas:
                modelo += envio_mineral[m, p] == pulp.lpSum(uso_mineral[m, p, t] for t in ["alto", "bajo"])
        # Balance de planta: lo que entra = lo que se procesa
        for p in plantas:
            modelo += pulp.lpSum(envio_mineral[m, p] for m in minas) == pulp.lpSum(procesado[p, t] for t in ["alto", "bajo"])
        for p in plantas:
            for t in ["alto", "bajo"]:
                modelo += pulp.lpSum(distribucion[p, c, t] for c in paises) <= procesado[p, t]
        for c in paises:
            for t in ["alto", "bajo"]:
                modelo += pulp.lpSum(distribucion[p, c, t] for p in plantas) == paises[c][t]

        # RESTRICCIONES ESPECÍFICAS DEL USUARIO
        for restr in st.session_state["restricciones_especificas"]:
            m = restr["mina"]
            p = restr["planta"]
            expr = envio_mineral[m, p]
            if restr["oper"] == "<=" :
                modelo += expr <= restr["valor"]
            elif restr["oper"] == ">=":
                modelo += expr >= restr["valor"]
            else:
                modelo += expr == restr["valor"]

        modelo.solve()

        if pulp.LpStatus[modelo.status] == "Optimal":
            st.success(f"✅ Solución óptima encontrada. Costo total: ${pulp.value(modelo.objective):,.2f}")

            # TABLA 1: Envío de mineral de minas a plantas
            st.subheader("Envío de mineral de minas a plantas")
            rows_envio = [
                {"Mina": m, "Planta": p, "Toneladas": envio_mineral[m, p].varValue}
                for m in minas for p in plantas if envio_mineral[m, p].varValue > 0
            ]
            st.dataframe(pd.DataFrame(rows_envio))

            # TABLA 2: Producción por planta y tipo
            st.subheader("Producción por planta y tipo")
            rows_prod = [
                {"Planta": p, "Tipo": t, "Toneladas": procesado[p, t].varValue}
                for p in plantas for t in ["alto", "bajo"] if procesado[p, t].varValue > 0
            ]
            st.dataframe(pd.DataFrame(rows_prod))

            # TABLA 3: Distribución de acero a países
            st.subheader("Distribución de acero a países")
            rows_dist = [
                {"Desde": p, "Hacia": c, "Tipo": t, "Toneladas": distribucion[p, c, t].varValue}
                for p in plantas for c in paises for t in ["alto", "bajo"] if distribucion[p, c, t].varValue > 0
            ]
            st.dataframe(pd.DataFrame(rows_dist))
        else:
            st.error("No se encontró una solución óptima.")

# =======================
# PANEL DE RESTRICCIONES MATEMÁTICAS EDITABLES (ESPECÍFICO Y AMIGABLE)
# =======================

# Estructura: lista de restricciones, cada una es un dict con: {"tipo": str, "mina": str, "planta": str, "oper": str, "valor": float}
# tipo: "limite_mina", "capacidad_planta", "mezcla", "balance", etc.
# oper: ">=", "<=", "="

restricciones_default = []
for m in minas:
    for p in plantas:
        restricciones_default.append({
            "tipo": "limite_mina",
            "mina": m,
            "planta": p,
            "oper": "<=",
            "valor": minas[m]["limite"]
        })
for p in plantas:
    for m in minas:
        restricciones_default.append({
            "tipo": "capacidad_planta",
            "mina": m,
            "planta": p,
            "oper": "<=",
            "valor": plantas[p]["capacidad"]
        })

if "restricciones_especificas" not in st.session_state:
    st.session_state["restricciones_especificas"] = restricciones_default.copy()

with st.expander("✏️ Restricciones matemáticas (afectan el modelo, edición específica)"):
    st.markdown("Puedes editar, agregar o eliminar restricciones matemáticas. Cada restricción es de la forma: [mina] [operador] [planta] [valor].")
    for i, restr in enumerate(st.session_state["restricciones_especificas"]):
        cols = st.columns([2,1,2,1,2,1])
        with cols[0]:
            restr["mina"] = st.selectbox(f"Mina", list(minas.keys()), index=list(minas.keys()).index(restr["mina"]), key=f"mina_{i}")
        with cols[1]:
            st.write("↔")
        with cols[2]:
            restr["planta"] = st.selectbox(f"Planta", list(plantas.keys()), index=list(plantas.keys()).index(restr["planta"]), key=f"planta_{i}")
        with cols[3]:
            restr["oper"] = st.selectbox("Operador", ["<=", ">=", "="], index=["<=", ">=", "="].index(restr["oper"]), key=f"oper_{i}")
        with cols[4]:
            restr["valor"] = st.number_input("Valor", value=restr["valor"], key=f"valor_{i}")
        with cols[5]:
            if st.button("Eliminar", key=f"elim_esp_{i}"):
                st.session_state["restricciones_especificas"].pop(i)
                st.rerun()
    if st.button("Agregar restricción vacía (específica)"):
        st.session_state["restricciones_especificas"].append({"tipo": "limite_mina", "mina": list(minas.keys())[0], "planta": list(plantas.keys())[0], "oper": "<=", "valor": 0.0})
        st.rerun()
