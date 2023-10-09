import flet
from produtos import SideBar,ProductContainer
import shutil
import os
import sqlite3

class Adicionar(flet.Container):
    def __init__(self,master):
        super().__init__()
        self.master=master
        self.product_container=ProductContainer(nome='Produto',imagem='_imagens\produtos\image_not_found.jpg',quantidade=1,preco=1,readonly=True)
        self.width=950
        self.campo_nome=flet.TextField(label='Nome',bgcolor='#e0e1dd',label_style=flet.TextStyle(color='#0D1B2A'),color='#0D1B2A',on_change=self.preencher_container)
        self.campo_quantidade=flet.TextField(label='Quantidade',bgcolor='#e0e1dd',label_style=flet.TextStyle(color='#0D1B2A'),color='#0D1B2A',width=150,on_change=self.preencher_container)
        self.linha_imagem=flet.Row(controls=[self.buttonContainer(flet.icons.IMAGE,'Escolha uma imagem')])
        self.campo_preco=flet.TextField(label='Preço',bgcolor='#e0e1dd',label_style=flet.TextStyle(color='#0D1B2A'),color='#0D1B2A',width=150,prefix_text='R$',prefix_style=flet.TextStyle(color='black',size=15),on_change=self.preencher_container)
        self.height=580
        self.bgcolor='#778DA9'
        self.border_radius=10
        self.picker=flet.FilePicker(on_result=self.on_pick_file)
        self.content=flet.Row(
            controls=[
                flet.Column(
                    width=460,
                    height=580,
                    controls=[
                        flet.Divider(height=20,color='transparent'),
                        flet.Text(value='Adicionar ao Estoque',weight='bold',size=20),
                        self.campo_nome,
                        flet.Divider(height=20,color='transparent'),
                        self.picker,
                        self.linha_imagem,
                        flet.Divider(height=20,color='transparent'),
                        flet.Row(controls=[self.campo_quantidade,self.campo_preco]),
                        flet.ElevatedButton(text='Adicionar',bgcolor='#0d1b2a',on_click=self.adicionar_dados)
                    ]
                ),
                flet.VerticalDivider(color='white',width=20),
                flet.Column(
                    width=460,
                    height=580,
                    controls=[
                        self.product_container
                    ],
                    alignment='center',
                    horizontal_alignment='center'
                )
            ]
        )
        self.master.page.overlay.clear()
        self.master.page.overlay.append(self.picker)
    
    def on_pick_file(self,e):
        path_original=e.files[0].path if e.files!=None else None
        self.nome=e.files[0].name if e.files!=None else None
        self.path_destino=r'_imagens/produtos'
        arquivos_existentes=os.listdir('_imagens/produtos')
        if e.files!=None:
            if e.files[0].name not in arquivos_existentes:
                shutil.copy(path_original,self.path_destino)
                self.product_container.content.controls[1].src=f'{self.path_destino}/{self.nome}'
                self.imagemnaofinalizada=f'{self.path_destino}/{self.nome}'
                self.linha_imagem.controls.append(flet.IconButton(icon=flet.icons.REMOVE_CIRCLE_OUTLINE,icon_color='red',on_click=self.remove_image))
                self.linha_imagem.update()
                self.product_container.update()
            else:
                alerta=flet.AlertDialog(title=flet.Text('Imagen já relacionada a um produto'))
                self.page.dialog=alerta
                alerta.open=True
                self.update()
                self.page.update()
    
    def preencher_container(self,e):
        if e.control.label=='Nome':
            self.product_container.content.controls[0].value=e.control.value
        elif e.control.label=='Quantidade':
            self.product_container.content.controls[2].value=f'Quantidade:{e.control.value}'
        elif e.control.label=='Preço':
            self.product_container.content.controls[3].value=f'Preço:R${e.control.value}'
        self.update()
        self.page.update()

    def buttonContainer(self,icon_name,name):
        return flet.Container(
            width=200,
            height=50,
            on_click=lambda _:self.picker.pick_files(file_type=flet.FilePickerFileType.CUSTOM,allowed_extensions=['png']),
            animate=flet.animation.Animation(100),
            border_radius=10,
            on_hover=self.highlight,
            content=flet.Row(
                controls=[
                flet.Icon(name=icon_name,color='white',opacity=1),
                flet.Text(value=name,color='white',opacity=1)
                ]
            )
        )
    
    def highlight(self,e):
        if e.data=='true':
            e.control.bgcolor=flet.colors.with_opacity(0.5,'bluegrey')
        else:
            e.control.bgcolor='transparent'
        
        e.control.update()
        self.page.update()
    
    def remove_image(self,e):
        os.remove(os.path.join(self.path_destino,self.nome))
        self.product_container.content.controls[1].src='_imagens\produtos\image_not_found.jpg'
        self.product_container.update()
        self.linha_imagem.controls.pop()
        self.linha_imagem.update()
        self.page.update()
    
    def adicionar_dados(self,e):
        def verificar_float(numero):
            try:
                float(numero)
                return True
            except ValueError:
                return False
                
        
        if self.campo_nome.value=='':
            alerta=flet.AlertDialog(title=flet.Text('Insira o nome do produto'))
            self.page.dialog=alerta
            alerta.open=True
            self.campo_nome.border_color='red'
            self.update()
            self.page.update()
        elif self.campo_quantidade.value=='':
            alerta=flet.AlertDialog(title=flet.Text('Insira a quantidade do produto'))
            self.page.dialog=alerta
            alerta.open=True
            self.campo_quantidade.border_color='red'
            self.update()
            self.page.update()
        elif self.campo_preco.value=='':
            alerta=flet.AlertDialog(title=flet.Text('Insira o preço do produto'))
            self.page.dialog=alerta
            alerta.open=True
            self.campo_preco.border_color='red'
            self.update()
            self.page.update()
        else:
            nome=self.campo_nome.value
            imagem=self.product_container.content.controls[1].src
            quantidade=self.campo_quantidade.value
            preco=self.campo_preco.value
            if quantidade.isdigit()==False:
                alerta=flet.AlertDialog(title=flet.Text('Insira uma quantidade válida'))
                self.page.dialog=alerta
                alerta.open=True
                self.campo_quantidade.border_color='red'
                self.update()
                self.page.update()
            elif verificar_float(preco)==False:
                alerta=flet.AlertDialog(title=flet.Text('Insira um preço válido'))
                self.page.dialog=alerta
                alerta.open=True
                self.campo_preco.border_color='red'
                self.update()
                self.page.update() 
            else:
                conn=sqlite3.connect('banco.db')
                c=conn.cursor()
                c.execute('SELECT * FROM produtos WHERE nome=?',(nome,))
                retorno=c.fetchall()
                if len(retorno)==0:
                    c.execute("""
                            INSERT INTO produtos (nome,imagem,quantidade,preco)
                            VALUES (?,?,?,?)
                            """,(nome,imagem,quantidade,preco))
                    conn.commit()
                    c.close()
                    alerta=flet.AlertDialog(title=flet.Text('Produto adicionado'))
                    self.page.dialog=alerta
                    alerta.open=True
                    self.update()
                    self.page.update() 
                    self.reiniciar()
                    self.imagemnaofinalizada=None
                else:
                    alerta=flet.AlertDialog(title=flet.Text('Produto já registrado'))
                    self.page.dialog=alerta
                    alerta.open=True
                    self.update()
                    self.page.update() 
                    c.close()

    def reiniciar(self):
        self.campo_nome.value=''
        self.campo_nome.border_color='blue'
        self.campo_preco.value=''
        self.campo_preco.border_color='blue'
        self.campo_quantidade.value=''
        self.campo_quantidade.border_color='blue'
        self.linha_imagem.controls.clear()
        self.linha_imagem.controls.append(self.buttonContainer(flet.icons.IMAGE,'Escolha uma imagem'))
        self.product_container=ProductContainer(nome='Produto',imagem='_imagens\produtos\image_not_found.jpg',quantidade=1,preco=1,readonly=True)
        self.content.controls[2].controls[0]=self.product_container
        self.update()
        self.page.update()
        
        
class AdicionarControl(flet.UserControl):
    def __init__(self,page:flet.Page):
        super().__init__()
        self.page=page
        self.page.title='Adicionar'
    
    def build(self):
        with open('temp.txt','r') as arquivo:
            linhas=arquivo.readlines()
        linhas=list(map(lambda x:x.removesuffix('\n'),linhas))
        usuario=linhas[0]
        cargo=linhas[1]
        return flet.Row(
            controls=[
                SideBar(self.page.window_height,usuario,cargo),
                Adicionar(self),
            ]
        )