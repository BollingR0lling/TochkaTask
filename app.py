from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import uuid
from http import HTTPStatus
import enum

# Init app
app = Flask(__name__)
# Connect db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.user_info'  # поменять базу данных на db.user_info
db = SQLAlchemy(app)


class User(db.Model):
    Uuid = db.Column(db.String(80), primary_key=True)
    fio = db.Column(db.String(255))
    balance = db.Column(db.Integer)
    hold = db.Column(db.Integer)
    status = db.Column(db.String(10))


class Status(enum.Enum):
    open = "открыт"
    closed = "закрыт"


# Add user
@app.route('/<fio>/<balance>/<hold>/<status>')
def index(fio, balance, hold, status):
    user = User(Uuid=str(uuid.uuid4()),
                fio=fio,
                balance=balance,
                hold=hold,
                status=bool(status))
    db.session.add(user)
    db.session.commit()

    return '<h1>Added new user</h1>'


@app.route('/api/ping', methods=['GET'])
def ping():
    return {'status': HTTPStatus.OK,
            'result': True,
            'additional': {},
            'description': {'message': 'Сервер работает'}
            }, HTTPStatus.OK


@app.route('/api/add', methods=['POST'])
def add():
    data_json = request.get_json()
    addition = data_json.get('addition')
    summ = int(addition.get('sum'))
    user = User.query.filter_by(Uuid=addition.get('uuid')).first()
    if user:
        if user.status == Status.open.value:
            user.balance += summ
            db.session.commit()
            return {'status': HTTPStatus.OK,
                    'result': True,
                    'addition': {'fio': user.fio,
                                 'balance': user.balance,
                                 'status': user.status},
                    'discriprion': {'message': 'Операция проведена успешно'}
                    }, HTTPStatus.OK
        return {'status': HTTPStatus.BAD_REQUEST,
                'result': False,
                'addition': {},
                'discriprion': {'message': 'Счет данного пользователя закрыт'}
                }, HTTPStatus.BAD_REQUEST
    return {'status': HTTPStatus.BAD_REQUEST,
            'result': False,
            'addition': {},
            'discriprion': {'message': 'Такого пользователя не существует'}
            }, HTTPStatus.BAD_REQUEST


@app.route('/api/substract', methods=['POST'])
def substract():
    data_json = request.get_json()
    addition = data_json.get('addition')
    summ = int(addition.get('sum'))
    user = User.query.filter_by(Uuid=addition.get('uuid')).first()
    if user and user.status == Status.open:
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


@app.route('/api/status', methods=['GET'])
def status():
    data_json = request.get_json()
    addition = data_json.get('addition')
    user = User.query.filter_by(Uuid=addition.get('uuid')).first()
    if user:
        return {'status': HTTPStatus.OK,
                'result': True,
                'addition': {'balance': user.balance,
                             'status': user.status},
                'discriprionпр': {'message': 'Операция прошла успешно'}
                }, HTTPStatus.OK
    else:
        return {'status': HTTPStatus.BAD_REQUEST,
                'result': False,
                'addition': {},
                'discriprion': {'message': 'Такого пользователя не существует'}
                }, HTTPStatus.BAD_REQUEST


if __name__ == "__main__":
    app.run()