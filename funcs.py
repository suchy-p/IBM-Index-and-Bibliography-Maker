import re

import PyPDF2
import spacy
from pygments.lexer import default
from spacy.matcher import Matcher
from spacy.pipeline.dep_parser import defaultdict
from spacy.tokens import Span


# func to add PERSON and processed page num to index
def add_person(doc: spacy.tokens.Doc, secondary_nlp: spacy.Language) -> list:
    name_list = list()
    for ent in doc.ents:

        if ent.label_ == "PERSON":

            clean_index = remove_line_breaking(ent)

            # ent.lemma_ not working correctly for polish names; pl pipeline for handling declension issues
            doc_lemma = secondary_nlp(clean_index)

            # remove nums sometimes left from footnotes or footnote references
            tokens = [token for token in doc_lemma if
                      token.text.isnumeric() == False]

            # reverse list of tokens if contains more than just a surname (Stanislaw Lem -> Lem Stanislaw)
            if len(tokens) > 1 and (tokens[1].text == "." or tokens[
                -2].text == "."): tokens.insert(0, tokens.pop())

            # create lemmas
            surname = [token.lemma_ for token in tokens]

            # remove leading and trailing spaces, leftover punctuation
            trimmed_surname = trimmer_index(surname)

            name_list.append(trimmed_surname.title())

    return name_list

def add_to_bibliography(
        key: str, surname: str, current_page: PyPDF2.PageObject,
        secondary_nlp: spacy.Language, matcher: spacy.matcher.Matcher) -> list:

    matcher = matcher
    pattern = surname
    # regex for: surname, title etc.
    publication_regex = rf"{pattern}[,]\s\D+[,].+\d+"
    search = re.findall(publication_regex, current_page.extract_text())
    secondary_nlp = secondary_nlp

    bibliography_from_current_page = list()

    for found_publication in search:
        # probability check if found_publication starts with surname
        if found_publication[0].isupper():
            trimmed_publication = trimmer_bibliography(found_publication, secondary_nlp, matcher)
            formatted_publication = remove_line_breaking(trimmed_publication)
            # replace surname with key from index: 'Lem, Solaris...' -> 'Lem Stanislaw, Solaris...'

            bibliography_from_current_page.append(formatted_publication.replace(pattern, key))

    return bibliography_from_current_page

def remove_line_breaking(item: str | spacy.tokens.Span) -> str:
    # remove line breaking in text (Ro-\n bert)
    # used in index and bibliography
    no_line_breaks = item if type(item) is str else item.text
    remove = [" \xad ", " \xad\n", "\n", "\xa0"]

    for break_sign in remove:
        no_line_breaks = no_line_breaks.replace(break_sign, " ") if (break_sign == "\xa0") \
            else no_line_breaks.replace(break_sign, "")

    return no_line_breaks

def trimmer_bibliography(item: str, secondary_nlp: spacy.Language, matcher: spacy.matcher.Matcher) -> str:

    # doc of given bibliographical address, pl pipeline
    doc = secondary_nlp(item)
    matches = matcher(doc)

    if len(matches) > 0:
        # get ending index of place and year of publication
        for match_id, start, end in matches:
            matched_span = doc[start:end]
            place_and_year_index = matched_span.end

            # trimming bibliographical address, converting doc obj to str
            trimmed = doc[0: place_and_year_index].text + "."
    else:
        # '\033[1m' + [...] + '\033[0m' spanning for bold text
        trimmed = doc[0::].text + '\033[1m' + '\t <<< \t check required' + '\033[0m'

    return trimmed

def trimmer_index(item: list[str]) -> str:
    # remove leftover spaces or punctuation; sometimes there are leftovers from footnotes or footnote references
    # item is a list of lemmas, joining list items, removing leading and trailing spaces
    whitespace_trimmed = " ".join(item).strip()
    # removing "." and",", one more whitespace trimming in case there were any after punctuation
    punctuations_trimmed = whitespace_trimmed.lstrip("., ")
    # removing whitespace before "." after name initials [Smith J . => Smith J.; Smith A. J. => Smith A.J.]
    trimmed_item = punctuations_trimmed.replace(" .", ".").replace(". ", ".")

    return trimmed_item


def write_bibliography_output(bibliography: list[str]):
    output = sorted(set(bibliography))
    #with open ("bibliography_output.doc","w", encoding="utf-8" ) as file:
    with open("bibliography_output.txt", "w", encoding="utf-8") as file:
        for item in output:
            file.write(item+"\n")


def write_index_output(index: defaultdict[str|set]):
    with open("index_output.txt", "w", encoding="utf-8") as file:
    #with open ("index_output.doc","w", encoding="utf-8" ) as file:
        for key, subdict in sorted(index.items()):
            # pages for given person, set from "index" dict joined into string
            pages = ", ".join([str(value) for value in sorted(subdict)])
            # person + tabulator visually separating it from pages
            file.write(key+"\t")
            file.write(pages)
            file.write("\n")


if __name__ == '__main__':
    app.mainloop()
