import requests
from app.config import get_settings

settings = get_settings()

# Connection pooling: reutilizar conexiones TCP entre llamadas
_session = requests.Session()
_session.headers.update({"Content-Type": "application/json"})

DEFAULT_ENTITIES = [
    "CHILE_RUT", "EMAIL_ADDRESS", "PERSON", 
    "DATA_SALUD", "DATA_ETNIA", "DATA_POLITICA", "DATA_RELIGION", "DATA_SEXUALIDAD",
    "DATA_SINDICAL", "DATA_SOCIOECONOMICO", "DATA_IDEOLOGIA", "DATA_BIOLOGICO", "DATA_BIOMETRICO",
    "PHONE_NUMBER", "DATE_TIME",
    "DOMICILIO", "NACIONALIDAD", "DATA_PENAL",
    "PASAPORTE", "LICENCIA_CONDUCIR", "CUENTA_BANCARIA", "NUMERO_SERIE_DOC"
]

AD_HOC_RECOGNIZERS = [
    {
        "name": "DetectorRUT",
        "supported_entity": "CHILE_RUT",
        "supported_language": "es",
        "patterns": [
            # El OCR suele agregar espacios fantasma, comas en vez de puntos, o separar
            # el guión (ej: '19.456 . 789 - K'). Este regex es altamente tolerante al ruido.
            {"name": "rut", "regex": r"\b\d{1,2}[\s,.]*\d{3}[\s,.]*\d{3}[\s.-]*[\dkK]\b", "score": 0.9}
        ]
    },
    {
        "name": "DetectorEmail",
        "supported_entity": "EMAIL_ADDRESS",
        "supported_language": "es",
        "patterns": [
            {"name": "email", "regex": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "score": 0.95}
        ]
    },
    {
        # El NER generico (spaCy) falla en documentos tipo carnet: son fragmentos
        # de mayusculas sueltas (etiqueta: valor) sin estructura de oracion normal,
        # y el modelo de nombres esta entrenado para texto corrido. Este detector
        # busca secuencias de 2 a 4 palabras en MAYUSCULAS (nombres/apellidos en
        # carnets, contratos, formularios). Los falsos positivos institucionales
        # ("REPUBLICA DE CHILE", "SERVICIO DE REGISTRO CIVIL", etc.) se filtran
        # aparte en analyze_text() usando _BOILERPLATE_WORDS.
        "name": "DetectorNombreMayusculas",
        "supported_entity": "PERSON",
        "supported_language": "es",
        "patterns": [
            # (?-i:...) fuerza sensibilidad a mayusculas: Presidio compila los
            # patrones ad-hoc con IGNORECASE por defecto, y sin este scoped-flag
            # el regex tambien matcheaba palabras en minuscula/mixtas (ruido OCR).
            {"name": "nombre_mayusculas", "regex": r"(?-i:\b(?!(?:REPUBLICA|CHILE|SERVICIO|REGISTRO|CIVIL|IDENTIFICACION|CEDULA|IDENTIDAD|NACIONALIDAD|SEXO|FECHA|NACIMIENTO|EMISION|VENCIMIENTO|DOCUMENTO|NUMERO|FIRMA|TITULAR|APELLIDOS|NOMBRES|CHILENA|CHILENO|RUN|RUT)\b)[A-ZÁÉÍÓÚÑ]{3,}(?:\s+(?!(?:REPUBLICA|CHILE|SERVICIO|REGISTRO|CIVIL|IDENTIFICACION|CEDULA|IDENTIDAD|NACIONALIDAD|SEXO|FECHA|NACIMIENTO|EMISION|VENCIMIENTO|DOCUMENTO|NUMERO|FIRMA|TITULAR|APELLIDOS|NOMBRES|CHILENA|CHILENO|RUN|RUT)\b)[A-ZÁÉÍÓÚÑ]{3,}){1,4}\b)", "score": 0.55}
        ],
        "context": ["apellidos", "nombres", "titular", "cedula", "identidad"]
    },
    {
        "name": "DetectorTelefono",
        "supported_entity": "PHONE_NUMBER",
        "supported_language": "es",
        "patterns": [
            {"name": "telefono", "regex": r"\b(?:\+?56\s*[92]\s*\d{4}\s*\d{4}|\+?56\s*[92]\s*\d{8}|[92]\s*\d{8}|[92]\s*\d{4}\s*\d{4})\b", "score": 0.9}
        ]
    },
    {
        "name": "DetectorFecha",
        "supported_entity": "DATE_TIME",
        "supported_language": "es",
        "patterns": [
            {"name": "fecha", "regex": r"\b(?:\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{4}/\d{2}/\d{2}|\d{2}/\d{2}/\d{4})\b", "score": 0.85},
            {
                # El sufijo [a-z]* cubre tanto la forma abreviada (MAY) como el
                # nombre completo del mes (MAYO), que es como lo imprime el carnet.
                "name": "fecha_carnet",
                "regex": r"(?i)\b\d{1,2}\s?(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)[a-z]*\s?\d{4}\b",
                "score": 0.8
            }
        ]
    },
    {
        "name": "DetectorSalud",
        "supported_entity": "DATA_SALUD",
        "supported_language": "es",
        "patterns": [
            {
                "name": "medico",
                "regex": r"(?i)\b(cáncer|cancer|vih|sida|diabetes|depresión|depresion|biopsia|alzheimer|ansiedad|trastorno|asma|hipertensión|hipertension|artrosis|artritis|epilepsia|leucemia|cardiopatía|cardiopatia|infarto|esclerosis|lupus|obesidad|escoliosis|alergia|esquizofrenia|autismo|celiaquía|celiaquia|parkinson|demencia|tumor|hepatitis|gastritis|colon\s+irritable|fibromialgia|insuficiencia\s+renal|marcapasos|psiquiatra|psiquiatría|oncología|oncologia|quimioterapia|radioterapia|diálisis|dialisis|tratamiento\s+médico|tratamiento\s+medico|diagnóstico|diagnostico)\b",
                "score": 0.6
            }
        ],
        "context": [
            "paciente", "diagnóstico", "diagnostico", "clínica", "clinica", "doctor", "médico", "medico", "examen", 
            "licencia", "resultados", "informe", "positivo", "arroja", "presencia", "tratamiento", 
            "ficha", "receta", "terapia", "ingreso", "alta", "patología", "patologia", "enfermedad"
        ]
    },
    {
        "name": "DetectorEtnia",
        "supported_entity": "DATA_ETNIA",
        "supported_language": "es",
        "patterns": [
            {
                "name": "pueblos",
                "regex": r"(?i)\b(mapuche|aymara|rapa\s*nui|diaguita|atacameño|atacameno|colla|kawésqar|kawesqar|yagán|yagan|indígena|indigena|quechua|alacalufe|chango|yamana|tribal|afrodescendiente|licanantay|chono|pueblo\s+originario|pueblos\s+originarios)\b",
                "score": 0.6
            }
        ],
        "context": [
            "conadi", "certificado", "ascendencia", "origen", "pueblo", "etnia", "comunidad", 
            "beca", "subsidio", "pertenece", "identidad", "linaje", "registro", "etnico", "étnico"
        ]
    },
    {
        "name": "DetectorPolitica",
        "supported_entity": "DATA_POLITICA",
        "supported_language": "es",
        "patterns": [
            {
                "name": "politica",
                "regex": r"(?i)\b(partido\s+comunista|udi|renovación\s+nacional|rn|frente\s+amplio|partido\s+socialista|dc|democracia\s+cristiana|republicano|republicanos|evópoli|evopoli|comunes|revolución\s+democrática|rd|convergencia\s+social|partido\s+de\s+la\s+gente|pdg|partido\s+radical|pr|ppd|demócratas|democratas|amarillos|comunista|socialista|derecha|izquierda|gremialismo|gremialista|centroderecha|centroizquierda|militancia|militante|afiliado\s+político|afiliado\s+politico|partido\s+político|partido\s+politico)\b",
                "score": 0.6
            }
        ],
        "context": [
            "militante", "afiliado", "cuota", "descuento", "planilla", "votación", "votacion", "delegado", 
            "padrón", "padron", "inscripción", "inscripcion", "huelga", "aportes", "partido", "política", "politica", "elecciones", 
            "candidato", "comité", "comite"
        ]
    },
    {
        "name": "DetectorReligion",
        "supported_entity": "DATA_RELIGION",
        "supported_language": "es",
        "patterns": [
            {
                "name": "religiones",
                "regex": r"(?i)\b(católico|catolico|evangélico|evangelico|judío|judio|musulmán|musulman|mormón|mormon|testigo\s+de\s+jehová|testigo\s+de\s+jehova|protestante|anglicano|bautista|budista|hindú|hindu|ortodoxo|adventista|islam|judaísmo|judaismo|cristianismo|catolicismo|religión|religion|creencia|creencias|credo|parroquia|iglesia|templo|sinagoga|mezquita)\b",
                "score": 0.6
            }
        ],
        "context": [
            "bautizo", "sacramento", "diezmo", "iglesia", "parroquia", "culto", "congregación", "congregacion", 
            "retiro", "capellán", "capellan", "religión", "religion", "creencia", "fe", "perteneciente", "pastor", 
            "sacerdote", "obispo", "templo", "comunión", "comunion"
        ]
    },
    {
        "name": "DetectorSexualidad",
        "supported_entity": "DATA_SEXUALIDAD",
        "supported_language": "es",
        "patterns": [
            {
                "name": "sexualidad",
                "regex": r"(?i)\b(homosexual|heterosexual|bisexual|transgénero|transgenero|transexual|transexualidad|lesbiana|gay|queer|pansexual|asexual|no\s+binario|no-binario|intersexual|lgbt|lgbtq|lgbtqia|pansexualidad|asexualidad|demisexual|orientación\s+sexual|orientacion\s+sexual|identidad\s+de\s+género|identidad\s+de\s+genero)\b",
                "score": 0.6
            }
        ],
        "context": [
            "orientación", "orientacion", "identidad", "género", "genero", "pareja", "convivencia", "discriminación", "discriminacion", 
            "transición", "transicion", "acuerdo de unión civil", "auc", "diversidad", "colectivo"
        ]
    },
    {
        "name": "DetectorSindical",
        "supported_entity": "DATA_SINDICAL",
        "supported_language": "es",
        "patterns": [
            {
                "name": "sindical",
                "regex": r"(?i)\b(sindicato|sindical|colegiatura|afiliación\s+sindical|afiliacion\s+sindical|federación\s+sindical|federacion\s+sindical|gremio|asociación\s+gremial|asociacion\s+gremial|cut|anef|colegio\s+de\s+profesores|confederación\s+de\s+trabajadores|confederacion\s+de\s+trabajadores|asociación\s+de\s+funcionarios|asociacion\s+de\s+funcionarios|sindicalizado|sindicalizado|huelga|negociación\s+colectiva|negociacion\s+colectiva|dirigente\s+sindical|fuero\s+sindical)\b",
                "score": 0.6
            }
        ],
        "context": [
            "afiliado", "cuota", "descuento", "huelga", "socio", "gremio", "directiva", 
            "negociación colectiva", "negociacion colectiva", "sindicato", "federación", "federacion", "asociación", "asociacion", "anef", 
            "cut", "profesores"
        ]
    },
    {
        "name": "DetectorSocioeconomico",
        "supported_entity": "DATA_SOCIOECONOMICO",
        "supported_language": "es",
        "patterns": [
            {
                "name": "socioeconomico",
                "regex": r"(?i)\b(quintil|decil|registro\s+social\s+de\s+hogares|rsh|ficha\s+social|vulnerabilidad\s+social|subsidio\s+familiar|subsidio\s+único\s+familiar|suf|ficha\s+de\s+protección\s+social|ficha\s+de\s+proteccion\s+social|bono\s+marzo|psu|paes|beca\s+junaeb|gratuidad|subsidio\s+habitacional|fonasa|isapre|tramo\s+fonasa|pilar\s+solidario|pensión\s+garantizada\s+universal|pgu|puntaje\s+rsh|tramo\s+de\s+ingresos|subsidio\s+estatal|ingreso\s+mensual|renta\s+mensual|situación\s+socioeconómica|situacion\s+socioeconomica)\b",
                "score": 0.6
            },
            {
                "name": "monto_dinero",
                "regex": r"\b(?:\$|clp|uf|utm)?\s*\d{1,3}(?:\.\d{3})+(?:,\d+)?\b|\b\d{5,8}(?:\.\d+)?\b",
                "score": 0.4
            }
        ],
        "context": [
            "clasificación", "clasificacion", "vulnerabilidad", "tramo", "puntaje", "registro", "ingresos", 
            "hogares", "nivel socioeconómico", "nivel socioeconomico", "subsidio", "bono", "beca", "fonasa", 
            "isapre", "pgu", "afiliación", "afiliacion", "renta", "sueldo", "salario", "remuneración", 
            "remuneracion", "ingreso", "pago"
        ]
    },
    {
        "name": "DetectorIdeologia",
        "supported_entity": "DATA_IDEOLOGIA",
        "supported_language": "es",
        "patterns": [
            {
                "name": "ideologia",
                "regex": r"(?i)\b(pacifismo|veganismo|humanismo\s+secular|librepensador|ecologismo|marxismo|anarquismo|conservadurismo|liberalismo|credo\s+filosófico|credo\s+filosofico|feminismo|feminista|anarco|libertarismo|libertario|neoliberalismo|nacionalismo|progresismo|marxista|ideología|ideologia|postura\s+ideológica|postura\s+ideologica|convicción\s+filosófica|conviccion\s+filosofica)\b",
                "score": 0.6
            }
        ],
        "context": [
            "convicción", "conviccion", "filosófica", "filosofica", "ideológica", "ideologica", "postura", "pensamiento", "creencia", 
            "adherente", "ideología", "ideologia", "corriente", "movimiento"
        ]
    },
    {
        "name": "DetectorBiologico",
        "supported_entity": "DATA_BIOLOGICO",
        "supported_language": "es",
        "patterns": [
            {
                "name": "biologico",
                "regex": r"(?i)\b(adn|genoma|cariotipo|secuencia\s+de\s+adn|marcador\s+genético|marcador\s+genetico|secuenciación\s+genética|secuenciacion\s+genetica|genotipo|alelo|grupo\s+sanguíneo|grupo\s+sanguineo|factor\s+rh|rna|arn|ácido\s+desoxirribonucleico|acido\s+desoxirribonucleico|ácido\s+ribonucleico|acido\s+ribonucleico|huella\s+genética|huella\s+genetica|ácido\s+nucleico|acido\s+nucleico|perfil\s+genético|perfil\s+genetico|código\s+genético|codigo\s+genetico)\b",
                "score": 0.6
            },
            {
                "name": "grupo_sanguineo",
                "regex": r"\b(?:A|B|AB|O)[+-]\b",
                "score": 0.4
            }
        ],
        "context": [
            "muestra", "secuencia", "análisis", "analisis", "perfil", "biológico", "biologico", "paterno", "materno", 
            "compatibilidad", "herencia", "laboratorio", "adn", "grupo", "rh", "sangre"
        ]
    },
    {
        "name": "DetectorBiometrico",
        "supported_entity": "DATA_BIOMETRICO",
        "supported_language": "es",
        "patterns": [
            {
                "name": "biometrico",
                "regex": r"(?i)\b(huella\s+dactilar|reconocimiento\s+facial|huella\s+digital|patrón\s+de\s+voz|patron\s+de\s+voz|iris|biometría|biometria|biométrico|biometrico|registro\s+biométrico|registro\s+biometrico|escáner\s+de\s+iris|escaner\s+de\s+iris|reconocimiento\s+de\s+voz|reconocimiento\s+de\s+firma|firma\s+digitalizada|geometría\s+de\s+la\s+mano|geometria\s+de\s+la\s+mano|sensor\s+biométrico|sensor\s+biometrico|lector\s+de\s+huellas|facial\s+3d)\b",
                "score": 0.6
            },
            {
                "name": "biometrico_hash",
                "regex": r"\b[a-fA-F0-9]{32,128}\b",
                "score": 0.4
            }
        ],
        "context": [
            "registro", "verificación", "verificacion", "autenticación", "autenticacion", "acceso", "lector", "biométrico", "biometrico", 
            "identidad", "huella", "firma", "facial", "iris", "reconocimiento", "patrón", "patron", "hash"
        ]
    },
    {
        "name": "DetectorDomicilio",
        "supported_entity": "DOMICILIO",
        "supported_language": "es",
        "patterns": [
            {
                "name": "direccion_chilena",
                "regex": r"(?i)\b(?:av(?:enida)?|calle|pasaje|pje|psje|villa|condominio|depto|departamento|block|bloque|torre|piso|parcela|lote|sitio|camino|ruta|carretera|autopista|circunvalación|circunvalacion|diagonal|costanera|rotonda|bulevar|boulevar|vereda|callejón|callejon|alameda|gran\s+avenida|panamericana)\.?\s+[A-ZÁÉÍÓÚÑa-záéíóúñ0-9#°\s,.-]{3,60}\b",
                "score": 0.6
            }
        ],
        "context": [
            "dirección", "direccion", "domicilio", "residencia", "vivienda", "hogar", "comuna", "ciudad",
            "región", "region", "localidad", "sector", "población", "poblacion", "barrio",
            "código postal", "codigo postal", "vive", "reside", "ubicación", "ubicacion"
        ]
    },
    {
        "name": "DetectorNacionalidad",
        "supported_entity": "NACIONALIDAD",
        "supported_language": "es",
        "patterns": [
            {
                "name": "gentilicios",
                "regex": r"(?i)\b(chileno|chilena|peruano|peruana|boliviano|boliviana|colombiano|colombiana|venezolano|venezolana|argentino|argentina|ecuatoriano|ecuatoriana|haitiano|haitiana|brasileño|brasileña|brasileno|brasilena|mexicano|mexicana|dominicano|dominicana|cubano|cubana|paraguayo|paraguaya|uruguayo|uruguaya|guatemalteco|guatemalteca|panameño|panameña|panameno|panamena|costarricense|hondureño|hondureña|hondureno|hondurena|salvadoreño|salvadoreña|salvadoreno|salvadorena|nicaragüense|nicaraguense|puertorriqueño|puertorriqueña|puertorriqueno|puertorriquena|español|española|espanol|espanola|estadounidense|norteamericano|norteamericana|canadiense|francés|francesa|frances|alemán|alemana|aleman|italiano|italiana|chino|china|japonés|japonesa|japones|coreano|coreana|indio|india|ruso|rusa|ucraniano|ucraniana|británico|británica|britanico|britanica|australiano|australiana|sudafricano|sudafricana)\b",
                "score": 0.6
            }
        ],
        "context": [
            "nacionalidad", "pasaporte", "migración", "migracion", "visa", "extranjero", "extranjera",
            "ciudadanía", "ciudadania", "residencia", "país", "pais", "origen", "natural de",
            "nacido", "nacida", "inmigrante", "emigrante", "permiso", "patria"
        ]
    },
    {
        "name": "DetectorPenal",
        "supported_entity": "DATA_PENAL",
        "supported_language": "es",
        "patterns": [
            {
                "name": "penal_judicial",
                "regex": r"(?i)\b(condena|condenado|condenada|sentencia\s+penal|antecedente\s+penal|antecedentes\s+penales|prontuario|homicidio|parricidio|femicidio|hurto|robo|estafa|narcotráfico|narcotrafico|tráfico\s+de\s+drogas|trafico\s+de\s+drogas|lavado\s+de\s+activos|violación|violacion|abuso\s+sexual|delito|delitos|imputado|imputada|procesado|procesada|formalizado|formalizada|recluso|reclusa|privado\s+de\s+libertad|privada\s+de\s+libertad|presidio|reclusión|reclusion|libertad\s+condicional|remisión\s+condicional|remision\s+condicional|pena\s+remitida|inhabilitación|inhabilitacion|reincidente|reincidencia|extracto\s+de\s+filiación|extracto\s+de\s+filiacion|certificado\s+de\s+antecedentes|registro\s+civil\s+penal|omisión\s+de\s+antecedentes|omision\s+de\s+antecedentes|medida\s+cautelar|prisión\s+preventiva|prision\s+preventiva|arresto\s+domiciliario|firma\s+periódica|firma\s+periodica|libertad\s+vigilada)\b",
                "score": 0.6
            }
        ],
        "context": [
            "juzgado", "tribunal", "fiscalía", "fiscalia", "defensoría", "defensoria",
            "ministerio público", "ministerio publico", "certificado", "omisión", "omision",
            "penal", "criminal", "judicial", "causa", "rol", "expediente", "sumario",
            "sentencia", "condena", "antecedentes", "prontuario", "gendarmería", "gendarmeria"
        ]
    },
    {
        "name": "DetectorPasaporte",
        "supported_entity": "PASAPORTE",
        "supported_language": "es",
        "patterns": [
            {
                "name": "pasaporte_cl",
                "regex": r"(?i)\b(?:pasaporte|passport)\s*(?:n[°ºo.]?|#)?\s*[A-Z]{0,3}\d{6,9}\b",
                "score": 0.85
            },
            {
                "name": "pasaporte_generico",
                "regex": r"\b[A-Z]{1,3}\d{6,9}\b",
                "score": 0.4
            }
        ],
        "context": [
            "pasaporte", "passport", "documento", "viaje", "migración", "migracion",
            "extranjería", "extranjeria", "frontera", "aduana", "consulado", "embajada",
            "visa", "PDI", "policía", "policia", "internacional"
        ]
    },
    {
        "name": "DetectorLicenciaConducir",
        "supported_entity": "LICENCIA_CONDUCIR",
        "supported_language": "es",
        "patterns": [
            {
                "name": "licencia_cl",
                "regex": r"(?i)\b(?:licencia\s+de\s+conducir|licencia\s+conducir|lic\.?\s*cond\.?|carnet\s+de\s+conducir|brevete|permiso\s+de\s+conducir)\s*(?:n[°ºo.]?|#|clase)?\s*[A-F]?\s*\d{4,12}\b",
                "score": 0.85
            },
            {
                "name": "clase_licencia",
                "regex": r"(?i)\b(?:clase|tipo)\s+[A-F]\b",
                "score": 0.4
            }
        ],
        "context": [
            "licencia", "conducir", "conducción", "conduccion", "vehículo", "vehiculo",
            "clase", "municipalidad", "tránsito", "transito", "brevete", "carnet",
            "vigencia", "renovación", "renovacion", "vencimiento", "conductor", "conductora"
        ]
    },
    {
        "name": "DetectorCuentaBancaria",
        "supported_entity": "CUENTA_BANCARIA",
        "supported_language": "es",
        "patterns": [
            {
                "name": "tarjeta_credito_debito",
                "regex": r"\b(?:4\d{3}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}|5[1-5]\d{2}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}|3[47]\d{2}[\s-]?\d{6}[\s-]?\d{5}|3(?:0[0-5]|[68]\d)\d{1}[\s-]?\d{6}[\s-]?\d{4})\b",
                "score": 0.9
            },
            {
                "name": "cuenta_bancaria_cl",
                "regex": r"(?i)\b(?:cuenta|cta)\.?\s*(?:corriente|ahorro|vista|rut|nómina|nomina)?\s*(?:n[°ºo.]?|#)?\s*\d{7,20}\b",
                "score": 0.7
            }
        ],
        "context": [
            "banco", "cuenta", "tarjeta", "crédito", "credito", "débito", "debito",
            "bancario", "bancaria", "transferencia", "depósito", "deposito", "ahorro",
            "corriente", "vista", "BancoEstado", "Santander", "BCI", "Itaú", "Itau",
            "Scotiabank", "Falabella", "BICE", "Consorcio", "Security", "BBVA",
            "visa", "mastercard", "amex", "vencimiento", "CVV", "CVC"
        ]
    },
    {
        "name": "DetectorNumeroSerieDoc",
        "supported_entity": "NUMERO_SERIE_DOC",
        "supported_language": "es",
        "patterns": [
            {
                "name": "numero_serie_doc",
                "regex": r"(?i)\b(?:n[°ºo.]?\s*(?:de\s+)?(?:serie|documento|folio|registro|inscripción|inscripcion|certificado|boleta|factura|orden)|serie\s*n[°ºo.]?|folio\s*n[°ºo.]?|n[°ºo.]?\s*doc\.?)\s*[:#]?\s*[A-Z0-9]{2,}[-/]?[A-Z0-9]{2,20}\b",
                "score": 0.7
            }
        ],
        "context": [
            "serie", "documento", "folio", "registro", "inscripción", "inscripcion",
            "certificado", "número", "numero", "boleta", "factura", "orden",
            "comprobante", "recibo", "cédula", "cedula", "carnet", "credencial"
        ]
    }
]

def stem_word_es(word: str) -> str:
    """Retorna la raíz (stem) simplificada de una palabra en español."""
    if not word:
        return ""
    # 1. Minúsculas y quitar acentos
    word = word.lower()
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n'
    }
    for k, v in replacements.items():
        word = word.replace(k, v)
        
    # 2. Quitar sufijos comunes de plurales
    if word.endswith('es'):
        word = word[:-2]
    elif word.endswith('s') and not word.endswith('is'):
        word = word[:-1]
        
    # 3. Quitar sufijos derivacionales comunes para llegar a la raíz
    suffixes = [
        'acion', 'icion', 'idad', 'ismo', 'ista', 'ico', 'ica', 
        'tico', 'tica', 'al', 'ario', 'aria', 'ero', 'era', 'oso', 'osa'
    ]
    suffixes.sort(key=len, reverse=True)
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            word = word[:-len(suffix)]
            break
            
    return word

# Generar automáticamente las versiones raíz (stems) para todas las palabras de contexto
for rec in AD_HOC_RECOGNIZERS:
    if "context" in rec:
        extended_context = set(rec["context"])
        for word in rec["context"]:
            stemmed = stem_word_es(word)
            if stemmed:
                extended_context.add(stemmed)
        rec["context"] = list(extended_context)

# Pre-computar recognizers por idioma para evitar reconstruirlos en cada llamada
_cached_recognizers: dict[str, list[dict]] = {}

def _get_recognizers_for_language(entities: tuple, language: str) -> list[dict]:
    """Retorna recognizers filtrados y cacheados para un conjunto de entidades e idioma."""
    cache_key = f"{language}:{','.join(sorted(entities))}"
    if cache_key not in _cached_recognizers:
        recs = []
        for r in AD_HOC_RECOGNIZERS:
            if r["supported_entity"] in entities:
                r_copy = r.copy()
                r_copy["supported_language"] = language
                recs.append(r_copy)
        _cached_recognizers[cache_key] = recs
    return _cached_recognizers[cache_key]

def analyze_text(text: str, entities: list[str] = None, language: str = "es", context: list[str] = None) -> list[dict]:
    """Analiza texto para identificar entidades de datos personales (PII) mediante Presidio."""
    if not text or not text.strip():
        return []
        
    if entities is None:
        entities = DEFAULT_ENTITIES

    # Usar recognizers cacheados
    req_recognizers = _get_recognizers_for_language(tuple(entities), language)

    payload = {
        "text": text,
        "language": language,
        "entities": entities,
        "ad_hoc_recognizers": req_recognizers
    }
    if context:
        # Expandir la lista de contexto con sus raíces morfológicas
        stemmed_context = [stem_word_es(w) for w in context if w]
        payload["context"] = list(set(context + stemmed_context))

    try:
        res = _session.post(settings.PRESIDIO_URL, json=payload, timeout=60)
        if res.status_code == 200:
            return _filter_boilerplate_person(res.json(), text)
        else:
            raise Exception(f"Presidio retornó status code {res.status_code}")
    except Exception as e:
        raise Exception(f"Error al analizar texto con Presidio: {str(e)}")


# Palabras institucionales/de etiqueta que DetectorNombreMayusculas puede
# confundir con un nombre real por tener la misma forma (todo en mayusculas).
_BOILERPLATE_WORDS = {
    "REPUBLICA", "CHILE", "SERVICIO", "REGISTRO", "CIVIL", "IDENTIFICACION",
    "CEDULA", "IDENTIDAD", "ESPECIMEN", "NACIONALIDAD", "SEXO", "FECHA",
    "NACIMIENTO", "EMISION", "VENCIMIENTO", "DOCUMENTO", "NUMERO", "FIRMA",
    "TITULAR", "APELLIDOS", "NOMBRES", "CHILENA", "CHILENO", "RUN", "RUT",
}


def _strip_accents(value: str) -> str:
    replacements = {"Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N"}
    for k, v in replacements.items():
        value = value.replace(k, v)
    return value


def _filter_boilerplate_person(results: list[dict], text: str) -> list[dict]:
    """Descarta hallazgos PERSON cuyo texto sea puro boilerplate institucional
    (ej. 'REPUBLICA DE CHILE'), que DetectorNombreMayusculas puede matchear al
    tener la misma forma (secuencia de palabras en mayusculas) que un nombre real."""
    filtered = []
    for item in results:
        if item.get("entity_type") == "PERSON":
            matched = _strip_accents(text[item["start"]:item["end"]].upper())
            words = matched.split()
            if any(w in _BOILERPLATE_WORDS for w in words):
                continue
        filtered.append(item)
    return filtered

def check_health() -> bool:
    """Verifica si el servicio de Presidio Analyzer está operativo."""
    try:
        res = _session.get(settings.PRESIDIO_HEALTH_URL, timeout=5)
        return res.status_code == 200
    except Exception:
        return False
