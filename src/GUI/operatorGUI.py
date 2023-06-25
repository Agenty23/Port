import PySimpleGUI as sg
import datetime
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

window.close()
containerID = values[1]
collection = datetime.datetime.strptime(input(), "%Y:%d:%m").date()
print(collection)
print(event, values[0], values[1], values["Date"])