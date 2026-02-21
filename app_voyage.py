import streamlit as st
import pandas as pd
import urllib.parse
import streamlit.components.v1 as components
import math
import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Dz Tour | Réservation", page_icon="🌍", layout="wide")

# --- AJOUT DE LA FONCTIONNALITÉ PWA (APPLICATION TÉLÉCHARGEABLE) ---
pwa_code = """
<script>
    if (!window.parent.document.querySelector('link[rel="manifest"]')) {
        const manifest = {
            "name": "Dz Tour Réservation",
            "short_name": "Dz Tour",
            "start_url": window.parent.location.origin + window.parent.location.pathname,
            "display": "standalone",
            "background_color": "#f5f5f5",
            "theme_color": "#003580",
            "icons": [
                {
                    "src": "https://cdn-icons-png.flaticon.com/512/2060/2060284.png", 
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        };
        const stringManifest = JSON.stringify(manifest);
        const blob = new Blob([stringManifest], {type: 'application/json'});
        const manifestURL = URL.createObjectURL(blob);
        
        const link = window.parent.document.createElement('link');
        link.rel = 'manifest';
        link.href = manifestURL;
        window.parent.document.head.appendChild(link);
    }
</script>
"""
components.html(pwa_code, height=0, width=0)
# -------------------------------------------------------------------

# --- 2. CSS STYLE "BOOKING.COM" AVANCÉ ---
st.markdown("""
<style>
    .stApp { background-color: #f5f5f5; }
    
    .hero-section {
        background-color: #003580;
        padding: 20px 30px 60px 30px;
        margin-top: -60px; 
        margin-bottom: -30px;
        padding-top: 60px;
        color: white;
    }
    
    .booking-navbar { display: flex; gap: 15px; margin-bottom: 30px; overflow-x: auto; }
    .nav-item { color: white; text-decoration: none; padding: 10px 15px; border-radius: 20px; font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 8px; cursor: pointer; }
    .nav-item.active { background-color: rgba(255, 255, 255, 0.15); border: 1px solid white; }
    .nav-item:hover { background-color: rgba(255, 255, 255, 0.1); }

    .hero-title { font-size: 36px; font-weight: bold; margin: 0 0 10px 0; }
    .hero-subtitle { font-size: 20px; margin: 0; }

    /* LA BARRE DE RECHERCHE JAUNE */
    div[data-testid="stForm"] {
        background-color: #febb02;
        border: 4px solid #febb02;
        border-radius: 8px;
        padding: 4px;
        margin-top: -30px; 
        z-index: 10;
        position: relative;
    }
    
    div[data-testid="stForm"] button {
        background-color: #0071c2 !important;
        color: white !important;
        font-size: 15px !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        border: none !important;
        width: 100%;
        height: 100%;
        margin-top: 25px; 
    }
    div[data-testid="stForm"] button:hover { background-color: #005999 !important; }

    div[data-testid="stLinkButton"] > a { background-color: #0071c2 !important; color: white !important; border: none !important; border-radius: 4px; font-weight: bold; transition: 0.2s; text-decoration: none !important; }
    div[data-testid="stLinkButton"] > a:hover { background-color: #005999 !important; color: white !important; }
    
    .price-container { text-align: right; margin-top: 10px; margin-bottom: 10px; }
    .price-label { font-size: 12px; color: #6b6b6b; }
    .price-value { font-size: 22px; font-weight: bold; color: #333333; }
    .agency-badge { display: inline-block; background-color: #febb02; color: #333; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 10px; }

    .footer-title { color: #003580; font-weight: bold; font-size: 18px; margin-bottom: 15px; }
    .footer-text { color: #333; font-size: 14px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA MÉMOIRE (POUR LES FILTRES) ---
if 'page_actuelle' not in st.session_state:
    st.session_state.page_actuelle = 1
if 'destination_recherchee' not in st.session_state:
    st.session_state.destination_recherchee = "Toutes les destinations"
if 'agence_recherchee' not in st.session_state:
    st.session_state.agence_recherchee = "Toutes les agences"
if 'budget_max' not in st.session_state:
    st.session_state.budget_max = 0
if 'date_pub_min' not in st.session_state:
    st.session_state.date_pub_min = None

# --- FONCTION POUR NETTOYER LES NUMÉROS DE TÉLÉPHONE ---
def nettoyer_telephone(tel):
    val = str(tel).strip()
    if val.lower() == 'nan' or val == '':
        return ""
    if val.endswith('.0'):
        val = val[:-2]
    if len(val) == 9 and val.isdigit():
        val = "0" + val
    return val

# --- 3. CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=600)
def load_data():
    SHEET_ID = "1U0htakTYEc4gV5TKDEOiZI-PGYSVlx6K9HxxHy2mrdY"
    SHEET_NAME = "Feuille 1"
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"
    try:
        df = pd.read_csv(url, low_memory=False)
        df.columns = [str(c).strip().lower() for c in df.columns]
        df = df.fillna("")
        df['id_unique'] = range(len(df))
        return df
    except:
        return pd.DataFrame()

df = load_data()
id_sel = st.query_params.get("id")

# ==========================================
#        VUE 1 : PAGE DES DÉTAILS
# ==========================================
if id_sel is not None:
    try:
        post = df[df['id_unique'] == int(id_sel)].iloc[0]
        
        st.write("<br>", unsafe_allow_html=True)
        if st.button("← Retour aux résultats"):
            st.query_params.clear()
            st.rerun()

        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-top:10px;">
                <div>
                    <span class="agency-badge">{post.get('nom_agence', '')}</span>
                    <h1 style="margin:0; color:#333;">🌍 {post.get('destination', '')}</h1>
                </div>
                <div style="text-align:right; background:white; padding:15px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                    <div class="price-label">Prix de l'offre</div>
                    <div class="price-value" style="color:#0071c2;">{post.get('prix', '')} DA</div>
                </div>
            </div>
            <hr>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.subheader("À propos de cette offre")
            
            # --- ENCART DE CONTACT NETTOYÉ ---
            tel1 = nettoyer_telephone(post.get('telephone_1', ''))
            tel2 = nettoyer_telephone(post.get('telephone_2', ''))
            
            lien_fb = str(post.get('lien_facebook', '')).strip()
            if lien_fb.lower() == 'nan': 
                lien_fb = ""
            
            contact_html = """
            <div style='background-color: #e8f4fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0071c2;'>
                <h4 style='margin-top: 0; margin-bottom: 10px; color: #003580;'>📞 Contacter l'agence</h4>
            """
            
            if tel1 or tel2:
                contact_html += "<div style='margin-bottom: 5px;'><b>Téléphone :</b> "
                if tel1: contact_html += f"{tel1}"
                if tel1 and tel2: contact_html += " / "
                if tel2: contact_html += f"{tel2}"
                contact_html += "</div>"
                
            if lien_fb:
                contact_html += f"<div><b>Facebook :</b> <a href='{lien_fb}' target='_blank' style='color: #0071c2; font-weight: bold; text-decoration: none;'>Voir la page officielle ↗</a></div>"
                
            contact_html += "</div>"
            
            st.markdown(contact_html, unsafe_allow_html=True)
            
            # --- AFFICHAGE DU TEXTE ORIGINAL CORRIGÉ (TAILLE NORMALE) ---
            texte_brut = str(post.get('texte_original', ''))
            texte_html = texte_brut.replace('\n', '<br>')
            st.markdown(f"<div style='font-size: 15px; line-height: 1.6; color: #333;'>{texte_html}</div>", unsafe_allow_html=True)
            
        with c2:
            fb_url = str(post.get('lien_facebook', ''))
            if "facebook.com" in fb_url:
                enc = urllib.parse.quote(fb_url)
                components.html(f'<iframe src="https://www.facebook.com/plugins/post.php?href={enc}&show_text=true" width="100%" height="550" style="border:none;overflow:hidden;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);" scrolling="no" frameborder="0" allowfullscreen="true"></iframe>', height=550)
    except Exception as e:
        st.query_params.clear()
        st.rerun()

# ==========================================
#        VUE 2 : PAGE D'ACCUEIL
# ==========================================
else:
    # --- 1. LE HEADER BLEU ET LA NAVIGATION ---
    st.markdown("""
        <div class="hero-section">
            <div class="booking-navbar">
                <div class="nav-item active">🛏️ Hébergements</div>
                <div class="nav-item">✈️ Vols</div>
                <div class="nav-item">🚗 Voitures de location</div>
                <div class="nav-item">🎡 Attractions</div>
                <div class="nav-item">🚕 Taxis aéroport</div>
            </div>
            <h1 class="hero-title">Envie de Voyage!!, quelle sera votre prochaine destination ?</h1>
            <p class="hero-subtitle">Trouvez des avantages exclusifs aux quatre coins du monde !</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- 2. LA NOUVELLE BARRE DE RECHERCHE JAUNE ---
    villes = ["Toutes les destinations"] + sorted([str(v) for v in df['destination'].unique() if v])
    agences = ["Toutes les agences"] + sorted([str(a) for a in df['nom_agence'].unique() if a and str(a).lower() != 'nan'])
    
    with st.form(key="search_form"):
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5])
        
        with col1:
            idx_dest = villes.index(st.session_state.destination_recherchee) if st.session_state.destination_recherchee in villes else 0
            dest = st.selectbox("📍 Destination", villes, index=idx_dest)
            
        with col2:
            idx_ag = agences.index(st.session_state.agence_recherchee) if st.session_state.agence_recherchee in agences else 0
            agence = st.selectbox("🏢 Agence", agences, index=idx_ag)
            
        with col3:
            d_pub = st.date_input("📅 Publié depuis", value=st.session_state.date_pub_min, format="DD/MM/YYYY")
            
        with col4:
            budget = st.number_input("💰 Max (DA) 0=Tout", min_value=0, step=10000, value=st.session_state.budget_max)
            
        with col5:
            submit_search = st.form_submit_button("Rechercher")
            
        with col6:
            reset_search = st.form_submit_button("🔄 Effacer")
            
        if submit_search:
            st.session_state.destination_recherchee = dest
            st.session_state.agence_recherchee = agence
            st.session_state.date_pub_min = d_pub
            st.session_state.budget_max = budget
            st.session_state.page_actuelle = 1 
            st.rerun()

        if reset_search:
            st.session_state.destination_recherchee = "Toutes les destinations"
            st.session_state.agence_recherchee = "Toutes les agences"
            st.session_state.date_pub_min = None
            st.session_state.budget_max = 0
            st.session_state.page_actuelle = 1
            st.rerun()

    # --- 3. LOGIQUE DE FILTRAGE DES DONNÉES ---
    df_f = df.copy()

    # Filtre 1 : Destination
    if st.session_state.destination_recherchee != "Toutes les destinations":
        df_f = df_f[df_f['destination'] == st.session_state.destination_recherchee]

    # Filtre 2 : Agence
    if st.session_state.agence_recherchee != "Toutes les agences":
        df_f = df_f[df_f['nom_agence'] == st.session_state.agence_recherchee]

    # Filtre 3 : Tarif Max
    if st.session_state.budget_max > 0:
        def nettoyer_prix(p):
            chiffres = ''.join(c for c in str(p) if c.isdigit())
            return float(chiffres) if chiffres else float('inf')
        
        df_f['prix_numerique'] = df_f['prix'].apply(nettoyer_prix)
        df_f = df_f[df_f['prix_numerique'] <= st.session_state.budget_max]

    # Filtre 4 : Date de publication
    if st.session_state.date_pub_min is not None:
        col_date = None
        for col in df_f.columns:
            if 'date' in col or 'publication' in col:
                col_date = col
                break
                
        if col_date:
            df_f['date_formattee'] = pd.to_datetime(df_f[col_date], errors='coerce', dayfirst=True)
            df_f = df_f[df_f['date_formattee'].dt.date >= st.session_state.date_pub_min]

    # --- 4. AFFICHAGE DES RÉSULTATS ---
    st.write("<br>", unsafe_allow_html=True)
    total_offres = len(df_f)
    st.markdown(f"<h3>Algeria : {total_offres} offres Disponibles</h3>", unsafe_allow_html=True)

    # NOUVEAU RÉGLAGE : 12 OFFRES PAR PAGE AU LIEU DE 9
    OFFRES_PAR_PAGE = 12
    
    total_pages = max(1, math.ceil(total_offres / OFFRES_PAR_PAGE))
    debut_idx = (st.session_state.page_actuelle - 1) * OFFRES_PAR_PAGE
    fin_idx = debut_idx + OFFRES_PAR_PAGE
    df_page = df_f.iloc[debut_idx:fin_idx]

    if total_offres == 0:
        st.warning("Aucune offre ne correspond à vos critères de recherche.")
    else:
        cols = st.columns(3)
        for i, row in enumerate(df_page.itertuples()):
            with cols[i % 3]:
                with st.container(border=True):
                    fb_url = str(row.lien_facebook)
                    if "facebook.com" in fb_url:
                        enc = urllib.parse.quote(fb_url)
                        embed = f"https://www.facebook.com/plugins/post.php?href={enc}&show_text=false&width=350"
                        components.html(f"""
                            <iframe src="{embed}" width="100%" height="250" style="border:none;overflow:hidden;border-radius:4px;" scrolling="no" frameborder="0" loading="lazy"></iframe>
                        """, height=250)
                    
                    st.markdown(f"<span class='agency-badge'>{row.nom_agence}</span>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='color:#0071c2; margin-top:0;'>{row.destination}</h4>", unsafe_allow_html=True)
                    txt = str(row.texte_original)
                    st.markdown(f"<div style='font-size:13px; color:#444; height:40px; overflow:hidden;'>{txt[:80]}...</div>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <div class='price-container'>
                            <span class='price-label'>Tarif</span><br>
                            <span class='price-value'>DZD {row.prix}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    st.link_button("Voir plus de détails", f"?id={row.id_unique}", use_container_width=True)

        if total_pages > 1:
            st.write("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.session_state.page_actuelle > 1:
                    if st.button("⬅️ Page précédente", use_container_width=True):
                        st.session_state.page_actuelle -= 1
                        st.rerun()
            with col2:
                st.markdown(f"<div style='text-align:center; padding-top:5px; font-weight:bold;'>Page {st.session_state.page_actuelle} sur {total_pages}</div>", unsafe_allow_html=True)
            with col3:
                if st.session_state.page_actuelle < total_pages:
                    if st.button("Page suivante ➡️", use_container_width=True):
                        st.session_state.page_actuelle += 1
                        st.rerun()

# ==========================================
#   FOOTER : INFOS, CONTACT & ESPACE AGENCES
# ==========================================
st.write("<br><br><br>", unsafe_allow_html=True)
st.markdown("---") 

foot_col1, foot_col2, foot_col3 = st.columns([1.2, 1, 1.5])

with foot_col1:
    st.markdown("<div class='footer-title'>À propos de Dz Tour 🇩🇿</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='footer-text'>
        <b>Dz Tour</b> est la première plateforme agrégatrice d'offres de voyages en Algérie.<br><br>
        Notre mission est de vous simplifier la recherche de vos prochaines vacances en regroupant les meilleures offres des agences de voyages partenaires à travers le pays, le tout sur une interface simple, rapide et transparente.
    </div>
    """, unsafe_allow_html=True)

with foot_col2:
    st.markdown("<div class='footer-title'>Nous Contacter 📞</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='footer-text'>
        📍 <b>Adresse :</b> Oum El Bouaghi, Algérie<br>
        📧 <b>Email :</b> contact@dztour.dz<br>
        📱 <b>Téléphone :</b> +213 XX XX XX XX<br>
        🕒 <b>Horaires :</b> Dimanche - Jeudi (9h - 17h)
        <br><br>
        Suivez-nous sur nos réseaux sociaux pour ne rater aucune offre exclusive !
    </div>
    """, unsafe_allow_html=True)

with foot_col3:
    st.markdown("<div class='footer-title'>🏢 Espace Agences (Rejoignez-nous)</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer-text' style='margin-bottom:10px;'>Vous êtes une agence de voyage et souhaitez publier vos offres ici ? Remplissez ce formulaire :</div>", unsafe_allow_html=True)
    
    with st.form("inscription_agence", clear_on_submit=True):
        ag_nom = st.text_input("Nom de l'agence *")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            ag_email = st.text_input("Email professionnel *")
        with col_f2:
            ag_tel = st.text_input("Numéro de téléphone *")
        
        ag_msg = st.text_area("Lien de votre page Facebook ou Site web *")
        
        submit_agence = st.form_submit_button("Envoyer la demande d'inscription")
        
        if submit_agence:
            if ag_nom and ag_email and ag_tel and ag_msg:
                st.success("✅ Merci ! Votre demande a été enregistrée. Notre équipe vous contactera dans les plus brefs délais.")
            else:
                st.error("⚠️ Veuillez remplir tous les champs avec une étoile (*).")

st.write("---")
st.markdown("<div style='text-align:center; color:#0071c2; font-size:12px; margin-bottom: 20px;'>Copyright © 2026 Dz Tour. Tous droits réservés.</div>", unsafe_allow_html=True)