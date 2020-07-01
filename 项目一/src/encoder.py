import tkinter.messagebox as messagebox
from tkinter import ttk
from tkinter import *
import tkinter.filedialog
import tool
import CRC

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('编码器')
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        #设置界面宽度为530，高度为365像素，并且基于屏幕居中
        width = 530
        height = 365
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.master.geometry(size)
        self.pack()
        self.create_widgets()


    def create_widgets(self):
        Label(self, text="").grid(row=0, pady=5, columnspan=3)
        self.interval = StringVar()
        Label(self, text="时间限制(s)：").grid(row=3, sticky='W', pady=5)
        Entry(self, textvariable=self.interval, width=9).grid(row=3, column=1, sticky='W')
        
        
        
        

#        self.keyheight = StringVar()
 #       Label(self, text="照片的高(pixel)：").grid(row=5, sticky='W', pady=5)
 #       Entry(self, textvariable=self.keyheight, width=40).grid(row=5, column=1, sticky='W')


 #       self.keywidth = StringVar()
 #       Label(self, text="照片的宽(pixel)：").grid(row=6, sticky='W', pady=5)
  #      Entry(self, textvariable=self.keywidth, width=40).grid(row=6, column=1, sticky='W')

        def xz():
            filename = tkinter.filedialog.askopenfilename()
            if filename != '':
                Label(self, text=filename).grid(row=7, column=1, sticky='w')
                self.filename_in=filename
 #       def xz2():
#            filename = tkinter.filedialog.asksaveasfilename()
  #          if filename != '':
  #              Label(self, text=filename).grid(row=8, column=1, sticky='w')
  #              self.filename_out=filename

        

        Label(self, text="输入文件夹：").grid(row=7, column=0, sticky='W', pady=5)
        Button(self, text=" ... ", command=xz).grid(row=7, column=2, sticky='W', padx=2)


#       Label(self, text="输出文件夹：").grid(row=8, column=0, sticky='W', pady=5)
 #       Button(self, text=" ... ", command=xz2).grid(row=8, column=2, sticky='W', padx=2)
        Button(self,text='确定',width=5,height=2, command=self.quit).grid(row=14,column=1,sticky='W',padx=100)
def ENCODE():
    app = Application()
    app.mainloop()
    x=tool.encoder(app.filename_in,int(app.interval.get()))
    return x
