import flet
from produtos import ProductsView,SideBar
import sqlite3


dicionario_produtos={}
dicionario_carrinho={}

def atualizar(e):
    global dicionario_carrinho,dicionario_produtos
    index=e.control.selected_index
    tab=e.control.tabs[index]
    if index==0:
        search_bar=tab.content.controls[0].content
        search_bar.value=''
        search_bar.update()
        product_view=tab.content.controls[1]
        product_view.controls.clear()
        for key,value in dicionario_produtos.items():
            product_view.controls.append(ProductAddContainer(None,key,value['imagem'],value['quantidade'],value['preco'],master=product_view))
        product_view.update()
    else:
        product_view=tab.content.controls[0]
        product_view.controls.clear()
        for key,value in dicionario_carrinho.items():
            product_view.controls.append(ProductShowContainer(tab,key,value['imagem'],value['quantidade'],value['preco'],master=product_view))
        product_view.update()
        if len(dicionario_carrinho.keys())>0:
            qt=0
            totpreco=0
            for value in dicionario_carrinho.values():
                qt+=value['quantidade']
                totpreco+=eval(f"{value['quantidade']}*{value['preco']}")
            tab.content.controls[1].content.controls[0].controls[0].value=f"Quantidade de Itens:{qt}"
            tab.content.controls[1].content.controls[0].controls[0].update()
            tab.content.controls[1].content.controls[0].controls[1].value=f"Valor Total da Compra:R$ {totpreco}"
            tab.content.controls[1].content.controls[0].controls[1].update()
        else:
            tab.content.controls[1].content.controls[0].controls[0].value=f"Quantidade de Itens:"
            tab.content.controls[1].content.controls[0].controls[0].update()
            tab.content.controls[1].content.controls[0].controls[1].value=f"Valor Total da Compra:"
            tab.content.controls[1].content.controls[0].controls[1].update()
            
            
class CaixaController(flet.UserControl):
    global dicionario_produtos
    def __init__(self,page):
        super().__init__()
        self.page=page
        self.page.title='Caixa'
        self.product_view=ProductsView(page.window_width,page.window_height)
    
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
        for key,value in dicionario_produtos.items():
            self.product_view.controls.append(ProductAddContainer(self.page,key,value['imagem'],value['quantidade'],value['preco'],master=self.product_view))
        return flet.Row(
            controls=[
            SideBar(self.page.window_height,usuario,cargo),
            flet.Tabs(
                height=self.page.window_height-50,
                width=self.page.window_width-200,
                selected_index=0,
                animation_duration=300,
                tabs=[Tab1(self.product_view,self.page),Tab2(self.page)],
                on_change=atualizar
            )
            ]
        )
    

class Tab1(flet.Tab):
    global dicionario_produtos
    def __init__(self,productview,page):
        super().__init__()
        self.page=page
        self.text='Produtos'
        self.product_view=productview
        self.content=flet.Column(
            controls=[
            SearchBar(self.product_view),
            self.product_view
            ]
        )

class Tab2(flet.Tab):
    global dicionario_produtos,dicionario_carrinho
    def __init__(self,page):
        super().__init__()
        self.text='Carrinho'
        self.page=page
        self.qtText=flet.Text('Quantidade de Itens:',size=20)
        self.precoText=flet.Text('Valor Total da Compra:',size=20)
        self.product_view=ProductsView(self.page.window_width,self.page.window_height-130)
        self.content=flet.Column(
            controls=[
            self.product_view,
            flet.Container(
                width=self.page.window_width-150,
                height=100,
                bgcolor=flet.colors.with_opacity(0.5,'#0D1B2A'),
                border_radius=10,
                content=flet.Row(
                    alignment=flet.MainAxisAlignment.SPACE_AROUND,
                    controls=[
                        flet.Column(
                    alignment='center',
                    controls=[
                        self.qtText,
                        self.precoText
                    ]
                ),
                        flet.ElevatedButton(text='Finalizar Compra',on_click=self.finalizar)
                    ]
                )
                  )
            ]
        )
    def finalizar(self,e):
        if len(dicionario_carrinho.keys())>0:
            conn=sqlite3.connect('banco.db')
            c=conn.cursor()
            for key,value in dicionario_produtos.items():
                c.execute('UPDATE produtos SET quantidade=? WHERE nome=?',(value['quantidade'],key))
                conn.commit()
            c.close()
            self.product_view.controls.clear()
            self.product_view.update()
            self.content.controls[1].content.controls[0].controls[0].value='Quantidade de Itens:'
            self.content.controls[1].content.controls[0].controls[0].update()
            self.content.controls[1].content.controls[0].controls[1].value='Valor Total da Compra:'
            self.content.controls[1].content.controls[0].controls[1].update()
            alerta=flet.AlertDialog(title=flet.Text('Compra Finalizada'))
            self.page.dialog=alerta
            alerta.open=True
            self.page.update()
        
        
    

class ProductAddContainer(flet.Container):
    global dicionario_produtos,dicionario_carrinho
    def __init__(self,page,nome,imagem,quantidade,preco,readonly=False,master=None):
        super().__init__()
        self.page=page
        self.nome=nome
        self.readonly=readonly
        self.master=master
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
                flet.Row(width=170,alignment=flet.MainAxisAlignment.SPACE_AROUND,controls=[flet.TextField(label='QT',width=90,height=55),flet.IconButton(flet.icons.ADD_CIRCLE_OUTLINE_OUTLINED,icon_color='green',on_click=lambda e,nome=nome:self.adicionar_ao_carrinho(e,nome,self))])
            ]
        )
    def adicionarImagem(self):
        if self.imagem==None:
            return flet.Image('_imagens\produtos\image_not_found.jpg',width=230,height=130,border_radius=10,fit=flet.ImageFit.CONTAIN)
        else:
            return flet.Image(self.imagem,width=230,height=130,border_radius=10,fit=flet.ImageFit.CONTAIN)
    
    def adicionar_ao_carrinho(self,e,nome,master):
        texto=master.content.controls[4].controls[0]
        if texto.value.isdigit():
            valor=int(texto.value)
            quantidade_estoque=dicionario_produtos[nome]['quantidade']
            if valor<=quantidade_estoque:
                if nome not in dicionario_carrinho.keys():
                    dicionario_carrinho[nome]=dicionario_produtos[nome].copy()
                    dicionario_carrinho[nome]['quantidade']=valor
                else:
                    dicionario_carrinho[nome]['quantidade']+=valor
                dicionario_produtos[nome]['quantidade']-=valor
                
                master.content.controls[2].value=f"Quantidade:{dicionario_produtos[nome]['quantidade']}"
                master.content.controls[4].controls[0].value=''
                master.update()
            else:
                alerta=flet.AlertDialog(title=flet.Text('Por favor, insira um valor válido'))
                self.page.dialog=alerta
                alerta.open=True
                self.page.update()
        else:
            alerta=flet.AlertDialog(title=flet.Text('Por favor, insira um valor válido'))
            self.page.dialog=alerta
            alerta.open=True
            self.page.update()

class SearchBar(flet.Container):
    global dicionario_produtos
    def __init__(self,master):
        super().__init__()
        self.master=master
        self.padding=flet.padding.only(top=20)
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
                    self.master.controls.append(ProductAddContainer(nome,imagem,quantidade,preco,master=self.master))
                self.master.update()
        else:
            self.master.controls.clear()
            for key,value in dicionario_produtos.items():
                self.master.controls.append(ProductAddContainer(key,value['imagem'],value['quantidade'],value['preco'],master=self.master))
            self.master.update()

class ProductShowContainer(flet.Container):
    global dicionario_produtos,dicionario_carrinho
    def __init__(self,tab,nome,imagem,quantidade,preco,readonly=False,master=None):
        super().__init__()
        self.tab=tab
        self.nome=nome
        self.readonly=readonly
        self.master=master
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
                flet.Text(value=f'TOT: R${preco*quantidade}',size=15,width=230,text_align='center'),
                flet.Row(width=170,alignment=flet.MainAxisAlignment.SPACE_AROUND,controls=[flet.IconButton(flet.icons.REMOVE_CIRCLE_OUTLINE,icon_color='red',on_click=lambda e,nome=nome:self.remover_do_carrinho(e,nome))])
            ]
        )
    def adicionarImagem(self):
        if self.imagem==None:
            return flet.Image('_imagens\produtos\image_not_found.jpg',width=230,height=130,border_radius=10,fit=flet.ImageFit.CONTAIN)
        else:
            return flet.Image(self.imagem,width=230,height=130,border_radius=10,fit=flet.ImageFit.CONTAIN)
    
    def remover_do_carrinho(self,e,nome):
        valor=dicionario_carrinho[nome]['quantidade']
        dicionario_produtos[nome]['quantidade']+=valor
        dicionario_carrinho.pop(nome)
        controles=self.master.controls
        nomes=[]
        for controle in controles:
            nomes.append(controle.nome)
        for i in range(0,len(nomes)):
            if nomes[i]==nome:
                self.master.controls.pop(i)
                self.master.update()
                break
        if len(dicionario_carrinho.keys())>0:
            qt=0
            totpreco=0
            for value in dicionario_carrinho.values():
                qt+=value['quantidade']
                totpreco+=eval(f"{value['quantidade']}*{value['preco']}")
            self.tab.content.controls[1].content.controls[0].controls[0].value=f"Quantidade de Itens:{qt}"
            self.tab.content.controls[1].content.controls[0].controls[0].update()
            self.tab.content.controls[1].content.controls[0].controls[1].value=f"Valor Total da Compra:R$ {totpreco}"
            self.tab.content.controls[1].content.controls[0].controls[1].update()
        else:
            self.tab.content.controls[1].content.controls[0].controls[0].value=f"Quantidade de Itens:"
            self.tab.content.controls[1].content.controls[0].controls[0].update()
            self.tab.content.controls[1].content.controls[0].controls[1].value=f"Valor Total da Compra:"
            self.tab.content.controls[1].content.controls[0].controls[1].update()