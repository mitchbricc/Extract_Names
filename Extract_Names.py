import fitz  # PyMuPDF
import spacy
import re
import tkinter as tk
from tkinter import filedialog

def select_pdf_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf")],
        title="Select a PDF file"
    )
    return file_path

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def decompose_name(name):
    title_pattern = r"^(Mr\.|Mrs\.|Ms\.|Dr\.)"
    number_pattern = r"((M*)?(D{0,3})?(C{0,3})?(L{0,3})?(X{0,3})?(V{0,3})?(I{0,3})?)"
    roman_numeral_pattern = number_pattern+"?"+number_pattern+"?"
    suffix_pattern = r"(Jr\.|Sr\.|" + roman_numeral_pattern + r")$"
    
    title = re.match(title_pattern, name)
    if title:
        title = title.group(0)
        name = name[len(title):].strip()
    else:
        title = None
    
    suffix = re.search(suffix_pattern, name)
    if suffix:
        suffix = suffix.group(0)
        name = name[:name.rfind(suffix)].strip()
    else:
        suffix = None
    if len(suffix) == 0:
        suffix = None
    name_parts = name.split()
    
    if len(name_parts) > 1:
        last_name = name_parts[-1]
        first_name = name_parts[0]
        middle_names = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else None
    else:
        first_name = name_parts[0]
        last_name = None
        middle_names = None
    is_full_name = first_name != None and last_name != None and middle_names != None
    return {
        "title": title,
        "first_name": first_name,
        "middle_names": middle_names,
        "last_name": last_name,
        "suffix": suffix,
        "is_full_name" : is_full_name
    }
#parameter: decomposed, is a dictionary with name information
#adds a decomposed name to appropriate list
def add_name(decomposed):
    if(decomposed["is_full_name"]):
        is_unique = True
        for name in full_names:
            if(decomposed["is_full_name"] and name["first_name"] == decomposed["first_name"] 
            and name["middle_names"] == decomposed["middle_names"] and name["last_name"] == decomposed["last_name"]):
                is_unique = False
        if(is_unique):
            full_names.append(decomposed) 
    elif(decomposed["first_name"] != None and decomposed["last_name"] != None):
        is_unique = True
        for name in full_names: #checks if decomposed is already in full_names
            if(name["first_name"] == decomposed["first_name"] 
               and name["last_name"] == decomposed["last_name"]):
                is_unique = False
        for name in first_last_names: #checks if decomposed is already in first_last_names
            if(name["first_name"] == decomposed["first_name"] 
               and name["last_name"] == decomposed["last_name"]):
                is_unique = False
        if(is_unique):
            first_last_names.append(decomposed)      
    else:
        all_people.append(decomposed)

#user input
is_correct_input = False
while is_correct_input == False:
    source_type = input("From what source of text do you want names extracted? type \"pdf\" or type \"string\": ")
    if(source_type == "pdf"):
        is_correct_input = True
        print("Select file from opened window.")
        pdf_path = select_pdf_file()
        print(pdf_path)
        if not pdf_path:
            print("No file selected. Try Again")
            is_correct_input = False
        text = extract_text_from_pdf(pdf_path)
    elif(source_type == "string"):
        is_correct_input = True
        text = input("Please write string: ")

nlp = spacy.load("en_core_web_trf")#en_core_web_sm") use en_core_web_sm for speed, but misses titles and suffix most times
doc = nlp(text)
full_names = []
first_last_names = []
all_people = []
decomposed_names = []



for ent in doc.ents: #ent = named entity: this prints all Persons in the doc
    if ent.label_ == "PERSON" and ent.text not in full_names:
        decomposed_names.append(decompose_name(ent.text))
for decomposed in decomposed_names: 
    # decomposed = {
    #     "title": title,
    #     "first_name": first_name,
    #     "middle_names": middle_names,
    #     "last_name": last_name,
    #     "suffix": suffix,
    #     "is_full_name" : is_full_name
    # }
    add_name(decomposed)
print("full Names")
for name in full_names:
    print(name)
print("first last Names")
for name in first_last_names:
    print(name["first_name"]+" "+name["last_name"])
for name in all_people:
    print(name)