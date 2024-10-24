# AUTOGENERATED! DO NOT EDIT! File to edit: ../name_surname_join_from_dataset.ipynb.
# may be useful later for fine-tuning fo indexes, exported here just in case

# %% auto 0
__all__ = ['female_names', 'male_names', 'surnames', 'two_names_females', 'two_names_males', 'random_males', 'create_two_names',
           'random_name_surname']

# %% ../name_surname_join_from_dataset.ipynb 2
import random

# %% ../name_surname_join_from_dataset.ipynb 3
female_names = list(open('C:\\Users\\Patryk\\Downloads\\archive\\polish_female_firstnames.txt', 'r', encoding='utf-8'))

# %% ../name_surname_join_from_dataset.ipynb 4
male_names = list(open('C:\\Users\\Patryk\\Downloads\\archive\\polish_male_firstnames.txt', 'r', encoding='utf-8'))

# %% ../name_surname_join_from_dataset.ipynb 5
surnames = list(open('C:\\Users\\Patryk\\Downloads\\archive\\polish_surnames.txt', 'r', encoding='utf-8'))

# %% ../name_surname_join_from_dataset.ipynb 6
two_names_females = list()

# %% ../name_surname_join_from_dataset.ipynb 7
two_names_males = list()

# %% ../name_surname_join_from_dataset.ipynb 9
def create_two_names(first_names, two_names):
    temp_names = list()
    for name in first_names[:len(first_names)//2]:
        temp_names.append(name.replace('\n',' ')) if len(temp_names) < 2 else two_names.append(temp_names.pop(0) + temp_names.pop())    

# %% ../name_surname_join_from_dataset.ipynb 17
def random_name_surname (names, surnames, randomized):
    random.shuffle(surnames)
    trimmed_names = [name.replace('\n', ' ') for name in names]
    randomized = zip(trimmed_names, surnames)
    return randomized

# %% ../name_surname_join_from_dataset.ipynb 20
# example of creating list
random_males = [name + surname for name, surname in random_name_surname(male_names, surnames, random_males)]
