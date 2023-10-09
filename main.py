import flet
import sqlite3
import cv2 as cv

biblioteca_instalada=True
try:
    import face_recognition as fr
except ModuleNotFoundError:
    biblioteca_instalada=False

import threading
import base64
import os
import numpy as np


class App(flet.UserControl):
    def __init__(self,page:flet.Page):
        self.page=page
        self.page.title='Login'
        self.running=False
        super().__init__()
        self.stack=flet.Stack()
        self.campo_nome=flet.TextField(
            width=350,
            height=50,
            bgcolor='#E0E1DD',
            color='#0D1B2A',
            label='Nome',
            cursor_color='#0D1B2A',
            label_style=flet.TextStyle(color='#0D1B2A'),
            border_radius=10,
            on_submit=self.verificar_campos
                                        )
        self.campo_senha=flet.TextField(
            width=350,
            height=50,
            bgcolor='#E0E1DD',
            color='#0D1B2A',
            label='Senha',
            cursor_color='#0D1B2A',
            label_style=flet.TextStyle(color='#0D1B2A'),
            border_radius=10,
            password=True,
            on_submit=self.verificar_campos
                                        )
        self.tela=flet.Container(
            animate_offset=flet.animation.Animation(500),
            offset=(0,0),
            width=400,
            height=500,
            bgcolor='#0D1B2A',
            border_radius=10,
            content=flet.Column(
                controls=[
                    flet.Row(alignment='center',controls=[flet.Text(value='PyStock',style=flet.TextThemeStyle.HEADLINE_MEDIUM)]),
                    flet.Divider(height=32,color='transparent'),
                    flet.Row(
                        alignment='center',
                        controls=[
                            flet.Container(on_click=self.construirSegundaTela,content=flet.Image('_imagens\python_image.png',border_radius=100,width=140,height=140,fit=flet.ImageFit.CONTAIN))
                        ]
                    ),
                    flet.Divider(height=0,color='transparent'),
                    flet.Row(
                        alignment='center',
                        controls=[self.campo_nome]
                    ),
                    flet.Divider(height=10,color='transparent'),
                    flet.Row(
                        alignment='center',
                        controls=[self.campo_senha]
                    ),
                    flet.Divider(height=5,color='transparent'),
                    flet.Row(
                        alignment='center',
                        controls=[
                            flet.ElevatedButton(
                                text='Login',
                                width=260,
                                height=52,
                                bgcolor='#D9D9D9',
                                color='#000000',
                                on_click=self.verificar_campos
                            )
                        ]
                    )
                ]
            )
        )
        self.segundaTela=flet.Container(
            animate_offset=flet.animation.Animation(500),
            offset=(0,0),
            width=400,
            height=500,
            bgcolor='#0D1B2A',
            border_radius=10
        )
    
    def build(self):
        self.stack.controls.append(self.segundaTela)
        self.stack.controls.append(self.tela)
        return self.stack

    def verificar_campos(self,e):
        if self.campo_nome.value=='':
            alerta=flet.AlertDialog(title=flet.Text('Preencha o nome de usuário'))
            self.page.dialog=alerta
            self.campo_nome.border_color='red'
            alerta.open=True
            self.update()
            self.page.update()
        elif self.campo_senha.value=='':
            alerta=flet.AlertDialog(title=flet.Text('Preencha sua senha'))
            self.page.dialog=alerta
            self.campo_senha.border_color='red'
            alerta.open=True
            self.update()
            self.page.update()
        else:
            self.login()
    
    def login(self):
        conn=sqlite3.connect('banco.db')
        c=conn.cursor()
        c.execute("""
                  SELECT * FROM usuarios WHERE nome=?
                  """,(self.campo_nome.value.lower().replace(' ',''),))
        dados_usuario=c.fetchall()
        self.nome_usuario=dados_usuario[0][0]
        self.cargo_usuario=dados_usuario[0][1]
        senha_usuario=dados_usuario[0][2]
        senha_digitada=self.campo_senha.value
        c.close()
        if dados_usuario==[]:
            alerta=flet.AlertDialog(title=flet.Text('Usuário não encontrado'))
            self.page.dialog=alerta
            alerta.open=True
            self.update()
            self.page.update()
        elif senha_usuario!=senha_digitada:
            alerta=flet.AlertDialog(title=flet.Text('Senha Incorreta'))
            self.page.dialog=alerta
            self.campo_senha.border_color='red'
            alerta.open=True
            self.update()
            self.page.update()
        else:
            with open('temp.txt','w') as arquivo:
                arquivo.write(f'{self.nome_usuario}\n{self.cargo_usuario}')
            if self.cargo_usuario=='gerente':
                self.page.go('/estoque')
            elif self.cargo_usuario=='vendedor':
                self.page.go('/caixa')
    
    def construirSegundaTela(self,e):
        global biblioteca_instalada
        if biblioteca_instalada:
            self.segundaTela.offset=flet.transform.Offset(0.52,0)
            self.segundaTela.update()
            self.tela.offset=flet.transform.Offset(-0.52,0)
            self.tela.update()
            self.coluna_principal=flet.Column()
            self.botao_fechar=flet.ElevatedButton(
                bgcolor='red',
                text='X',
                color='#000000',
                on_click=self.fecharSegundaJanela
            )
            self.espaco_camera=flet.Row(
                controls=[flet.Container(
                    width=300,
                    height=300,
                    bgcolor='#415a77',
                    border_radius=10,
                    content=flet.Image(src='_imagens/profile-user.png',fit=flet.ImageFit.COVER)
                )],
                alignment='center'
            )
            self.coluna_principal.controls.append(flet.Row(controls=[self.botao_fechar]))
            self.coluna_principal.controls.append(self.espaco_camera)
            self.segundaTela.content=self.coluna_principal
            self.segundaTela.update()
            threading.Thread(target=self.rec_facial).start()
        else:
            alerta=flet.AlertDialog(title=flet.Text('Instale os módulos opcionais para usar essa opção'))
            self.page.dialog=alerta
            alerta.open=True
            self.page.update()
    
    def fecharSegundaJanela(self,e):
        self.running=False
        self.segundaTela.offset=flet.transform.Offset(0,0)
        self.tela.offset=flet.transform.Offset(0,0)
        self.tela.update()
        self.segundaTela.clean()
        self.segundaTela.update()
        self.camera.release()
        
    
    def rec_facial(self):
        self.running=True
        index=0
        with open('camera_index.txt','r') as arquivo:
            index=int(arquivo.readlines()[0])
        self.camera=cv.VideoCapture(index,cv.CAP_DSHOW)
        self.camera.set(cv.CAP_PROP_FRAME_WIDTH,300)
        self.camera.set(cv.CAP_PROP_FRAME_HEIGHT,300)
        while self.running:
            _,frame=self.camera.read()
            faces=fr.face_locations(frame)
            if len(faces)>0:
                x1,y1,x2,y2=faces[0]
                cv.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),1)
                valores=self.verificarencode(frame)
                if valores[0]==True:
                    self.preencher_espacos(valores[1])
            _,imarr=cv.imencode('.png',frame)
            imb64=base64.b64encode(imarr)
            self.espaco_camera.controls[0].content.src_base64=imb64.decode('utf-8')
            self.espaco_camera.update()
            
            
    def verificarencode(self,frame):
        encodes=os.listdir('codificacoes')
        encode_mandado=fr.face_encodings(frame)
        matriz=[]
        encontrado=False
        nome='Vazio'
        for encode in encodes:
            with open(f'codificacoes/{encode}','r') as arquivo:
                texto=arquivo.readlines()
                texto.pop(0)
                texto=list(map(lambda x:x.removesuffix('\n'),texto))
                texto=list(map(float,texto))
                matriz=np.array(texto)
            try:
                if fr.compare_faces(matriz,encode_mandado):
                    encontrado=True
                    nome=encode.removesuffix('.txt')
                    break
            except ValueError:
                pass
        return (encontrado,nome)
    
    def preencher_espacos(self,nome):
        conn=sqlite3.connect('banco.db')
        c=conn.cursor()
        c.execute("""
                  SELECT * FROM usuarios WHERE nome=?
                  """,(nome,))
        dados=c.fetchall()
        self.nome_usuario=dados[0][0]
        senha_usuario=dados[0][2]
        self.campo_nome.value=self.nome_usuario
        self.campo_senha.value=senha_usuario
        self.tela.update()
        self.fecharSegundaJanela('e')
