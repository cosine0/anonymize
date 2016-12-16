# coding=utf-8
import re
import Levenshtein
import statistics
from datetime import datetime
import numpy as np


# anonymized, additional: list들의 list 형태
# is_quasi_identifier: bool들의 list 형태
# attribute_mapping: addtional의 각 속성이 anonymized 어느 속성에 해당하는지 인덱스의 리스트로 줌.
# 리턴 값: 재식별 위험도 %수. float형으로.
def risk(anonymized, data_types, is_sensitive_information, additional, attribute_mapping):
    if not any(is_sensitive_information):
        return 0.0
    # Transpose anonymized
    anonymized_T = np.array(anonymized)
    anonymized_T = anonymized_T.T.tolist()
    # 두 대상을 비교하기 위해서 anony list 생성. 해당 list에 걸맞는 is_sensitive list 새로 생성
    anony = []
    is_sensitive = []
    for i in range(len(attribute_mapping)):
        if attribute_mapping[i] is None:
            anony.append([None] * len(anonymized[0]))
            is_sensitive.append(None)
        else:
            anony.append(anonymized_T[attribute_mapping[i]])
            is_sensitive.append(is_sensitive_information[attribute_mapping[i]])
    anony = np.array(anony)
    anony = anony.T.tolist()
    score_list = [[1 for col in range(len(anony))] for row in range(len(additional))]
    att_list = [dict() for row in range(len(additional[0]))]
    weight(additional, att_list)
    score(additional, anony, att_list, score_list, data_types, is_sensitive)
    eccentricity = 0.00000001
    matching = [dict() for row in range(len(additional))]
    matching_set(score_list, matching, eccentricity)
    res = get_result(anonymized, matching, is_sensitive_information)
    return res


# 매칭 셋을 토대로 return value 구하기
# _anony_origial: 수정 없는 초기의 비식별된 database.
# _matching: matching set
# _is_sensitive_original: 수정 없는 초기의 민감 정보
def get_result(_anony_original, _matching, _is_sensitive_original):
    sensitive_ratio = [dict() for row in range(len(_matching))]
    count = 0
    for row in range(len(_matching)):
        for key in _matching[row].keys():
            temp = ""
            for col in range(len(_anony_original[key])):
                if _is_sensitive_original[col]:
                    temp += _anony_original[key][col]
            # dictionary에 {temp: }있으면 +1, 아니면 새로 추가
            if temp in sensitive_ratio[row].keys():
                sensitive_ratio[row][temp] += 1
            else:
                sensitive_ratio[row][temp] = 1
        total = sum(sensitive_ratio[row].values())
        criterion = 0.95
        max_ratio = 0
        for value in sensitive_ratio[row].values():
            ratio = float(value) / float(total)
            if ratio > max_ratio:
                max_ratio = ratio
        print max_ratio, total
        if max_ratio >= criterion:
            count += 1

    risk_possibility = float(count) / float(len(_matching))
    return risk_possibility


# 매칭 셋 구하기.
# _score: score 점수를 가지고 있는 list
# _matching: 함수 결과로 나오게 될 list. dictionary의 list로 이루어져 있으며, dictionary는 {인덱스: 유사도,}로 이루어짐
def matching_set(_score, _matching, _eccentricity):
    for row in range(len(_score)):
        maximum = max(_score[row])
        temp = _score[row][:]
        temp.remove(maximum)
        # maimum, second maximum 구하기
        while True:
            try:
                second_maximum = max(temp)
                if second_maximum == maximum:
                    temp.remove(second_maximum)
                else:
                    deviation = statistics.stdev(_score[row])
                    break
            except:
                second_maximum = 0
                deviation = 1
                break
        # 그 후, maximum 값과 second maximum 값이 유의미한 차이를 보이고
        # 해당 maximum을 값으로 후보를 모두 matching set에 입력
        if (maximum - second_maximum) / deviation >= _eccentricity:
            deleted_num = 0
            while True:
                _matching[row][_score[row].index(maximum) + deleted_num] = maximum
                _score[row].remove(maximum)
                deleted_num += 1
                try:
                    maximum = max(_score[row])
                    if maximum == second_maximum:
                        break
                except:
                    break


# 가중치 계산 함수. _anony 내의 각 속성마다 값의 분포를 구하여 att_list에 저장한다.
# _anony: 입력으로 들어오는 비식별 처리된 database
# _att_list: 각 attribute의 비율을 가지는 dictionary의 list
def weight(_anony, _att_list):
    att_num = len(_anony[0])
    record_num = len(_anony)
    for att in range(att_num):
        dictkeys_list = list(_att_list[att].keys())
        for record in range(record_num):
            if _anony[record][att] not in dictkeys_list:
                _att_list[att][_anony[record][att]] = 0
                dictkeys_list.append(_anony[record][att])
            _att_list[att][_anony[record][att]] += 1
        for num_dictkeys in range(len(dictkeys_list)):
            _att_list[att][dictkeys_list[num_dictkeys]] /= record_num


# score를 계산하는 함수. 내부에서 sim_case 함수를 통해 케이스가 나누어진다.
# database: 입력으로 들어오는 비식별 처리된 database
# aux_array: 입력으로 들어오는 알려진 database (물론 또다른 비식별 처리된 database여도 된다.)
# att_list: 각 attribute의 비율을 가지는 dictionary의 list
# output: score 배열을 출력
# metadata: metadata
# is_sensitive: 민감정보인가?
def score(database, aux_array, att_list, output, metadata, is_sensitive):
    for record in range(len(database)):
        for aux in range(len(aux_array)):
            res = 0
            for attribute in range(len(metadata)):
                if not is_sensitive[attribute]:
                    temp = (1 - att_list[attribute][database[record][attribute]])
                    if temp == 0:
                        temp = 1
                    res += temp * sim_case(aux_array[aux][attribute], database[record][attribute], metadata[attribute])
            output[record][aux] = round(res, 4)


# 단일 숫자 유사율 계산
def sim_num(aux, record):
    try:
        aux_pure = int(aux)
    except:
        aux_pure = 0
    try:
        record_pure = int(record)
    except:
        record_pure = 0
    if record_pure == 0:
        return 0
    diff = abs(aux_pure - record_pure)
    if diff > record_pure:
        return 0
    return 1 - diff / record_pure


# 날짜 데이터 유사율 계산
def sim_date(aux, record):
    try:
        aux_date = datetime.strptime(aux, '%Y-%m-%d')
    except:
        aux_date = datetime.strptime('9999-12-31', '%Y-%m-%d')
    try:
        record_date = datetime.strptime(record, '%Y-%m-%d')
    except:
        record_date = datetime.strptime('9999-12-31', '%Y-%m-%d')
    delta = abs(aux_date - record_date)
    if delta.days == 0:
        return 1
    elif delta.days <= 7:
        return 0.5
    else:
        return 0


# 문자열 유사율 계산. Levenshtein 알고리즘을 이용
def sim_string(aux, record):
    error = Levenshtein.distance(str(record), str(aux))
    length = len(str(record)) if len(str(record)) > len(str(aux)) else len(str(aux))
    return 1 - (error / length)


# 범위형 숫자 유사율 계산
def sim_numrange(aux, record):
    # 속성값이 10,000~20,000 처럼 범위형으로 들어오고 , \과 같은 특수문자가 들어온다면 제거해준다.
    aux_pure = re.sub('[\$\[,]', '', aux)
    record_pure = re.sub('[\$\[,]', '', record)
    # 10000~20000 등과 같을 때 1차원 배열 ( 10000 20000 ) 으로 문자를 치환 [~ => 띄어쓰기]
    aux_pure = re.sub('~', ' ', aux_pure)
    record_pure = re.sub('~', ' ', record_pure)
    # split by space
    aux_pure = aux_pure.split()
    record_pure = record_pure.split()

    if len(aux_pure) == 1:
        aux_pure.append(aux_pure[0])
    if len(record_pure) == 1:
        record_pure.append(record_pure[0])
    try:
        for i in range(len(aux_pure)):
            aux_pure[i] = float(aux_pure[i])
            aux_pure[i] = int(aux_pure[i])
    except:
        # 만일 동질집합처리 때문에 숫자가 아니라 '*'가 들어오면 의미없는 숫자[0, 1]로 대체
        aux_pure[0] = 0
        aux_pure[0] = 1
    try:
        for i in range(len(record_pure)):
            record_pure[i] = float(record_pure[i])
            record_pure[i] = int(record_pure[i])
    except:
        # 만일 동질집합처리 때문에 숫자가 아니라 '*'가 들어오면 의미없는 숫자[2, 3]로 대체. 단, aux와 겹치면 안 됌.
        record_pure[0] = 2
        record_pure[1] = 3

    # releaseD 의 범위 내에 aux 의 값이 포함되어있는지, 포함되어있다면 다음과 같이 유사도를 낸다.
    # 유사도 = (포함되는 수 개수 / 더 넓은 숫자범위)
    match = 0
    for i in range(record_pure[0], record_pure[1] + 1):
        if i in range(aux_pure[0], aux_pure[1] + 1):
            match += 1
    length = (record_pure[1] - record_pure[0] + 1) if (record_pure[1] - record_pure[0]) > (
        record_pure[1] - record_pure[0]) else (record_pure[1] - record_pure[0] + 1)
    return match / length


def sim_case(aux, record, metadata):
    if metadata == u'인덱스':
        return 0
    elif metadata == u'문자열':
        return sim_string(aux, record)
    elif metadata == u'범위':
        return sim_numrange(aux, record)
    elif metadata == u'숫자':
        return sim_num(aux, record)
    elif metadata == u'날짜':
        return sim_date(aux, record)
    raise ValueError(u'{} 올바르지 않은 타입'.format(metadata))


# 테스트 코드
if __name__ == '__main__':
    test_anonymized = \
        [[u'남자', u'고혈압', u'10대', u'서울대병원'],
         [u'남자', u'고혈압', u'10대', u'서울대병원'],
         [u'남자', u'고혈압', u'10대', u'서울대병원'],
         [u'남자', u'감기', u'10대', u'중앙병원']]
    test_data_types = [u'문자열', u'문자열', u'문자열']
    test_is_sensitive_information = [False, True, False, True]
    test_additional = [[u'10대', u'불교', u'남자']]
    test_attribute_mapping = [2, None, 0]
    print risk(test_anonymized, test_data_types, test_is_sensitive_information, test_additional, test_attribute_mapping)
