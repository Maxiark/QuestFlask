import io
import json
import logging
import sys
import os

from flask import jsonify, render_template


# create logger instance
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
            
def render(text, anslist, health, invent, welcome, status):
    """"""
    return render_template(
        'QuestWindow.html',
        data=zip([text], [anslist], [health], [invent], [welcome], [status])
#        текст квеста, список ответов, здоровье, инвентарь
    )


# Вывод текста с переносом строк (длина строки - lenght). 
#     (Абзацы вставляюся вместо пробелов)
def StrCut(text, lenght):
    if len(text) <= lenght:
        res = text
    else:
        n = len(text)//lenght
        
        res=''
        for i in range(n+1):
            si = 0
            si2 = 0
            while si < lenght and si>-1:
                si2 = si
                si = text.find(' ',si+1)
            res += text[:si2]+'\n'
            text = text[si2:]
        res = res[:-1]
        res += ' '+text
    return res


#         запуск сценария (номер локации, номер квеста в ней)
def Start(LNum, QNum):
    global LL, P, Curent_Quest, Curent_Locate, CurentAnsList
    print('Starting... ', LNum, QNum)
#    дополнительные переменный для работы команд из сценария (P,L,Q)
    NextLocate = list(filter(lambda x: int(x.ID) == int(LNum), LL))[0]
    L = NextLocate
    NextQuest = list(filter(lambda x: int(x.ID) == int(QNum),
                            L.Quests_list))[0]
    Q = NextQuest
    
#             проверка наличия условий для запуска данного скрипта
    g = 0
    for check in Q.CheckList:
        if check != '':
            if eval(check[:check.index(':')]) == False:
#                   выполнение иного квеста, если проверка не пройдена:
                print('Запуск другого квеста')
                exec(check[check.index(':')+1:].strip())
                g=1
            
#       если условий нет или проверка пройдена, то запускать этот квест. 
    if g == 0:
#                 счётчик вызова данного квеста
        Q.count += 1
#                 установка данного квеста как текущего
        Curent_Locate = L
        Curent_Quest = Q
        with open(os.path.join(dir0, 'log.txt'),'a') as log_e:
            log_e.write('ok, set Quest:'+str(LNum)+
                        ' - '+str(QNum)+'\n')
        
#                 Применение эффектов при старте квеста. 
        for eff in Curent_Quest.Effects:
            if eff != '':
                exec(eff.strip())
                with open(os.path.join(dir0, 'log.txt'), 'a') as log_e:
                    log_e.write('\t\t Effects now: '+
                                eff.strip()+'\n')
                
#                 Обновление информации в окне:
    return(SetInfo())
    

def SetInfo():
    global P, Curent_Locate, Curent_Quest, CurentAnsList
    L = Curent_Locate
    Q = Curent_Quest
    
    
#             Проверка снижения здоровья до нуля.
    if P.Health <= 0 and P.Status == 'Жив':
        P.Dead()
        Start(0,0)
    
#       применение эффекта Токсин - снижение здоровья на каждое действие. 
    if 'Toxin' in P.Effects:
        P.Health -= 1
    
#    заголовок локации, текст, инвентарь перса
    Welcome = Curent_Locate.Name
    
    TextQuest = Curent_Quest.Text
    
    StrInv=''
    for thing in P.Inventory:
        StrInv += str(thing)+'\t  |  \t'
    InvList = StrInv
    
#             установка списка вариантов ответа
    S=''
    n=1
    CurentAnsList = []
#             проверка доступности варианта
    for Ans1 in Curent_Quest.AnsName:
        ians = Curent_Quest.AnsName.index(Ans1)
        CheckCond = Curent_Quest.AnsCheck[ians].replace('"','\'')
        if CheckCond == '':
            S+=str(n)+'. '+Ans1+'\n'
            n+=1
            CurentAnsList.append(Ans1)
        elif eval(CheckCond) == True:
            S+=str(n)+'. '+Ans1+'\n'
            n+=1
            CurentAnsList.append(Ans1)
    AnsList = ('Возможные действия: \n'+S[:-1])
    
    return([TextQuest, AnsList, P.Health, InvList, Welcome])
    
#         приём ответа 
def AnswerEnter(ans):
    global Curent_Locate, Curent_Quest, CurentAnsList
#             убираем лишние пробелы
    ans = ans.strip()
    print('ans strip: ', ans)
    print('anslist: ', CurentAnsList)
    qi = None # индекс выбранного варианта
#             проверяем наличие текстового варианта (без учёта регистра)
    if ans.upper() in Curent_Quest.AnsName:
        qi = Curent_Quest.AnsName.index(ans.upper())
#             проверка численного ввода варианта
    elif ans.isdigit():
        if int(ans) in range(1,len(CurentAnsList)+1):
            elem = CurentAnsList[int(ans)-1]
            qi = Curent_Quest.AnsName.index(elem)
            
#                 если варианта нет, то вывод ошибки. 
        else:
            print('Wrong!')
            
    else:
        print('Wrong!')
        
    print('ok, qi=', qi)    
#                 Если вариант всё же найден - запуск следующего квеста
    if qi != None:
        qnid = Curent_Quest.AnsNextQ[qi] # ID следующего квеста
        
#                 проверка на пересылку в другую локацию (другой сценарий)
        if '-' in qnid:
            LocID = int(qnid[:qnid.index('-')])
            NextLocate = list(filter(lambda x:
                                     int(x.ID) == int(LocID), LL))[0]
            Curent_Locate = NextLocate
            qnid = int(qnid[qnid.index('-')+1:])
            NextQuest = list(filter(lambda x: int(x.ID) == int(qnid),
                                    Curent_Locate.Quests_list))[0]
            Curent_Quest = NextQuest
            
            
#                 если квест в этой локации:
        else:
            qnid = int(qnid.replace('.0', ''))
            with open(os.path.join(dir0, 'log.txt'),'a') as log_e:
                log_e.write('ok, go to QID:'+str(qnid)+'\n')
            print('ok, go to QID=', qnid)
            
#                     установка нужного квеста текущим:
            NextQuest = list(filter(lambda x: x.ID == qnid,
                                    Curent_Locate.Quests_list))[0]
            Curent_Quest = NextQuest
            
#             запуск найденного квеста
        resInfo = Start(Curent_Locate.ID, Curent_Quest.ID)
        return resInfo
    
#         Перезагрузка игры:
def Restart():
    P.Reset()
    Reset()
    Start(1, 0)
    
#   Класс игрока. Вообще используется 1, но можно добавить профили. 
class Player:
    def __init__(self, Name='Безымянный'):
        self.Name = Name
        self.Health = 100
        self.Inventory = []
        self.Progress = {}
        self.Status = 'Жив'
        self.Effects = []
    
    def Dead(self):
        self.Health = 0
        self.Status = 'Мёртв'
        self.Inventory = []
        self.Effects = []
    
    def Reset(self):
        self.Health = 100
        self.Inventory = []
        self.Progress = {}
        self.Status = 'Жив'
        self.Effects = []

#             Класс квеста (текущих заданий в локации)
class Quest:
    def __init__(self, info, answers):
        self.ID = int(info[info.find('QID=[')+5:info.find(']',
                           info.find('QID=['))])
        self.CheckList = list(info[info.find('QCheck=[')+8 : info.find(']',
                                   info.find('QCheck=['))].split(';'))
        self.Text = info[info.find('QText=[')+7 : info.find(']',
                         info.find('QText=['))]
        self.Effects = (info[info.find('QEffect=[')+9:info.find(']',
                             info.find('QEffect=['))]).split(';')
        self.count = 0
        self.Var = (info[info.find('QVar=[')+6 : info.find(']',
                         info.find('QVar=['))])
        if self.Var == '':
            self.Var = {}
        else:
            d = {}
            self.Var = list(self.Var.split(';'))
            for vari in self.Var:
                vari = list(vari.split(':'))
                d.update({vari[0]:vari[1]})
            self.Var = d
            
        self.AnsName = []
        self.AnsCheck = []
        self.AnsNextQ = []
        for ans in answers:
            self.AnsName.append(ans[ans.find('qatext=[')+8 : ans.find(']',
                                    ans.find('qatext=['))].upper())
            self.AnsCheck.append(ans[ans.find('qacheck=[')+9 : ans.find(']',
                                     ans.find('qacheck=['))])
            self.AnsNextQ.append(str(ans[ans.find('qn=[')+4 : ans.find(']',
                                         ans.find('qn=['))]))
            
        
#     Класс локаций (в т.ч. чтение сценариев и формирование квестов данной локации в init)
class Location:
    def __init__(self, File):
        with open(File, 'r', encoding='utf-8') as F:
            LocalStr=F.read()
                    
        self.Location_info = LocalStr.split('\\Quest')[0]
        self.Quests_Info_list=LocalStr.split('\\Quest')[1::]
        self.Quests_list=[]
        for questinfo in self.Quests_Info_list:
            q_ans_list = questinfo.split('\qa')[1::]
            q_info = questinfo.split('\qa')[0]
            self.Quests_list.append(Quest(q_info, q_ans_list))
        
        self.ID = self.Location_info[self.Location_info.find('LID=[')+5 :
                                     self.Location_info.find(']',
                                     self.Location_info.find('LID='))]
        self.Name = self.Location_info[self.Location_info.find('LHello=[')+8 :
                                       self.Location_info.find(']',
                                       self.Location_info.find('LHello='))]
        self.ID_Name = self.Location_info[self.Location_info.find('LName=[')+7 :
                                          self.Location_info.find(']',
                                          self.Location_info.find('LName='))]
        self.Var = (self.Location_info[self.Location_info.find('LVar=[')+6 :
                                       self.Location_info.find(']',
                                       self.Location_info.find('LVar='))])
        
        if self.Var == '':
            self.Var = {}
        else:
            d = {}
            self.Var = list(self.Var.split(';'))
            for vari in self.Var:
                vari = list(vari.strip().split(':'))
                if vari[1].isdigit():
                    vari[1] = int(vari[1].strip())
                d.update({vari[0]:vari[1]})
            self.Var = d
    
#     Перезагрузка игры. Чтение сценариев заново, формирование нового списка локаций. 
def Reset():
    print('Reset!')
    fi=0
    for f in os.listdir(pf):
        scriptf = os.path.join(pf,f)
        LL[fi] = Location(scriptf)
        fi+=1
    with open(os.path.join(dir0, 'log.txt'),'w') as log_e:
            log_e.write('Start Quest')

def Init():
    global dir0, pf, pf0, P, LL, Curent_Locate, Curent_Quest
    # path to programm and scripts defolt
    dir0 = os.getcwd()
    pf = os.path.join(dir0,'Scripts')
    pf0 = pf


    #     Объявление игрока и формирование списка локаций (чтение сценариев)
    P = Player()
    LL=[]
    for f in os.listdir(pf):
        scriptf = os.path.join(pf,f)
        LL.append(Location(scriptf))

    Curent_Locate = LL[0]
    Curent_Quest = LL[0].Quests_list[0]

    Restart()
