from django.shortcuts import render
from django.http import HttpResponse
from django .shortcuts import redirect
from django.views.generic import TemplateView
from .models import AnswerModel
import random
from operator import itemgetter
import ast
from django.contrib import messages
import json
#from .forms import QuestionnaireAnswerForm

# Create your views here.
def index(request):
    return HttpResponse('survey')

class Survey(TemplateView):

    def __init__(self):
        self.params = {
            'title': 'アンケート',
            'message': '車選びで重視するものを選択してください',
            'data': ''
        }

    def get(self, request):
        user_id = int(request.session['user_id'])
        pattern = countCheck(user_id)
        rsl = selectSurvey(pattern, user_id)
        self.params['data'] = rsl
        request.session['data'] = rsl
        return render(request, 'survey/questionnaire.html', self.params)

    def post(self, request):
        #チェックされたアンケート項目を取得
        checks_value = request.POST.getlist('checks[]')
        print(request.session['data'])
        print(checks_value)
        anser_dict = {}
        #取得したアンケート項目を仕分けして適切な位置に保存
        anser_dict = checkAnswer(request.session['data'], anser_dict, False)
        anser_dict = checkAnswer(checks_value, anser_dict, True)
        #結果を格納した辞書オブジェクトをsort
        items_sorted = sorted(anser_dict.items(), key=itemgetter(0))
        anser_dict = dict(items_sorted)
        print(anser_dict)
        user_id = int(request.session['user_id'])
        pattern = countCheck(user_id)
        print(pattern)
        push(user_id, anser_dict, pattern)
        messages.success(request, 'ご回答ありがとうございました')
        del request.session['data']
        #jsonファイルを作成 (おすすめ車両AIに投げる用)
        makeJsonFile(user_id)
        return redirect(to='carsharing_req:index')






# 回答するアンケート項目を抽出
def selectSurvey(pattern, user_id):
    rsl = []
    #アンケート全項目
    survey_list = [
        (1, '乗り心地がいい'),
        (2, '荷室の使いやすさ'),
        (3, '燃費の良さ'),
        (4, '排気量の少なさ'),
        (5, '車内空間が広い'),
        (6, '静かに走る'),
        (7, '馬力がある'),
        (8, '乗車定員が多い'),
        (9, '小回りが利く'),
        (10, '乗車しやすい'),
        (11, '安全性能が高い'),
        (12, '走行性能が高い'),
        (13, '車両サイズが小さい')
    ]
    if pattern == 0:
        # survey_listの中からランダムに5つ選ぶ
        survey_list = random.sample(survey_list, 4)
        for item in survey_list:
            rsl.append(item[1])
    else:
        # 過去に答えた部分を省く (previous_answer: 蓄積データ)
        answer = AnswerModel.objects.filter(user_id=user_id).values('answer').order_by("id").last()
        previous_answer = answer['answer']
        previous_answer = ast.literal_eval(previous_answer)
        print(previous_answer)
        del_list = []
        for del_num in previous_answer:
            del_list.append(del_num)
        index = 0
        print(del_list)
        # 未回答からrandom
        if pattern == 1:
            for item in survey_list:
                if item[0] == del_list[index]:
                    if index < 3:
                        index += 1
                else:
                    rsl.append(item[1])
            print(rsl)
            rsl = random.sample(rsl, 4)
        # 未回答を抽出
        elif pattern == 2:
            for item in survey_list:
                if item[0] == del_list[index]:
                    if index < 7:
                        index += 1
                else:
                    rsl.append(item[1])
    return rsl



#今回のアンケート結果を集計する関数(list, dict, bool), <void : dict>
def checkAnswer(data, answer, flag):
    for item in data:
        if item == '乗り心地がいい':
            if flag == False:
                answer[1] = False
            else:
                answer[1] = True
        elif item == '荷室の使いやすさ':
            if flag == False:
                answer[2] = False
            else:
                answer[2] = True
        elif item == '燃費の良さ':
            if flag == False:
                answer[3] = False
            else:
                answer[3] = True
        elif item == '排気量の少なさ':
            if flag == False:
                answer[4] = False
            else:
                answer[4] = True
        elif item == '車内空間が広い':
            if flag == False:
                answer[5] = False
            else:
                answer[5] = True
        elif item == '静かに走る':
            if flag == False:
                answer[6] = False
            else:
                answer[6] = True
        elif item == '馬力がある':
            if flag == False:
                answer[7] = False
            else:
                answer[7] = True
        elif item == '乗車定員が多い':
            if flag == False:
                answer[8] = False
            else:
                answer[8] = True
        elif item == '小回りが利く':
            if flag == False:
                answer[9] = False
            else:
                answer[9] = True
        elif item == '乗車しやすい':
            if flag == False:
                answer[10] = False
            else:
                answer[10] = True
        elif item == '安全性能が高い':
            if flag == False:
                answer[11] = False
            else:
                answer[11] = True
        elif item == '走行性能が高い':
            if flag == False:
                answer[12] = False
            else:
                answer[12] = True
        elif item == '車両サイズが小さい':
            if flag == False:
                answer[13] = False
            else:
                answer[13] = True

    return answer

#回答パターン検索
def countCheck(user_id):
    answer_count = AnswerModel.objects.filter(user_id=user_id).values("count").order_by("id").last()
    #初めての回答
    if answer_count == None:
        pattern = 0
    #全件回答済
    elif answer_count['count'] == 3:
        pattern = 0
    #10件未回答
    elif answer_count['count'] == 1:
        pattern = 1
    #5件未回答
    elif answer_count['count'] == 2:
        pattern = 2

    return pattern


#DBへsave
def push(user_id, anser_dict, pattern):
    if pattern == 0:
        record = AnswerModel(user_id = user_id, answer = anser_dict)
        record.save()
    else:
        obj = AnswerModel.objects.filter(user_id=user_id).values().order_by("id").last()
        print(obj)
        count = int(obj['count']) + 1
        print(count)
        record_id = int(obj['id'])
        print(record_id)
        # 結果の追加
        previous_answer = obj['answer']
        previous_answer = ast.literal_eval(previous_answer)
        anser_dict.update(previous_answer)
        print(anser_dict)
        # 結果を格納した辞書オブジェクトをsort
        items_sorted = sorted(anser_dict.items(), key=itemgetter(0))
        anser_dict = dict(items_sorted)
        print(anser_dict)
        # update
        record = AnswerModel.objects.filter(user_id=user_id).order_by("id").last()
        record.user_id = user_id
        record.answer = anser_dict
        record.count = count
        print(record)
        record.save()



#jsonファイル作成
def makeJsonFile(user_id):
    path = '/Django/data/recommend/user_' + str(user_id) + '.json'
    data_list = list(AnswerModel.objects.filter(user_id=user_id).values("answer").order_by("id"))
    print(data_list)
    survey_list = [
        (0, '項目'),
        (1, '乗り心地がいい'),
        (2, '荷室の使いやすさ'),
        (3, '燃費の良さ'),
        (4, '排気量の少なさ'),
        (5, '車内空間が広い'),
        (6, '静かに走る'),
        (7, '馬力がある'),
        (8, '乗車定員が多い'),
        (9, '小回りが利く'),
        (10, '乗車しやすい'),
        (11, '安全性能が高い'),
        (12, '走行性能が高い'),
        (13, '車両サイズが小さい')
    ]
    json_dict = {}
    for data_str in data_list:
        data_dict = ast.literal_eval(data_str['answer'])
        print(data_dict)
        for index in range(1, 14):
            print(index)
            print(data_dict.get(index))
            print(survey_list[index][1])
            if data_dict.get(index) == True:
                json_dict[survey_list[index][1]] = data_dict.get(index)
            print(data_dict)
    # エンコード
    json_data = json.dumps(json_dict, sort_keys=True, indent=4)
    # デコード
    print(json.loads(json_data))

    # ファイルを開く(上書きモード)
    with open(path, 'w') as f:
        # jsonファイルの書き出し
        f.write(json_data)
