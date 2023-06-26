import PySimpleGUI as sg
import datetime

isRunning = True

while(isRunning):
    window = sg.Window(
                title="Port Container Client",
                layout=[
                    [sg.Text("Choose operation  "),sg.Combo(["Arrival","Departure"], size = (20,4))],
                    [sg.Text("Please enter your Name, Container ID, Date")],
                    [sg.Text("Name", size=(15, 2)), sg.InputText()],
                    [sg.Text("Container ID", size=(15, 2)), sg.InputText()],
                    [
                        sg.Text("Date", size=(15, 2)),
                        sg.InputText(key="Date"),
                        sg.CalendarButton(
                            "Select Date",
                            close_when_date_chosen=True,
                            target="Date",
                            format="%Y:%m:%d",
                            size=(10, 1),
                        ),
                    ],
                    [sg.Submit(), sg.Cancel()],
                ],
                margins=(500, 300),
            )
    event, values = window.read()
    print(event)
    if(event == 'Cancel' or event == sg.WIN_CLOSED):
        isRunning = False
    print(event == 'Submit')
    if(event == 'Submit'):
        containerID = values[1]
        collection = datetime.datetime.strptime(values['Date'], "%Y:%m:%d").date()
        print(event, values[0], values[1], values[2], values["Date"])
        window2 = sg.Window(
                    title="More actions",
                    layout=[
                        [sg.Text("Do you want to continue with next container?")],
                        [sg.Yes(), sg.No()],
                    ],
                    margins=(500, 300),
                    modal=True,
                )
        event, values = window2.read()
        if (event == 'No' or event == sg.WIN_CLOSED):
            isRunning = False
        window2.close()
if(window):
    window.close()






