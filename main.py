from collections import defaultdict
import os
from threading import Thread
import tkinter as tk
from tkinter import filedialog as fd
import tkinter.ttk as ttk

from PyPDF2 import PdfReader
import spacy
from spacy.matcher import Matcher

import funcs


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('400x200')
        self.resizable(False, False)
        self.title('IBM')

        # primary nlp object, "trf" = eng pipeline with the best accuracy for searching for entities
        self.primary_nlp = spacy.load('en_core_web_trf')
        # secondary nlp object for lemmatization of entities; eng pipeline can't handle declension in pl
        self.secondary_nlp = spacy.load('pl_core_news_lg')
        # matcher for bibliography, more in 'create_bibliography'
        self.matcher = Matcher(self.secondary_nlp.vocab)

        # list for bibliography, later sorted for output
        self.bibliography = list()
        # index; defaultdict, ent.label == PERSON from doc as key, set of pages as default value
        self.index = defaultdict(set)

        # if index_ready == True bibliography can be made
        self.index_ready = False
        # num of analyzed page in reader object
        self.page_num = 0


    def create_index(self, file_path):

        reader = PdfReader(file_path)

        for page in reader.pages:

            current_page = reader.pages[self.page_num]
            doc = self.primary_nlp(current_page.extract_text())
            names_on_page = funcs.add_person(doc, self.secondary_nlp)

            for name in names_on_page:
                self.index[name].add(self.page_num+1)

            self.page_num += 1

        funcs.write_index_output(self.index)
        self.index_ready = True
        self.page_num = 0
        self.enable_buttons()
        view.lbl3.config(text='Index file saved in pdf directory')

    def create_bibliography(self, file_path) :

        index = self.index
        reader = PdfReader(file_path)

        # add search pattern for matcher; bibliographical address in polish system usually ends with place and year
        # of publication -> [...], Krakow 2006
        pattern = [
            {"ENT_TYPE": "placeName"},
            {"ENT_TYPE": "date"}
        ]

        self.matcher.add("address_ending_pattern", [pattern])

        for page in reader.pages:
            # indexed names (keys) are used to search for publications on each page
            for key in sorted(index.keys()):

                current_page = reader.pages[self.page_num]
                # split indexed name, use surname only for publications search
                surname = key.split()[0]
                self.bibliography.extend(funcs.add_to_bibliography
                                         (key, surname, current_page, self.secondary_nlp, self.matcher))
            self.page_num += 1

        funcs.write_bibliography_output(self.bibliography)
        view.lbl3.configure(text='Bibliography file saved in pdf directory')


    def disable_buttons(self):
        view.select_button.config(state='disabled')
        view.bibliography_button.config(state='disabled')
        view.index_button.config(state='disabled')


    def enable_buttons(self):
        view.select_button.config(state='enabled')
        view.bibliography_button.config(state='enabled')
        view.index_button.config(state='enabled')


    def get_file_path(self, label):
        file = fd.askopenfile(mode='r', filetypes=[('Pdf files','*.pdf')])
        file_path = os.path.abspath(file.name)
        os.chdir(os.path.dirname(file_path))
        view.lbl2.config(text=file_path, wraplength=355)
        view.index_button.configure(state='enabled')
        # disable bibliography_button as precaution in case of changing input pdf after creating index
        # or index and bibliography
        view.bibliography_button.configure(state='disabled')
        return file_path


    def thread1(self, func):
        t1 = Thread(target=self.index_run)
        t1.start()


    def index_run(self):
        view.lbl3.config(text='Creating personal index')
        self.disable_buttons()
        self.create_index(view.lbl2.cget('text'))


    def thread2(self, func):
        t2 = Thread(target=self.bibliography_run)
        t2.start()


    def bibliography_run(self):
        view.lbl3.config(text='Creating bibliography from personal index')
        self.disable_buttons()
        self.create_bibliography(view.lbl2.cget('text'))#self.index, view.lbl2.cget('text'), self.secondary_nlp)


class View:
    # tkinter view object
    def __init__(self):
        self.frame1 = tk.LabelFrame(width=355)
        self.lbl1 = tk.Label(text='Select pdf file')
        self.lbl2 = tk.Label(self.frame1, text='No file selected', anchor='center')
        self.lbl3 = tk.Label()
        self.output_info = tk.StringVar(self.lbl3)
        self.bibliography_button = ttk.Button(text='Create bibliography')
        self.index_button = ttk.Button(text='Create index')
        self.select_button = ttk.Button(text='Open file')


app = App()
view = View()

# pdf file selection
view.lbl1.grid(column=0, row=1, padx=20,pady=5)
view.select_button.grid(column=1, columnspan = 1, row=1, padx=10, pady=10)
view.select_button.bind('<Button-1>', app.get_file_path)
# display path of selected file
view.lbl2.pack()
view.frame1.grid(column=0, columnspan=2, row=2, rowspan=2, padx=10, pady=15, sticky='ew')

view.index_button.grid(column=0, row=4, pady=5)
view.index_button.bind('<Button-1>', app.thread1)

view.bibliography_button.grid(column=1, row=4, pady=5)
view.bibliography_button.bind('<Button-1>', app.thread2)

# output text messages
view.lbl3.grid(column=0, columnspan=2, row=5, pady=10)

# disable buttons before selecting pdf file
view.bibliography_button.config(state='disabled')
view.index_button.config(state='disabled')

# divide window into two equal columns
app.columnconfigure(0, weight=1)
app.columnconfigure(1, weight=1)


if __name__ == '__main__':
    app.mainloop()


