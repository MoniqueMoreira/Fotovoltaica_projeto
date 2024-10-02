# funcao.py
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Carregar os dados para a primeira funcionalidade
url = "https://docs.google.com/spreadsheets/d/1W1V5ExxROoVLTQAdsYKVv98rweN_bEoSwFwct9DN3Ao/gviz/tq?tqx=out:csv"
df = pd.read_csv(url)
df['Data_Hora'] = pd.to_datetime(df['Data_Hora'], format='%d/%m/%y %H:%M')
df['Radiação'] = df['Radiação'].str.replace(',', '.').astype(float)
df['Temp_Cel'] = df['Temp_Cel'].str.replace(',', '.').astype(float)

# Função para desenhar o gráfico no canvas
def draw_figure(canvas, figure):
    # Remove o gráfico anterior se existir
    for widget in canvas.winfo_children():
        widget.destroy()

    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

# Função para plotar dados da primeira funcionalidade
def plot_hourly_data(selected_hour, selected_minute, canvas):
    start_time = pd.Timestamp('2019-11-01 00:00:00') + pd.Timedelta(hours=selected_hour)
    end_time = start_time + pd.Timedelta(hours=1)
    filtered_data = df[(df['Data_Hora'] >= start_time) & (df['Data_Hora'] < end_time)]

    if not filtered_data.empty and selected_minute < len(filtered_data):
        temperatura_atual = filtered_data['Temp_Cel'].iloc[selected_minute]
        irradiancia_atual = filtered_data['Radiação'].iloc[selected_minute]

        fig, axs = plt.subplots(1, 2, figsize=(12, 6))

        # Gráfico de Radiação
        axs[0].plot(filtered_data['Data_Hora'], filtered_data['Radiação'], label='Radiação')
        axs[0].scatter(filtered_data['Data_Hora'].iloc[selected_minute], irradiancia_atual, color='red')
        axs[0].annotate(f"{irradiancia_atual:.2f} W/m²",
                         xy=(filtered_data['Data_Hora'].iloc[selected_minute], irradiancia_atual),
                         xytext=(5, 5), textcoords='offset points', fontsize=10, color='red')
        axs[0].set_title('Radiação')
        axs[0].set_xlabel('Data e Hora')
        axs[0].set_ylabel('Radiação (W/m²)')
        axs[0].tick_params(axis='x', rotation=45)

        # Gráfico de Temperatura
        axs[1].plot(filtered_data['Data_Hora'], filtered_data['Temp_Cel'], label='Temperatura')
        axs[1].scatter(filtered_data['Data_Hora'].iloc[selected_minute], temperatura_atual, color='red')
        axs[1].annotate(f"{temperatura_atual:.2f} °C",
                         xy=(filtered_data['Data_Hora'].iloc[selected_minute], temperatura_atual),
                         xytext=(5, 5), textcoords='offset points', fontsize=10, color='red')
        axs[1].set_title('Temperatura')
        axs[1].set_xlabel('Data e Hora')
        axs[1].set_ylabel('Temperatura (°C)')
        axs[1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        draw_figure(canvas, fig)
        plt.close(fig)

# Função para plotar dados da segunda funcionalidade
def plot_custom_values(reactive_power, phase_angle, amplitude, canvas):
    Vp = 220 * np.sqrt(2)
    Pm = 1000
    f = 60
    w = 2 * np.pi * f
    L = 50e-3
    t = np.linspace(0, 2 * 1 / f, 1000)

    reactive_power = float(reactive_power)
    phase_angle = float(phase_angle)
    amplitude = float(amplitude)

    Vr = Vp * np.cos(w * t)
    Ip = (2 * Pm) / Vp
    Ir = Ip * np.cos(w * t + phase_angle)

    Pt_r = Vr * Ir
    Pa_r = (Vp * Ip / 2) * np.cos(2 * w * t) * np.cos(phase_angle) + (Vp * Ip / 2) * np.cos(phase_angle)
    Pr_r = -reactive_power * np.sin(w * t)

    I_fv = -Ir
    Vl = -np.max(Ip) * w * L * np.sin(w * t)
    Vfv = Vl + Vr
    Pt_fv = Vfv * I_fv

    fig, axs = plt.subplots(2, 2, figsize=(14, 8))

    axs[0, 0].plot(t, Vr, label="Tensão da rede (Vr)", color='blue')
    axs[0, 0].set_ylabel("Tensão (V)")
    axs[0, 0].set_xlabel("Tempo (s)")
    axs[0, 0].grid(True)
    axs[0, 0].twinx().plot(t, Ir, label="Corrente da rede (Ir)", color='red')
    axs[0, 0].set_title("Tensão e Corrente da Rede")
    axs[0, 0].legend(loc="upper left")

    axs[0, 1].plot(t, Pt_r, label="Potência total da rede (Pt_r)", color='green')
    axs[0, 1].plot(t, Pa_r, label="Potência ativa da rede (Pa_r)", color='purple')
    axs[0, 1].plot(t, Pr_r, label="Potência reativa (Pr_r)", color='orange')
    axs[0, 1].set_title("Potências da Rede")
    axs[0, 1].set_xlabel("Tempo (s)")
    axs[0, 1].set_ylabel("Potência (W)")
    axs[0, 1].grid(True)
    axs[0, 1].legend(loc="upper right")

    axs[1, 0].plot(t, Vfv, label="Tensão da fotovoltaica (Vfv)", color='blue')
    axs[1, 0].set_ylabel("Tensão (V)")
    axs[1, 0].set_xlabel("Tempo (s)")
    axs[1, 0].grid(True)
    axs[1, 0].twinx().plot(t, I_fv, label="Corrente da fotovoltaica (Ifv)", color='red')
    axs[1, 0].set_title("Tensão e Corrente da Fotovoltaica")
    axs[1, 0].legend(loc="upper left")

    axs[1, 1].plot(t, Pt_fv, label="Potência total da fotovoltaica (Pt_fv)", color='green')
    axs[1, 1].set_title("Potências da Fotovoltaica")
    axs[1, 1].set_xlabel("Tempo (s)")
    axs[1, 1].set_ylabel("Potência (W)")
    axs[1, 1].grid(True)
    axs[1, 1].legend(loc="upper right")

    plt.tight_layout()
    draw_figure(canvas, fig)
    plt.close(fig)