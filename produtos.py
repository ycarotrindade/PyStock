
import flet
import sqlite3
import os

dicionario_produtos={}


class ProductUser(flet.UserControl):
    global dicionario_produtos
    def __init__(self,page:flet.Page):
        super().__init__()
        self.page=page
        self.page.title='Estoque'
        self.product_view=ProductsView(self.page.window_width,self.page.window_height)
        self.produtos_indices=[]
        self.search=SearchBar(self.product_view)
        
    def build(self):
        with open('temp.txt','r') as arquivo:
            linhas=arquivo.readlines()

        linhas=list(map(lambda x:x.removesuffix('\n'),linhas))
        usuario=linhas[0]
        cargo=linhas[1]
        conn=sqlite3.connect('banco.db')
        c=conn.cursor()
        c.execute("SELECT * FROM produtos")
        produtos=c.fetchall()
        c.close()
        for produto in produtos:
            dicionario_produtos[produto[0]]={'imagem':produto[1],'quantidade':produto[2],'preco':produto[3]}
        for key,val in dicionario_produtos.items():
            self.product_view.controls.append(ProductContainer(key,val['imagem'],val['quantidade'],val['preco'],master=self.product_view))
        return flet.Row(controls=[SideBar(self.page.window_height,usuario,cargo),flet.Column(controls=[self.search,self.product_view])])
        

class SearchBar(flet.Container):
    global dicionario_produtos
    def __init__(self,master):
        super().__init__()
        self.master=master
        self.content=flet.TextField(
            width=1000,
            height=40,
            label='Nome do produto',
            on_change=self.search
            )
    
    def search(self,e):
        valor=e.control.value
        produtos_comparados=[]
        if valor!='':
            for key in dicionario_produtos.keys():
                if key.find(valor)!=-1:
                    produtos_comparados.append(key)
            if produtos_comparados!=[]:
                self.master.controls.clear()
                for produto in produtos_comparados:
                    nome=produto
                    imagem=dicionario_produtos[nome]['imagem']
                    quantidade=dicionario_produtos[nome]['quantidade']
                    preco=dicionario_produtos[nome]['preco']
                    self.master.controls.append(ProductContainer(nome,imagem,quantidade,preco,master=self.master))
                self.master.update()
        else:
            self.master.controls.clear()
            for key,value in dicionario_produtos.items():
                self.master.controls.append(ProductContainer(key,value['imagem'],value['quantidade'],value['preco'],master=self.master))
            self.master.update()
           
class ProductContainer(flet.Container):
    global dicionario_produtos
    def __init__(self,nome,imagem,quantidade,preco,readonly=False,master=None):
        super().__init__()
        self.nome=nome
        self.readonly=readonly
        self.master=master
        self.on_hover=self.mostrarlixeira
        self.imagem=imagem
        self.bgcolor='#0d1b2a'
        self.alignment=flet.alignment.center
        self.border_radius=10
        self.width=200
        self.height=300
        self.content=flet.Column(
            controls=[
                flet.Text(value=nome,weight='bold',size=20,text_align='center',width=230),
                self.adicionarImagem(),
                flet.Text(value=f'Quantidade:{quantidade}',size=15,width=230,text_align='center'),
                flet.Text(value=f'Preço: R${preco}',size=15,width=230,text_align='center'),
                flet.Row(width=135,controls=[flet.IconButton(flet.icons.DELETE,icon_color='red',opacity=0,on_click=lambda e,nome=nome:self.apagar_produto(e,nome))],alignment='end')
            ]
        )
    
    def adicionarImagem(self):
        if self.imagem==None:
            return flet.Image('_imagens\produtos\image_not_found.jpg',width=230,height=130,border_radius=10,fit=flet.ImageFit.CONTAIN)
        else:
            return flet.Image(self.imagem,width=230,height=130,border_radius=10,fit=flet.ImageFit.CONTAIN)
    
    def mostrarlixeira(self,e):
        if e.data=='true':
            e.control.content.controls[4].controls[0].opacity=1
            e.control.update()
        else:
            e.control.content.controls[4].controls[0].opacity=0
            e.control.update()
    
    def apagar_produto(self,e,nome):
        if self.readonly==False:
            path_imagem=dicionario_produtos[nome]['imagem']
            conn=sqlite3.connect('banco.db')
            c=conn.cursor()
            c.execute('DELETE FROM produtos WHERE nome=?',(nome,))
            conn.commit()
            c.close()
            os.remove(path_imagem)
            dicionario_produtos.pop(nome)
            controles=self.master.controls
            nomes=[]
            for controle in controles:
                nomes.append(controle.nome)
            for i in range(0,len(nomes)):
                if nomes[i]==nome:
                    self.master.controls.pop(i)
                    self.master.update()
                    break
                    
        
        
class ProductsView(flet.GridView):
    def __init__(self,width,height):
        super().__init__()
        self.runs_count=4
        self.spacing=5
        self.child_aspect_ratio=0.8
        self.run_spacing=5
        self.height=height-100
        self.width=width-150
        self.padding=flet.padding.all(30)
        

class SideBar(flet.Container):
    def __init__(self,height,nome,posicao):
        super().__init__()
        self.iniciais=nome[:2]
        self.nome=nome
        self.posicao=posicao
        self.width=200
        self.height=height
        self.bgcolor='#0d1b2a'
        self.border_radius=flet.border_radius.only(top_right=10,bottom_right=10)
        self.offset=flet.Offset(-0.1,0)
        self.animate=flet.animation.Animation(1000)
        self.padding=flet.padding.only(left=15)
        self.user_image=flet.Image(width=100,height=100,fit=flet.ImageFit.FILL,border_radius=100)
        lista_de_nomes=os.listdir('_imagens/imagem_usuarios')
        imagem='_imagens/profile-user.png'
        for i in lista_de_nomes:
            retorno=i.find(self.nome)
            if retorno!=-1:
                imagem=f'_imagens/imagem_usuarios/{i}'
        self.user_image.src=imagem
        self.content=flet.Column(
            controls=[
            flet.Row(
                controls=[
                    self.user_image,
                    flet.Column(
                        controls=[
                            flet.Text(value=self.iniciais,weight='bold',size=20,color='#E0E1DD'),
                            flet.Text(value=self.posicao,size=15,opacity=0.5,color='#E0E1DD')
                        ]
                    )
                ]
            ),
            flet.Divider(height=10,color='transparent'),
            flet.Row(controls=[self.buttonContainer(flet.icons.SHELVES,'estoque')]),
            flet.Row(controls=[self.buttonContainer(flet.icons.ADD_CIRCLE,'adicionar')]),
            flet.Row(controls=[self.buttonContainer(flet.icons.SHOPPING_CART,'caixa')]),
            flet.Row(controls=[self.buttonContainer(flet.icons.BUILD_ROUNDED,'ajustes')])
            ]
        )
    def buttonContainer(self,icon_name,name):
        return flet.Container(
            on_click=self.mudarjanela,
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
    
    def mudarjanela(self,e):
        with open('temp.txt','r') as arquivo:
            cargo=arquivo.readlines()[1]
        pagina_atual=self.page.route
        pagina_destino=f'/{e.control.content.controls[1].value}'
        if pagina_atual!=pagina_destino and cargo=='gerente':
            self.page.go(pagina_destino)
        elif pagina_atual!=pagina_destino and cargo=='vendedor':
            alerta=flet.AlertDialog(title=flet.Text('Você não tem permissão para acessar essa aba'))
            self.page.dialog=alerta
            alerta.open=True
            self.page.update()