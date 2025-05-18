import sqlite3
db_name = 'quiz.sqlite'
conn = None
curor = None

def open():
    global conn, cursor
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

def close():
    cursor.close()
    conn.close()

def do(query):
    cursor.execute(query)
    conn.commit()

def clear_db():
    ''' удаляет все таблицы '''
    open()
    #query = '''DROP TABLE IF EXISTS quiz_content'''
    #do(query)
    query = '''DROP TABLE IF EXISTS question'''
    do(query)
    query = '''DROP TABLE IF EXISTS quiz'''
    do(query)
    close()
    
    
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
    conn.commit()
    close()

#create()
#add_questions()
#add_quiz()


def link_quiz_question():
    query = "INSERT INTO quiz_content (quiz_id, question_id) VALUES (?,?)"
    answer = input("Добавить связь (y / n)?")
    open()
    while answer != 'n':
        quiz_id = int(input("id викторины: "))
        question_id = int(input("id вопроса: "))
        cursor.execute(query, [quiz_id, question_id])
        conn.commit()
        answer = input("Добавить связь (y / n)?")
    close()

def get_question_after2(question_id, quiz_id):
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
    #print(result)
    close()
    return result
def get_question_after(last_id=0, vict_id=1):
    open()
    query = '''
    SELECT quiz_content.id, question.question, question.answer, question.wrong1, question.wrong2, question.wrong3
    FROM question, quiz_content 
    WHERE quiz_content.question_id == question.id
    AND quiz_content.id > ? AND quiz_content.quiz_id == ? 
    ORDER BY quiz_content.id '''
    cursor.execute(query,[last_id, vict_id])
    result = cursor.fetchone()
    close()
    return result

def get_quises():
    open()
    eeee = cursor.execute('''SELECT * FROM quiz ORDER BY id''')
    eeee = cursor.fetchall()
    close()
    return eeee


def show(table):
    query = 'SELECT * FROM ' + table
    open()
    cursor.execute(query)
    print(cursor.fetchall())
    close()

def show_tables():
    show('question')
    show('quiz')
    show('quiz_content')

def main():
    clear_db()
    create()
    add_quiz()
    add_questions()
    link_quiz_question()
    show_tables()

if __name__ == "__main__":
    main()

def check_answer(q_id,ans_text):
    query = '''SELECT question.answer
            FROM quiz_content, question
            WHERE quiz_content.id = (?) And quiz_content.question_id = question.id
            '''
    open()
    cursor.execute(query, str(q_id))
    result = cursor.fetchone()
    close()
    if result is None:
        return False
    else:
        if result[0] == ans_text:
            return True
        else:
            return False