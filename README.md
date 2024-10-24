# Index and Bibliography Maker
## Overview
Index and Bibligraphy Maker (IBM in short) was created as an attempt to automate one of most time consuming and boring parts of publishing book in humanities.
Creating personal index can take anywhere from several days to over a week. Also bibliography is often neglected by authors (or can be real pain if you're writing), so the editor has to go through all footnotes to check, correct or even create one.
Goal of this app is to do both things for you using natural language processing. All you have to do is check output files for nlp model mistakes, radically reducing time required to do both things.
## Technologies
- Python 3.12
- PyPDF2 3.0.1
- spaCy 3.7.6
    * en_core_news_trf 3.7.3
    * pl_core_news_lg 3.7.0
## How does it work
For personal index each page of selected pdf file is analyzed by spaCy en_core_news_trf model in search for named entites labeled "PERSON". English model was chosen mainly because its much more versatile when it comes to surnames. It has no issues recognizing entities using names and surnames from many languages, while polish model mostly ignored non-polish surnames.

Found entity is then lemmatized by polish model, because english model isn't very good at managing polish declension. Meanwhile it's trimmed from leftover punctuation, linebreaking signs etc. and added as key to defaultdict with page as value. Sorted dict is written as doc file for output in selected pdf file directory.
>[!NOTE]
>Fun fact: Beacuse of usage of english model to detect entities, it actually is better for analyzing english text than polish.

Bibliography creation is based on index. Basically, surnames are searched for in pdf. When found, regex pattern is used to check if next to surname is a bibliographic address. Next it is trimmed down from any unwanted text. Saved as list, sorted is written as doc file for output in selected pdf file directory.
## How to handle it
IBM was made to be easy to use. You have only few buttons, none of them is usable when you are not allowed to. GUI was made with tkinter.
More important, you should check your output files, they will be in need of your attention. Aside from my mistakes or disputable choices, used models will make errors.

## Deployment
Basic idea was that you could run IBM on your office PC using exe file. Unfortunately, looks like PyInstaller (ver. 6.10.0) won't do. There are some issues with transformer based models, PyInstaller seems to ignore transformer files. As far as I know I wasn't only one who run on this problem and it still has to be solved. 

Nuitka (ver. 2.4.8) works fine. Command line:
```
python -m nuitka --enable-plugin=tk-inter --spacy-language-model=all --include-package=curated_transformers --include-package=spacy_curated_transformers --include-package=spacy_alignments --include-distribution-metadata=spacy --standalone main.py
```
## Known bugs
- Creating bibliography for larger files ends with End of Index Error: main.py line 88.
- Name reversing in index often doesn't work as intended.
- Clicking 'Create bibliography' after generating it for first time doesn't run from index 0 but last index + 1 and freezes.

## Upcoming changes
- Include selected file name in output doc.
- Add custom created indexes. Main idea is that you could load file with list of items you want indexed, for instance geographical locations, to create any index you need, in this case geographical index. If such list of items for indexation is created during editorial works, custom index could save a lot of work later.
- Rework bibliography search. Right now it's rather poorly optimised, looking for every surname on every page. I intend to use pages from index as guidelines where to look for what and see how that works out. 
