import streamlit as st
import os
import random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# for model in genai.list_models():
#    print(model.name)

model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

st.title("Gestalte deine Zukunft!")

# Auswahloptionen
regierungsform = st.selectbox("Regierungsform", ["Demokratisch", "Technokratisch", "Plattformgesteuert"])
verteilungslogik = st.selectbox("Verteilungslogik", ["Eigentumsbasiert", "Leistungsbasiert", "Bedarfsbasiert"])
produktionsweise = st.selectbox("Produktionsweise", ["Marktliberal", "Genossenschaftlich", "Vollautomatisiert"])
rolle_carearbeit = st.selectbox("Care-Arbeit", ["Zentral vergütet", "Unsichtbar", "Ehrenamtlich"])
innovationsverständnis = st.selectbox("Innovationen", ["Degrowth", "Profitgetrieben", "Gemeinwohlorientiert"])
oekologie = st.selectbox("Ökologie", ["Externes Problem", "Lebensgrundlage", "Greenwashed"])

zufall_trigger = random.random() < 0.3
zusatzfaktoren = ["Dabei hat leider eine Revolution die Zukunft verändert und es gibt nun eine Militärelite.", "Leider ist die Umweltverschmutzung deutlich schlimmer als geplant und ein Leben ohne Schutzausrüstung nicht mehr möglich.", "Leider brechen reglmäßig globale Pandemien aus und es müssen harsche Vorkehrungen dagegen getroffen werden. Passe die Zukunft daran an."]
zufall_auswahl = random.choice(zusatzfaktoren) if zufall_trigger else None

prompt = (
    f"Beschreibe in unter 150 Wörtern eine Zukunft, in der die Welt {regierungsform.lower()} regiert wird, "
    f"sie {verteilungslogik.lower()} funktioniert, die Produkte {produktionsweise.lower()} hergestellt werden, "
    f"{rolle_carearbeit.lower()} ist, Innovationen {innovationsverständnis.lower()} sind und die Ökologie als "
    f"{oekologie.lower()} betrachtet wird."
)

if zufall_auswahl:
    prompt += f" {zufall_auswahl}."

if st.button("Zukunft generieren"):
    with st.spinner("Antwort wird geladen..."):
        try:
            response = model.generate_content(prompt)
            st.markdown("### Deine Zukunft:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Fehler beim Senden:\n\n{e}")
