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
FileStat = ''


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
    global QuestText, AnsList, Health, Invent, Welcome, FileStat
    """This triggers when you first open the site with your browser"""
#     assert len(inputs) == len(outputs)
    print('QT pull=',QuestText)
    return process.render(QuestText, AnsList, Health, Invent, Welcome, str(FileStat))

# Ввод ответа, выполнение действия, обновление информации
@app.route('/enter_ans', methods=['POST'])
def enter_ans():
    global QuestText, AnsList, Health, Invent, Welcome, FileStat
    FileStat = ''
    answer = request.form['input_ans']
    NewInfo = process.AnswerEnter(answer)
    if NewInfo != None:
        [QuestText, AnsList, Health, Invent, Welcome] = NewInfo
    else:
        FileStat = 'Ответ не принят. Проверьте введённый ответ'
    return redirect('/')

# перезапуск скрипта
@app.route('/restart', methods=['POST'])
def restart_game():
    global QuestText, AnsList, Health, Invent, Welcome, FileStat
    process.Restart()
    [QuestText, AnsList, Health, Invent, Welcome] = process.Start(1, 0)
    FileStat = 'Игра перезапущена'
    return redirect('/')

# обновление файлов скриптов при выборе новых
@app.route('/update_path', methods=['POST'])
def update_path():
    global FileStat
    FileStat=''
    print('try get file...')
    AllF = request.files.getlist('file')
    nfile=0
    upfile=0
    for file in AllF:
        filename = secure_filename(file.filename)
        if filename!="":
            nfile+=1
            File=os.path.join(dir0, 'Scripts', filename)
            file.save(File)
            with open(File, 'r', encoding='utf-8') as F:
                FileText=F.read()
            Param = ['LID=','LName=','LHello=','LVar=','\\Quest']
            g=0
            for elem in Param:
                if FileText.find(elem) == -1:
                    os.remove(File)
                    print('It is not Sqript for Quest!')
                    FileStat += 'Error: Это не похоже на файлы квеста:'+filename+'\n'
                    g=-1
                    break
            if g==0:
                FileStat+='Ok: '+filename+' save. \n'
                upfile+=1
                Location_info=FileText
                LID = Location_info[Location_info.find('LID=[')+5 :
                                     Location_info.find(']',
                                     Location_info.find('LID='))]
                for f in os.listdir(os.path.join(dir0, 'Scripts')):
                    if f!=filename:
                        scriptf = os.path.join(dir0, 'Scripts', f)
                        with open(scriptf, 'r', encoding='utf-8') as F:
                            Loctext=F.read()
                        LID2 = Loctext[Loctext.find('LID=[')+5 :
                                       Loctext.find(']',
                                       Loctext.find('LID='))]
                        if LID2 == LID:
                            os.remove(scriptf)
                            break
    FileStat+='Итого загружено {0} из {1} отправленных'.format(upfile, nfile)
    return redirect('/')

# this makes your Flask application start
if __name__ == "__main__":
    app.run(debug=True)

