import streamlit as st
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import urllib.parse

st.set_page_config(page_title="ProWashCare – Aanvraag", layout="centered")
st.title("🧼 ProWashCare – Aanvraagformulier")
st.write("Vraag vrijblijvend een reiniging aan. Wij nemen snel contact met u op.")

# ================= SESSION STATE =================
if "aanvragen" not in st.session_state:
    st.session_state.aanvragen = []

# ================= KLANTGEGEVENS =================
with st.form("klant_form"):
    st.subheader("Uw gegevens")
    naam = st.text_input("Naam *")
    email = st.text_input("E-mail *")
    telefoon = st.text_input("Telefoon")

    st.subheader("Adres")
    straat = st.text_input("Straat + nummer *")
    postcode = st.text_input("Postcode *")
    gemeente = st.text_input("Gemeente *")

    spamveld = st.text_input("Laat dit veld leeg", label_visibility="collapsed")
    klant_ok = st.form_submit_button("Gegevens opslaan")

if klant_ok and spamveld:
    st.stop()

# ================= DIENST SELECTIE =================
st.divider()
st.subheader("Dienst toevoegen")

dienst = st.selectbox(
    "Kies een dienst",
    ["Ramen wassen", "Zonnepanelen", "Gevelreiniging", "Oprit / Terras / Bedrijfsterrein"]
)

# ---------- RAMEN ----------
if dienst == "Ramen wassen":
    col1, col2 = st.columns(2)
    with col1:
        klein_binnen = st.number_input("Kleine ramen – binnen", 0, step=1)
        groot_binnen = st.number_input("Grote ramen – binnen", 0, step=1)
    with col2:
        klein_buiten = st.number_input("Kleine ramen – buiten", 0, step=1)
        groot_buiten = st.number_input("Grote ramen – buiten", 0, step=1)

    if st.button("Dienst toevoegen"):
        details = []
        if klein_binnen: details.append(f"Kleine ramen binnen: {klein_binnen}")
        if klein_buiten: details.append(f"Kleine ramen buiten: {klein_buiten}")
        if groot_binnen: details.append(f"Grote ramen binnen: {groot_binnen}")
        if groot_buiten: details.append(f"Grote ramen buiten: {groot_buiten}")

        if details:
            st.session_state.aanvragen.append({
                "titel": "Ramen wassen",
                "details": "\n".join(details)
            })
            st.success("Ramen wassen toegevoegd")
            st.rerun()
        else:
            st.warning("Geef minstens één raam op")

# ---------- ZONNEPANELEN ----------
elif dienst == "Zonnepanelen":
    aantal = st.number_input("Aantal zonnepanelen", min_value=1, step=1)

    if st.button("Dienst toevoegen"):
        st.session_state.aanvragen.append({
            "titel": "Zonnepanelen reinigen",
            "details": f"Aantal panelen: {aantal}"
        })
        st.success("Zonnepanelen toegevoegd")
        st.rerun()

# ---------- GEVEL ----------
elif dienst == "Gevelreiniging":
    m2 = st.number_input("Oppervlakte (m²)", min_value=1.0)
    impregneren = st.checkbox("Impregneerbehandeling")

    if st.button("Dienst toevoegen"):
        detail = f"{m2} m²"
        if impregneren:
            detail += "\nOptie: Impregneren"

        st.session_state.aanvragen.append({
            "titel": "Gevelreiniging",
            "details": detail
        })
        st.success("Gevelreiniging toegevoegd")
        st.rerun()

# ---------- OPRIT / TERRAS / BEDRIJFSTERREIN ----------
elif dienst == "Oprit / Terras / Bedrijfsterrein":
    type_keuze = st.radio("Type", ["Oprit", "Terras", "Bedrijfsterrein"], horizontal=True)
    m2 = st.number_input("Oppervlakte (m²)", min_value=1.0)

    col1, col2, col3, col4 = st.columns(4)
    reinigen = col1.checkbox("Reinigen")
    zand = col2.checkbox("Zand invegen")
    onkruid = col3.checkbox("Onkruidwerend voegzand")
    coating = col4.checkbox("Coating")

    opties = []
    if reinigen: opties.append("Reinigen")
    if zand: opties.append("Zand invegen")
    if onkruid: opties.append("Onkruidwerend voegzand")
    if coating: opties.append("Coating")

    if st.button("Dienst toevoegen"):
        if opties:
            st.session_state.aanvragen.append({
                "titel": type_keuze,
                "details": f"{m2} m²\nBehandelingen: {', '.join(opties)}"
            })
            st.success(f"{type_keuze} toegevoegd")
            st.rerun()
        else:
            st.warning("Selecteer minstens één behandeling")

# ================= OVERZICHT =================
st.divider()
st.subheader("Overzicht aanvraag")

if not st.session_state.aanvragen:
    st.info("Nog geen diensten toegevoegd.")
else:
    for i, item in enumerate(st.session_state.aanvragen):
        col1, col2 = st.columns([9,1])
        col1.markdown(f"**{item['titel']}**\n\n{item['details'].replace('\n','  \n')}")
        if col2.button("❌", key=f"del_{i}"):
            st.session_state.aanvragen.pop(i)
            st.rerun()

# ================= VERZENDEN =================
st.divider()
if st.button("📩 Aanvraag verzenden"):
    if not (naam and email and straat and postcode and gemeente):
        st.error("Vul alle verplichte velden in.")
    elif not st.session_state.aanvragen:
        st.error("Voeg minstens één dienst toe.")
    else:
        try:
            volledig_adres = f"{straat}, {postcode} {gemeente}"
            maps_link = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(volledig_adres)

            inhoud = ""
            for item in st.session_state.aanvragen:
                inhoud += f"{item['titel']}\n{item['details']}\n\n"

            sg = SendGridAPIClient(st.secrets["SENDGRID_API_KEY"])

            mail_admin = Mail(
                from_email="aanvraag@prowashcare.com",
                to_emails="thaikis@gmail.com",
                subject="Nieuwe aanvraag – ProWashCare",
                plain_text_content=f"""
Naam: {naam}
E-mail: {email}
Telefoon: {telefoon}

Adres:
{volledig_adres}
Google Maps:
{maps_link}

Aangevraagde diensten:
{inhoud}
"""
            )

            mail_klant = Mail(
                from_email="ProWashCare <aanvraag@prowashcare.com>",
                to_emails=email,
                subject="Wij hebben uw aanvraag ontvangen – ProWashCare",
                plain_text_content=f"""
Beste {naam},

Bedankt voor uw aanvraag bij ProWashCare.
Wij nemen spoedig contact met u op.

Uw aanvraag:
{inhoud}

Met vriendelijke groeten,
ProWashCare
"""
            )

            sg.send(mail_admin)
            sg.send(mail_klant)

            st.success("✅ Uw aanvraag is verzonden.")
            st.session_state.aanvragen = []

        except Exception as e:
            st.error("Er ging iets mis bij het verzenden.")
            st.exception(e)
