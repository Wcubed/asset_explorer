import PySimpleGUI as sg


def main():
    sg.theme("Dark")

    layout = [
        [sg.Text("This is testing text.")],
        [sg.Text("A testing input:"), sg.InputText()],
        [sg.Button("It's a button!")]
    ]

    window = sg.Window("A testing window", layout)

    # Event loop.
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            # Stop the program.
            break

    window.close()


if __name__ == '__main__':
    main()
