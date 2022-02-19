import tkinter as tk
from tkinter import messagebox

from ..Tkinter_Addins.Custom_Text import CustomText


def autoscroll(s_bar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        s_bar.grid_remove()
    else:
        s_bar.grid()
    s_bar.set(first, last)


def message_boxes(type_msg, title, msg):
    """ Method used to show different kinds of messages """
    answer = ""
    if type_msg == "info":
        messagebox.showinfo(title=title, message=msg)
    elif type_msg == "warning":
        messagebox.showwarning(title=title, message=msg)
    elif type_msg == "error":
        messagebox.showerror(title=title, message=msg)
    elif type_msg == "askokcancel":
        answer = messagebox.askokcancel(title=title, message=msg)
    elif type_msg == "askquestion":
        answer = messagebox.askquestion(title=title, message=msg)
    elif type_msg == "askyesno":
        answer = messagebox.askyesno(title=title, message=msg)
    return answer


def read_help():
    win = tk.Toplevel()
    win.title("Ajuda")
    about = """
    No ecrã de boas vindas existe a possibilidade de definir novos utilizadores, com 2 níveis diferentes de permissões: 
    "Utilizador" ou "Administrador". O segundo nível permite ao utilizador aceitar ou rejeitar possíveis alterações de  
    preço que existam no momento da leitura das faturas e respectivos produtos. Pode-se ainda, alterar a palavra-passe
    de um utilizador. 
    
    Passando-se o ecrã de boas vindas, a ferramenta está dividida em três sub-janelas (enumeradas da esquerda para a
     direita): \n
        1- Tabelas que têm como objectivo o auxílio da gestão das faturas a serem lidas. A tabela superior apresenta
        as faturas abertas no ecosistema da ferramenta. A tabela a meio contém as faturas que já foram lidas e
        "convertidas" pelo leitor. A tabela inferior revela as faturas que já foram validadas pelo utilizador.
        Por fim, note-se que este painel pode ser escondido por forma a disponibilizar uma maior área de trabalho.
        
        2- Sub-janela que pretende mostrar, numa primeira instância, a fatura sem marcações. Assim que as faturas
        são lidas, passa a ser apresentada a fatura com rectângulos que demarcam a localização da informação e que
        possibilitam a correspondência com as entradas na sub-janela mais à direita.
        
        Existe uma barra vertical que torna possível a definição por parte do utilizador da divisão do espaço entre
        as sub-janelas 2 e 3.
        
        3- Sub-janela que contém a mais relevante zona de trabalho. É nesta janela que é seleccionado o fornecedor e 
        respectivo template a utilizar na leitura das faturas. Aquando da selecção de determinado fornecedor, são 
        apresentados os campos que vão ser lidos, de forma tentativa, na fatura. Tal como referido no ponto 2, as
        cores associadas a cada rectângulo de entrada irão ser utilizadas para estabelecer uma ligação com os campos
        lidos na fatura. Se existir uma tabela no template do fornecedor poderão ser utilizados as diferentes
        funcionalidades expectáveis na gestão de uma tabela (adicionar/remover linhas, mover células (drag & drop),
        etc.) Inicialmente colapsado é providenciado um quadro onde se apresentam algumas verificações feitas em 
        tempo real das leituras feitas pela ferramenta, ou das alterações executadas pelo utilizador. Por último, 
        existe um conjunto de botões que tencionam facilitar a navegação dentro da ferramenta.
        
    Funcionalidades da versão 1.0 da ferramenta:
        \u2022 Permite fazer undo-redo das alterações feitas pelo utilizador aos campos preenchidos aquando da
         leitura da fatura.
        \u2022 Navegar entre as diferentes faturas lidas através dos botões de "avançar e "recuar. 
        \u2022 Permite navegar de forma mais rápida entre as faturas lidas/validadas, utilizando um duplo click com
        a tecla do lado esquerdo do rato, sobre a fatura que se pretende abrir. 
        \u2022 Aproximar, afastar ou re-dimensionar a imagem de modo a ficar dentro dos limites da sub-janela #2.
        \u2022 Apagar a fatura dos registos da ferramenta.
        \u2022 Carregar os resultados originais de leitura de uma determinada fatura.
        
    Importa também referir algumas limitações da versão 1.0 da ferramenta:
        \u2022 As faturas têm de ser todas do mesmo fornecedor de cada vez que são lidas.
        \u2022 Alguma dificuldade na gestão de números isolados no momento da leitura das faturas
        \u2022 Sensibilidade baixa para com documentos que não se apresentem nas condições de preservação ideais, i.e.
        papel direito e sem estar rodado, com bom constraste nos campos de leitura, idealmente a preto e branco, etc.
        
    Se tiver problemas, por favor contacte por email os seus responsáveis.
    """
    # about = re.sub("\n\s*", "\n", about)  # remove leading whitespace from each line
    win.rowconfigure(0, weight=1)
    win.columnconfigure((0, 1), weight=1)
    t = CustomText(win, wrap="word", width=100, borderwidth=0, font=("Verdana", 11))
    t.tag_configure("blue", foreground="blue")
    t.grid(row=0, column=0, sticky="nsew")
    t.insert(tk.END, about)
    scroll = tk.Scrollbar(win)
    t.configure(yscrollcommand=scroll.set)
    scroll.config(command=t.yview)
    scroll.grid(row=0, column=1, sticky="ns")
    t.HighlightPattern("^.*? - ", "blue")
    close_btn = tk.Button(win, text='Fechar', font=("Verdana", 10), command=win.destroy)
    close_btn.grid(row=1, column=0, columnspan=2, pady=3)
