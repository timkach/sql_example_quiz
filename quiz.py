from flask import Flask, session, request, redirect, url_for
from random import shuffle
from db_scripts import get_question_after, get_quises, open, close, check_answer
from flask import render_template
import os
folder = os.getcwd()
def start_quis(quiz_id):
    session['quiz'] = quiz_id
    session['last_question'] = 0
    session['answers']=0
    session['total']=0

def save_answers():
    answer = request.form.get('ans_text')
    quest_id = request.form.get('q_id')
    session['last_question'] = quest_id
    session['total'] += 1
    if check_answer(quest_id, answer):
        session['answers'] += 1
 
def end_quiz():
    session.clear()


''' функция получает список викторин из базы и формирует форму с выпадающим списком'''
"""def quiz_form():
    html_beg = '''<html><body><h2>Выберите викторину:</h2><form method="post" action="index"><select name="quiz">'''
    frm_submit = '''<p><input type="submit" value="Выбрать"> </p>'''

    html_end = '''</select>''' + frm_submit + '''</form></body></html>'''
    options = ''' '''
    q_list = get_quises()
    #print('11111',q_list)
    for id, name in q_list:
        option_line = ('''<option value="''' +
                        str(id) + '''">''' +
                        str(name) + '''</option>
                      ''')
        options = options + option_line
    return html_beg + options + html_end"""

def quiz_form():
    q_list = get_quises()
    return render_template('start.html',q_list=q_list)


''' Первая страница: если пришли запросом GET, то выбрать викторину, 
если POST - то запомнить id викторины и отправлять на вопросы'''
def index():
    if request.method == 'GET':
        # викторина не выбрана, сбрасываем id викторины и показываем форму выбора
        start_quis(-1)
        return quiz_form()
    else:
        # получили дополнительные данные в запросе! Используем их:
        quest_id = request.form.get('quiz') # выбранный номер викторины 
        start_quis(quest_id)
        return redirect(url_for('test'))

def question_form(question):
    print(question)
    answers_list = [
        question[2],question[3],question[4],question[5]
    ]
    shuffle(answers_list)
    return(render_template('test.html',question = question[1], quest_id=question[0],answers_list=answers_list))
#def next_question():

'''возвращает страницу вопроса'''
'''def test():
    # если пользователь без выбора викторины пошел сразу на адрес '/test'
    if not ('quiz' in session) or int(session['quiz']) < 0:
        return redirect(url_for('index'))
    else:
        # тут пока старая версия функции:
        result = get_question_after(session['last_question'], session['quiz'])
        if result is None or len(result) == 0:
            return redirect(url_for('result'))
        else:
            session['last_question'] = result[0]
            # если мы научили базу возвращать Row или dict, то надо писать не result[0], а result['id']
            #return '<h1>' + str(session['quiz']) + '<br>' + str(result) + '</h1>'
            html = render_template('test.html')
            return html'''
def test():
    if not ('quiz' in session) or int(session['quiz']) < 0:
        return redirect(url_for('index'))
    else:
        if request.method =='POST':
            save_answers()
        next_question = get_question_after(session['last_question'],session['quiz'])
        if next_question is None or len(next_question) == 0:
            return redirect(url_for('result'))
        else:
            return question_form(next_question)
def result():
    html = render_template('result.html', right=session['answers'],total=session['total'])
    end_quiz()
    return html

app = Flask(__name__, template_folder=folder, static_folder=folder) # создаём объект веб-приложения
app.config['SECRET_KEY'] = 'iuyipuyipuyiou'
app.add_url_rule('/', 'index', index, methods = ['GET','POST'])
app.add_url_rule('/index', 'index', index, methods = ['GET','POST'])
app.add_url_rule('/test', 'test', test, methods = ['GET','POST'])
app.add_url_rule('/result', 'result', result)

if __name__ == "__main__":   
    #app.run()  # запускаем веб-сервер
    app.run(host=('0.0.0.0'))
    from quiz import app as application


"""from flask import *
from flask import session
from random import randint
import sqlite3
#session['counter'] = 0
db_name = "quiz.sqlite"
conn = None
cursor = None
quiz = 1
last_question=1
def open():
    global conn, cursor
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

def close():
    cursor.close()
    conn.close()

def do(sql):
    cursor.execute(sql)
    conn.commit()
    
def create():
    open()
    cursor.execute('''PRAGMA foreign_keys=on''')

    do('''CREATE TABLE IF NOT EXISTS quiz
    (id INTEGER PRIMARY KEY,
    name VARCHAR)''')

    do('''CREATE TABLE IF NOT EXISTS question
    (id INTEGER PRIMARY KEY,
    question VARCHAR,
    answer VARCHAR,
    wrong1 VARCHAR,
    wrong2 VARCHAR,
    wrong3 VARCHAR)''')
    do('''CREATE TABLE IF NOT EXISTS quiz_content (
            id INTEGER PRIMARY KEY,
            quiz_id INTEGER,
            question_id INTEGER,
            FOREIGN KEY (quiz_id) REFERENCES quiz (id),
            FOREIGN KEY (question_id) REFERENCES question (id))''')
    close()

def add_questions():
    open()
    questions = [
        ('Сколько месяцев в году имеют 28 дней?', 'Все', 'Один', 'Ни одного', 'Два'),
        ('Каким станет зеленый утес, если упадет в Красное море?', 'Мокрым', 'Красным', 'Не изменится', 'Фиолетовым'),
        ('Какой рукой лучше размешивать чай?', 'Ложкой', 'Правой', 'Левой', 'Любой'),
        ('Что не имеет длины, глубины, ширины, высоты, а можно измерить?', 'Время', 'Глупость', 'Море', 'Воздух'),
        ('Когда сетью можно вытянуть воду?', 'Когда вода замерзла', 'Когда нет рыбы', 'Когда уплыла золотая рыбка', 'Когда сеть порвалась'),
        ('Что больше слона и ничего не весит?', 'Тень слона', 'Воздушный шар', 'Парашют', 'Облако')]
    cursor.executemany(''' INSERT INTO question
    (question,answer,wrong1,wrong2,wrong3)
    VALUES(?,?,?,?,?) ''',questions)
    conn.commit()
    close()

def add_quiz():
    open()
    quizes = [
        ('Своя игра', ),
        ('Кто хочет стать миллионером?', ),
        ('Самый умный', )]

    cursor.executemany(''' INSERT INTO quiz (name) VALUES(?) ''',quizes)
    data = cursor.execute('''SELECT * FROM quiz''')
    data = cursor.fetchall()
    close()

create()
add_questions()
add_quiz()


def link_quiz_question():
    query = "INSERT INTO quiz_content (quiz_id, question_id) VALUES (?,?)"
    answer = input("Добавить связь (y / n)?")
    while answer != 'n':
        quiz_id = int(input("id викторины: "))
        question_id = int(input("id вопроса: "))
        cursor.execute(query, [quiz_id, question_id])
        conn.commit()
        answer = input("Добавить связь (y / n)?")

def get_question_after(question_id, quiz_id):
    open()
    data = cursor.execute('''SELECT quiz_content.id, question.question, question.answer
    FROM quiz_content, question
    WHERE quiz_content.question_id == question.id
    AND quiz_content.quiz_id == (?)
    AND question.id >(?)
    ORDER BY quiz_content.id''', [quiz_id,question_id])
    #data = cursor.execute('''SELECT * FROM quiz''')
    result = cursor.fetchone()

    #result = data.fetchone()
    #result = cursor.fetchone()
    print(result)
    close()
    return result

#link_quiz_question()

print('11',get_question_after(3,1))
print('22',get_question_after(2,1))

open()
data = cursor.execute('''SELECT * FROM quiz_content''')
data = cursor.fetchall()
print(data)
close()

def test1():
    global quiz, last_question
    session['last'] = 1
    max_quiz = 3
    #quiz = randint(1, max_quiz)
    #last_question = 0
    return '''
    <p>test1</p>
    <p>go to test 2 >>> </p>
    <a href='/test2'>test2</a>
    <button type='button' name='20'>button test</button>
    <button type='button' disabled>disabled test button</button>\n
    <button name="ttt" value="ttt">
        <img style="vertical-align: middle; width: 24px;" src="https://symbl-world.akamaized.net/i/webp/fe/da2cf7320c6aacab49335ec1c339d9.webp" alt="" />
        puk
    </button>'''
def test2():
    global quiz, last_question
    session['last'] = 1
    print(last_question)
    print(session['last'])
    result = get_question_after(session['last'],quiz)
    print(result)
    if result is None or len(result) == 0:
        return redirect(url_for('result'))
    else:
        #last_question = result[0]
        session['last'] +=1
        print("rttewt",session['last'])
        return '<h1>' + str(quiz) + '<br>' + str(result) + '</h1>'
    '''max_quiz = 3
    quiz = randint(1, max_quiz)
    last_question = 0
    return "<p>test2</p>\n<p>go to test 1 >>> </p><a href='/test1'>test1</a>"'''
def result():
    return "<p>oiewoiewtowtoit</p>"
app = Flask(__name__) # создаём объект веб-приложения
app.config['SECRET_KEY'] = 'iuyipuyipuyiou'
app.add_url_rule('/', 'test1', test1)
app.add_url_rule('/test1', 'test1', test1)
app.add_url_rule('/test2', 'test2', test2)
app.add_url_rule('/result', 'result', result)
if __name__ == "__main__":   
    
    app.run()  # запускаем веб-сервер
"""

