import tkinter as tk
from tkinter import filedialog
from tkinter import *



class MAIDS_Canvas:

    def __init__(self):
        self.master = tk.Tk()
        self.master.title("MAIDS")

        wframe = Frame(self.master)
        wframe.pack(fill=X)


        wel = tk.Label(wframe, text= "WELCOME TO MAIDS !", background="black", foreground="green", font='helvetica 14 bold')
        wel.pack(fill=X)
        welcome = tk.Text(wframe)


        frame = Frame(self.master)
        frame.pack(fill=X)


        lbl = tk.Label(frame, text = "Selected directory: ")
        lbl.pack(side=LEFT, padx = 10, pady=10)

        path_button = tk.Button(frame, text="Select dir", width=20, command=self.path_init)
        path_button.pack(side=RIGHT, padx=10, pady=10)

        self.initialized_path = tk.Entry(frame)
        self.initialized_path.pack(fill=X, padx=10, pady=10)

        PATH = self.initialized_path.get()
        print(PATH)
        tk.mainloop()



    def path_init(self):
        PATH = filedialog.askdirectory()
        self.initialized_path.delete(0, END)
        self.initialized_path.insert(0, PATH)





MC = MAIDS_Canvas()