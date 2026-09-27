import streamlit as st
import math

# Page configuration
st.set_page_config(
    page_title="Eurocode 3 Steel Beam Design Tool",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App Title & Header
st.title("🏗️ Eurocode 3 Steel Beam Analysis & Design Tool")
st.caption("Final Year Research Project — Structural Steel Beam Verification according to BS EN 1993")

st.info("💡 **Instructions:** Adjust the design inputs in the left sidebar to analyze different beam configurations. Review the tabs below for detailed design checks.")

# Sidebar Controls
st.sidebar.header("1. Beam Configuration")
beam_type = st.sidebar.radio("Select Beam Support Condition:", ["Restrained Beam", "Unrestrained Beam"])

st.sidebar.header("2. Span & Applied Loads")
L = st.sidebar.number_input("Span Length, L (m):", min_value=0.5, max_value=30.0, value=8.0, step=0.5)
Gk = st.sidebar.number_input("UDL Dead Load, Gk (kN/m):", min_value=0.0, value=25.0, step=1.0)
Qk = st.sidebar.number_input("UDL Live Load, Qk (kN/m):", min_value=0.0, value=35.0, step=1.0)

PL_Gk = st.sidebar.number_input("Point Load Dead, PL Gk (kN):", min_value=0.0, value=0.0, step=1.0)
PL_Qk = st.sidebar.number_input("Point Load Live, PL Qk (kN):", min_value=0.0, value=0.0, step=1.0)

st.sidebar.header("3. Steel Section Properties")
fy = st.sidebar.selectbox("Steel Grade / Yield Strength, fy (MPa):", [275, 355, 460], index=1)
h = st.sidebar.number_input("Total Depth, h (mm):", min_value=10.0, value=607.6, step=1.0)
b = st.sidebar.number_input("Flange Width, b (mm):", min_value=10.0, value=228.2, step=1.0)
tw = st.sidebar.number_input("Web Thickness, tw (mm):", min_value=1.0, value=11.1, step=0.1)
tf = st.sidebar.number_input("Flange Thickness, tf (mm):", min_value=1.0, value=17.3, step=0.1)
r = st.sidebar.number_input("Root Radius, r (mm):", min_value=0.0, value=12.7, step=0.1)
A = st.sidebar.number_input("Cross-sectional Area, A (cm²):", min_value=1.0, value=144.0, step=1.0)
Wpl = st.sidebar.number_input("Plastic Section Modulus, Wpl,y (cm³):", min_value=1.0, value=1450.0, step=10.0)
I_x = st.sidebar.number_input("Second Moment of Area, Ix (cm⁴):", min_value=1.0, value=98600.0, step=100.0)

if beam_type == "Unrestrained Beam":
    st.sidebar.header("4. Buckling / LTB Parameters")
    Lcr = st.sidebar.number_input("Unrestrained Length, Lcr (mm):", min_value=100.0, value=4000.0, step=100.0)
    Iz = st.sidebar.number_input("Minor Axis Inertia, Iz (mm⁴):", min_value=1.0, value=33900000.0, step=100000.0)
    IT = st.sidebar.number_input("Torsional Constant, IT (mm⁴):", min_value=1.0, value=1780000.0, step=10000.0)
    Iw = st.sidebar.number_input("Warping Constant, Iw (mm⁶):", min_value=1.0, value=2320000000000.0, step=100000000.0)

# ==========================================
# EUROCODE 3 CALCULATIONS
# ==========================================

# Design loads & internal forces
design_udl = (1.35 * Gk) + (1.5 * Qk)
design_pl = (1.35 * PL_Gk) + (1.5 * PL_Qk)

Ved = (design_udl * L / 2) + (design_pl / 2)
Med = (design_udl * (L ** 2) / 8) + (design_pl * L / 4)

# Section Classification
epsilon = round(math.sqrt(235 / fy), 2)
hw = h - (2 * tf)
c_t_web = round(hw / tw, 2)
web_limit = round(72 * epsilon, 2)
web_class = "Class 1" if c_t_web <= web_limit else ("Class 2" if c_t_web <= 83*epsilon else ("Class 3" if c_t_web <= 124*epsilon else "Class 4"))

cf = (b - tw - (2 * r)) / 2
c_t_flange = round(cf / tf, 2)
flange_limit = round(9 * epsilon, 2)
flange_class = "Class 1" if c_t_flange <= flange_limit else ("Class 2" if c_t_flange <= 10*epsilon else ("Class 3" if c_t_flange <= 14*epsilon else "Class 4"))

# Shear Check
Av = round((A * 100) - (2 * b * tf) + (tw + (2 * r)) * tf, 2)
Vpl_Rd = round((Av * (fy / math.sqrt(3)) / 1.0) / 1000, 2)
shear_check = Ved <= Vpl_Rd

hw_tw = round((h - (2 * tf)) / tw, 2)
shear_buckling_limit = round(72 * epsilon / 1.0, 2)
shear_buckling_req = hw_tw > shear_buckling_limit

# Bending Check
Mc_Rd = round(((Wpl * 1000) * fy / 1.0) / 1000000, 2)
bending_ratio = round(Med / Mc_Rd, 2)
bending_check = Med <= Mc_Rd

high_shear_limit = round(0.5 * Vpl_Rd, 2)
high_shear = Ved > high_shear_limit

# Deflection Check
L_mm = L * 1000
E = 210000
I_mm4 = I_x * 10000

delta_allow = round(L_mm / 360, 2)
delta_udl = (5 * Qk * (L_mm ** 4)) / (384 * E * I_mm4)
delta_pl = (PL_Qk * 1000 * (L_mm ** 3)) / (48 * E * I_mm4)
delta_max = round(delta_udl + delta_pl, 2)
deflection_check = delta_max <= delta_allow

# ==========================================
# PRESENTATION TABS
# ==========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Loading & Actions", 
    "2. Section Classification", 
    "3. Shear & Bending Checks", 
    "4. Deflection Check", 
    "5. Buckling / Summary"
])

with tab1:
    st.header("1. Design Loading & Internal Actions")
    col1, col2, col3 = st.columns(3)
    col1.metric("Design UDL (w_ed)", f"{design_udl:.2f} kN/m")
    col2.metric("Max Shear Force (V_ed)", f"{Ved:.2f} kN")
    col3.metric("Max Bending Moment (M_ed)", f"{Med:.2f} kNm")

with tab2:
    st.header("2. Section Classification")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Web Classification")
        st.write(f"Epsilon (ε): **{epsilon}**")
        st.write(f"Web c/t ratio: **{c_t_web}** (Limit 72ε = {web_limit})")
        st.info(f"Classification: **{web_class}**")
    
    with col2:
        st.subheader("Flange Classification")
        st.write(f"Flange c/t ratio: **{c_t_flange}** (Limit 9ε = {flange_limit})")
        st.info(f"Classification: **{flange_class}**")

with tab3:
    st.header("3. Shear & Bending Verification")
    
    st.subheader("Shear Resistance Check")
    col1, col2 = st.columns(2)
    col1.metric("Shear Capacity (V_pl,Rd)", f"{Vpl_Rd:.2f} kN")
    if shear_check:
        col2.success("✅ PASS: Shear Resistance is Adequate")
    else:
        col2.error("❌ FAIL: Shear Capacity Exceeded")
        
    st.caption(f"Web Buckling Check: hw/tw ({hw_tw}) ≤ Limit ({shear_buckling_limit}) ➔ {'Further check NOT required' if not shear_buckling_req else 'Further check IS required'}")

    st.divider()

    st.subheader("Bending Resistance Check")
    col1, col2 = st.columns(2)
    col1.metric("Moment Capacity (M_c,Rd)", f"{Mc_Rd:.2f} kNm", delta=f"Utilization: {bending_ratio*100:.1f}%", delta_color="inverse" if bending_ratio > 1 else "normal")
    if bending_check:
        col2.success("✅ PASS: Bending Resistance is Adequate")
    else:
        col2.error("❌ FAIL: Redesign Required - Exceeds Moment Resistance")
        
    if high_shear:
        st.warning("⚠️ High Shear Interaction detected (V_ed > 0.5 V_pl,Rd). Moment resistance must be reduced.")

with tab4:
    st.header("4. Serviceability Limit State: Deflection")
    col1, col2, col3 = st.columns(3)
    col1.metric("Allowable Deflection (δ_allow)", f"{delta_allow:.2f} mm")
    col2.metric("Actual Deflection (δ_max)", f"{delta_max:.2f} mm")
    
    if deflection_check:
        col3.success("✅ PASS: Deflection within Limits")
    else:
        col3.error("❌ FAIL: Deflection Exceeds Limit")

with tab5:
    if beam_type == "Unrestrained Beam":
        st.header("5. Lateral Torsional Buckling (LTB) Check")
        
        C1 = 1.88
        E_Nmm = 210000
        G_Nmm = 81000
        
        term1 = (C1 * (math.pi**2) * E_Nmm * Iz) / (Lcr**2)
        term2 = math.sqrt((Iw / Iz) + (((Lcr**2) * G_Nmm * IT) / ((math.pi**2) * E_Nmm * Iz)))
        Mcr = (term1 * term2) / 10**6
        
        lambda_LT = math.sqrt(((Wpl * 1000) * fy) / (Mcr * 10**6))
        
        hb_ratio = h / b
        buckling_curve = "a" if hb_ratio <= 2 else "b"
        alpha_LT = 0.21 if buckling_curve == "a" else 0.34
        
        phi_LT = 0.5 * (1 + alpha_LT * (lambda_LT - 0.2) + (lambda_LT ** 2))
        chi_LT = 1 / (phi_LT + math.sqrt(phi_LT**2 - lambda_LT**2))
        if chi_LT > 1.0:
            chi_LT = 1.0
            
        Mb_Rd = round((chi_LT * (Wpl * 1000) * fy / 1.0) / 10**6, 2)
        ltb_check = Med <= Mb_Rd
        
        col1, col2 = st.columns(2)
        col1.write(f"Elastic Critical Moment ($M_{{cr}}$): **{Mcr:.2f} kNm**")
        col1.write(f"Slenderness ($\lambda_{{LT}}$): **{lambda_LT:.3f}**")
        col1.write(f"Buckling Curve: **Curve {buckling_curve}** ($\alpha_{{LT}}$ = {alpha_LT})")
        col1.write(f"Reduction Factor ($\chi_{{LT}}$): **{chi_LT:.3f}**")
        
        col2.metric("Buckling Moment Resistance (M_b,Rd)", f"{Mb_Rd:.2f} kNm")
        if ltb_check:
            col2.success("✅ PASS: LTB Resistance is Adequate")
        else:
            col2.error("❌ FAIL: LTB Resistance Exceeded")
    else:
        st.header("5. Design Verification Summary")
        st.write("Beam Type: **Restrained Beam** (Fully supported against lateral-torsional buckling)")
        all_passed = shear_check and bending_check and deflection_check
        if all_passed:
            st.success("🎉 ALL CHECKS PASSED: The selected steel beam section is STRUCTURALLY ADEQUATE.")
        else:
            st.error("⚠️ CHECKS FAILED: Please select a larger section or reduce span/loading.")