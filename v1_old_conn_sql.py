import sqlite3

conn = sqlite3.connect('faq.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE faq
             (question text, answer text)''')

cursor.execute(
    "INSERT INTO faq VALUES ('Когда зарплата?',"
    "'Работай негр, солнце еще высоко')")
cursor.execute(
    "INSERT INTO faq VALUES ('Мы работаем с НДС?',"
    "'Не задавай глупых вопрос и не получишь глупых ответов')")

conn.commit()
conn.close()
