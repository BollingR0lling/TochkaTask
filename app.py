from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import uuid
from http import HTTPStatus

# Init app
app = Flask(__name__)
# Connect db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.user_info'
db = SQLAlchemy(app)


class User(db.Model):
    Uuid = db.Column(db.String(80), primary_key=True)
    fio = db.Column(db.String(255))
    balance = db.Column(db.Integer)# Balance и hold исправить с Integer на Real
    hold = db.Column(db.Integer)
    status = db.Column(db.String(10))


# Add user
@app.route('/<fio>/<balance>/<hold>/<status>')
def index(fio, balance, hold, status):
    user = User(Uuid=str(uuid.uuid4()),
                fio=fio,
                balance=balance,
                hold=hold,
                status=status)
    db.session.add(user)
    db.session.commit()

    return '<h1>Added new user</h1>'


# Database test
@app.route('/<balance>')
def get_user(balance):
    user = User.query.filter_by(balance=balance).first()
    user.balance -= 10
    db.session.commit()
    return f'The user is {user.fio}'


@app.route('/app/ping', methods=['GET'])
def ping():
    return request.get_json()
        # '<h1>Сервер работает</h1>'


"""
Message format:
{
“status“=<http_status>,
“result“:<bool:operation_status>,
“addition“:{},
“description“:{}
}  

◦status—http статус запроса
◦result—статус проведения текущей операции 
◦addition—поля для описания текущей операции(uuid,ФИО,сумма, статус и т.п.) 
◦description—дополнительные описания к текущей операции(прочие текстовые поля,если необходимо)
"""


# Все что ниже работает
@app.route('/app/add', methods=['POST'])
def add():
    data_json = request.get_json()
    addition = data_json.get('addition')
    summ = int(addition.get('sum'))
    user = User.query.filter_by(Uuid=addition.get('uuid')).first()
    if user and user.status == "открыт":
        user.balance += summ
        addition['sum'] = user.balance
        db.session.commit()
        data_json['status'] = HTTPStatus.OK
        return data_json
    else:
        data_json['status'] = HTTPStatus.BAD_REQUEST
        return data_json


@app.route('/app/substract', methods=['POST'])
def substract():
    data_json = request.get_json()
    addition = data_json.get('addition')
    summ = int(addition.get('sum'))
    user = User.query.filter_by(Uuid=addition.get('uuid')).first()
    if user and user.status == "открыт":
        result = user.balance - user.hold - summ
        if result < 0:
            data_json['status'] = HTTPStatus.BAD_REQUEST
            return data_json
        else:
            user.hold += summ
            addition['hold'] = user.hold
            db.session.commit()
            return data_json
    else:
        data_json['status'] = HTTPStatus.BAD_REQUEST
        return data_json


@app.route('/app/status', methods=['GET'])
def status():
    data_json = request.get_json()
    addition = data_json.get('addition')
    user = User.query.filter_by(addition.get('Uuid'))

    return user.balance, user.status


if __name__ == "__main__":
    app.run()
