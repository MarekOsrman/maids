import tkinter as tk
from tkinter import filedialog
from tkinter import *
import test1


class MAIDS_Canvas(test1.Maiden):

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


        frame2 = Frame(self.master)
        frame2.pack(fill = X)

        run_button = tk.Button(frame2, text="RUN", width=40, height=3, command=self.running)
        run_button.pack(fill=X, padx=10, pady=10)

        outFrame = Frame(self.master)
        outFrame.pack(fill=X)

        self.outText = Text(outFrame, height=10)
        self.outText.pack(fill=X)

        tk.mainloop()



    def path_init(self):
        PATH = filedialog.askdirectory()
        self.initialized_path.delete(0, END)
        self.initialized_path.insert(0, PATH)


    def running(self):
        path = self.initialized_path.get()
        if path == "":
            """TODO - show some message to initialize the path"""
            pass
        else:
            self.maid = test1.Maiden(path)
            self.maid.handler_run()
            self.outText.insert(END, "Artists: " + self.maid.get_artists() + "\n")


MC = MAIDS_Canvas()