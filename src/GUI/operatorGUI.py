import PySimpleGUI as sg
import datetime
from agents.operatorAgent import OperatorAgentAction, OperatorAgent


def getPortContainerClientInput(
    operator_jid: str, operator_password: str, yellow_pages_jid: str
):
    window = sg.Window(
        title="Port Container Client",
        layout=[
            [
                sg.Text("Choose operation  "),
                sg.Combo(["Arrival", "Departure"], size=(20, 4)),
            ],
            [
                sg.Text(
                    "Please enter Port location, Container IDs (comma separated) and Date"
                )
            ],
            [sg.Text("Port location", size=(15, 2)), sg.InputText()],
            [sg.Text("Container IDs", size=(15, 2)), sg.InputText()],
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
            [
                sg.Text("Hour"),
                sg.Combo([str(x) for x in range(24)], size=(15, 2), key="Hour"),
            ],
            [
                sg.Text("Minute"),
                sg.Combo([str(x) for x in range(60)], size=(15, 2), key="Minute"),
            ],
            [sg.Submit(), sg.Cancel()],
        ],
        margins=(500, 300),
    )

    while True:
        event, values = window.read()
        if event in (None, "Cancel"):
            break

        if (
            event == "Submit"
            and values[0] != ""
            and values[1] != ""
            and values[2] != ""
            and values["Date"] != ""
            and values["Hour"] != ""
            and values["Minute"] != ""
        ):
            action = (
                OperatorAgentAction.PICKUP
                if values[0] == "Departure"
                else OperatorAgentAction.DROPOFF
            )
            portLocation = values[1]
            containerIDs = [x.strip() for x in values[2].split(",")]
            date = datetime.datetime.strptime(
                values["Date"] + " " + values["Hour"] + ":" + values["Minute"],
                "%Y:%m:%d %H:%M",
            )
            operator = OperatorAgent(
                operator_jid,
                operator_password,
                action,
                containerIDs,
                date,
                portLocation,
                yellow_pages_jid,
            )
            operator.start()

    window.close()
