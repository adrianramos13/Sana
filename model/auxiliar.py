import requests
import json

def obtener_respuesta_api(data, url):
    print(f"URL: {url}")
    print(f"Data: {data}")
    try:
        response = requests.post(url, json=data, timeout=300)
        if response.status_code == 200:
            return response.json()  # Devuelve el JSON del servidor
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None
    
def formatear_json(json_obj):
    # Si el resultado viene como dict anidado con 'result' en texto JSON
    texto_json = json_obj.get("result", "")
    if isinstance(texto_json, dict):
        parsed = texto_json  # Ya es dict
    else:
        try:
            parsed = json.loads(texto_json)
        except json.JSONDecodeError:
            print("⚠️ El campo 'result' no contiene un JSON válido.")
            return None
    return parsed

def imprimir_campo(resultado, field):
    if resultado and "answer" in resultado:
        # Si el resultado viene como dict anidado con 'result' en texto JSON
        parsed = formatear_json(resultado["answer"])
        # Obtener el campo deseado
        campo = parsed.get(field)
        if campo:
            return campo
        else:
            print(f"⚠️ No se encontró el campo '{field}' en la respuesta.")
            return None
    else:
        print("⚠️ No se pudo obtener respuesta del modelo.")
        return None
        
def medicamentos(historial, diagnostico , url):
    print("¿Toma usted algún medicamento actualmente? En caso positivo, indique cuál o cuáles.")
    respuesta = input("Tú: ")
    data = {
        "diagnostico": diagnostico,
        "age": historial["edad"],
        "gender": historial["genero"],
        "medicamentos_actuales": respuesta
    }
    return obtener_respuesta_api(data, url)

def extraer_sintomas(query_text):
    if "Síntomas:" in query_text:
        sintomas = query_text.split("Síntomas:")[1].strip()
        # Elimina basura si hay JSON después por error
        sintomas = sintomas.split('"result"')[0].strip()
        return sintomas
    return "No especificados"

def extraer_clarificaciones(diagnostico):
    raw_query = diagnostico["answer"]["query"]

    # Buscar el JSON dentro del string
    try:
        inicio = raw_query.index("{")
        json_interno = raw_query[inicio:]
        parsed = json.loads(json_interno)
    except:
        return None

    # Ahora parsed["answer"]["clarifications"]
    try:
        return parsed["answer"].get("clarifications", "").strip()
    except:
        return None
    
def convertir_a_texto(valor):
    if isinstance(valor, list):
        return "\n".join(f"- {elem}" for elem in valor)
    return str(valor)

def guardar_pdf(datos_usuario, historial, diagnostico, recomendacion):
    from fpdf import FPDF
    import os, json

    pdf = FPDF()
    pdf.add_page()

    # Ruta correcta a /fonts/
    ruta_base = os.path.dirname(os.path.dirname(__file__))
    ruta_fuente_regular = os.path.join(ruta_base, "fonts", "ARIAL.TTF")
    ruta_fuente_bold = os.path.join(ruta_base, "fonts", "ARIALBD.TTF")

    pdf.add_font("ArialUnicode", "", ruta_fuente_regular, uni=True)
    pdf.add_font("ArialUnicode", "B", ruta_fuente_bold, uni=True)

    # ============= TÍTULO =============
    pdf.set_font("ArialUnicode", "B", 20)
    pdf.cell(0, 12, "Informe Médico", ln=True, align="C")
    pdf.ln(10)

    # ============= DATOS PERSONALES =============
    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(0, 10, "DATOS DEL PACIENTE", ln=True)
    pdf.ln(3)

    pdf.set_font("ArialUnicode", "B", 12)
    pdf.cell(40, 8, "Nombre:", ln=False)
    pdf.set_font("ArialUnicode", "", 12)
    pdf.cell(0, 8, datos_usuario['nombre'].title(), ln=True)

    pdf.set_font("ArialUnicode", "B", 12)
    pdf.cell(40, 8, "Edad:", ln=False)
    pdf.set_font("ArialUnicode", "", 12)
    pdf.cell(0, 8, str(datos_usuario['edad']), ln=True)

    pdf.set_font("ArialUnicode", "B", 12)
    pdf.cell(40, 8, "Género:", ln=False)
    pdf.set_font("ArialUnicode", "", 12)
    pdf.cell(0, 8, datos_usuario['genero'], ln=True)

    pdf.set_font("ArialUnicode", "B", 12)
    pdf.cell(40, 8, "Población:", ln=False)
    pdf.set_font("ArialUnicode", "", 12)
    pdf.cell(0, 8, datos_usuario['poblacion'].title(), ln=True)

    pdf.ln(10)

    # ============= SÍNTOMAS DEL PACIENTE =============
    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(0, 10, "SÍNTOMAS DEL PACIENTE", ln=True)
    pdf.ln(3)

    pdf.set_font("ArialUnicode", "", 12)
    query_text = diagnostico["answer"]["query"]
    sintomas = extraer_sintomas(query_text)
    pdf.multi_cell(0, 8, sintomas)
    pdf.ln(10)

    # ============= PREGUNTAS ACLARATORIAS =============
    clarificaciones = extraer_clarificaciones(diagnostico)

    if clarificaciones:
        pdf.set_font("ArialUnicode", "B", 14)
        pdf.cell(0, 10, "PREGUNTAS ACLARATORIAS", ln=True)
        pdf.ln(3)

        pdf.set_font("ArialUnicode", "", 12)
        pdf.multi_cell(0, 8, clarificaciones)
        pdf.ln(10)

    # ============= DIAGNÓSTICO =============
    pdf.set_font("ArialUnicode", "B", 14)
    pdf.cell(0, 10, "DIAGNÓSTICO DEFINITIVO", ln=True)
    pdf.ln(3)

    pdf.set_font("ArialUnicode", "", 12)
    parsed_diag = formatear_json(diagnostico["answer"])
    diagnostico_str = parsed_diag["Diagnóstico definitivo"]
    pdf.multi_cell(0, 8, convertir_a_texto(diagnostico_str))
    pdf.ln(10)

    # ============= RECOMENDACIÓN =============
    if recomendacion:
        pdf.set_font("ArialUnicode", "B", 14)
        pdf.cell(0, 10, "RECOMENDACIÓN", ln=True)
        pdf.ln(3)

        pdf.set_font("ArialUnicode", "", 12)
        raw = recomendacion["answer"]["result"]
        parsed = json.loads(raw)

        # Medicamento recomendado
        pdf.set_font("ArialUnicode", "B", 12)
        pdf.cell(0, 8, "Medicamento recomendado:", ln=True)
        pdf.set_font("ArialUnicode", "", 12)
        pdf.multi_cell(0, 8, parsed.get("Medicamento recomendado", "N/A"))
        pdf.ln(3)

        # Justificación
        pdf.set_font("ArialUnicode", "B", 12)
        pdf.cell(0, 8, "Justificación:", ln=True)
        pdf.set_font("ArialUnicode", "", 12)
        pdf.multi_cell(0, 8, parsed.get("Justificación", "N/A"))
        pdf.ln(3)

        # Advertencias
        pdf.set_font("ArialUnicode", "B", 12)
        pdf.cell(0, 8, "Advertencias:", ln=True)
        pdf.set_font("ArialUnicode", "", 12)
        pdf.multi_cell(0, 8, parsed.get("Advertencias o precauciones", "N/A"))
        pdf.ln(3)

    # ============= GUARDAR PDF =============
    ruta_actual = os.getcwd()
    carpeta_superior = os.path.dirname(ruta_actual)
    output_path = os.path.join(carpeta_superior, "informe_medico.pdf")

    pdf.output(output_path)
    print(f"Informe médico guardado en: {output_path}")

