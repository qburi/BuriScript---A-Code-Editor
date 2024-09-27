from bs4 import BeautifulSoup
import requests
import mysql.connector
import string

"""
text_in = ""
arguments = tuple()


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="PASSWORD",
  database='typeracer_details'
)
mycursor = mydb.cursor()


mycursor.execute("SELECT * FROM typeracer_details.typeracer_site_text_database;")

myresult = mycursor.fetchall()


final = ""
iterations = 0
for x in myresult:
    final += x[1] + '\n'
    iterations += 1
print(final, iterations)
with open("typeracer_database_text_1.txt", "w") as file_to_write:
    for x in myresult:
        file_to_write.write(x[1] + "\n")

"""
"""
def is_english(s):
    char_set = string.ascii_letters + string.punctuation + string.whitespace + string.ascii_lowercase + string.ascii_uppercase + string.digits
    return all((True if x in char_set else False for x in s))


count = 0
integer = 3810627

while count < 1:
    url = f"https://data.typeracer.com/pit/text_info?id={integer}"
    integer += 1
    print(integer, count)

    result = requests.get(url)

    docstring = BeautifulSoup(result.text, "html.parser")
    try:
        text_in = docstring.find(class_="fullTextStr")
        title_in = docstring.find('title').getText()
        text_to_table = text_in.get_text()
        print(text_to_table)
        count += 1
        if True:
            type_of_text = 'short' if len(text_in) < 75 else 'medium' if len(text_in) < 250 else 'long'
            sql = "INSERT INTO typeracer_details.typeracer_site_text_database (type, text) VALUES (%s, %s)"
            val = (rf"{type_of_text}", rf"{text_to_table}")
            mycursor.execute(sql, val)
            mydb.commit()
    except AttributeError:
        continue

# print(title_in, "\n", text_in, len(text_in), sep="")
"""
"""
    try:
        text_in = docstring.find('p').getText()
        title_in = docstring.find('title').getText()
    except AttributeError:
        continue
    # print(text_in, len(text_in))
    if 1000 > len(text_in) > 50 and is_english(text_in):
        type_of_text = 'short' if len(text_in) < 75 else 'medium' if len(text_in) < 250 else 'long'
        sql = "INSERT INTO text_database (title, type, text) VALUES (%s, %s, %s)"
        val = (rf"{title_in}", rf"{type_of_text}", rf"{text_in}")
        mycursor.execute(sql, val)
        mydb.commit()
        print(count)
        count += 1
"""