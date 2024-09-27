import time
from bs4 import BeautifulSoup
import requests
import mysql.connector
import pandas as pd
import csv
from pprint import pprint
import threading
import multiprocessing

values = []  # This list has values in the form List[str -> Text: id, str -> Text]

"""
# data = pd.read_html(r"https://typeracerdata.com/texts?texts=full&sort=relative_average")[0]
# final = data.values.tolist()
# final_data_to_process = []
with open("TypeRacerScraper_text_file.csv", mode="r", encoding='utf-8') as file_to_append:
    csv_file = csv.reader(file_to_append)
    for data in csv_file:
        values.append([data[1][1:], data[2]])
# pprint(values)

can_start_from_id = False # should be True
cut_index = 0

def run_get_requests_function(text_id , text):
    global cut_index, can_start_from_id
    if text_id == "4180144":
        can_start_from_id = False
        return
    elif not can_start_from_id:
        try:
            book_name_str, author_book_by_str = "", ""
            data = requests.get(fr'https://data.typeracer.com/pit/text_info?id={text_id}')
            docstring = BeautifulSoup(data.text, "html.parser")
            get_author_name = docstring.find_all("img", alt=True)
            get_book_name = docstring.find_all('a', href=True)
            author_book_by = []
            for x in get_author_name:
                if x != "":
                    author_book_by.append(x.text)
            author_book_by_str = ' '.join(author_book_by[1].replace("\n", "").strip().split("          "))
            book_name = []
            for x in get_book_name:
                book_name.append(x.text)
            book_name_str = book_name[34]
            # write_row_file.writerow([text_id, text, book_name_str, author_book_by_str])
            print(text)
            print(book_name_str, end=" ")
            print(author_book_by_str)
            cut_index += 1
            del book_name_str, author_book_by_str
        except IndexError:
            print(book_name_str, author_book_by_str)
            print(f"CUT AT {cut_index}")
            time.sleep(1)
            run_get_requests_function(text_id, text)
            # error_: --------------------------stopped-at--3810103-----------------------------------------------------

"""
"""
index: 34
"""

"""
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="PASSWORD",
    database="buriracer"
)
mycursor = mydb.cursor()
cut_index = 0
with open('TypeRacerDatabaseWithValues.csv', mode='r', encoding='utf-8', newline="") as file_to_append_write:
    read_row_file = csv.reader(file_to_append_write)
    for row in read_row_file:
        row_list = {
            'text_id': row[0],
            "text": row[1],
            "title": row[2],
        }
        author_name_with_type = row[3]
        type_ = author_name_with_type[author_name_with_type.find("(") + 1: author_name_with_type.find(")")]
        author_name = author_name_with_type[len(type_) + 2:].lstrip()[2:].lstrip()
        print(type_, "NAME:", author_name)
        query = f\"""INSERT INTO typeracertext(TypeRacer_text_ID, `Text`, Title, `Type`, Author) VALUES(%s, 
        %s, %s, %s, %s);\""" # delete the backlashes in front of quotes.
        # print(query)
        mycursor.execute(query, (row_list['text_id'], row_list["text"], row_list["title"], type_, author_name))
    mydb.commit()
"""

if __name__ == "__main__":
    pass


