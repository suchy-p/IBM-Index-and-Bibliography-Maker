import re


def add_matcher_pattern():
    matcher = Matcher(secondary_nlp.vocab)

    pattern = [
        {"ENT_TYPE": "placeName"},
        {"ENT_TYPE": "date"}
    ]

    matcher.add("adress_ending_pattern", [pattern])

# func to add PERSON and processed page num to index
def add_person():
    for ent in doc.ents:

        if ent.label_ == "PERSON":

            # remove line breaking in text (Ro-\n bert)
            clean_index = remove_line_breaking(ent)

            # ent.lemma_ not working correctly for polish names; pl pipeline for handling declension issues
            doc_lemma = secondary_nlp(clean_index)

            # remove nums sometimes left from footnotes or footnote references
            tokens = [token for token in doc_lemma if
                      token.text.isnumeric() == False]

            # reverse list of tokens if contains more than just a surname
            if len(tokens) > 1 and (tokens[1].text == "." or tokens[
                -2].text == "."): tokens.insert(0, tokens.pop())

            # make lemmas
            surname = [token.lemma_ for token in tokens]

            # remove leading and trailing spaces, lefotver punctuations
            trimmed_surname = trimmer(surname)

            # add trimmed surname as key, current page as value in "index" dict
            index[trimmed_surname.title()].add(
                reader.get_page_number(current_page))

def add_to_bibliography(key, name):
    pattern = name
    monography = rf"{pattern}[,]\s\D+[,].+\d+"
    search = re.findall(monography, current_page.extract_text())
    for i in search:
        if i[0].isupper():
            item = trimmer_bibliogr(i)
            item2 = remove_line_breaking(item)
            #print("i")
            #print(i)
            bibliography.append(item2.replace(pattern, key))
            print(item2.replace(pattern, key))

# remove line breaking
def remove_line_breaking(item):
    no_line_breaks = item if type(item) is str else item.text
    remove = [" \xad ", " \xad\n", "\n", "\xa0"]

    for break_sign in remove:
        no_line_breaks = no_line_breaks.replace(break_sign, " ") if (
                break_sign == "\xa0") else no_line_breaks.replace(
            break_sign, "")

    return no_line_breaks

def trimmer_bibliography(i):
    # doc of given bibliohraphical address, both eng (doc1) and pl (doc2) pipelines
    # doc1 = primary_nlp(i)
    doc2 = secondary_nlp(i)

    # index of place and year of publication
    # eveything after this should be removed
    # [author, title, year and place of publication]
    place_and_year_index = int()
    # reference_text =

    matches = matcher(doc2)

    if len(matches) > 0:
        # get ending index of place and year of publication
        for match_id, start, end in matches:
            matched_span = doc2[start:end]
            place_and_year_index = matched_span.end

            # trimming bibliographical address, converting doc obj to str
            trimmed = doc2[0: place_and_year_index].text + "."
    else:
        # '\033[1m' + [...] + '\033[0m' spanning for bold text
        trimmed = doc2[
                  0::].text + '\033[1m' + "\t <<< \t check required" + '\033[0m'

    return trimmed

def trimmer_index(item):
    # remove leftover spaces or punctuation; sometmies there are leftovers from footnotes or footnote references

    # item is a list of lemmas, joining list items, removing leading and trailing spaces
    whitespace_trimmed = " ".join(item).strip()

    # removing "." and",", one more whitespace trimming in case there were any after punctuation
    punctuations_trimmed = whitespace_trimmed.lstrip("., ")

    # removing whitespace before "." after name initials [Smith J . => Smith J.; Smith A. J. => Smith A.J.]
    trimmed_item = punctuations_trimmed.replace(" .", ".").replace(". ", ".")

    return trimmed_item

def write_bibliography_output(bibliography):
    with open ("bibliography_output.doc","w", encoding="utf-8" ) as file:
        for item in sorted(set(bibliography)):
            file.write(item+"\n")

def write_index_output(index):
    with open ("index_output.doc","w", encoding="utf-8" ) as file:
        for key, subdict in sorted(index.items()):
            # pages for given person, set from "index" dict joined into string
            pages = ", ".join([str(value) for value in sorted(subdict)])
            # person + tabulator visually separating it from pages
            file.write(key+"\t")
            file.write(pages)
            file.write("\n")

if __name__ == '__main__':
    main()
