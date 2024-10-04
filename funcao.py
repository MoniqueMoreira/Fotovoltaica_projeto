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

# Funções de cálculo
def deg_to_rad(degrees):
    return degrees * np.pi / 180

def rad_to_deg(radians):
    return radians * 180 / np.pi
    
def calculate_solar_parameters(data_hora, irradiancia_global, beta, gamma_p, lat, long_local, long_meridiano):
    dia = data_hora.timetuple().tm_yday
    B = (360 / 365) * (dia - 81)
    EoT = 9.87 * np.sin(np.radians(2 * B)) - 7.53 * np.cos(np.radians(B)) - 1.5 * np.sin(np.radians(B))
    EoT /= 60
    
    hora_local = data_hora.hour + data_hora.minute / 60
    hora_solar = hora_local - ((long_local - long_meridiano) / 15) + EoT
    
    declinacao_solar = 23.45 * np.sin(np.radians(360 * (284 + dia) / 365))
    omega = 15 * (hora_solar - 12)
    
    theta_z = np.degrees(np.arccos(np.sin(np.radians(lat)) * np.sin(np.radians(declinacao_solar)) +
                                    np.cos(np.radians(lat)) * np.cos(np.radians(declinacao_solar)) * np.cos(np.radians(omega))))
    
    gamma_solar = np.degrees(np.arctan2(np.sin(np.radians(omega)),
                                        (np.cos(np.radians(omega)) * np.sin(np.radians(lat)) -
                                         np.tan(np.radians(declinacao_solar)) * np.cos(np.radians(lat)))))


    theta_i = np.degrees(np.arccos(np.sin(np.radians(theta_z)) * np.cos(np.radians(gamma_p - gamma_solar)) * np.sin(np.radians(beta)) +
                                    np.cos(np.radians(theta_z)) * np.cos(np.radians(beta))))
    
    G_inc = irradiancia_global * np.cos(np.radians(theta_i))
    return hora_solar, theta_i, G_inc

def calcular_resultados(canvas,Pmed,Amp,ang):
    # Definindo variáveis
    f = 60
    w = 2 * np.pi * f
    t = np.linspace(0, 2 * (1/f), 200)

    Vp = Amp * np.sqrt(2)
    Ip = 2*Pmed / Vp

    # Tensão e corrente
    vt = Vp * np.cos(w * t)
    ph = np.radians(ang)
    it = Ip * np.cos(w * t + ph)

    # Potências
    pt = vt * it
    pt_max = np.max(pt)
    pt_media = np.mean(pt)
    pt_min = np.min(pt)

    # Cálculo da potência reativa
    pa = Vp * Ip / 2 * np.cos(2 * w * t) * np.cos(ph) + Vp * Ip / 2 * np.cos(ph)
    pr = -Vp * Ip / 2 * np.sin(2 * w * t) * np.sin(ph)
    amplitude_tensao = np.max(np.abs(vt))
    amplitude_corrente = np.max(np.abs(it))
   

    # Potência fotovoltaica
    L = 50e-3
    VL = -np.max(it) * (w * L) * np.sin(w * t)
    Vfv = vt + VL
    pfv = Vfv * (-it)

    pfv_max = np.max(pfv)
    pfv_media = np.mean(pfv)
    pfv_min = np.min(pfv)
    amplitude_tensao_fotovoltaico = np.max(np.abs(Vfv))
    amplitude_corrente_fotovoltaico = np.max(np.abs(-it))

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 5))

    # Figura 1: Tensões e Correntes
    # Subplot 1: Tensões e Correntes com escalas diferentes
    ax1.plot(t * 1e3, vt, 'blue', label='Tensão [V]')
    ax1.set_xlabel('Tempo [ms]')
    ax1.set_ylabel('Tensão [V]', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True)

    # Eixo y para a corrente (eixo da direita)
    ax1_corrente = ax1.twinx()
    ax1_corrente.plot(t * 1e3, it, 'orange', label='Corrente [A]')
    ax1_corrente.set_ylabel('Corrente [A]', color='orange')
    ax1_corrente.tick_params(axis='y', labelcolor='orange')

    # Legendas para ambos os eixos
    ax1.legend(loc='upper left')
    ax1_corrente.legend(loc='upper right')

    # Subplot 2: Potências
    ax2.plot(t * 1e3, pa + pr, 'y', label='pa+pr (pt)')
    ax2.plot(t * 1e3, pt, 'k', label='Pt')
    ax2.plot(t * 1e3, pa, 'b', label='P_at')
    ax2.plot(t * 1e3, pr, 'r', label='P_re')
    ax2.grid(True)
    ax2.set_xlabel('Tempo [ms]')
    ax2.set_ylabel('Potência total, ativa e reativa')
    ax2.legend()

    # Figura 3: Potência fotovoltaica
    # Subplot 3: Tensão e corrente fotovoltaica com escalas diferentes
    ax3.plot(t * 1e3, Vfv, 'b', label='Vfv [V]')
    ax3.set_xlabel('Tempo [ms]')
    ax3.set_ylabel('Tensão [V]', color='b')
    ax3.tick_params(axis='y', labelcolor='b')
    ax3.grid(True)

    # Eixo y para a corrente (eixo da direita)
    ax3_corrente = ax3.twinx()
    ax3_corrente.plot(t * 1e3, -it, 'orange', label='Corrente [A]')
    ax3_corrente.set_ylabel('Corrente [A]', color='orange')
    ax3_corrente.tick_params(axis='y', labelcolor='orange')

    # Legendas para ambos os eixos
    ax3.legend(loc='upper left')
    ax3_corrente.legend(loc='upper right')

    # Subplot 4: Potência fotovoltaica
    ax4.plot(t * 1e3, pfv, 'k', label='Pfv')
    ax4.grid(True)
    ax4.set_xlabel('Tempo [ms]')
    ax4.set_ylabel('Potência fotovoltaica [W]')
    ax4.legend()

    plt.tight_layout()
    draw_figure(canvas, fig)  # Desenha a figura no Canvas
    plt.close(fig)
    
    return (pt_max, pt_media, pt_min, np.mean(pr), Vfv, pfv, 
            amplitude_tensao, amplitude_corrente, pfv_max, pfv_min, pfv_media, 
            amplitude_tensao_fotovoltaico, amplitude_corrente_fotovoltaico)


def Corrente(I, V, Isc, Io,m, Rs, Rp, Vt, Ns,Np):
    """
    Calcula a corrente da célula fotovoltaica para uma dada tensão V e corrente I.
    """
    return -I + Np*Isc - Np*Io*(np.exp((V+((Ns/Np)*Rs*I))/(Ns*m*Vt)) - 1) - ((V + Rs*(Ns/Np)*I)/((Ns/Np)*Rp))

def Derivada(I, V,Isc,Io,m, Rs, Vt, Rp,Ns,Np):
    """
    Calcula a derivada da função corrente em relação a I.
    """
    h = 1e-3
    return (Corrente(I+h, V, Isc, Io,m, Rs, Rp, Vt, Ns,Np) - Corrente(I, V, Isc, Io,m, Rs, Rp, Vt, Ns,Np)) / h

# Função Newton-Raphson para encontrar corrente I
def newton_raphson_monique(V, Isc, Io,m, Vt, Rs, Rp,Ns, Np, tol=1e-6, max_iter=100):
    I = 0
    for _ in range(max_iter):
        f_I = Corrente(I, V, Isc, Io,m, Rs, Rp, Vt, Ns, Np)
        f_prime_I = Derivada(I, V, Isc,Io,m, Rs, Vt, Rp,Ns, Np)

        if f_prime_I == 0:
            break
        I_new = I - f_I / f_prime_I

        if abs(I_new - I) < tol:
            return max(I_new, 0)  # Garante que I não seja negativo
        I = I_new

    raise ValueError("Newton-Raphson não convergiu")
