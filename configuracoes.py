import flet
from produtos import SideBar

biblioteca_instalada_fr=True
try:
    import face_recognition as fr
except ModuleNotFoundError:
    biblioteca_instalada_fr=False


import cv2 as cv
import base64
import sqlite3
import numpy as np
import os

biblioteca_instalada_device=True
try:
    import device
except ModuleNotFoundError:
    biblioteca_instalada_device=False

import time

path=None

class ConfControl(flet.UserControl):
    def __init__(self,page):
        super().__init__()
        self.page=page
        self.page.title='Configurações'
    
    def build(self):
        return flet.Row(
            controls=[
                SideBar(self.page.window_height,'root','gerente'),
                Configuracoes(self.page)
            ]
        )
    
class Configuracoes(flet.Container):
    def __init__(self,page):
        super().__init__()
        self.page=page
        self.width=1000
        self.height=550
        self.list_view=flet.ListView(
            controls=[
                flet.ListTile(
                    leading=flet.Icon(flet.icons.PERM_IDENTITY_SHARP),
                    title=flet.Text('Adicionar Colaborador'),
                    on_click=lambda e,master=self:self.mudarjanela(e,master)
                ),
                flet.ListTile(
                    leading=flet.Icon(flet.icons.PERSON_REMOVE_ROUNDED),
                    title=flet.Text('Remover Colaborador'),
                    on_click=lambda e,master=self:self.mudarjanela(e,master)
                )
            ]
        )
        self.verificar_biblioteca()
        self.bgcolor='#0d1b2a'
        self.border_radius=10
        self.content=self.list_view
    
    def verificar_biblioteca(self):
        global biblioteca_instalada_device
        if biblioteca_instalada_device==True:
            self.list_view.controls.append(
                flet.ListTile(
                    leading=flet.Icon(flet.icons.CAMERA),
                    title=flet.Text('Selecionar Camera'),
                    on_click=lambda e,master=self:self.mudarjanela(e,master)
                )
            )
            
    
    def mudarjanela(self,e,master):
        janela=e.control.title.value.lower().replace(' ','') if e!=''else 'inicio'
        if janela=='inicio':
            master.content=self.list_view
        elif janela=='adicionarcolaborador':
            master.content=Colaborador(master)
        elif janela=='removercolaborador':
            master.content=EliminarColaborador(master)
        elif janela=='selecionarcamera':
            master.content=CameraOptions(master)
        self.update()

class Colaborador(flet.Column):
    global path
    def __init__(self,master:Configuracoes):
        super().__init__()
        self.master=master
        self.running=False
        self.codificacao=None
        self.scroll=flet.ScrollMode.ALWAYS
        self.imagem=None
        self.espaco_senha=flet.TextField(label='Senha',bgcolor='#e0e1dd',label_style=flet.TextStyle(color='#0D1B2A'),color='#0D1B2A')
        self.espaco_nome=flet.TextField(label='Nome',bgcolor='#e0e1dd',label_style=flet.TextStyle(color='#0D1B2A'),color='#0D1B2A')
        self.espaco_cargo=flet.Dropdown(label='Cargo',border_color='blue',options=[flet.dropdown.Option('Gerente'),flet.dropdown.Option('Vendedor')])
        self.espaco_imagem_rec=flet.Image(fit=flet.ImageFit.CONTAIN,width=300,height=300)
        self.espaco_imagem_perfil=flet.Image(fit=flet.ImageFit.CONTAIN,width=300,height=300)
        self.picker=flet.FilePicker(on_result=self.on_result_file)
        self.master.page.overlay.clear()
        self.master.page.overlay.append(self.picker)
        self.controls=[
            flet.Divider(height=10,color='transparent'),
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
                width=1000,
                controls=[
                    flet.IconButton(flet.icons.ARROW_BACK_ROUNDED,on_click=self.retornar),
                    flet.IconButton(flet.icons.SAVE,on_click=self.salvar,icon_color='green',icon_size=60)
                ]
            ),
            flet.Divider(height=10,color='transparent'),
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                width=1000,
                controls=[
                    self.espaco_nome,
                    self.espaco_senha,
                    self.espaco_cargo
                ]
                ),
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                width=1000,
                controls=[
                    flet.Text('Imagem para reconhecimento facial (opcional):',weight='bold',size=20),
                    flet.Row(controls=[self.buttonContainer(flet.icons.IMAGE,'Escolher face','imagem_face')]),
                    flet.Text(value='OU'),
                    flet.Row(controls=[self.buttonContainer(flet.icons.CAMERA_ALT_ROUNDED,'Tirar Foto','imagem_camera')])
                ]
            ),
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                width=1000,
                controls=[
                    flet.Text('Imagem de perfil (opcional):',weight='bold',size=20),
                    flet.Row(controls=[self.buttonContainer(flet.icons.IMAGE,'Escolher foto','imagem_perfil')]),
                    flet.Text('OU'),
                    flet.Row(controls=[self.buttonContainer(flet.icons.CAMERA_ALT_ROUNDED,'Tirar foto','foto_perfil')])
                ]
            )
        ]
        self.verificar_biblioteca()
    
    def verificar_biblioteca(self):
        global biblioteca_instalada_fr
        if biblioteca_instalada_fr==False:
            self.controls[4].controls[1].controls[0].on_click=None
            self.controls[4].controls[1].controls[0].on_hover=None
            self.controls[4].controls[1].controls[0].bgcolor='red'
            self.controls[4].controls[1].controls[0].content.controls[0].opacity=0.5
            self.controls[4].controls[1].controls[0].content.controls[1].opacity=0.5
            
            self.controls[4].controls[3].controls[0].on_click=None
            self.controls[4].controls[3].controls[0].on_hover=None
            self.controls[4].controls[3].controls[0].bgcolor='red'
            self.controls[4].controls[3].controls[0].content.controls[0].opacity=0.5
            self.controls[4].controls[3].controls[0].content.controls[1].opacity=0.5
    
    def retornar(self,e):
        self.running=False
        self.master.content=self.master.list_view
        self.master.update()
    
    def buttonContainer(self,icon_name,name,func):
        return flet.Container(
            height=100,
            on_click=lambda e,func=func:self.selecionarFuncionalidade(e,func),
            animate=flet.animation.Animation(100),
            border_radius=10,
            on_hover=self.highlight,
            content=flet.Row(
                controls=[
                flet.Icon(name=icon_name,color='white',opacity=0.5),
                flet.Text(value=name,color='white',opacity=0.5)
                ]
            )
        )
    
    def highlight(self,e):
        if e.data=='true':
            e.control.content.controls[0].opacity=1
            e.control.content.controls[1].opacity=1
            e.control.bgcolor=flet.colors.with_opacity(0.3,'bluegrey')
        else:
            e.control.content.controls[0].opacity=0.5
            e.control.content.controls[1].opacity=0.5
            e.control.bgcolor='transparent'
        
        e.control.update()
        self.page.update()
    
    def selecionarFuncionalidade(self,e,nome):
        global path
        if nome=='imagem_face':
            path='codificacoes'
            self.desabilitarbotoes('first')
            self.picker.pick_files(file_type=flet.FilePickerFileType.CUSTOM,allowed_extensions=['png','jpg'])
        elif nome=='imagem_camera':
            self.desabilitarbotoes('first')
            self.foto_rec()
        elif nome=='imagem_perfil':
            self.desabilitarbotoes('second')
            path='_imagens/imagem_usuarios'
            self.picker.pick_files(file_type=flet.FilePickerFileType.CUSTOM,allowed_extensions=['png','jpg'])
        elif nome=='foto_perfil':
            self.desabilitarbotoes('second')
            self.foto_perfil()

    def desabilitarbotoes(self,wich):
        if wich=='first':
            self.controls[4].controls[1].controls[0].on_click=None
            self.controls[4].controls[1].controls[0].on_hover=None
            self.controls[4].controls[1].controls[0].bgcolor='transparent'
            self.controls[4].controls[1].controls[0].content.controls[0].opacity=0.5
            self.controls[4].controls[1].controls[0].content.controls[1].opacity=0.5
            self.controls[4].controls[1].controls[0].update()
            
            self.controls[4].controls[3].controls[0].on_click=None
            self.controls[4].controls[3].controls[0].on_hover=None
            self.controls[4].controls[3].controls[0].bgcolor='transparent'
            self.controls[4].controls[3].controls[0].content.controls[0].opacity=0.5
            self.controls[4].controls[3].controls[0].content.controls[1].opacity=0.5
            self.controls[4].controls[3].controls[0].update()
        elif wich=='second':
            self.controls[5].controls[1].controls[0].on_click=None
            self.controls[5].controls[1].controls[0].on_hover=None
            self.controls[5].controls[1].controls[0].bgcolor='transparent'
            self.controls[5].controls[1].controls[0].content.controls[0].opacity=0.5
            self.controls[5].controls[1].controls[0].content.controls[1].opacity=0.5
            self.controls[5].controls[1].controls[0].update()
            
            self.controls[5].controls[3].controls[0].on_click=None
            self.controls[5].controls[3].controls[0].on_hover=None
            self.controls[5].controls[3].controls[0].bgcolor='transparent'
            self.controls[5].controls[3].controls[0].content.controls[0].opacity=0.5
            self.controls[5].controls[3].controls[0].content.controls[1].opacity=0.5
            self.controls[5].controls[3].controls[0].update()
    
    def retornarbotoes(self,wich):
        if wich=='all':
            self.controls[4].controls[1].controls[0]=self.buttonContainer(flet.icons.IMAGE,'Escolher Face','imagem_face')
            self.controls[4].controls[1].update()
            
            self.controls[4].controls[3].controls[0]=self.buttonContainer(flet.icons.CAMERA_ALT_ROUNDED,'Tirar Foto','imagem_camera')
            self.controls[4].controls[3].update()
            
            self.controls[5].controls[1].controls[0]=self.buttonContainer(flet.icons.IMAGE,'Escolher foto','imagem_perfil')
            self.controls[5].controls[1].update()
            
            self.controls[5].controls[3].controls[0]=self.buttonContainer(flet.icons.CAMERA_ALT_ROUNDED,'Tirar foto','foto_perfil')
            self.controls[5].controls[3].update()
        elif wich=='first':
            self.controls[4].controls[1].controls[0]=self.buttonContainer(flet.icons.IMAGE,'Escolher Face','imagem_face')
            self.controls[4].controls[1].update()
            
            self.controls[4].controls[3].controls[0]=self.buttonContainer(flet.icons.CAMERA_ALT_ROUNDED,'Tirar Foto','imagem_camera')
            self.controls[4].controls[3].update()
        elif wich=='second':
            self.controls[5].controls[1].controls[0]=self.buttonContainer(flet.icons.IMAGE,'Escolher foto','imagem_perfil')
            self.controls[5].controls[1].update()
            
            self.controls[5].controls[3].controls[0]=self.buttonContainer(flet.icons.CAMERA_ALT_ROUNDED,'Tirar foto','foto_perfil')
            self.controls[5].controls[3].update()
            
    def on_result_file(self,e):
        global path
        imagem=e.files[0].path if e.files!=None else None
        if path=='codificacoes' and imagem!=None:
            imagem=cv.imread(imagem)
            faces=fr.face_locations(imagem)
            if len(faces)==1:
                if len(self.controls)==6:
                    self.retornarbotoes('second')
                x1,y1,x2,y2=faces[0]
                self.codificacao=fr.face_encodings(imagem)[0]
                cv.rectangle(imagem,(x1,y1),(x2,y2),(0,255,0),(2))
                _,imarr=cv.imencode('.png',imagem)
                imb64=base64.b64encode(imarr)
                self.espaco_imagem_rec.src_base64=imb64.decode()
                self.controls[4].controls[1].controls.append(flet.IconButton(flet.icons.REMOVE_CIRCLE_OUTLINE,icon_color='red',on_click=lambda e,index=(4,1):self.remover_imagem_rec(e,index)))
                self.controls[4].controls[1].update()
                self.linha_imagem_rec=flet.Row(
                    alignment=flet.MainAxisAlignment.SPACE_AROUND,
                    width=1000,
                    controls=[
                        flet.Text('Verifique se o quadrado verde está na face'),
                        self.espaco_imagem_rec
                    ]
                )
                self.controls.append(self.linha_imagem_rec)
                self.update()
            else:
                alerta=flet.AlertDialog(title=flet.Text('Imagem não permitida'))
                self.master.page.dialog=alerta
                alerta.open=True
                self.master.page.update()
                self.retornarbotoes('all')
        elif path=='_imagens/imagem_usuarios' and imagem!=None:
            self.controls[5].controls[1].controls.append(flet.IconButton(flet.icons.REMOVE_CIRCLE_OUTLINE,icon_color='red',on_click=lambda e,index=(5,1):self.remover_imagem_perfil(e,index)))
            self.controls[5].controls[1].update()
            self.espaco_imagem_perfil.src=imagem
            self.imagem=cv.imread(imagem,cv.IMREAD_UNCHANGED)
            self.linha_imagem_perfil=flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                width=1000,
                controls=[
                    flet.Text('Essa é a foto que vai aparecer quando você logar'),
                    self.espaco_imagem_perfil
                ]
            )
            self.controls.append(self.linha_imagem_perfil)
            self.update()
            if len(self.controls)==6:
                self.retornarbotoes('first')
        elif path=='codificacoes' and imagem==None:
            self.retornarbotoes('first')
        elif path=='_imagens/imagem_usuarios' and imagem==None:
            self.retornarbotoes('second')
    
    def salvar(self,e):
        nome=self.espaco_nome.value
        cargo=self.espaco_cargo.value
        senha=self.espaco_senha.value
        conn=sqlite3.connect('banco.db')
        c=conn.cursor()
        c.execute('SELECT nome FROM usuarios')
        nomes=c.fetchall()
        nomes_formatado=[]
        for i in nomes:
            nomes_formatado.append(i[0])
        if nome=='':
            alerta=flet.AlertDialog(title=flet.Text('Por favor preenchar o campo nome'))
            self.master.page.dialog=alerta
            alerta.open=True
            self.master.page.update()
        elif senha=='':
            alerta=flet.AlertDialog(title=flet.Text('Por favor preenchar o campo senha'))
            self.master.page.dialog=alerta
            alerta.open=True
            self.master.page.update()
        elif cargo==None:
            alerta=flet.AlertDialog(title=flet.Text('Por favor selecione um cargo'))
            self.master.page.dialog=alerta
            alerta.open=True
            self.master.page.update()
        elif nome in nomes_formatado:
            alerta=flet.AlertDialog(title=flet.Text('Nome já usado por outro usuário'))
            self.master.page.dialog=alerta
            alerta.open=True
            self.master.page.update()
        else:
            nome=nome.lower().replace(' ','')
            cargo=cargo.lower()
            imagem=self.imagem
            codificacao=self.codificacao
            if isinstance(imagem,np.ndarray):
                path=f'_imagens/imagem_usuarios/{nome}.png'
                cv.imwrite(path,imagem)
            if isinstance(codificacao,np.ndarray):
                open(f'codificacoes/{nome}.txt','w')
                with open(f'codificacoes/{nome}.txt','a') as arquivo:
                    for i in codificacao:
                        arquivo.write(f'\n{str(i)}')
            conn=sqlite3.connect('banco.db')
            c=conn.cursor()
            c.execute(
                """
                INSERT INTO usuarios VALUES (?,?,?)
                """,
                (nome,cargo,senha)
            )
            conn.commit()
            c.close()
            alerta=flet.AlertDialog(title=flet.Text('Colaborador adicionado'))
            self.master.page.dialog=alerta
            alerta.open=True
            self.master.page.update()
            self.reiniciar()
    
    def remover_imagem_rec(self,e,index):
        global path
        self.controls[index[0]].controls[index[1]].controls.pop()
        self.controls[index[0]].controls[index[1]].update()
        self.controls.pop(self.controls.index(self.linha_imagem_rec))
        self.update()
        path=None
        self.retornarbotoes('first')
        
    def foto_rec(self):
        self.running=True
        with open('camera_index.txt','r') as arquivo:
            index=int(arquivo.readlines()[0])
        camera=cv.VideoCapture(index,cv.CAP_DSHOW)
        camera.set(cv.CAP_PROP_FRAME_WIDTH,300)
        camera.set(cv.CAP_PROP_FRAME_HEIGHT,300)
        self.linha_imagem_rec=flet.Row(
            alignment=flet.MainAxisAlignment.SPACE_AROUND,
            width=1000,
            controls=[
                flet.Text('Verifique se o quadrado verde está na face'),
                self.espaco_imagem_rec,
                flet.ElevatedButton(text='Tirar Foto',on_click=self.tirarfoto)
            ]
        )
        self.controls.append(self.linha_imagem_rec)
        self.update()
        while self.running:
            _,frame=camera.read()
            copia_frame=frame
            face=fr.face_locations(frame)
            if len(face)==1:
                x1,y1,x2,y2=face[0]
                cv.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            _,imarr=cv.imencode('.png',frame)
            imb64=base64.b64encode(imarr)
            self.espaco_imagem_rec.src_base64=imb64.decode()
            self.linha_imagem_rec.update()
        camera.release()
        try:
            self.codificacao=fr.face_encodings(copia_frame)[0]
        except Exception:
            alerta=flet.AlertDialog(title=flet.Text('Impossível codificar imagem'))
            self.master.page.dialog=alerta
            alerta.open=True
            self.master.page.update()
            self.remover_imagem_rec('e',(4,3))
            
    def tirarfoto(self,e):
        self.running=False
        self.linha_imagem_rec.controls.pop()
        self.controls[4].controls[3].controls.append(flet.IconButton(flet.icons.REMOVE_CIRCLE_OUTLINE,icon_color='red',on_click=lambda e,index=(4,3):self.remover_imagem_rec(e,index)))
        self.controls[4].controls[3].update()
        if len(self.controls)==6:
            self.retornarbotoes('second')
        
    def tirarperfil(self,e):
        self.running=False
        self.linha_imagem_perfil.controls.pop()
        self.controls[5].controls[3].controls.append(flet.IconButton(flet.icons.REMOVE_CIRCLE_OUTLINE,icon_color='red',on_click=lambda e,index=(5,3):self.remover_imagem_perfil(e,index)))
        self.controls[5].controls[3].update()
        if len(self.controls)==6:
            self.retornarbotoes('first')
        self.imagem=self.espaco_imagem_perfil.src_base64
        self.imagem=base64.b64decode(self.imagem)
        self.imagem=np.frombuffer(self.imagem,np.uint8)
        self.imagem=cv.imdecode(self.imagem,cv.IMREAD_UNCHANGED)
        
    def remover_imagem_perfil(self,e,index):
        global path
        self.controls[index[0]].controls[index[1]].controls.pop()
        self.controls[index[0]].controls[index[1]].update()
        self.controls.pop(self.controls.index(self.linha_imagem_perfil))
        self.update()
        path=None
        self.retornarbotoes('second')

    def foto_perfil(self):
        self.running=True
        with open('camera_index.txt','r') as arquivo:
            index=int(arquivo.readlines()[0])
        camera=cv.VideoCapture(index,cv.CAP_DSHOW)
        camera.set(cv.CAP_PROP_FRAME_WIDTH,300)
        camera.set(cv.CAP_PROP_FRAME_HEIGHT,300)
        self.linha_imagem_perfil=flet.Row(
            alignment=flet.MainAxisAlignment.SPACE_AROUND,
            width=1000,
            controls=[
                flet.Text('Essa é a imagem que irá aparecer quando você logar'),
                self.espaco_imagem_perfil,
                flet.ElevatedButton(text='Tirar Foto',on_click=self.tirarperfil)
            ]
        )
        self.controls.append(self.linha_imagem_perfil)
        self.update()
        while self.running:
            _,frame=camera.read()
            _,imarr=cv.imencode('.png',frame)
            imb64=base64.b64encode(imarr)
            self.espaco_imagem_perfil.src_base64=imb64.decode()
            self.linha_imagem_perfil.update()
        camera.release()
        self.imagem=self.espaco_imagem_perfil.src_base64
        self.imagem=base64.b64decode(self.imagem)
        self.imagem=np.frombuffer(self.imagem,np.uint8)
        self.imagem=cv.imdecode(self.imagem,cv.IMREAD_UNCHANGED)

    def reiniciar(self):
        self.running=False
        self.codificacao=None
        self.scroll=flet.ScrollMode.ALWAYS
        self.imagem=None
        self.espaco_senha=flet.TextField(label='Senha',bgcolor='#e0e1dd',label_style=flet.TextStyle(color='#0D1B2A'),color='#0D1B2A')
        self.espaco_nome=flet.TextField(label='Nome',bgcolor='#e0e1dd',label_style=flet.TextStyle(color='#0D1B2A'),color='#0D1B2A')
        self.espaco_cargo=flet.Dropdown(label='Cargo',border_color='blue',options=[flet.dropdown.Option('Gerente'),flet.dropdown.Option('Vendedor')])
        self.espaco_imagem_rec=flet.Image(fit=flet.ImageFit.CONTAIN,width=300,height=300)
        self.espaco_imagem_perfil=flet.Image(fit=flet.ImageFit.CONTAIN,width=300,height=300)
        self.picker=flet.FilePicker(on_result=self.on_result_file)
        self.controls.clear()
        self.controls=[
            self.picker,
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
                width=1000,
                controls=[
                    flet.IconButton(flet.icons.ARROW_BACK_ROUNDED,on_click=self.retornar),
                    flet.IconButton(flet.icons.SAVE,on_click=self.salvar,icon_color='green',icon_size=60)
                ]
            ),
            flet.Divider(height=10,color='transparent'),
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                width=1000,
                controls=[
                    self.espaco_nome,
                    self.espaco_senha,
                    self.espaco_cargo
                ]
                ),
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                width=1000,
                controls=[
                    flet.Text('Imagem para reconhecimento facial (opcional):',weight='bold',size=20),
                    flet.Row(controls=[self.buttonContainer(flet.icons.IMAGE,'Escolher face','imagem_face')]),
                    flet.Text(value='OU'),
                    flet.Row(controls=[self.buttonContainer(flet.icons.CAMERA_ALT_ROUNDED,'Tirar Foto','imagem_camera')])
                ]
            ),
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                width=1000,
                controls=[
                    flet.Text('Imagem de perfil (opcional):',weight='bold',size=20),
                    flet.Row(controls=[self.buttonContainer(flet.icons.IMAGE,'Escolher foto','imagem_perfil')]),
                    flet.Text('OU'),
                    flet.Row(controls=[self.buttonContainer(flet.icons.CAMERA_ALT_ROUNDED,'Tirar foto','foto_perfil')])
                ]
            )
        ]
        self.verificar_biblioteca()
        self.update()

class EliminarColaborador(flet.Column):
    def __init__(self,master):
        super().__init__()
        self.master=master
        self.dicionario_usuarios={}
        self.espaco_codificacao=flet.TextField(bgcolor='#E0E1DD',color='#0D1B2A',label='Tem cod?',label_style=flet.TextStyle(color='#0D1B2A'),border_radius=10,read_only=True)
        self.espaco_nomes=flet.Dropdown(label='Funcionários',on_change=self.mudou_funcionario)
        self.espaco_imagem=flet.Image('_imagens\profile-user.png',fit=flet.ImageFit.CONTAIN,width=200,height=200,border_radius=100)
        self.montar_dicionario_usuarios()
        self.espaco_cargo=flet.TextField(bgcolor='#E0E1DD',color='#0D1B2A',label='Cargo',label_style=flet.TextStyle(color='#0D1B2A'),border_radius=10,read_only=True)
        self.controls=[
            flet.Row(
                controls=[
                    flet.IconButton(flet.icons.ARROW_BACK_ROUNDED,on_click=self.retornar)
                ]
            ),
            flet.Divider(height=20,color='transparent'),
            flet.Row(
                width=1000,
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    self.espaco_nomes,
                    self.espaco_cargo
                ]
            ),
            flet.Divider(height=20,color='transparent'),
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                width=1000,
                controls=[
                    self.espaco_imagem,
                    self.espaco_codificacao
                ]
            ),
            flet.Row(
                width=1000,
                alignment=flet.MainAxisAlignment.CENTER,
                controls=[
                    flet.ElevatedButton('Deletar Colaborador',bgcolor='red',color='white',on_click=self.elimiar_colaborador)
                ]
            )
        ]
    
    def elimiar_colaborador(self,e):
        if self.espaco_nomes.value==None:
            pass
        else:
            nome=self.espaco_nomes.value.lower()
            qtGerentes=0
            permitido=False
            for value in self.dicionario_usuarios.values():
                qtGerentes+=1 if value['cargo']=='gerente' else 0
            if self.dicionario_usuarios[nome]['cargo']=='gerente' and qtGerentes>1:
                permitido=True
            elif self.dicionario_usuarios[nome]['cargo']=='gerente' and qtGerentes==1:
                permitido=False
            elif self.dicionario_usuarios[nome]['cargo']=='vendedor':
                permitido=True
            
            if permitido==False:
                alerta=flet.AlertDialog(title=flet.Text('Tem que haver pelo menos um gerente'))
                self.master.page.dialog=alerta
                alerta.open=True
                self.master.page.update()
            else:
                conn=sqlite3.connect('banco.db')
                c=conn.cursor()
                c.execute('DELETE FROM usuarios WHERE nome=?',(nome,))
                conn.commit()
                c.close()
                if self.dicionario_usuarios[nome]['imagem']!=None:
                    os.remove(self.dicionario_usuarios[nome]['imagem'])
                if self.dicionario_usuarios[nome]['cod']==True:
                    os.remove(f'codificacoes/{nome}.txt')
                alerta=flet.AlertDialog(title=flet.Text(f'Colaborador {nome} apagado do sistema'))
                self.master.page.dialog=alerta
                alerta.open=True
                self.master.page.update()
                self.reiniciar()
    
    def reiniciar(self):
        self.dicionario_usuarios={}
        self.espaco_codificacao=flet.TextField(bgcolor='#E0E1DD',color='#0D1B2A',label='Tem cod?',label_style=flet.TextStyle(color='#0D1B2A'),border_radius=10,read_only=True)
        self.espaco_nomes=flet.Dropdown(label='Funcionários',on_change=self.mudou_funcionario)
        self.espaco_imagem=flet.Image('_imagens\profile-user.png',fit=flet.ImageFit.CONTAIN,width=200,height=200,border_radius=100)
        self.montar_dicionario_usuarios()
        self.espaco_cargo=flet.TextField(bgcolor='#E0E1DD',color='#0D1B2A',label='Cargo',label_style=flet.TextStyle(color='#0D1B2A'),border_radius=10,read_only=True)
        self.controls.clear()
        self.controls=[
            flet.Row(
                controls=[
                    flet.IconButton(flet.icons.ARROW_BACK_ROUNDED,on_click=self.retornar)
                ]
            ),
            flet.Divider(height=20,color='transparent'),
            flet.Row(
                width=1000,
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    self.espaco_nomes,
                    self.espaco_cargo
                ]
            ),
            flet.Divider(height=20,color='transparent'),
            flet.Row(
                alignment=flet.MainAxisAlignment.SPACE_AROUND,
                width=1000,
                controls=[
                    self.espaco_imagem,
                    self.espaco_codificacao
                ]
            ),
            flet.Row(
                width=1000,
                alignment=flet.MainAxisAlignment.CENTER,
                controls=[
                    flet.ElevatedButton('Deletar Colaborador',bgcolor='red',color='white',on_click=self.elimiar_colaborador)
                ]
            )
        ]
        self.update()
        
    def mudou_funcionario(self,e):
        funcionario=self.espaco_nomes.value.lower()
        self.espaco_cargo.value=self.dicionario_usuarios[funcionario]['cargo'].capitalize()
        self.espaco_cargo.update()
        if self.dicionario_usuarios[funcionario]['imagem']==None:
            self.espaco_imagem.src='_imagens\profile-user.png'
        else:
            self.espaco_imagem.src=self.dicionario_usuarios[funcionario]['imagem']
        self.espaco_imagem.update()
        if self.dicionario_usuarios[funcionario]['cod']==True:
            self.espaco_codificacao.bgcolor=flet.colors.with_opacity(0.5,'green')
            self.espaco_codificacao.value='TEM'
        else:
            self.espaco_codificacao.bgcolor=flet.colors.with_opacity(0.5,'red')
            self.espaco_codificacao.value='NÃO TEM'
        self.espaco_codificacao.update()
       
    def retornar(self,e):
        self.master.content=self.master.list_view
        self.master.update()
    
    def montar_dicionario_usuarios(self):
        conn=sqlite3.connect('banco.db')
        c=conn.cursor()
        c.execute('SELECT nome,cargo FROM usuarios')
        dados_usuarios=c.fetchall()
        imagens_usuarios=os.listdir('_imagens/imagem_usuarios')
        imagens_usuarios=list(map(lambda x:x.removesuffix('.png'),imagens_usuarios))
        codificacoes_usuarios=os.listdir('codificacoes')
        codificacoes_usuarios=list(map(lambda x:x.removesuffix('.txt'),codificacoes_usuarios))
        
        for i in range(len(dados_usuarios)):
            self.dicionario_usuarios[dados_usuarios[i][0]]={'cargo':dados_usuarios[i][1],'imagem':None}
            self.dicionario_usuarios[dados_usuarios[i][0]]['imagem']=f'_imagens/imagem_usuarios/{dados_usuarios[i][0]}.png' if dados_usuarios[i][0] in imagens_usuarios else None
            self.dicionario_usuarios[dados_usuarios[i][0]]['cod']=True if dados_usuarios[i][0] in codificacoes_usuarios else False
            
        for nome in self.dicionario_usuarios.keys():
            self.espaco_nomes.options.append(flet.dropdown.Option(nome))

class CameraOptions(flet.Column):
    def __init__(self,master):
        super().__init__()
        self.master=master
        self.index=0
        self.camera_ativa=False
        self.running=False
        self.radio_group=flet.RadioGroup(on_change=self.mudarcamera)
        self.espaco_camera=flet.Image(fit=flet.ImageFit.CONTAIN,width=300,height=300,src='_imagens\profile-user.png')
        self.linha_camera=flet.Row(width=1000,alignment=flet.MainAxisAlignment.CENTER,controls=[self.espaco_camera])
        self.criar_radio()
        self.controls=[
            flet.IconButton(icon=flet.icons.ARROW_BACK_ROUNDED,on_click=self.retornar),
            flet.Divider(height=20,color='transparent'),
            self.radio_group,
            self.linha_camera,
            flet.ElevatedButton('Salvar Configurações',color='green',on_click=self.salvar)
        ]
    
    def salvar(self,e):
        with open('camera_index.txt','w') as arquivo:
            arquivo.write(f'{self.index}')
        alerta=flet.AlertDialog(title=flet.Text('Salvo'))
        self.master.page.dialog=alerta
        alerta.open=True
        self.master.page.update()
    
    def mudarcamera(self,e):
        valor=int(e.control.value)
        self.index=valor
        if self.camera_ativa:
            self.pararcamera('e')
        self.iniciarcamera()
        
    def pararcamera(self,e):
        self.running=False
        time.sleep(0.5)
        self.linha_camera.controls.clear()
        self.espaco_camera=self.espaco_camera=flet.Image(fit=flet.ImageFit.CONTAIN,width=300,height=300,src='_imagens\profile-user.png')
        self.linha_camera.controls.append(self.espaco_camera)
        self.linha_camera.update()
        self.camera_ativa=False
    
    def iniciarcamera(self):
        self.camera_ativa=True
        self.linha_camera.controls.append(flet.ElevatedButton(text='Parar Camera',color='red',on_click=self.pararcamera))
        self.linha_camera.update()
        self.running=True
        camera=cv.VideoCapture(self.index,cv.CAP_DSHOW)
        camera.set(cv.CAP_PROP_FRAME_HEIGHT,300)
        camera.set(cv.CAP_PROP_FRAME_WIDTH,300)
        while self.running:
            _,frame=camera.read()
            _,im_arr=cv.imencode('.png',frame)
            imb64=base64.b64encode(im_arr)
            self.espaco_camera.src_base64=imb64.decode()
            self.espaco_camera.update()
    
    def retornar(self,e):
        self.running=False
        self.master.content=self.master.list_view
        self.master.update()
    
    def criar_radio(self):
        device_list=device.getDeviceList()
        content=flet.Column()
        for dev in range(0,len(device_list)):
            content.controls.append(flet.Radio(value=dev,label=device_list[dev][0]))
        self.radio_group.content=content