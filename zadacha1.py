from flask import Flask, session, redirect, url_for, escape, request, jsonify
import sqlite3 as sql


db = sql.connect('new_base.db')
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY, login varchar(100), password varchar(50));")
cur.close()


app = Flask(__name__)


@app.route('/')
def index():
    if 'username' in session:
        return f'''Добро пожаловать, {escape(session["username"])}
            <form action="/logout" method="get">
                <p><input type=submit value=Выход>
            </form>
        '''  
    return redirect(url_for('authorization'))
    

@app.route('/admin')
def admin():
    if 'username' in session:
        return f'''Добро пожаловать, {escape(session["username"])}
            <form action="/logout" method="get">
                <p><input type=submit value=Выход>
            </form>
            <form action="/list_users" method="get">
                <p><input type=submit value=Пользователи>
            </form>
        '''  
    return redirect(url_for('authorization'))


@app.route('/list_users', methods=['GET'])
def list_users():
    db = sql.connect('new_base.db')
    cur = db.cursor()
    cur.execute(f"SELECT login FROM users WHERE id>0;")
    db_login = cur.fetchall()
    db.commit()
    cur.close()
    return jsonify(db_login)


@app.route('/authorization', methods=['GET'])
def authorization():
    return '''
        <form action="/check_registration" method="post">
            <p align='center'>Авторизация
            <p align='center'>Введите имя пользователя:
            <input id=username type=text name=username>
            <p align='center'>Введите пароль:
            <input id=password type=password name=password>
            <p align='center'><input type=submit value=Ok>
        </form>
    
        <form action="/registration" method="get">
            <p align='center'>Нет профиля?
            <p align='center'><input type=submit value=Регистрация>
        </form>
    '''


@app.route('/registration', methods=['GET'])
def registration():
    return '''
        <form action="/add_new_user" method="post">
            <p align='center'>Регистрация нового пользователя
            <p align='center'>Введите имя пользователя:
            <input id=username type=text name=username>
            <p align='center'>Введите пароль:
            <input id=password type=password name=password>
            <p align='center'><input type=submit value=Ok>
        </form>
    '''
    

@app.route('/add_new_user', methods=['POST'])
def add_new_user():
    username = request.form['username']
    password = request.form['password']
    info = (username, password)
    pass_username = ('',)
    pass_password = ''
    user = tuple([username])
    db = sql.connect('new_base.db')
    cur = db.cursor()
    cur.execute(f"SELECT login FROM users WHERE login=(?);", user)
    db_login = cur.fetchall()
    if user in db_login and user != pass_username:
        return '''
            <form action="/registration" method="get">
                <p align='center'>Имя пользователя занято, попробуйте выбрать другое
                <p align='center'><input type=submit value=Вернуться>
            </form>
        '''
    elif user == pass_username or password == pass_password:
        return redirect(url_for('registration'))
    cur.execute(f'INSERT INTO users(login, password) VALUES(?, ?);', info)
    db.commit()
    cur.close()
    return redirect(url_for('authorization'))


@app.route('/check_registration', methods=['POST'])
def check_registration():
    username = tuple([request.form['username']])
    password = tuple([request.form['password']])
    pass_password = ('',)
    db = sql.connect('new_base.db')
    cur = db.cursor()
    cur.execute(f"SELECT password FROM users WHERE login=(?);", username)
    db_password = cur.fetchall()
    db.commit()
    cur.close()
    if username == ('admin',) and password in db_password:
        session['username'] = request.form['username']
        return redirect(url_for('admin'))
    elif password == pass_password:
        return redirect(url_for('authorization'))
    elif password in db_password:
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="/authorization" method="get">
            <p align='center'>Такого пользователя не существует
            <p align='center'><input type=submit value=Вернуться>
        </form>
        <form action="/registration" method="get">
            <p align='center'><input type=submit value=Регистрация>
        </form>
    '''


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


if __name__ == '__main__':
   app.run(debug = True)
