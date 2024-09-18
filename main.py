from collections import defaultdict
import os
import re
from threading import Event, Thread
import tkinter as tk
from tkinter import filedialog as fd
import tkinter.ttk as ttk

from PyPDF2 import PdfReader
import spacy
from spacy.matcher import Matcher

import funcs


# reader object from given pdf
#reader = PdfReader('C:\\Users\\YaTeż\\Downloads\\BP61-A3-Les.pdf')

# primary nlp object,
# "trf" = eng pipeline with highest accuracy for searching for entities
primary_nlp = spacy.load('en_core_web_trf')               #load("en_core_web_trf"))

# secondary nlp object,
# for lemmatization of entities
# eng pipeline can't handle declension in pl
secondary_nlp = spacy.load('pl_core_news_lg')

# index; defaultdict, ent.label == PERSON from doc as key,
# set of pages as default value


# if index_ready == True bibliography can be made
index_ready = False

# list for bibliography, later sorted for output
bibliography = list()

# tkinter object
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('400x200')
        self.resizable(False, False)
        self.title('IBM')
        self.page_num = 0
        self.index = defaultdict(set)

    def create_index(self, file_path):

        print(file_path)
        reader = PdfReader(file_path)

        for page in reader.pages:
            view.lbl3.config(text=f'Indexing page: '
                                  f'{self.page_num + 1}')
            current_page = reader.pages[self.page_num]
            doc = primary_nlp(current_page.extract_text())
            funcs.add_person(doc, secondary_nlp)

            self.page_num += 1

        funcs.write_index_output(self.index)
        index_ready = True
        self.page_num = 0
        view.lbl3.config(text='Index file saved in pdf directory')

    def create_bibliography(self, index):

        if index_ready == False:
            self.create_index()
            self.create_bibliography()
        else:
            funcs.add_matcher_pattern()

            for key in sorted(index.keys()):
                surname = key.split()[0]
                funcs.add_to_bibliography(key, surname)

        funcs.write_bibliography_output(bibliography)
        view.lbl3.config(text='Bibliography file saved in pdf directory')

    def get_file_path(self, label):
        file = fd.askopenfile(mode='r', filetypes=[('Pdf files','*.pdf')])
        file_path = os.path.abspath(file.name)
        os.chdir(os.path.dirname(file_path))
        view.lbl2.config(text=file_path)
        index_ready = False

        return file_path

    def thread1(self, func):
        t1 = Thread(target=self.create_index(view.lbl2.cget('text')))
        t1.start()

    def thread2(self, func):
        t2 = Thread(target=self.create_bibliography)
        t2.start()

class View:
    # tkinter view object
    def __init__(self):
        self.lbl1 = tk.Label(text='Select pdf file')
        self.lbl2 = tk.Label(text='')
        self.lbl3 = tk.Label(text='')

        self.bibliography_button = ttk.Button(text='Create bibliography')
        self.cancel_button = ttk.Button(text='Cancel')
        self.index_button = ttk.Button(text='Create index')
        self.select_button = ttk.Button(text='Open file')


app = App()
view = View()

view.lbl1.grid(column=0, row=1, padx=20,pady=5)
view.select_button.grid(column=1, row=1, padx=10, pady=10)
view.select_button.bind('<Button-1>', app.get_file_path)
view.lbl2.grid(column=0, columnspan=4, row=2, padx=10, pady=10)
view.index_button.grid(column=0, row=3, pady=5)
view.index_button.bind('<Button-1>', app.thread1)
view.bibliography_button.grid(column=1, row=3, pady=5)
view.bibliography_button.bind('<Button-1>', app.thread2)
view.lbl3.grid(column=0, columnspan=3, row=4, pady=5)
#view.cancel_button.grid(column=2, row=3, pady=5)
#view.cancel_button.bind('<Button-1>', app.cancel)


if __name__ == '__main__':
    app.mainloop()

