import streamlit as st
import base64
import sqlite3
import os
import random
import google.generativeai as genai
from dotenv import load_dotenv
import time

### Noch to do:
# Boxen kleiner

# SVG-Bilder einfügen
# Optionen kleiner, darunter kommt CE-Logo & Fortschrittsbalken

# Video-Einbindung - mp4

# Am Ende Text drucken als Button → Nächster Sprint
# mit QR-Code direkt aufs Handy - Code muss danach nicht weiter funktionieren

### API ###
load_dotenv()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

### Datenbank ###
conn = sqlite3.connect('antworten.db')
c = conn.cursor()

### Fragen-Dict ###
fragen = {
    "frage1": ("Wem vertraust du, wenn es um die Zukunft deines Landes geht?", [
        ("Mir selbst. Ich will mit entscheiden, auch wenn es kompliziert wird.", "Assets/Optionen/F1_Opti1.svg",
         "Demokratie"),
        ("Experten. Wer kann besser entscheiden als jemand, der sich auskennt?", "Assets/Optionen/F1_Opti2.svg",
         "Technokratie"),
        ("Wir brauchen keine Herrscher. Menschen können selbst über ihre Zukunft entscheiden.",
         "Assets/Optionen/F1_Opti3.svg", "Anarchie")
    ]),
    "frage2": ("Wie sollte Wohlstand verteilt werden, damit es gerecht ist?", [
        ("Alle sollen bekommen, was sie zum Leben brauchen - unabhängig von Leistung.",
         "Assets/Optionen/F2_Opti1.svg", "Bedarfsbasiert"),
        ("Wer mehr leistet, soll auch mehr bekommen. Das motiviert und ist fair.",
         "Assets/Optionen/F2_Opti2.svg", "Leistungsbasiert"),
        ("Wer viel besitzt, der darf es auch nutzen, um mehr zu bekommen. Das ist verdient.",
         "Assets/Optionen/F2_Opti3.svg", "Eigentumsbasiert")
    ]),
    "frage3": ("Wie sollte in Zukunft produziert werden?", [
        ("Gemeinsam und demokratisch. Menschen sollen Betriebe mitgestalten.",
         "Assets/Optionen/F3_Opti1.svg", "Genossenschaftlich"),
        ("Angebot und Nachfrage regeln das. Wir brauchen einen freien Markt.",
         "Assets/Optionen/F3_Opti2.svg", "Marktliberal"),
        ("Maschinen übernehmen. Möglichst effizient und ohne Menschen.",
         "Assets/Optionen/F3_Opti3.svg", "Vollautomatisiert")
    ]),
    "frage4": ("Wie sollte mit Sorgearbeit wie Pflege und Erziehung umgegangen werden?", [
        ("Das ist zentrale Arbeit für die Gesellschaft. Natürlich bezahlen wir das gut.",
         "Assets/Optionen/F4_Opti1.svg", "Zentral Vergütet"),
        ("Das macht man aus Liebe. Freiwilligkeit zählt mehr als Geld.",
         "Assets/Optionen/F4_Opti2.svg", "Ehrenamtlich"),
        ("Das passiert einfach im Hintergrund. Das ist kein Thema für die Politik.",
         "Assets/Optionen/F4_Opti3.svg", "Unsichtbar und Privat")
    ]),
    "frage5": ("Wofür sollen neue Ideen und Technologien in Zukunft entwickelt werden?", [
        ("Zum Wohl aller – Fortschritt soll das Leben fairer und nachhaltiger machen.",
         "Assets/Optionen/F5_Opti1.svg", "Gemeinwohlorientierung"),
        ("Hauptsache es bringt Geld. Wer investiert, soll auch profitieren.",
         "Assets/Optionen/F5_Opti2.svg", "Profitorientiert"),
        ("Weniger ist mehr. Nicht Innovation, sondern Reduktion ist das Ziel.",
         "Assets/Optionen/F5_Opti3.svg", "Degrowth")
    ]),
    "frage6": ("Wie sollte mit Umwelt- und Klimaschutz in Zukunft umgegangen werden?", [
        ("Ohne eine intakte Natur gibt es kein Leben. Sie steht an erster Stelle.",
         "Assets/Optionen/F6_Opti1.svg", "Lebensgrundlage"),
        ("Wichtig, aber nicht unsere Hauptaufgabe. Andere Länder oder die Zukunft müssen das lösen.",
         "Assets/Optionen/F6_Opti2.svg", "Unsichtbar"),
        ("Klingt gut, aber die Wirtschaft regelt das. Es gibt doch ganz viele Siegel dafür.",
         "Assets/Optionen/F6_Opti3.svg", "Greenwashing")
    ])
}

# Tabelle anlegen, falls nicht existient
c.execute('''
CREATE TABLE IF NOT EXISTS auswahl_zaehler (
    frage TEXT,
    antwort TEXT,
    zaehler INTEGER,
    PRIMARY KEY (frage, antwort)
)
''')
conn.commit()


def increment_antwort(frage, antwort):
    c.execute('SELECT zaehler FROM auswahl_zaehler WHERE frage=? AND antwort=?', (frage, antwort))
    row = c.fetchone()
    if row:
        c.execute('UPDATE auswahl_zaehler SET zaehler=zaehler+1 WHERE frage=? AND antwort=?', (frage, antwort))
    else:
        c.execute('INSERT INTO auswahl_zaehler (frage, antwort, zaehler) VALUES (?, ?, 1)', (frage, antwort))
    conn.commit()


def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def svg_to_base64_image(path):
    try:
        with open(path, "r") as f:
            svg_content = f.read()
        return f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"
    except Exception:
        # Fallback: THA_Logo.svg als Ersatz
        with open("Assets/Optionen/THA_Logo.svg", "r") as f:
            fallback_svg = f.read()
        return f"data:image/svg+xml;base64,{base64.b64encode(fallback_svg.encode()).decode()}"


st.set_page_config(page_title="Zukunftsgenerator", layout="wide")

# Globales CSS: schwarzer Hintergrund & oranger Button
st.markdown("""
    <style>
        body, html, .main, .block-container, .css-1v3fvcr, section.main {
            background-color: black;
            background-position: center 25vh;  
            color: white;
            height: 100vh;
        }

        [data-testid="stSidebar"] {
            background-color: #111;
        }

        .header-img {
            display: block;
            margin-left: 0;
            margin-right: auto;
            height: 11vw;
            min-height: 100px;
        }

        .button-spacer-top {
            margin-top: 14vh;
            margin-bottom: 1vh;
            display: flex;
            justify-content: center;
        }
        .button-spacer-bottom {
            margin-top: 2vh;
            margin-bottom: 17vh;
            display: flex;
            justify-content: center;
        }

        /* Oranger Style für alle primären Buttons */
        button[kind="primary"]  {
            background-color: #fd4825;
            color: white;
            border-radius: 999px;
            padding: 0.5rem auto;
            font-weight: bold;
            font-size: 1.2rem;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
            width: 30vw;
            text-shadow: 0px 0px 5px rgba(0, 0, 0, 0.8);
        }
    
        
        /* Option Buttons größer und vertikal zentriert */
        button[kind="secondary"] {
            display: inline-block;
            white-space: normal; /* Mehrzeilig */
            padding: 1rem;
            text-align: center;
            font-size: 1rem; /* Optional: anpassen */
        }

        /* Zentrierung und Styling für Titel- und Untertiteltexte */
        .center-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            margin-bottom: 2rem;
        }

        .title-text {
            font-size: 2.5rem;
            font-weight: bold;
            color: white;
            margin-bottom: 0.5rem;
        }

        .subtitle-text {
            font-size: 1.2rem;
            font-weight: normal;
            color: #ddd;
            margin-top: 0;
        }

        .footer-text {
            margin-top: 2rem;
            font-size: 1rem;
            text-align: center;
            max-width: 90%;
            color: #ccc;
            margin-left: auto;
            margin-right: auto;
        }
        
        .frage-box {
            background-color: #fd4825;
            color: white;
            border-radius: 50px;
            padding: 0.5rem 2rem; /*Textabstand Höhe Breite */
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            margin: 2rem auto 4rem auto;
            width: fit-content;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        
        .option-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            width: 50%;
            gap: 0.5rem;
            margin: 0 auto;
            margin-bottom: 0.4vh;
        }
        
        .svg-wrapper {
            background-color: white;
            border: 2px solid white;
            border-radius: 12px;
            width: 75%;
            aspect-ratio: 1 / 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10%;
            margin-bottom: 1rem;
        }
        
        .svg-wrapper svg {
            max-width: 100%;
            max-height: 100%;
        }
    </style>
    """, unsafe_allow_html=True)


def read_base64_txt(path):
    with open(path, "r") as f:
        return f.read().strip()


def set_png_as_page_bg(png_file):
    bin_str = read_base64_txt(png_file)
    page_bg_img = f"""
        <style>
        body, html, .main, .block-container, .css-1v3fvcr, section.main {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: max(300px, 33vw) auto;
            background-repeat: no-repeat;
            color: white;
            height: 90vh;
        }}
        </style>
        """
    st.markdown(page_bg_img, unsafe_allow_html=True)


def frage_seite(frage_nummer, frage_text, optionen, fragen_keys):
    st.markdown(f"""
        <div class="frage-box">{frage_text}</div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(optionen))

    for idx, (label, svg_path, begriff) in enumerate(optionen):
        with cols[idx]:
            # Lade das SVG-Bild oder Fallback
            img_data = svg_to_base64_image(svg_path)

            # Zeige Bild über img-Tag
            st.markdown(f"""
                <div class="option-container">
                    <div class='svg-wrapper'>
                        <img src="{img_data}" style="max-width: 100%; max-height: 100%;" />
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Button mittig
            centr_cols = st.columns([1, 3, 1])
            with centr_cols[1]:
                if st.button(label, key=f"btn_{frage_nummer}_{idx}", type="secondary"):
                    st.session_state.antworten[frage_nummer] = begriff
                    increment_antwort(frage_nummer, begriff)

                    aktuelle_index = fragen_keys.index(frage_nummer)
                    if aktuelle_index + 1 < len(fragen_keys):
                        st.session_state.page = fragen_keys[aktuelle_index + 1]
                    else:
                        st.session_state.page = "generierung"
                    st.rerun()
    svg_path_ladebalken = "Assets/Optionen/ladebalken_" + frage_nummer
    st.write("svg_path_ladebalken =" + svg_path_ladebalken)
    svg_path_ladebalken = svg_to_base64_image(svg_path_ladebalken)
    st.markdown(f"""
        <div class="option-container">
            <div class='svg-wrapper'>
                <img src="{svg_path_ladebalken}" style="max-width: 100%; max-height: 100%;" />
            </div>
        </div>
    """, unsafe_allow_html=True)
    data_svg_logo = svg_to_base64_image("Assets/Optionen/logo")
    st.markdown(f"""
                    <div class="option-container">
                        <div class='svg-wrapper'>
                            <img src="{data_svg_logo}" style="max-width: 100%; max-height: 100%;" />
                        </div>
                    </div>
                """, unsafe_allow_html=True)




if "page" not in st.session_state:
    st.session_state.page = "start"

if "antworten" not in st.session_state:
    st.session_state.antworten = {}

# --- STARTSEITE ---
if st.session_state.page == "start":
    set_png_as_page_bg("Assets/Form_Base64.txt")
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div {
        text-align: center;
    }

    </style>
    """, unsafe_allow_html=True)

    with open("Assets/Future_Automat.png", "rb") as img_file:
        b64_img = base64.b64encode(img_file.read()).decode()
    st.markdown(f'<img src="data:image/png;base64,{b64_img}" class="header-img" />', unsafe_allow_html=True)
    st.markdown('<div class="button-spacer-top">', unsafe_allow_html=True)
    if st.button("Generiere deine Zukunft", type="primary"):
        st.session_state.page = "frage1"
        st.rerun()
    st.markdown('<div class="button-spacer-bottom"></div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="footer-text">
            [SYSTEM BOOTING...] _ Zukunftsmodul aktiviert. Willkommen im Future Automat!<br><br>
             In wenigen Schritten wirst du grundlegende Entscheidungen treffen zu Politik, Technologie, Arbeit, Umwelt und Zusammenleben.<br>
            Aus deinen Antworten entsteht ein mögliches Zukunftsszenario. 
        </div>
    """, unsafe_allow_html=True)

# --- FRAGESEITE ---
elif st.session_state.page.startswith("frage"):
    frage_id = st.session_state.page
    frage_text, optionen = fragen[frage_id]
    frage_seite(frage_id, frage_text, optionen, list(fragen.keys()))


# --- KI-GENERIERUNG ---
elif st.session_state.page == "generierung":
    st.markdown("""
    <div class="center-wrapper">
        <div class="title-text">Deine Auswahl wird verarbeitet ...</div>
    </div>
    """, unsafe_allow_html=True)
    # st.write(st.session_state.antworten)

    prompt = (
        f"Beschreibe in unter 150 Wörtern eine Zukunft, in der die Welt durch {st.session_state.antworten["frage1"]}"
        f" regiert wird, sie {st.session_state.antworten["frage2"]} funktioniert, die Produkte "
        f"{st.session_state.antworten["frage3"]} hergestellt werden, {st.session_state.antworten["frage4"]} ist, "
        f"Innovationen {st.session_state.antworten["frage5"]} sind und die Ökologie als "
        f"{st.session_state.antworten["frage6"]} betrachtet wird."
    )

    try:
        response = model.generate_content(prompt)
        st.markdown("### Deine Zukunft:")
        st.write(response.text)
    except Exception as e:
        st.error(f"Fehler beim Senden:\n\n{e}")

    if st.button("Zurück zum Start"):
        st.session_state.page = "start"
        st.session_state.antworten = {}
        st.rerun()




