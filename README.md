# PyStock

Uma aplicação de controle de estoque e frente de caixa para MEIs

## Pré-requisitos
- Python 3
- Biblioteca Flet
- Biblioteca Numpy
- Biblioteca OpenCv

## Opcionais
- Biblioteca Face-Recognition
- Biblioteca python-capture-device-list

## Instalação Obrigatórias
1. Clone esse repositório para sua máquina
2. Instale as bibliotecas necessárias
```bash
pip install opencv-python flet
```

## Instalação Opcionais
1. Para instalar a bilbioteca face-recognition eu recomendo assitir a esse vídeo: https://youtu.be/h4yCzcIMOug?si=KwNkCOrK0G3euSOI
2. No entanto você pode acessar a página GitHub do projeto em: https://github.com/ageitgey/face_recognition
3. Para instalar a biblioteca python-capture-device-list você deve acessar a página GitHub: https://github.com/yushulx/python-capture-device-list
4. Clone o repositório GitHub da página
5. Instale a biblioteca necessária
```bash
pip install scikit-build
```
6. Siga as instruções em "How to Build the CPython Extension"
7. Instale a biblioteca pelo PyPi
```bash
pip install windows-capture-device-list
```
8. Mova a pasta "device" para o projeto

## Features
1. Controle de Estoque
2. Frente de Caixa
3. Reconhecimento Facial
4. Opção de adicionar diversos colaboradores (vendedores ou gerentes)

## Uso
1. Rode a aplicação app.py
2. logue como "root", a senha é "mudar123"
3. Você pode adicionar colaboradores em "Ajustes", lembre-se que tem de haver pelo menos um gerente no banco de dados
4. Você pode pressionar "ESC" para sair do programa
