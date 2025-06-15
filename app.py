import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pulp import LpMaximize, LpProblem, LpVariable

st.set_page_config(page_title="Sistem Pemilihan Model Industri", layout="centered")
st.title("🏭 Sistem Pemilihan Model Matematika Industri")

# Pilihan model
model = st.sidebar.selectbox("Pilih Model Matematis:", (
    "Model Antrian M/M/1",
    "Model EOQ",
    "Optimasi Produksi Beras",
    "Break-Even Point (BEP)"
))

if model == "Model Antrian M/M/1":
    st.header("⏳ Simulasi Antrian - Model M/M/1")
    st.markdown("""
    **Penjelasan Singkat**  
    Model ini digunakan untuk menganalisis sistem antrian satu jalur satu server.  
    **Rumus penting:**  
    - Utilisasi sistem: ρ = λ / μ  
    - Rata-rata pelanggan dalam sistem: L = λ / (μ - λ)  
    - Rata-rata pelanggan dalam antrian: Lq = λ² / (μ(μ - λ))  
    - Waktu rata-rata dalam sistem: W = 1 / (μ - λ)  
    - Waktu menunggu rata-rata: Wq = λ / (μ(μ - λ))  
    """)

    lambda_val = st.number_input("Rata-rata kedatangan per jam (λ)", min_value=0.1, value=4.0)
    mu_val = st.number_input("Rata-rata pelayanan per jam (μ)", min_value=0.1, value=6.0)

    if lambda_val >= mu_val:
        st.error("⚠️ Sistem tidak stabil! λ harus lebih kecil dari μ.")
    else:
        rho = lambda_val / mu_val
        L = lambda_val / (mu_val - lambda_val)
        Lq = (lambda_val**2) / (mu_val * (mu_val - lambda_val))
        W = 1 / (mu_val - lambda_val)
        Wq = lambda_val / (mu_val * (mu_val - lambda_val))

        st.subheader("📈 Hasil Perhitungan")
        st.write(f"**Utilisasi sistem (ρ):** {rho:.2f}")
        st.write(f"**Rata-rata pelanggan dalam sistem (L):** {L:.2f}")
        st.write(f"**Rata-rata pelanggan dalam antrian (Lq):** {Lq:.2f}")
        st.write(f"**Waktu rata-rata dalam sistem (W):** {W:.2f} jam")
        st.write(f"**Waktu rata-rata menunggu (Wq):** {Wq:.2f} jam")

        st.subheader("📊 Grafik: Jumlah Pelanggan vs Tingkat Kedatangan")
        lambdas = np.linspace(0.1, mu_val - 0.01, 100)
        Ls = lambdas / (mu_val - lambdas)
        Lqs = (lambdas**2) / (mu_val * (mu_val - lambdas))

        fig, ax = plt.subplots()
        ax.plot(lambdas, Ls, label='L (dalam sistem)', color='blue')
        ax.plot(lambdas, Lqs, label='Lq (dalam antrian)', color='orange')
        ax.axvline(lambda_val, color='red', linestyle='--', label=f"λ saat ini = {lambda_val}")
        ax.set_xlabel("λ (Kedatangan per jam)")
        ax.set_ylabel("Jumlah pelanggan")
        ax.set_title("Simulasi Antrian M/M/1")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

elif model == "Model EOQ":
    st.header("📦 Perhitungan EOQ (Economic Order Quantity)")
    st.markdown("""
    **Penjelasan Singkat**  
    EOQ digunakan untuk menentukan jumlah pemesanan optimal agar biaya total minimum.  
    **Rumus:**  
    EOQ = √(2DS / H)  
    - D: Permintaan per periode  
    - S: Biaya pemesanan  
    - H: Biaya penyimpanan  
    """)

    D = st.number_input("Permintaan bulanan (kg)", min_value=1, value=10000)
    S = st.number_input("Biaya pemesanan per kali order (Rp)", min_value=1, value=200000)
    H = st.number_input("Biaya simpan per kg per bulan (Rp)", min_value=1, value=100)

    EOQ = (2 * D * S / H) ** 0.5
    st.subheader("📊 Hasil Perhitungan EOQ")
    st.write(f"**EOQ Optimal:** {EOQ:.2f} kg per order")

    st.subheader("📈 Grafik Biaya vs Jumlah Pemesanan")
    Q = np.linspace(100, D * 2, 500)
    biaya_pesan = (D / Q) * S
    biaya_simpan = (Q / 2) * H
    total_biaya = biaya_pesan + biaya_simpan

    fig, ax = plt.subplots()
    ax.plot(Q, biaya_pesan, label='Biaya Pemesanan', linestyle='--')
    ax.plot(Q, biaya_simpan, label='Biaya Penyimpanan', linestyle='--')
    ax.plot(Q, total_biaya, label='Total Biaya', color='black', linewidth=2)
    ax.axvline(EOQ, color='red', linestyle=':', label=f'EOQ ≈ {EOQ:.0f} kg')
    ax.set_xlabel('Jumlah Pemesanan (kg)')
    ax.set_ylabel('Biaya (Rp)')
    ax.set_title('Grafik EOQ: Biaya vs Jumlah Pemesanan')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

elif model == "Optimasi Produksi Beras":
    st.header("📊 Optimasi Produksi Beras")
    st.markdown("""
    **Penjelasan Singkat**  
    Model ini menggunakan Linear Programming untuk memaksimalkan keuntungan dari produksi dua jenis beras: Premium dan Medium.  
    **Model Tujuan:**  
    Maksimalkan Z = 40x + 60y  
    **Kendala:**  
    - Konsumsi gabah: (Gabah_Premium × x + Gabah_Medium × y) ≤ Total Gabah  
    - Produksi Premium minimal 20%  
    - x, y ≥ 0  
    """)

    total_gabah = st.number_input("Jumlah Gabah Tersedia (kg)", min_value=0.0, value=10000.0)

    st.subheader("⚙️ Data Konversi Gabah")
    premium_gabah = st.number_input("Gabah/kg untuk Beras Premium", min_value=0.1, value=1.2)
    medium_gabah = st.number_input("Gabah/kg untuk Beras Medium", min_value=0.1, value=1.0)

    if st.button("🚀 Hitung Optimasi"):
        from pulp import LpMaximize, LpProblem, LpVariable

        # Buat model LP
        model_lp = LpProblem("Optimasi_Produksi_Beras", LpMaximize)
        x = LpVariable("Beras_Premium", lowBound=0)
        y = LpVariable("Beras_Medium", lowBound=0)

        # Fungsi Objektif: Z = 40x + 60y
        model_lp += 40 * x + 60 * y

        # Kendala:
        model_lp += premium_gabah * x + medium_gabah * y <= total_gabah  # Batas gabah
        model_lp += x >= (0.2 * total_gabah / premium_gabah)             # Min 20% premium

        # Selesaikan model
        model_lp.solve()

        x_val = x.varValue
        y_val = y.varValue
        total_profit = 40 * x_val + 60 * y_val

        st.subheader("📈 Hasil Optimasi Produksi")
        st.success(f"✅ Produksi Beras Premium: {x_val:.2f} kg")
        st.success(f"✅ Produksi Beras Medium: {y_val:.2f} kg")
        st.success(f"💰 Total Keuntungan Maksimum (Z): Rp {total_profit:,.0f}")

        st.subheader("📊 Grafik Produksi")
        fig, ax = plt.subplots()
        ax.bar(["Beras Premium", "Beras Medium"], [x_val, y_val], color=["green", "orange"])
        ax.set_ylabel("Jumlah Produksi (kg)")
        ax.set_title("Perbandingan Produksi Beras")
        st.pyplot(fig)


elif model == "Break-Even Point (BEP)":
    st.header("🧮 Analisis Titik Impas (Break-Even Point)")
    st.markdown("""
    **Penjelasan Singkat**  
    BEP menunjukkan jumlah unit minimum yang harus dijual agar tidak rugi.  
    **Rumus:**  
    BEP = Biaya Tetap / (Harga Jual per Unit - Biaya Variabel per Unit)  
    """)

    fixed_cost = st.number_input("🔧 Biaya Tetap (Rp)", min_value=0, value=20000000, step=100000)
    variable_cost = st.number_input("⚙️ Biaya Variabel per Unit (Rp)", min_value=0, value=20000, step=1000)
    price_per_unit = st.number_input("💵 Harga Jual per Unit (Rp)", min_value=0, value=50000, step=1000)

    if price_per_unit <= variable_cost:
        st.error("⚠️ Harga jual per unit harus lebih besar dari biaya variabel per unit agar ada titik impas.")
    else:
        bep_unit = fixed_cost / (price_per_unit - variable_cost)
        st.subheader("📌 Hasil Perhitungan")
        st.success(f"🎯 Titik Impas (Break-Even Point): {bep_unit:.0f} unit")
        st.markdown(f"💡 Anda harus menjual minimal **{bep_unit:.0f} unit** agar tidak rugi.")

        st.subheader("📈 Grafik Pendapatan dan Biaya vs Jumlah Unit")
        units = np.arange(0, int(bep_unit * 2) + 100, 100)
        total_cost = fixed_cost + variable_cost * units
        total_revenue = price_per_unit * units

        fig, ax = plt.subplots()
        ax.plot(units, total_cost, label="Total Biaya", color="red")
        ax.plot(units, total_revenue, label="Total Pendapatan", color="green")
        ax.axvline(bep_unit, linestyle="--", color="blue", label=f"BEP ≈ {bep_unit:.0f} unit")
        ax.set_xlabel("Jumlah Unit")
        ax.set_ylabel("Rupiah (Rp)")
        ax.set_title("Break-Even Analysis")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

