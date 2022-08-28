import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import logging
logger = logging.getLogger(__name__)  
logger.setLevel(logging.WARNING)
# define file handler and set formatter
file_handler = logging.FileHandler('app.log')
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
# add file handler to logger
logger.addHandler(file_handler)

application = Flask(__name__)

application.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

mongo = PyMongo(application)
db = mongo.db



#Rabitmq broker
from flask_rabmq import RabbitMQ

application.config.setdefault('RABMQ_RABBITMQ_URL', 'amqp://admin:admin@mq:5672//')
application.config.setdefault('RABMQ_SEND_EXCHANGE_NAME', 'flask_rabmq')
application.config.setdefault('RABMQ_SEND_EXCHANGE_TYPE', 'topic')

ramq = RabbitMQ()
ramq.init_app(app=application)


@application.route('/')
def index():
        # send message
    ramq.send({'message_id': 222222, 'a': 7}, routing_key='flask_rabmq.test', exchange_name='flask_rabmq')
    # delay send message, expiration second(support float).
    # ramq.delay_send({'message_id': 333333, 'a': 7}, routing_key='flask_rabmq.test', exchange_name='flask_rabmq',
    #                 delay=random.randint(1, 20))

    return jsonify(
        status=True,
        message='Welcome to the Dockerized Flask MongoDB app!'
    )

@application.route('/todo')
def todo():
    _todos = db.todo.find()

    item = {}
    data = []
    for todo in _todos:
        item = {
            'id': str(todo['_id']),
            'todo': todo['todo']
        }
        data.append(item)

    return jsonify(
        status=True,
        data=data
    )

@application.route('/todo', methods=['POST'])
def createTodo():
    data = request.get_json(force=True)
    item = {
        'todo': data['todo']
    }
    db.todo.insert_one(item)

    return jsonify(
        status=True,
        message='Todo saved successfully!'
    ), 201


# received message
@ramq.queue(exchange_name='flask_rabmq', routing_key='flask_rabmq.test')
def flask_rabmq_test(body):
    """
    :param body: json string.
    :return: True/False
        return True, the message will be acknowledged.
        return False, the message is resended(default 3 count) to the queue.
        :exception, the message will not be acknowledged.
    """
    print(body)
    logger.info(body)
    # logger.info(body)
    return True


ramq.run_consumer()

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
