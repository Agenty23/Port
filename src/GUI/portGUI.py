import sys
import random
import PySimpleGUI as sg
 
mode = "tkinter"
mysize = (10,1)
BAR_WIDTH = 150
BAR_SPACING = 175
EDGE_OFFSET = 10
GRAPH_SIZE = (500,500)
DATA_SIZE = (500,500)
PORT_NAME = "Mock"
N_OPERATIONS = "500"
 
bcols = ['blue','lightgray','lightblue']
myfont = "Ariel 26"
 
 
graph = sg.Graph(GRAPH_SIZE, (0,0), DATA_SIZE)
 
layout = [[sg.Text('Dashboard',font=myfont)],
  [sg.Text(f"Port name: {PORT_NAME}", font='_ 20')],
  [sg.Text(f"Number of operations: {N_OPERATIONS}", font='_ 20')],
  [graph],
  [sg.Text('Field 1',text_color=bcols[0],font=myfont,size= mysize ),
  sg.Text('Field 2',text_color=bcols[1],font=myfont,size= mysize ),
  sg.Text('Field 3',text_color=bcols[2],font=myfont,size= mysize)],
  [sg.Text('Available spots:', font='_ 18')],
  [sg.Exit()]]
 

window = sg.Window('Dashboard', layout, margins=(100, 25))
while True:
    event, values = window.read(timeout=100)
    if event in (None, 'Exit'):
        break
 
    graph.erase()
    graph_value = [130,240,80]
    for i in range(3):
        graph.draw_rectangle(top_left=(i * BAR_SPACING + EDGE_OFFSET, graph_value[i]),
        bottom_right=(i * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0), fill_color=bcols[i])
        graph.draw_text(text=graph_value[i], location=(i*BAR_SPACING+EDGE_OFFSET+25,graph_value[i]+10), font='_ 16')
 
window.close()