from flask import Flask, jsonify, request, redirect, send_from_directory
import logging
import os
from werkzeug.utils import secure_filename

import process

# the main Flask application object
app = Flask(__name__)

# текущая рабочая папка. Необходимо для сохранения скриптов
dir0 = os.getcwd()

# create logger instance
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

# global Var with Info fot Quest
Welcome = 'Name of Locate'
QuestText = 'text quest'
AnsList = '1. ans \n 2. list \n 3. for quest'
Health = 50
Invent = []

# First start. Read Scripts, Start quest 1. 
process.Init()
[QuestText, AnsList, Health, Invent, Welcome] = process.Start(1, 0)


@app.route('/favicon.ico')
def favicon():
    """Handles browser's request for favicon"""
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico'
    )

# основная команда - устанавливает информацию в окне на странице.
@app.route('/', methods=['GET'])
def get():
    global QuestText, AnsList, Health, Invent, Welcome
    """This triggers when you first open the site with your browser"""
#     assert len(inputs) == len(outputs)
    print('QT pull=',QuestText)
    return process.render(QuestText, AnsList, Health, Invent, Welcome)

# Ввод ответа, выполнение действия, обновление информации
@app.route('/enter_ans', methods=['POST'])
def enter_ans():
    global QuestText, AnsList, Health, Invent, Welcome
    answer = request.form['input_ans']
    NewInfo = process.AnswerEnter(answer)
    if NewInfo != None:
        [QuestText, AnsList, Health, Invent, Welcome] = NewInfo
    return redirect('/')

# перезапуск скрипта
@app.route('/restart', methods=['POST'])
def restart_game():
    global QuestText, AnsList, Health, Invent, Welcome
    process.Restart()
    [QuestText, AnsList, Health, Invent, Welcome] = process.Start(1, 0)
    return redirect('/')

# обновление файлов скриптов при выборе новых
@app.route('/update_path', methods=['POST'])
def update_path():
    AllF = request.files.getlist('file')
    for file in AllF:
        filename = secure_filename(file.filename)
        file.save(os.path.join(dir0, 'Scripts', filename))
    return redirect('/')

# this makes your Flask application start
if __name__ == "__main__":
    app.run(debug=True)

