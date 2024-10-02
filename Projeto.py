import PySimpleGUI as sg
import pandas as pd
from funcao import plot_hourly_data, plot_custom_values


def main_menu():
    menu_layout = [
        [sg.Text('Menu Principal', font=('Helvetica', 16), justification='center')],
        [sg.Push(), sg.Button('Plotar Dados por Hora', size=(25, 2)), sg.Push()],
        [sg.Push(), sg.Button('Plotar Valores Personalizados', size=(25, 2)), sg.Push()],
        [sg.Push(), sg.Button('Sair', size=(25, 2)), sg.Push()]
    ]

    window = sg.Window('Menu Principal', menu_layout, size=(400, 300))

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Sair':
            break
        elif event == 'Plotar Dados por Hora':
            hour_selection(window)
        elif event == 'Plotar Valores Personalizados':
            custom_values_selection(window)

    window.close()

def hour_selection(parent_window):
    hour_layout = [
        [sg.Text('Selecione a Hora:', justification='center'),
         sg.Slider(range=(0, 23), default_value=0, orientation='h', key='-HOUR-', size=(40, 20))],
        [sg.Text('Selecione o Minuto:', justification='center'),
         sg.Slider(range=(0, 59), default_value=0, orientation='h', key='-MINUTE-', size=(40, 20))],
        [sg.Button('Plotar'), sg.Button('Voltar')],
        [sg.Canvas(key='-CANVAS-', size=(800, 600))]
    ]

    hour_window = sg.Window('Plotar Dados por Hora', hour_layout, size=(850, 700), finalize=True)

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
        elif hour_event == 'Plotar':
            selected_hour = int(hour_values['-HOUR-'])
            selected_minute = int(hour_values['-MINUTE-'])
            plot_hourly_data(selected_hour, selected_minute, hour_window['-CANVAS-'].TKCanvas)

def custom_values_selection(parent_window):
    custom_layout = [
        [sg.Text('Potência Reativa:', justification='right'), 
         sg.InputText(size=(20, 1), key='-REACTIVE-', default_text='300'),sg.Text('Digite valor em W')],
        [sg.Text('Ângulo de Fase:', justification='right'), 
         sg.InputText(size=(20, 1), key='-PHASE-', default_text='3.14'),sg.Text('Digite valor em rad')],
        [sg.Text('Amplitude:', justification='right'), 
         sg.InputText(size=(20, 1), key='-AMPLITUDE-', default_text='220'),sg.Text('Digite valor em V')],
        [sg.Button('Plotar'), sg.Button('Voltar')],
        [sg.Canvas(key='-CANVAS-CUSTOM-', size=(800, 600))]
    ]

    custom_window = sg.Window('Plotar Valores Personalizados', custom_layout, size=(850, 700), finalize=True)

    while True:
        custom_event, custom_values = custom_window.read()
        
        if custom_event == sg.WINDOW_CLOSED:
            custom_window.close()
            parent_window.un_hide()  # Retorna ao menu principal
            break
        elif custom_event == 'Voltar':
            custom_window.close()
            parent_window.un_hide()  # Retorna ao menu principal
            break
        elif custom_event == 'Plotar':
            reactive_power = custom_values['-REACTIVE-']
            phase_angle = custom_values['-PHASE-']
            amplitude = custom_values['-AMPLITUDE-']
            plot_custom_values(reactive_power, phase_angle, amplitude, custom_window['-CANVAS-CUSTOM-'].TKCanvas)

# Executar o programa
main_menu()
