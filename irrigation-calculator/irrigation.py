import streamlit as st
import math

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Irrigation Pro Calc",
    page_icon="💧",
    layout="centered"
)

# --- 2. LES FORMULES (BACKEND) ---
def calculer_volume_bassin(H, a, b, c, d):
    surface_superieure = a * b
    surface_fond = c * d
    racine_surfaces = math.sqrt(a * b * c * d)
    return (H / 3) * (surface_superieure + surface_fond + racine_surfaces)

def calculer_etp_bac(k_bac, e_bac):
    return k_bac * e_bac

def calculer_et0_serre(rg, kp, L):
    return (0.67 * rg * kp) / L if L > 0 else 0

def calculer_etc(et0, kc):
    return et0 * kc

def calculer_hm(masse_eau, masse_sol_sec):
    return (masse_eau / masse_sol_sec) * 100 if masse_sol_sec > 0 else 0

def calculer_hv_directe(volume_eau, volume_total_sol):
    return (volume_eau / volume_total_sol) * 100 if volume_total_sol > 0 else 0

def calculer_hv_via_hm(hm, da):
    return hm * da

def calculer_he(hv, z_dm):
    return hv * z_dm

def calculer_ru(hcc, hpf, da, z_dm):
    return (hcc - hpf) * da * z_dm

def calculer_rfu(ru):
    return (2 / 3) * ru

def calculer_besoin_net(et0, kc, kr, pu, delta_rfu):
    return (et0 * kc * kr) - (pu + delta_rfu)

def calculer_besoin_brut(bnet, ea):
    return bnet / ea if ea > 0 else 0

def calculer_irrigation_bilan(etc, d, delta_s, pu):
    return etc + d + delta_s - pu

def calculer_dnm(hcc, hpf, f, z_mm, ph):
    return (hcc - hpf) * (f / 100) * z_mm * (ph / 100)

def calculer_irrigation_via_dnm(dnm, bbp):
    return dnm / bbp if bbp > 0 else 0

def modifier_nb_irrigations(bbp, dnm):
    return bbp / dnm if dnm > 0 else 0

def calculer_duree_t(bbp, pf):
    return bbp / pf if pf > 0 else 0


# --- 3. INTERFACE UTILISATEUR (FRONTEND) ---
st.title("💧 Outils de Calcul d'Irrigation")
st.write("Sélectionnez la formule exacte que vous souhaitez utiliser.")

option = st.sidebar.selectbox(
    "Formules disponibles :",
    [
        "1. Volume d'un Bassin",
        "2. ETp (via Bac d'évaporation)",
        "3. ET0 Serre",
        "4. ETc / ETM (Besoin en eau)",
        "5. Humidité du sol (Hm, Hv, he)",
        "6. Réserves du sol (RU, RFU)",
        "7. Besoins Nets (Bnet) & Bruts (Bbrut)",
        "8. Bilan Hydrique (Calcul de I)",
        "9. Pilotage Irrigation (DNM, Nombre, Durée T)"
    ]
)

st.divider()

# --- OPTIONS DU MENU DE CALCUL ---

if option == "1. Volume d'un Bassin":
    st.header("📐 Calcul du Volume d'un Bassin")
    H = st.number_input("Profondeur du bassin (H en m)", value=0.0)
    a = st.number_input("Longueur supérieure (a en m)", value=0.0)
    b = st.number_input("Largeur supérieure (b en m)", value=0.0)
    c = st.number_input("Longueur du fond (c en m)", value=0.0)
    d = st.number_input("Largeur du fond (d en m)", value=0.0)
    
    if st.button("Calculer le Volume"):
        vol = calculer_volume_bassin(H, a, b, c, d)
        st.success(f"Le volume du bassin est de : {vol:.2f} m³")

elif option == "2. ETp (via Bac d'évaporation)":
    st.header("🪣 Calcul de l'ETp (Formule : K bac * E bac)")
    k_bac = st.number_input("Coefficient du bac (K bac)", value=0.0)
    e_bac = st.number_input("Évaporation du bac (E bac en mm)", value=0.0)
    
    if st.button("Calculer l'ETp"):
        etp = calculer_etp_bac(k_bac, e_bac)
        st.success(f"ETp = {etp:.2f} mm")

elif option == "3. ET0 Serre":
    st.header("🛖 Calcul de l'ET0 en Serre (Formule : 0,67 * Rg * Kp / L)")
    rg = st.number_input("Rayonnement global (Rg)", value=0.0)
    kp = st.number_input("Coefficient de la serre (Kp)", value=0.0)
    L = st.number_input("Chaleur latente de vaporisation (L)", value=0.0)
    
    if st.button("Calculer l'ET0 Serre"):
        et0_s = calculer_et0_serre(rg, kp, L)
        st.success(f"ET0 Serre = {et0_s:.2f} mm")

elif option == "4. ETc / ETM (Besoin en eau)":
    st.header("🌱 Besoins en eau de la culture (Formule : ET0 * Kc)")
    et0 = st.number_input("Évapotranspiration de référence (ET0 en mm/jour)", value=0.0)
    kc = st.number_input("Coefficient de la culture (Kc)", value=0.0)
    
    if st.button("Calculer l'ETc"):
        etc = calculer_etc(et0, kc)
        st.success(f"Besoin en eau (ETc / ETM) = {etc:.2f} mm/jour")

elif option == "5. Humidité du sol (Hm, Hv, he)":
    st.header("🪵 Humidité et Lame d'eau dans le sol")
    
    st.subheader("Humidité Massique (Hm %)")
    m_eau = st.number_input("Masse de l'eau (g)", value=0.0)
    m_sec = st.number_input("Masse du sol sec (g)", value=0.0)
    hm = calculer_hm(m_eau, m_sec)
    st.info(f"Hm = {hm:.2f} %")
    
    st.subheader("Humidité Volumique (Hv %)")
    mode_hv = st.radio("Méthode de calcul pour Hv :", ("Via volumes", "Via Hm et Da"))
    if mode_hv == "Via volumes":
        v_eau = st.number_input("Volume de l'eau (cm³)", value=0.0)
        v_sol = st.number_input("Volume total du sol (cm³)", value=0.0)
        hv = calculer_hv_directe(v_eau, v_sol)
    else:
        da_input = st.number_input("Densité apparente (Da) [pour Hv]", value=0.0)
        hv = calculer_hv_via_hm(hm, da_input)
    st.info(f"Hv = {hv:.2f} %")
    
    st.subheader("Lame d'eau équivalente (he)")
    z_dm = st.number_input("Profondeur racinaire explorée (Z en dm)", value=0.0)
    if st.button("Calculer he"):
        he = calculer_he(hv, z_dm)
        st.success(f"he = {he:.2f} mm")

elif option == "6. Réserves du sol (RU, RFU)":
    st.header("💧 Réserve Utile (RU) & Facilement Utilisable (RFU)")
    hcc = st.number_input("Humidité à la capacité au champ (Hcc %)", value=0.0)
    hpf = st.number_input("Humidité au point de flétrissement (HpF %)", value=0.0)
    da = st.number_input("Densité apparente (da)", value=0.0)
    z = st.number_input("Profondeur réellement explorée par les racines (Z en dm)", value=0.0)
    
    if st.button("Calculer les Réserves"):
        ru = calculer_ru(hcc, hpf, da, z)
        rfu = calculer_rfu(ru)
        st.success(f"Réserve Utile (RU) = {ru:.2f} mm")
        st.success(f"Réserve Facilement Utilisable (RFU = 2/3 RU) = {rfu:.2f} mm")

elif option == "7. Besoins Nets (Bnet) & Bruts (Bbrut)":
    st.header("💦 Besoins Nets et Bruts journaliers")
    et0 = st.number_input("ET0 (mm/j)", value=0.0)
    kc = st.number_input("Kc", value=0.0)
    kr = st.number_input("Coefficient de réduction / localisation (Kr)", value=0.0)
    pu = st.number_input("Précipitation utile (Pu)", value=0.0)
    delta_rfu = st.number_input("Variation de la RFU (ΔRFU)", value=0.0)
    ea = st.number_input("Efficience de l'application (Ea)", value=0.0)
    
    if st.button("Calculer les Besoins"):
        bnet = calculer_besoin_net(et0, kc, kr, pu, delta_rfu)
        bbrut = calculer_besoin_brut(bnet, ea)
        st.success(f"Besoin Net (Bnet) = {bnet:.2f} mm/j")
        st.success(f"Besoin Brut (Bbrut) = {bbrut:.2f} mm/j")

elif option == "8. Bilan Hydrique (Calcul de I)":
    st.header("⚖️ Bilan Hydrique (Formule : Pu + I = ETc + D + ΔS)")
    etc = st.number_input("Évapotranspiration réelle de la culture (ETc en mm)", value=0.0)
    d = st.number_input("Drainage (D en mm)", value=0.0)
    delta_s = st.number_input("Variation du stock d'eau (ΔS = Stock Final - Stock Initial en mm)", value=0.0)
    pu = st.number_input("Précipitation utile (Pu en mm)", value=0.0)
    
    if st.button("Calculer l'Irrigation Requise (I)"):
        irrigation = calculer_irrigation_bilan(etc, d, delta_s, pu)
        st.success(f"Irrigation nécessaire (I) = {irrigation:.2f} mm")

elif option == "9. Pilotage Irrigation (DNM, Nombre, Durée T)":
    st.header("🎯 Pilotage de l'Irrigation Localisée")
    hcc = st.number_input("Humidité à la capacité au champ (Hcc %)", value=0.0)
    hpf = st.number_input("Humidité au point de flétrissement (Hpf %)", value=0.0)
    f = st.number_input("Pourcentage de la RU à restituer (f %)", value=0.0)
    z_mm = st.number_input("Profondeur d'enracinement à humidifier (Z en mm)", value=0.0)
    ph = st.number_input("Pourcentage réellement humecté de la parcelle (PH %)", value=0.0)
    bbp = st.number_input("Besoin en eau brut de la pointe (Bbp)", value=0.0)
    pf = st.number_input("Pluviométrie du système ou Débit (Pf)", value=0.0)
    
    if st.button("Lancer les calculs de Pilotage"):
        dnm = calculer_dnm(hcc, hpf, f, z_mm, ph)
        i_via_dnm = calculer_irrigation_via_dnm(dnm, bbp)
        nb_irrigations = modifier_nb_irrigations(bbp, dnm)
        duree_t = calculer_duree_t(bbp, pf)
        
        st.success(f"Dose Nette Maximale (DNM) = {dnm:.2f} mm")
        st.info(f"Irrigation (I = DNM / Bbp) = {i_via_dnm:.2f}")
        st.info(f"Nombre d'irrigations par jour (Bbp / DNM) = {nb_irrigations:.2f}")
        st.success(f"Durée d'irrigation (T = Bbp / Pf) = {duree_t:.2f} heures")