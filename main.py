from collections import defaultdict
import os
from threading import Thread
import tkinter as tk
from tkinter import filedialog as fd
import tkinter.ttk as ttk
from tkinter.constants import CENTER

from PyPDF2 import PdfReader
import spacy
from click import command
from spacy.matcher import Matcher
from typer.cli import state

import funcs


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('400x225')
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
        view.main_lbl3.config(text='Index file saved in pdf directory')

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
        self.enable_buttons()
        view.main_lbl3.configure(text='Bibliography file saved in pdf directory')


    def disable_buttons(self):
        view.bibliography_button.config(state='disabled')
        view.index_button.config(state='disabled')
        view.select_button.config(state='disabled')
        view.tab_control.tab(1, state='disabled')


    def enable_buttons(self):
        view.bibliography_button.config(state='normal')
        view.index_button.config(state='normal')
        view.select_button.config(state='normal')
        view.tab_control.tab(1, state='normal')


    def get_file_path(self):#, label):
        file = fd.askopenfile(mode='r', filetypes=[('Pdf files','*.pdf')])
        file_path = os.path.abspath(file.name)
        os.chdir(os.path.dirname(file_path))
        view.main_lbl2.config(text=file_path, wraplength=355)
        view.index_button.configure(state='enabled')
        # disable bibliography_button as precaution in case of changing input pdf after creating index
        # or index and bibliography
        view.bibliography_button.configure(state='disabled')
        return file_path


    def thread1(self):#, func):
        t1 = Thread(target=self.index_run)
        t1.start()


    def index_run(self):
        view.main_lbl3.config(text='Creating personal index')
        self.disable_buttons()
        self.create_index(view.main_lbl2.cget('text'))


    def thread2(self):#, func):
        t2 = Thread(target=self.bibliography_run)
        t2.start()


    def bibliography_run(self):
        view.main_lbl3.config(text='Creating bibliography from personal index')
        self.disable_buttons()
        self.create_bibliography(view.main_lbl2.cget('text'))


class View:
    # tkinter view object
    def __init__(self):
        self.tab_control = ttk.Notebook(app)
        self.main_tab = ttk.Frame(self.tab_control)

        #self.main_frame = tk.Frame(self.main_tab)
        #self.custom_frame = tk.Frame(self.custom_tab)
        self.main_frame1 = tk.LabelFrame(self.main_tab, width=355)

        self.main_lbl1 = tk.Label(self.main_tab, text='Select pdf file')
        self.main_lbl2 = tk.Label(self.main_frame1, text='No file selected', anchor='center')
        self.main_lbl3 = tk.Label(self.main_tab)
        self.main_output_info = tk.StringVar(self.main_lbl3)
        self.bibliography_button = ttk.Button(self.main_tab,text='Create bibliography', command=app.thread2)
        self.index_button = ttk.Button(self.main_tab, text='Create index', command=app.thread1)
        self.select_button = ttk.Button(self.main_tab, text='Open file', command=app.get_file_path)

        # tab for creating custom indexes
        self.custom_tab = ttk.Frame(self.tab_control)
        self.custom_output_info = tk.Label(self.custom_tab, text='Creating custom indexes\n\n'
                                                                 'Currently under construction')



app = App()
view = View()

# pdf file selection
view.main_lbl1.grid(column=0, row=1, padx=20, pady=5)
view.select_button.grid(column=1, columnspan = 1, row=1, padx=10, pady=10)
#view.select_button.bind('<Button-1>', app.get_file_path)
# display path of selected file
view.main_lbl2.pack()
view.main_frame1.grid(column=0, columnspan=2, row=2, rowspan=2, padx=10, pady=15, sticky='ew')

view.index_button.grid(column=0, row=4, pady=5)
#view.index_button.bind('<Button-1>', app.thread1)

view.bibliography_button.grid(column=1, row=4, pady=5)
#view.bibliography_button.bind('<Button-1>', app.thread2)

# output text messages
view.main_lbl3.grid(column=0, columnspan=2, row=5, pady=10)

# disable buttons before selecting pdf file
view.bibliography_button.config(state='disabled')
view.index_button.config(state='disabled')

# divide main_tab into two equal columns
view.main_tab.columnconfigure(0, weight=1)
view.main_tab.columnconfigure(1, weight=1)

# custom_tab
view.custom_output_info.pack(anchor=CENTER, pady=65)

view.tab_control.add(view.main_tab, text='Main')
view.tab_control.add(view.custom_tab, text='Custom')
view.tab_control.pack(expand=1, fill='both')


if __name__ == '__main__':
    app.mainloop()


