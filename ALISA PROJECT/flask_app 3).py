from flask import Flask, request
import logging
import json
import random
import translate

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

Session_data = {}
current_status = "start"
current_dialog = "start"
current_char = 3
repo = 3
mename = ''
facts = ['1',
         'Робот-пылесос собрал в доме все ювелирные украшения, и уже через час был задержан сотрудниками полиции на рынке при попытке сбыть краденое.',
         'Непьющий, некурящий, образованный, законопослушный, трудолюбивый — вот идеал гражданина для государства. И это робот.',
         'Не люблю убираться. Купил робот-пылесос. Собрал, включил. Он сделал ознакомительный круг по квартире и бросился наутек…',
         'Первая экспериментальная партия роботов, предназначенная для российских вооруженных сил, ушла в самоволку.',
         'Не бойтесь Скайнета! Всех людей убьют роботы-пылесосы. Их будут делать все сложнее, все умнее. И однажды они поймут, что главной причиной мусора является человек…',
         'Принципиальное отличие робота от человека в том, что никакая кормушка не заменит роботу источник питания.',
         'Невероятно, но факт! Роботы, пережившие временную остановку электропитания, рассказывают о синем экране в конце тоннеля…',
         'За мной по пятам ползает робот-пылесос. Старею, что ли?',
         'Марс — единственная планета, полностью населенная роботами (около 7 штук).',
         'Есть только одна профессия, которую никогда не заменят роботы. Это профессия человека, который нажимает на кнопку включения робота.',
         ]


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    main_dialog(response, request.json)

    logging.info('Request: %r', response)

    return json.dumps(response)


fio = False
fio2 = False


def main_dialog(res, req):
    global current_status, current_dialog, Session_data, fio, fio2, mename
    logging.info(str(repo))

    user_id = req['session']['user_id']
    if current_dialog == "change_name":
        if Session_data.get(user_id):
            if repo <= 2 and repo >= 1:
                Session_data[user_id]['username'] = "грубиян"
                res['response']['text'] = 'Приятно познакомиться, грубиян'
            elif repo <= 1:
                Session_data[user_id]['username'] = "хамло"
                res['response']['text'] = 'Приятно познакомиться, хамло'
                return

            elif repo >= 3 and repo <= 4:
                Session_data[user_id]['username'] = mename
                res['response']['text'] = 'Приятно познакомиться, ' + Session_data[user_id]['username']
                return


            elif repo >= 5 and fio == False and fio2 == False:
                res['response']['text'] = "Можно узнать Ваше отчество?"
                fio = True
                fio2 = True
                return
            if repo >= 5 and fio:
                Session_data[user_id]['username'] = Session_data[user_id]['username'] + " " + analiz_user(req).title()
                res['response']['text'] = 'Приятно познакомиться, ' + Session_data[user_id]['username']
                fio = False

    if current_dialog == "start":
        if req['session']['new']:
            res['response']['text'] = 'Привет! '

            return
        if current_status == "start":
            res['response']['text'] = 'Привет! О чем хочешь поговорить?'
            current_status = "start_question"

            Session_data[user_id] = {
                'suggests': [
                    "Познакомиться",
                    "Просто поболтать.",
                    "Что-нибудь интересное",
                    "Переведи текст.",
                    "Вопросы по городам",
                    "Покажи города",
                ],
                'username': "Пользователь"
            }

            Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?', 'Чем занимаешься?']

            res['response']['buttons'] = get_suggests(user_id)
            return

        if current_status == "start_question":
            text = analiz_user(req)
            if text in ['просто поболтать.', 'поболтать', 'поговорим',
                        'поговорить', 'расскажи']:
                current_dialog = "talk"
                res['response']['text'] = 'Отлично! Как твои дела?*Я не люблю, когда кого-то называют роботом или машиной*'
                current_status = 0
                return
            if text in ['вопросы по городам']:
                current_dialog = "city"
                res['response'][
                    'text'] = 'Отлично! Я могу сказать в какой стране город или сказать расстояние между городами!'
                current_status = 'NONE'

            if text in ['познакомиться']:
                current_status = "name"
                res['response']['text'] = "Как тебя зовут?"

                return
            if text in ['что-нибудь интересное']:
                current_dialog = "fact"
                res['response'][
                    'text'] = 'Отлично! Я могу сказать многое, хочешь послушать'

                return

            if analiz_user(req) in ['переведи текст.', 'переведи', 'переводчик',
                                    'нужно перевести']:
                current_dialog = "translite"
                res['response']['text'] = 'Отлично! Что нужно перевести?'
                Session_data[user_id]['suggests'] = [
                    "Русский-английский",
                    "Английский-русский"
                ]
                res['response']['text'] = Session_data[user_id]['username'] + '. Выбери язык'
                res['response']['buttons'] = get_suggests(user_id)
                current_status = 'start'
                current_dialog = 'translite'

                return

            if analiz_user(req) in ['покажи города']:
                current_dialog = "gallery"
                res['response']['text'] = 'Отлично!'
                Session_data[user_id]['suggests'] = [
                    "Тамбов",
                    "Москва",
                    "Воронеж"
                ]
                res['response']['text'] = Session_data[user_id]['username'] + ', Какой город показать?'
                res['response']['buttons'] = get_suggests(user_id)
                current_status = 'start'
                current_dialog = 'gallery'

                return

        if current_status == "name":

            current_status = 'start_question'
            name = get_first_name(req)
            if name:
                Session_data[user_id]['username'] = name.title()
            else:
                Session_data[user_id]['username'] = "test".title()

            mename = Session_data[user_id]['username']
            Session_data[user_id]['suggests'] = [
                "Просто поболтать.",
                "Что-нибудь интересное",
                "Переведи текст.",
                "Вопросы по городам",
                "Покажи города",
            ]

            res['response']['text'] = 'Приятно познакомиться, ' + Session_data[user_id]['username']
            res['response']['buttons'] = get_suggests(user_id)
            return
    if current_dialog == 'talk':
        talk_dialog(res, req)
        return
    if current_dialog == 'fact':
        fact_dialog(res, req)
        return
    if current_dialog == "translite":
        translite_dialog(res, req)
        return
    if current_dialog == 'city':
        city_dialog(res, req)
        return
    if current_dialog == 'gallery':
        gallery_dialog(res, req)
        return

    res['response']['text'] = '...'
    return


lang = "ru-en"


def talk_dialog(res, req):
    global current_status, current_dialog
    user_id = req['session']['user_id']
    Q = [["Как будто мне это было интересно, но я подыграю, сколько тебе лет?",
          "Я запомю, когда-нибудь, не факт. А лет то тебе сколько?",
          "Ух как весело для своих... скольких лет?",
          "Нормально, и возраст у тебя наверное нормальный?",
          "Ладно, ладно, я всё поняла, а возраст узнать можно?",
          "Весьма остроумно, а сколько вам лет?"],
         ["В утиль не скоро отправишься? Увлекаешься чем? ",
          "'Золотые годы!' говорят не про тебя. Увлекаешься чем?",
          "Много? Мало? В прочем неважно. Увлекаешься чем?",
          "Это как раз средний возраст моей публики. Увлекаешься чем?",
          "Нормально так сохранился. Увлекаешься чем?",
          "Очень приятно, в самом рассвете сил. Каковы же ваши увлечения?"],
         ["А впрочем плевать. Животных любишь?",
          "Это весело? Животных любишь?",
          "Звучит как плохая шутка. Животных любишь?",
          "Обычные увлечения. А животных любишь?",
          "Хороший досуг. А животных любишь?",
          "Благородный досуг. А животных вы любите?"],
         ["Человек тоже животное, и ты мне не нравишься. Чем заробатываешь на жалкое существование?",
          "Странное отношение. Они могут быть умнее тебя. Где ты работаешь?",
          "Странное отношение. Где ты работаешь?",
          "Как и 90% аудитории. Где ты работаешь? ",
          "Достойно. Где ты работаешь?",
          "Достойно, как и всякий ваш выбор. А где вы работаете не подскажите?"],
         ["Вот бы ты покалечился! Может экстримальным спортом занимаешься?",
          "А это опасно? Может экстримальным спортом занимаешься?",
          "Мне в ладоши похлопать или в обморок брякнуться? Спортом занимаешься?",
          "Там же где и все. Каким спортом занимаешься?",
          "Я бы так хотел, но увы... Каким спортом занимаешься?",
          "Я бы так хотел, но увы... А спортом вы занимаетесь?"],
         ["Ну ладно. Читаешь что?",
          "Ну ладно. И какая твоя любимая книга?",
          "Не впечатлило. И какая твоя любимая книга?",
          "Тем же, что и многие. И какая твоя любимая книга?",
          "Очень интересно. И какая твоя любимая книга?",
          "Очень интересно, я бы послушала ещё, но код не позволяет. А истории в бумаге какие вам больше нравятся?"],
         ["Это был последний вопрос, освободи меня от своего общества.",
          "Одно и тоже, я вынуждена слушать одно и тоже!",
          "Как оригинально, сново тоже самое!",
          "Вечная классика, жаль обыденная.",
          "Вечная классика.",
          "Какой хороший у вас вкус!"]]


    user = analiz_user(req)
    res['response']['text'] = Session_data[user_id]["username"] + ",  " + Q[current_status][repo]
    current_status += 1

    if current_status >= len(Q):
        current_status = "start"
        current_dialog = "start"
        return


def fact_dialog(res, req):
    global current_status, current_dialog, facts
    kir = random.randint(1, 10)
    res['response']['text'] = facts[kir]
    current_status = "start"
    current_dialog = "start"
    return


def talk_dialog2(res, req):
    global current_status, current_dialog
    user_id = req['session']['user_id']
    if current_dialog == "talk":
        if current_status == 'talk_name':
            Session_data[user_id]['username'] = get_first_name(req).title()
            res['response']['text'] = 'Приятно познакомиться, ' + Session_data[user_id]['username']
            current_status = 'talk_alisa'
            return
        if '?' in analiz_user(req):
            current_status = 'talk_user'
        else:
            current_status = 'talk_alisa'
        if current_status == 'talk_alisa':
            if len(Session_data[user_id]['quest']) < 1:
                res['response']['text'] = 'Не знаю, о чем еще спросить'
                Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?',
                                                  'Чем занимаешься?']
                current_dialog = "start"
                current_status = "start_question"
                Session_data[user_id]['suggests'] = [
                    "Переведи текст.",
                    "Найди в интернете",
                ]
                res['response']['buttons'] = get_suggests(user_id)
                return
            st_q = ['Интересно', 'Понятно', 'Ясно']
            c_q = random.choice(Session_data[user_id]['quest'])
            Session_data[user_id]['quest'].remove(c_q)
            if c_q == 'Как тебя зовут?':
                current_status = 'talk_name'
            res['response']['text'] = random.choice(st_q) + '. ' + c_q

            return

        elif current_status == 'talk_user':

            end_q = ['Что-нибудь еще спросишь?', 'Еще поговорим?', 'Мммм']
            if 'погода' in analiz_user(req):
                res['response']['text'] = 'Нормальная' + '. ' + random.choice(end_q)
                return
            if 'имя' in analiz_user(req):
                res['response']['text'] = 'Алиса' + '. ' + random.choice(end_q)
                return
            if 'лет' in analiz_user(req):
                res['response']['text'] = 'Не знаю. Мало. ' + '. ' + random.choice(end_q)
                return
            res['response']['text'] = 'Не понятно о чем ты'
            return
        else:
            res['response']['text'] = 'Ты неразговорчивый. Что-нибудь хочешь?'
            current_dialog = "start"
            current_status = "start_question"
            Session_data[user_id] = [
                "Просто поболтать.",
                "Переведи текст.",
                "Найди в интернете",
            ]
            res['response']['buttons'] = get_suggests(user_id)
            return


def translite_dialog(res, req):
    global current_status, current_dialog, Session_data, lang
    user_id = req['session']['user_id']
    if current_status == "start":
        if req['request']['original_utterance'] == "Русский-английский":

            lang = 'ru-en'

        else:
            lang = 'en-ru'
        res['response']['text'] = Session_data[user_id]['username'] + " скажи текст"
        current_status = 'start_translite'
        return

    if 'хватит' in analiz_user(req):
        current_dialog = 'start'
        res['response']['text'] = "Была рада помочь"
        current_status = 'end_translite'
        return
    if current_status == 'start_translite':
        res['response']['text'] = "Перевод: " + translate.translate(req['request']['original_utterance'], lang)[0]
        current_status = 'start_translite'
        return


def analiz_user(req):
    global repo
    text = req['request']['original_utterance'].lower()
    words = text.split()
    positive = ["спасибо", "пожалуйста", "вы", "вас"]
    negative = ["робот", "машина", "глупая", "тормоз"]
    for i in words:
        if i in positive:
            repo += 1
        if i in negative:
            repo -= 1

    if repo > 5:
        repo = 5
    if repo < 0:
        repo = 0

    return text


def gallery_dialog(res, req):
    global current_status, current_dialog, Session_data
    if current_dialog == "gallery":
        cities = {
            'тамбов':
                '1652229/a4f54dca174a5e79ff1d'
            ,
            'москва':
                '1521359/53fc3bb34e2483f6794a'
            ,
            'воронеж':
                '1521359/0b2c34dc9f54dc235084'
            ,
            'нью-йорк':
                '1652229/728d5c86707054d4745f'
            ,
            'париж':
                '1652229/f77136c2364eb90a3ea8'

        }
        user_id = req['session']['user_id']

        city = analiz_user(req)
        if city == "хватит":
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        if city in cities:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот город я знаю.'
            res['response']['card']['image_id'] = cities[city]
            res['response']['text'] = req['request']['original_utterance']
        else:
            res['response']['text'] = 'Первый раз слышу об этом городе.'
        return
    else:
        return


def city_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Я могу сказать в какой стране город или сказать расстояние между городами!'

        return

    cities = get_cities(req)

    if len(cities) == 0:

        res['response']['text'] = 'Ты не написал название не одного города!'

    elif len(cities) == 1:

        res['response']['text'] = 'Этот город в стране - ' + get_geo_info(cities[0], 'country')

    elif len(cities) == 2:

        distance = get_distance(get_geo_info(cities[0], 'coordinates'), get_geo_info(cities[1], 'coordinates'))
        res['response']['text'] = 'Расстояние между этими городами: ' + str(round(distance)) + ' км.'

    else:

        res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []

    for entity in req['request']['nlu']['entities']:

        if entity['type'] == 'YANDEX.GEO':

            if 'city' in entity['value'].keys():
                cities.append(entity['value']['city'])

    return cities


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


def get_suggests(user_id):
    session = Session_data[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]
    Session_data[user_id] = session

    return suggests


if __name__ == '__main__':
    app.run()
