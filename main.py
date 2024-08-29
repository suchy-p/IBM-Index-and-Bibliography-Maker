from collections import defaultdict
import re

from PyPDF2 import PdfReader
import spacy
from spacy.matcher import Matcher

import funcs


# reader object from given pdf
reader = PdfReader('C:\\Users\\YaTeż\\Downloads\\BP61-A3-Les.pdf')

# primary nlp object,
# "trf" = eng pipeline with highest accuracy for searching for entities
primary_nlp = spacy.load("en_core_web_trf")

# secondary nlp object,
# for lemmatization of entities
# eng pipeline can't handle declension in pl
secondary_nlp = spacy.load("pl_core_news_lg")

# index; defaultdict, ent.label == PERSON from doc as key,
# set of pages as default value
index = defaultdict(set)