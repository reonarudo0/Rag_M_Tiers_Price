from multiprocessing import Process, Manager, freeze_support
from tkinter.ttk import Progressbar,Checkbutton
from ctypes import c_char_p
import tkinter as tk
import pandas as pd
import requests

def GetPriceContent(finalUrl,headers, sharedContent):
    sharedContent.value = (requests.get(finalUrl, headers=headers)).content

class TierPrices:

    def __init__(self, master):
        self.master = master
        self.master.title('Ragnarok M Tier Prices')
        self.master.geometry('500x600')
        self.master.resizable(width=False,height=False)

        self.url = 'https://api-global.poporing.life/get_latest_price/'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

        #self.siteUrl = 'https://www.romwiki.net/items/953/tights'

        self.canvas = tk.Canvas(self.master,width=490,height=540)
        self.canvas.place(x=5, y=30)

        self.urlLabel = tk.Label(self.master, text='Digite a URL:')
        self.urlLabel.place(x=5,y=5)
        self.urlEntry = tk.Entry(self.master)
        self.urlEntry.place(x=80,y=5)
        self.searchBtn = tk.Button(self.master, text='Procurar', command=self.GetPrice)
        self.searchBtn.place(x=210,y=2)

        self.scroll_y = tk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)

        self.frame = tk.Frame(self.canvas)

        self.pBar = Progressbar(self.master, mode='determinate', len=150)
        self.pBar.place(x=270,y=5)

        self.row = 0
        self.savedName,self.savedPrice = [''],['']
        self.savedData = pd.DataFrame(data={'Nome': self.savedName, 'Preço': self.savedPrice})

    def PrintDataFrame(self,data,place):
        row,col,width = self.row,0,0

        for element in data.iloc[:, col]:
            var = tk.BooleanVar()
            var.set(True)
            self.stateList.append(var)

            checkBtn = Checkbutton(place, var=self.stateList[-1], onvalue=True, offvalue=False)
            checkBtn.grid(row=row+1, column=0)

            row = row + 1
        row,col = self.row,0

        while (col != len(data.columns)):
            for element in data.iloc[:, col]:
                if (width == 0):
                    width = len(data.columns[col])
                if (len(str(element)) > width):
                    width = len(str(element))
            dataFrameTitles = tk.Label(place, text=data.columns[col], font='Arial 10 bold', relief=tk.RIDGE,width=width + 1,bg='#D3D3D3')
            dataFrameTitles.grid(row=row, column=col+1, sticky='w,e')
            row = row + 1
            color = 'White'
            for element in data.iloc[:, col]:
                dataFrameLabel = tk.Label(place, text=element, font='Arial 10', relief=tk.RIDGE, width=width + 1,bg=color)
                dataFrameLabel.grid(row=row, column=col+1, sticky='w,e')
                row = row + 1
                if (color == 'White'):
                    color = '#D3D3D3'
                else:
                    color = 'White'
            row,width = self.row,0
            col = col + 1
        self.row = self.row + len(data.index) + 1

    def GetPrice(self):
        self.searchBtn['state'] = 'disabled'
        self.pBar.start()
        self.frame.destroy()
        self.stateList, self.tierEnd, self.listTiersLabel, self.total   = [], [], [], []
        self.numItens = 0

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window(0, 0, anchor='nw', window=self.frame)

        siteUrl = self.urlEntry.get()
        try:
            content = (requests.get(siteUrl)).content
        except:
            exceptionLabel = tk.Label(self.frame, text='URL invalida.' , font='Arial 13')
            exceptionLabel.pack()
            self.pBar.stop()
            return None

        sep = str(content).split('rowspan="2">')

        total, error = [], [],

        self.pBar['maximum'] = 1
        for x in range(len(sep) - 1):
            self.pBar['value'] = (x/(len(sep)-1))

            self.master.update()
            tierTotal,valUnd, names, qtd = [],[],[],[]

            tempNames = sep[x + 1].split('</div><span>')
            tempQtd = sep[x + 1].split('class="mat-qty">&nbsp; x')

            for n in range(len(tempNames) - 1):
                name = tempNames[n + 1].split('</span>')[0]
                if ('[' in name):
                    name = name.split('[')
                    name = name[0] + name[1][0] + 's'
                if ('-' in name):
                    name = name.split('-')
                    name = ' '.join(name)
                if('.' in name):
                    name = name.split('.')
                    name = ''.join(name)
                if ('\'' in name):
                    name = name.split('\'')
                    name = name[0][:-1] + name[1]
                names.append(name)

            for n in range(len(tempQtd) - 1):
                qtd.append(tempQtd[n + 1].split('</span>')[0])

            data = pd.DataFrame(data={'Nome': names, 'Quantidade': qtd})

            for name in data['Nome']:
                if (len(self.savedData[self.savedData['Nome'].str.contains(name)]) == 1):

                    val = int(self.savedData[self.savedData['Nome'] == name].iloc[0, 1])
                    tot = val * int(data[data['Nome'] == name].iloc[0, 1])

                elif (name == 'Zeny'):
                    tot = int(data[data['Nome'] == name].iloc[0, 1])
                    val = tot

                else:
                    itemName = (name.lower()).split(' ')
                    itemName = '_'.join(itemName)

                    finalUrl = self.url + itemName

                    try:
                        sharedContent.value = ''
                        process = Process(target=GetPriceContent, args=(finalUrl,self.headers,sharedContent))
                        process.start()
                        while(sharedContent.value == ''):
                            self.master.update()
                        ultPrice = sharedContent.value
                        val = str(ultPrice).split('"price":')[1].split(',')[0]
                    except:
                        val = 'null'

                    if (val == 'null'):
                        error.append(str(name))
                        val = '0'

                    self.savedData.loc[-1] = [name, val]
                    self.savedData.reset_index(inplace=True)
                    self.savedData.drop('index', axis=1, inplace=True)

                    tot = int(val) * int(data[data['Nome'] == name].iloc[0, 1])

                valUnd.append(val)
                tierTotal.append(tot)
                self.total.append(tot)

            self.tierEnd.append((self.numItens, self.numItens + len(tierTotal)))
            self.numItens = self.numItens + len(tierTotal)

            data['Valor und'] = valUnd

            tierLabel = tk.Label(self.frame, text='Tier '+str(x + 1), fg='black', font='Arial 13 bold')
            tierLabel.grid(row=self.row, column=1, sticky='w')

            self.row = self.row+1

            self.PrintDataFrame(data,self.frame)

            tierTotalLabel = tk.Label(self.frame, text='Total: {:,}'.format(sum(tierTotal)), fg='red', font='Arial 13 bold')
            tierTotalLabel.grid(row=self.row,column=1, sticky='w')
            self.listTiersLabel.append(tierTotalLabel)
            self.row = self.row+1

        self.finalTotal = tk.Label(self.frame, text='Total Final: {:,}'.format(sum(self.total)), fg='red', font='Arial 13 bold')
        self.finalTotal.grid(row=self.row,column=1, sticky='w')
        self.row = self.row + 1

        refreshBtn = tk.Button(self.frame, text='Atualizar Preços', command=self.RefreshPrice)
        refreshBtn.grid(row=self.row,column=1, sticky='w')

        self.row = self.row + 1
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'), yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(fill='y', side='right')
        self.searchBtn['state'] = 'normal'
        self.pBar.stop()

        if(len(error)>0):
            errorText ='Não foi possivel encontrar preço de: \n'+str(', '.join(error))+'\nOs seus valores foram colocados como 0.'
            erroWin = tk.Toplevel()
            erroWin.title('Erro')
            erroLabel = tk.Label(erroWin, text=errorText, font='Arial 13')
            erroLabel.pack()

    def RefreshPrice(self):
        totalResult = 0
        for x in range(len(self.tierEnd)):
            tierResult = 0
            for y in range(self.tierEnd[x][0],self.tierEnd[x][1]):
                if(self.stateList[y].get()):
                    tierResult =  tierResult + self.total[y]

            self.listTiersLabel[x]['text'] = 'Total: {:,}'.format(tierResult)
            totalResult = totalResult + tierResult
        self.finalTotal['text'] = 'Total Final: {:,}'.format(totalResult)


if __name__ == '__main__':
    freeze_support()
    manager = Manager()
    sharedContent = manager.Value(c_char_p,'')
    root = tk.Tk()
    app = TierPrices(root)
    root.mainloop()