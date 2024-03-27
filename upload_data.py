import csv

from model.db import Question, session


with open('data.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        question_text = row[0]
        answer_text = row[1]

        question = Question(question=question_text, answer=answer_text)
        session.add(question)

session.commit()

session.close()
