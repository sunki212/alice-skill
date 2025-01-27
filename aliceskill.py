import json
import random
import logging
import re

subject_files = ['biology.json','history.json','math.json']

# Основная фунция
def handler(body):
    logging.debug('Request: %r', body)
    #global response
    #global session_storage

    # Хранилище данных сессии
    state = body.get("state")
    session_storage = state.get("session", dict()) if state else session_storage

    response = {
        'session':body['session'],
        'version':body['version'],
        'response': {
            'end_session' : False,
        },
        'session_state': session_storage
    }

    handle_dialog(body, response)
    logging.debug('Session storage: %r', session_storage)
    logging.debug('Response: %r', response)
    return response

# Создание сессии игрока
def create_teams(response):
    session_storage = response.get('session_state')
    if session_storage.get('score') is None:
        session_storage['score'] = 0
        reply = f'''У Вас {session_storage['score']} баллов. Для игры доступны 3 квест-локации: башня колдуна, если ты хочешь проверить свои знания по математике, загадки востока, если ты хочешь проверить свои знания по истории, магический лес, если ты хочешь проверить свои знания по биологии и природоведению.  Для выбора локации скажи ее название или название предмета'''
        response['response']['text'] = reply
        response['response']['tts'] = reply
        return response

# Выбор темы и вопросов из нее
def subject_choice(request_file, response):
    session_storage = response.get('session_state')
    if 'subject' not in session_storage and 'score' in session_storage:
        if request_file['request']['command'] in ['магический лес','биология', 'природоведение', 'природа', 'лес', 'волшебный лес']: # Нужны другие возможные варианты ответа
            subject = subject_files[0]
        elif request_file['request']['command'] in ['загадки востока', 'восток', 'история', 'загадки', 'Египет', 'пустыня']: # Нужны другие возможные варианты ответа
            subject = subject_files[1]
        elif request_file['request']['command'] in ['башня колдуна', 'башня мага', 'башня волшебника', 'магическая башня', 'волшебная башня', 'башня математика', 'волшебный замок','математика']: # Нужны другие возможные варианты ответа
            subject = subject_files[2]
        else:
            response['response']['text'] = 'Извините, я вас не поняла.'
            response['response']['tts'] = 'Извините, я вас не поняла.'
            return response
        session_storage['subject'] = subject
        return
# Функция для предоставления помощи
def provide_help(response):
    help_text = (
        "Чтобы получить вопрос, скажи 'вопрос'. Отвечай на вопросы, выбирая букву правильного ответа (А, Б, В или Г).После ответа на пять вопросов, скажи 'дальше', чтобы продолжить свой путь. За каждый правильный ответ будет начислен один балл. Если ответ будет неверным, я озвучу правильный вариант. Твой итоговый балл будет озвучен в конце игры."
    )
    response['response']['text'] = help_text
    response['response']['tts'] = help_text
    return response

# Функция открытия файлика
def open_file(file_path):
    with open(f'''data/{file_path}''', 'r', encoding='utf-8') as file:
        chosen_subject = json.load(file)
        return chosen_subject

# Функция выбора 25 случайных вопросов
def create_shuffled_questions(response, num_questions=25):
    session_storage = response.get('session_state')
    story = open_file(session_storage.get('subject'))
    selected_questions = random.sample(list(story['questions'].keys()), min(num_questions, len(story['questions'])))
    return selected_questions

# Функция перехода к следующей части истории
def get_next_part(response):
    session_storage = response.get('session_state')
    story = open_file(session_storage.get('subject'))
    if session_storage["current_part"] < len(story['legend']):
        part = story['legend'][f'location{session_storage["current_part"]}']
        session_storage["current_part"] += 1
        return part
    session_storage["current_part"] = 0
    return None

# Функция перехода к следующему вопросу
def get_next_question(response):
    session_storage = response.get('session_state')
    if session_storage["current_question"] < 5:       #len(session_storage["questions"])
        question = session_storage["questions"][session_storage["current_question"]]
        session_storage["current_question"] += 1
        return question
    session_storage["current_question"] = 0
    return None

# Функция проверки ответа
def check_answer(question, request_file, response):
    session_storage = response.get('session_state')
    story = open_file(session_storage.get('subject'))
    if session_storage["answered"] == True:
        return
    user_answer = request_file['request']['command']
    right_key = story['questions'][question]['правильный ответ']
    right_value = story['questions'][question][right_key]
    right  = re.search(f'\\b{right_key}\\b', user_answer, re.IGNORECASE) is not None or \
             re.search(f'\\b{right_value.replace(","," ")}\\b', user_answer, re.IGNORECASE) is not None
    if right: 
        session_storage["score"] += 1
    return right

# Здесь происходит обработка ответов
def handle_dialog(request, response):
    session_storage = response.get('session_state')
    response_text = "Я Вас не поняла."
    response['response']['text'] = response_text
    response['response']['tts'] = response_text

    if request['session']['new'] == True:
        session_storage.update({
            "current_part": 0,
            "current_question": 0,
            "questions": [],
            "path_start": True
        })
        response['response']['text'] = "Добро пожаловать в квест Миры Знаний, юный искатель приключений! Тебя ждет путешествие по трем волшебным локациям: Башня колдуна, Магический лес и Загадки востока. Во время путешествия тебе предстоит ответить на вопросы, чтобы продолжить свой путь. За каждый правильный ответ ты будешь получать один балл. За игру можно получить 25 баллов. Собери максимальное количество баллов и стань мастером знаний! Скажи начинаем, если готов."
        response['response']['tts'] = "Добро пожаловать в квест Миры Знаний, юный искатель приключений! Тебя ждет путешествие по трем волшебным локациям: Башня колдуна, Магический лес и Загадки востока. Во время путешествия тебе предстоит ответить на вопросы, чтобы продолжить свой путь. За каждый правильный ответ ты будешь получать один балл. За игру можно получить 25 баллов. Собери максимальное количество баллов и стань мастером знаний! Скажи начинаем, если готов."
        return response
    if request['request']['command'] in ["помощь", "помоги", "инструкция", "не понимаю", "непонятно", "повтори инструкцию"]:
        return provide_help(response)
    if 'score' not in session_storage and request['request']['command'] in ["дальше","далее","поехали","начинаем", "начнем", "давай", "начинай"]:
        create_teams(response)
        return
    if session_storage.get('score') is not None and session_storage.get('subject') is None:
        subject_choice(request, response)
        subject = session_storage.get('subject')
        if subject:
            chosen_subject = open_file(subject)
            if chosen_subject:
                session_storage["questions"] = create_shuffled_questions(response, num_questions=25)
                response['response']['text'] = chosen_subject['start']
                response['response']['tts'] = chosen_subject['start']
        return response
    elif request['request']['command'] in ["дальше","далее","поехали","начинаем", "начнем", "давай", "начинай", "да"] and session_storage['path_start']:
        part_text = get_next_part(response)
        session_storage['path_start'] = False
        if part_text:
            response_text = f"{part_text} Скажи 'вопрос', чтобы ответить на вопросы."
            response['response']['text'] = response_text
            response['response']['tts'] = response_text
            return response
        else:
            if subject:
                chosen_subject = open_file(subject)
                response_text = f"{chosen_subject['ending']} Наше приключение подошло к концу, мы набрали {session_storage['score']} баллов. Отлично!"
                response['response']['text'] = response_text
                response['response']['tts'] = response_text
                response['response']['end_session'] = True
                return response
    elif request['request']['command'] in ["вопрос"]:
        question = get_next_question(response)
        session_storage["started_questioning"] = True
        subject = session_storage.get('subject')
        if question and subject:
            chosen_subject = open_file(subject)
            if chosen_subject:
                options = f'''А: {chosen_subject['questions'][question]['а']}, Б: {chosen_subject['questions'][question]['б']}, В: {chosen_subject['questions'][question]['в']}, Г: {chosen_subject['questions'][question]['г']}'''
                response_text = f"Вопрос: {question}. Варианты: {options}"
                session_storage["answered"] = False
                response['response']['text'] = response_text
                response['response']['tts'] = response_text
            return response
        else:
            response_text = "Вопросы закончились. Скажи 'дальше', чтобы продолжить историю."
            response['response']['text'] = response_text
            response['response']['tts'] = response_text
            session_storage["started_questioning"] = False
            session_storage['path_start'] = True
            return response

    if session_storage.get("started_questioning", False): # значит текущий режим - получение ответа от юзера
        subject = session_storage.get('subject')
        if subject is None:
            return

        chosen_subject = open_file(subject)
        if chosen_subject is None:
            return

        question = session_storage["questions"][session_storage["current_question"] - 1]
        if question and check_answer(question, request, response) and not session_storage.get("answered", False):
            response_text = "Правильно! Скажи 'вопрос', чтобы продолжить."
            session_storage["answered"] = True
            response['response']['text'] = response_text
            response['response']['tts'] = response_text
            session_storage["questions"].remove(question)
            return response
        elif chosen_subject and not session_storage.get("answered", False):
            response_text = f"Неправильно. Правильный ответ: {chosen_subject['questions'][question][chosen_subject['questions'][question]['правильный ответ']]}. Скажи 'вопрос', чтобы продолжить."    
            session_storage["answered"] = True
            response['response']['text'] = response_text
            response['response']['tts'] = response_text
            session_storage["questions"].remove(question)
            return response
