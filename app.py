import flet
from main import App
from produtos import ProductUser
from adicionar import AdicionarControl
from caixa import CaixaController
from configuracoes import ConfControl
import os
import sqlite3

def main(page:flet.Page):
    
    def on_keyboard(e):
        if e.key=='Escape':
            page.window_destroy()
    
    def route_change(route):
        page.views.clear()
        page.views.append(
            flet.View(
                route='/',
                controls=[App(page)],
                bgcolor='#1b263b',
                vertical_alignment='center',
                horizontal_alignment='center'
            )
        )
        if page.route=='/estoque':
            page.views.append(
                flet.View(
                    route='/estoque',
                    bgcolor='#1b263b',
                    horizontal_alignment='left',
                    vertical_alignment='center',
                    controls=[ProductUser(page)]
                )
            )
        elif page.route=='/adicionar':
            page.views.append(
                flet.View(
                    route='/adicionar',
                    bgcolor='#1b263b',
                    horizontal_alignment='left',
                    vertical_alignment='center',
                    controls=[AdicionarControl(page)]               
                )
            )
        elif page.route=='/caixa':
            page.views.append(
                flet.View(
                    route='/caixa',
                    bgcolor='#1b263b',
                    horizontal_alignment='left',
                    vertical_alignment='center',
                    controls=[CaixaController(page)]
                )
            )
        elif page.route=='/ajustes':
            page.views.append(
                flet.View(
                    route='/ajustes',
                    bgcolor='#1b263b',
                    horizontal_alignment='left',
                    vertical_alignment='center',
                    controls=[ConfControl(page)]
                )
            )
        page.update()
    
    page.on_keyboard_event=on_keyboard
    page.window_full_screen=True
    page.on_route_change=route_change
    page.go(page.route)

flet.app(target=main,view=flet.FLET_APP)
try:
    os.remove('temp.txt')
except FileNotFoundError:
    pass

conn=sqlite3.connect('banco.db')
c=conn.cursor()
c.execute('SELECT imagem FROM produtos')
imagens=set(c.fetchall())
c.close()
nomes=['image_not_found.jpg']
for arquivo in imagens:
    if arquivo[0]!=None:
        nomes.append(arquivo[0][arquivo[0].rfind('/')+1:])
for arquivo in os.listdir('_imagens/produtos'):
    if arquivo not in nomes:
        os.remove(f'_imagens/produtos/{arquivo}')