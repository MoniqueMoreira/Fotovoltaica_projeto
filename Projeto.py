import PySimpleGUI as sg 
import pandas as pd
import numpy as np
from funcao import plot_hourly_data, calculate_solar_parameters, calcular_resultados,Ns_Np
 
# Carregar os dados
url = "https://docs.google.com/spreadsheets/d/1W1V5ExxROoVLTQAdsYKVv98rweN_bEoSwFwct9DN3Ao/gviz/tq?tqx=out:csv"
df = pd.read_csv(url)
df['Data_Hora'] = pd.to_datetime(df['Data_Hora'], format='%d/%m/%y %H:%M')
df['Radiação'] = df['Radiação'].str.replace(',', '.').astype(float)
df['Temp_Cel'] = df['Temp_Cel'].str.replace(',', '.').astype(float)
 
dados_por_hora = 'Plotar Dados por Hora'
irradiancia_paines_inclinacao = 'Calcular Irradiância para\nPainéis com Inclinação'
potencias_tensoes_correntes = 'Calcular Potências, Tensões e Correntes'
sair = 'Sair'

def main_menu():
    menu_layout = [
        [sg.Text('Menu Principal', font=('Helvetica', 16), justification='center')],
        [sg.Push(), sg.Button(dados_por_hora, size=(25, 3)), sg.Push()],
        [sg.Push(), sg.Button(irradiancia_paines_inclinacao, size=(25, 3)), sg.Push()],
        [sg.Push(), sg.Button(potencias_tensoes_correntes, size=(25, 3)), sg.Push()],
        [sg.Push(), sg.Button(sair, size=(25, 2)), sg.Push()]
    ]

    window = sg.Window('Menu Principal', menu_layout, size=(400, 300))

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == sair:
            break
        elif event == dados_por_hora:
            hour_selection(window)
        elif event == irradiancia_paines_inclinacao:
            inclinação(window)
        elif event == potencias_tensoes_correntes:
            potencias_selection(window)

    window.close()
 
def hour_selection(parent_window):
    hour_layout = [
        [sg.Text('Selecione a Hora:', justification='center'),
         sg.Slider(range=(0, 23), default_value=0, orientation='h', key='-HOUR-', size=(40, 20), enable_events=True)],
        [sg.Text('Selecione o Minuto:', justification='center'),
         sg.Slider(range=(0, 59), default_value=0, orientation='h', key='-MINUTE-', size=(40, 20), enable_events=True)],
        [sg.Button('Voltar')],
        [sg.Canvas(key='-CANVAS-', size=(800, 600))]
    ]
 
    hour_window = sg.Window('Plotar Dados por Hora', hour_layout, size=(850, 700), finalize=True)
 
    selected_hour = int(hour_window['-HOUR-'].DefaultValue)
    selected_minute = int(hour_window['-MINUTE-'].DefaultValue)
    plot_hourly_data(selected_hour, selected_minute, hour_window['-CANVAS-'].TKCanvas)
 
    while True:
        hour_event, hour_values = hour_window.read()
        
        if hour_event == sg.WINDOW_CLOSED:
            hour_window.close()
            parent_window.un_hide()  # Retorna ao menu principal
            break
        elif hour_event == 'Voltar':
            hour_window.close()
            parent_window.un_hide()  # Retorna ao menu principal
            break
        elif hour_event in ('-HOUR-', '-MINUTE-'):
            selected_hour = int(hour_values['-HOUR-'])
            selected_minute = int(hour_values['-MINUTE-'])
            plot_hourly_data(selected_hour, selected_minute, hour_window['-CANVAS-'].TKCanvas)
 
def inclinação(parent_window):
    layout = [
        [sg.Text('Digite a Data e Hora (yyyy-mm-dd HH:MM:SS):')],
        [sg.InputText('2019-11-01 12:00:00', key='data_hora_input', size=(20, 1), justification='center')],
        [sg.Text('Inclinação do painel (Graus °):'), sg.InputText('0', key='beta', size=(5, 1), justification='center')],
        [sg.Text('Angulação do painel (Graus°):'), sg.InputText('0', key='gamma_p', size=(5, 1), justification='center')],
        [sg.Text('Latitude:'), sg.InputText('0', key='latitude', size=(5, 1), justification='center')],
        [sg.Text('Longitude:'), sg.InputText('-46.6', key='longitude', size=(5, 1), justification='center')],
        [sg.Text('Meridiano Central:'), sg.InputText('-45', key='meridiano', size=(5, 1), justification='center')],
        [sg.Button('Calcular'), sg.Button('Voltar')],
        [sg.Text('Resultados:', size=(40, 1), font=('Helvetica', 16), justification='center')],
        [sg.Multiline(size=(45, 10), key='resultados', justification='center')]
    ]
 
    window_inc = sg.Window('Cálculo de Irradiância Solar', layout, element_justification='c')
 
    while True:
        event, values = window_inc.read()
        
        if event in (sg.WINDOW_CLOSED, 'Voltar'):
            window_inc.close()
            parent_window.un_hide()  # Retorna ao menu principal
            break
        
        if event == 'Calcular':
            try:
                data_hora_str = values['data_hora_input']
                data_hora = pd.to_datetime(data_hora_str, format='%Y-%m-%d %H:%M:%S')
                selected_index = df[df['Data_Hora'] == data_hora].index[0]
                irradiancia_global = df['Radiação'].iloc[selected_index]
                beta = float(values['beta'])
                gamma_p = float(values['gamma_p'])
                lat = float(values['latitude'])
                long_local = float(values['longitude'])
                long_meridiano = float(values['meridiano'])
                
                hora_solar, theta_i, G_inc = calculate_solar_parameters(data_hora, irradiancia_global, beta, gamma_p, lat, long_local, long_meridiano)
                
                resultados = f'Data e Hora Local: {data_hora}\n'
                resultados += f'Irradiância Global: {irradiancia_global} W/m²\n'
                resultados += f'Hora Solar: {hora_solar:.2f} horas\n'
                resultados += f'Ângulo de incidência: {theta_i:.2f} graus\n'
                resultados += f'Irradiância incidente: {G_inc:.2f} W/m²\n'
                window_inc['resultados'].update(resultados)
 
            except Exception as e:
                window_inc['resultados'].update(f'Erro: {str(e)}')
 
def potencias_selection(parent_window):
    layout = [
        [sg.Text('Potência Média desejada Rede(W):'), sg.InputText(default_text='1000', key='Pmed', size=(5, 1), justification='center', enable_events=True)],
        [sg.Text('Fase entre Tensão e Corrente (Graus°):'), sg.InputText(default_text='180', key='Ang', size=(5, 1), justification='center', enable_events=True)],
        [sg.Text('Amplitude (Vp):'), sg.InputText(default_text='220', key='Amp', size=(5, 1), justification='center', enable_events=True)],
        [sg.Button('Plotar'),sg.Button('Voltar')],
        [sg.Canvas(key='-CANVAS-CUSTOM-', size=(800, 600)), sg.Text('', key='-RESULTADOS-',font=('Helvetica', 10))]
    ]

    # Criação da janela
    window = sg.Window('Interface Gráfica', layout)

    # Função para verificar se todos os campos têm valores válidos
    def are_valid_inputs(values):
        try:
            float(values['Pmed'])
            float(values['Ang'])
            float(values['Amp'])
            return True
        except ValueError:
            return False

    # Atualiza resultados iniciais com os valores padrão
    values = window.read()[1]  # Lê os valores iniciais
    if are_valid_inputs(values) or event == 'Plotar':
        Pmed = float(values['Pmed'])
        Ang = float(values['Ang'])
        Amp = float(values['Amp']) 

        # Chama a função para calcular resultados
        canvas_widget = window['-CANVAS-CUSTOM-'].TKCanvas
        pt_max, pt_media, pt_min, media_pr, Vfv, pfv, amplitude_tensao, amplitude_corrente, pfv_max, pfv_min, pfv_media, amplitude_tensao_fotovoltaico, amplitude_corrente_fotovoltaico = calcular_resultados(canvas_widget, Pmed, Amp, Ang)

        # Atualiza o texto dos resultados
        resultados_texto = (
            "Informações sobre o Sistema:\n\n"
            f"Potência total máxima Rede: {pt_max:.2f}\n"
            f"Potência total mínima Rede: {pt_min:.2f}\n\n"
            f"Média da potência total Rede: {pt_media:.2f}\n"
            f"Média da potência reativa Rede: {media_pr:.2f}\n\n"
            f"Amplitude máxima da tensão Rede: {amplitude_tensao:.2f}\n"
            f"Amplitude máxima da corrente Rede: {amplitude_corrente:.2f}\n\n"
            f"Potência fotovoltaica máxima: {pfv_max:.2f}\n"
            f"Potência fotovoltaica mínima: {pfv_min:.2f}\n"
            f"Média da potência fotovoltaica: {pfv_media:.2f}\n\n"
            f"Amplitude máxima da tensão fotovoltaica: {amplitude_tensao_fotovoltaico:.2f}\n"
            f"Amplitude máxima da corrente fotovoltaica: {amplitude_corrente_fotovoltaico:.2f}\n\n"
        )
        window['-RESULTADOS-'].update(resultados_texto)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'Voltar':
            window.close()
            parent_window.un_hide()  # Retorna ao menu principal
            break
        
        # Verifica a validade dos inputs após qualquer mudança
        if event in ('Pmed', 'Ang', 'Amp'):
            if are_valid_inputs(values):
                Pmed = float(values['Pmed'])
                Ang = float(values['Ang'])
                Amp = float(values['Amp']) 

                # Chama a função para calcular resultados
                canvas_widget = window['-CANVAS-CUSTOM-'].TKCanvas
                pt_max, pt_media, pt_min, media_pr, Vfv, pfv, amplitude_tensao, amplitude_corrente, pfv_max, pfv_min, pfv_media, amplitude_tensao_fotovoltaico, amplitude_corrente_fotovoltaico = calcular_resultados(canvas_widget, Pmed, Amp, Ang)

                # Atualiza o texto dos resultados
                resultados_texto = (
                    "Informações sobre o Sistema:\n\n"
                    f"Potência total máxima Rede: {pt_max:.2f}\n"
                    f"Potência total mínima Rede: {pt_min:.2f}\n\n"
                    f"Média da potência total Rede: {pt_media:.2f}\n"
                    f"Média da potência reativa Rede: {media_pr:.2f}\n\n"
                    f"Amplitude máxima da tensão Rede: {amplitude_tensao:.2f}\n"
                    f"Amplitude máxima da corrente Rede: {amplitude_corrente:.2f}\n\n"
                    f"Potência fotovoltaica máxima: {pfv_max:.2f}\n"
                    f"Potência fotovoltaica mínima: {pfv_min:.2f}\n"
                    f"Média da potência fotovoltaica: {pfv_media:.2f}\n\n"
                    f"Amplitude máxima da tensão fotovoltaica: {amplitude_tensao_fotovoltaico:.2f}\n"
                    f"Amplitude máxima da corrente fotovoltaica: {amplitude_corrente_fotovoltaico:.2f}"
                )
                window['-RESULTADOS-'].update(resultados_texto)
            else:
                window['-RESULTADOS-'].update("Por favor, preencha todos os campos com valores numéricos válidos!")

    # Fechar a janela
    window.close()

 
main_menu()
