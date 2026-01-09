import streamlit as st
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import urllib.parse

st.set_page_config(page_title="ProWashCare – Aanvraag", layout="centered")

st.title("🧼 ProWashCare – Aanvraagformulier")
st.write("Vraag vrijblijvend een reiniging aan. Wij nemen snel contact met u op.")

# ========== FORMULIER ==========
with st.form("aanvraag_form"):
    naam = st.text_input("Naam *")
    email = st.text_input("E-mail *")
    telefoon = st.text_input("Telefoonnummer")

    st.write("### Adres")
    straat = st.text_input("Straat + nummer *")
    postcode = st.text_input("Postcode *")
    gemeente = st.text_input("Gemeente *")

    st.write("### Gewenste diensten")
    ramen = st.checkbox("Ramen wassen")
    zonnepanelen = st.checkbox("Zonnepanelen reinigen")
    gevel = st.checkbox("Gevelreiniging")
    oprit = st.checkbox("Oprit / Terras / Bedrijfsterrein")

    extra = st.text_area("Extra info of opmerkingen")

    # 🕵️‍♂️ Honeypot (ANTI-SPAM)
    spamveld = st.text_input("Laat dit veld leeg", value="", label_visibility="collapsed")

    verstuur = st.form_submit_button("📩 Aanvraag versturen")

# ========== LOGICA ==========
if verstuur:
    if spamveld:
        st.warning("Spam gedetecteerd.")
    elif not (naam and email and straat and postcode and gemeente):
        st.error("Gelieve alle verplichte velden in te vullen.")
    else:
        diensten = []
        if ramen: diensten.append("Ramen wassen")
        if zonnepanelen: diensten.append("Zonnepanelen reinigen")
        if gevel: diensten.append("Gevelreiniging")
        if oprit: diensten.append("Oprit / Terras / Bedrijfsterrein")

        if not diensten:
            st.error("Selecteer minstens één dienst.")
        else:
            try:
                volledig_adres = f"{straat}, {postcode} {gemeente}"
                maps_link = (
                    "https://www.google.com/maps/search/?api=1&query="
                    + urllib.parse.quote_plus(volledig_adres)
                )

                sg = SendGridAPIClient(st.secrets["SENDGRID_API_KEY"])

                # ===== MAIL NAAR JOU =====
                mail_naar_jou = Mail(
                    from_email="aanvraag@prowashcare.com",
                    to_emails="thaikis@gmail.com",
                    subject="Nieuwe aanvraag – ProWashCare",
                    plain_text_content=f"""
Nieuwe aanvraag ontvangen:

Naam: {naam}
E-mail: {email}
Telefoon: {telefoon}

Adres:
{volledig_adres}
Google Maps:
{maps_link}

Diensten:
""" + "\n".join(f"- {d}" for d in diensten) + f"""

Extra info:
{extra}
"""
                )

                # ===== BEVESTIGING NAAR KLANT =====
                mail_naar_klant = Mail(
                    from_email="ProWashCare <aanvraag@prowashcare.com>",
                    to_emails=email,
                    subject="Wij hebben uw aanvraag ontvangen – ProWashCare",
                    plain_text_content=f"""
Beste {naam},

Bedankt voor uw aanvraag bij ProWashCare.
Wij hebben uw aanvraag goed ontvangen en nemen spoedig contact met u op.

Adres:
{volledig_adres}

Aangevraagde diensten:
""" + "\n".join(f"- {d}" for d in diensten) + """

Met vriendelijke groeten,

ProWashCare
www.prowashcare.com
+32 470 87 43 39
"""
                )

                sg.send(mail_naar_jou)
                sg.send(mail_naar_klant)

                st.success("✅ Uw aanvraag is verzonden. Wij nemen spoedig contact met u op.")

            except Exception as e:
                st.error("Er ging iets mis bij het verzenden.")
                st.exception(e)
