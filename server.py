from flask import Flask, request
from datetime import datetime, timedelta
import time
import ast
from collections import OrderedDict
app = Flask(__name__)

# messages = []
users = {}


@app.route("/")
def hello():
    return "<h1>Welcome to Python Messenger</h1>"


@app.route("/status")
def status():
    now = datetime.now() + timedelta(hours=3)
    now = now.strftime('%d/%m/%Y %H:%M:%S')
    f = open('userbase.txt')
    users_num = 0
    for i in f:
        users_num += 1
    f.close()
    f = open('textbase.txt')
    mess_num = 0
    for i in f:
        mess_num += 1
    f.close()
    result = f'''
<p>Status: {True}
<p>Server time: {str(now)} GTM
<p>Number of users: {users_num} 
<p>Number of messages: {mess_num}
                '''
    return result


@app.route("/messages")
def messages_view():
    """
    Получение сообщения после отметки after
    input: after
    output: {
        "messages": [{"username": str, "text": str, "time": float},
        ...
    }
    """
    after = float(request.args['after'])
    text_open = open('textbase.txt', 'r')
    new_messages = []
    try:
        for message in text_open:
            if float(ast.literal_eval(message)['time']) > after:
                new_messages.append(message)
    except SyntaxError:
        pass
    return {'messages': new_messages}


@app.route("/send", methods=['POST'])
def send_view():
    """
    Отправка сообщения
    input: {
        "username": str,
        "password": str,
        "text": str
    }
    output: {"ok": bool}
    """
    data = request.json
    username = data["username"]
    password = data["password"]

    # if username not in users or users[username] != password:
    #     return {"ok": False}

    text = data["text"]
    text_file = open('textbase.txt', 'a')
    tmp_str = '{' + f'"user" : "{username}", "text" : "{text}", "time" : "{time.time()}"' + '}'
    text_file.write(str(tmp_str) + '\n')
    text_file.close()
    return {'ok': True}


@app.route("/auth", methods=['POST'])
def auth_view():
    """
    Авторизовать пользователя или сообщить о неверном пароле
    input: {
        "username": str,
        "password": str,
    }
    output: {"ok": bool}
    """

    data = request.json
    username = data["username"]
    password = data["password"]
    checking = False
    userfile = open('userbase.txt')
    for i in userfile:
        check = i.find(':')
        userstr = i[:check]
        passstr = i[check+1:-1]
        if username != userstr:
            pass
        else:
            checking = True
            break
    userfile.close()
    if not checking:
        userfile = open('userbase.txt', 'a')
        userfile.write(username + ':' + password + '\n')
        userfile.close()
        return {"ok": True}
    elif passstr == password:
        return {"ok": True}
    else:
        return {"ok": False}

app.run(host='192.168.1.103')
