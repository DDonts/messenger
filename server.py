from flask import Flask, request
from datetime import datetime, timedelta
import time

app = Flask(__name__)


messages = [
    # {"username": "Jack", "text": "Hello!", "time": time.time()},
    # {"username": "Sam", "text": "Kill, all humans!", "time": time.time()},
]
users = {
    # "Jack": '12345',
    # "Mary": '54321',
}


@app.route("/")
def hello():
    return "<h1>Welcome to Python Messenger</h1>"


@app.route("/status")
def status():
    now = datetime.now() + timedelta(hours=3)
    now = now.strftime('%d/%m/%Y %H:%M:%S')
    users_num = len(users)
    mess_num = len(messages)
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
    new_messages = [message for message in messages if message['time'] > after]
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
    if username not in users or users[username] != password:
        return {"ok": False}

    text = data["text"]
    messages.append({"username": username, "text": text, "time": time.time()})

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

    if username not in users:
        users[username] = password
        return {"ok": True}
    elif users[username] == password:
        return {"ok": True}
    else:
        return {"ok": False}


app.run()
