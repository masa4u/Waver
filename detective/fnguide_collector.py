# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import requests
from io import BytesIO
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pprint
import csv
import xmltodict
import os
from multiprocessing import pool, Process

marketTxt = None


def getConfig():
    import configparser
    global path, django_path, main_path
    config = configparser.ConfigParser()
    config.read('config.ini')
    path = config['COMMON']['PROJECT_PATH']
    django_path = path + r'\MainBoard'
    main_path = django_path + r'\MainBoard'


def fileCheck(workDir, code, name, type):
    filename = r"%s\financeData_%s_%s_%s.html" % (workDir,
                                                   name,
                                                   code,
                                                   type)
    # print(filename)
    # print(os.path.isfile(filename))
    # if os.path.isfile(filename):
    #     print(os.stat(filename).st_size, os.stat(filename).st_size > 0)
    return os.path.isfile(filename) and os.stat(filename).st_size > 0


def saveFile(workDir, code, name, type, xml, mode='wb', encoding='utf8'):
    if mode[-1] == 'b':
        file = open(r"%s\financeData_%s_%s_%s.html" % (workDir,
                                                       name,
                                                       code,
                                                       type), mode=mode)
    else:
        file = open(r"%s\financeData_%s_%s_%s.html" % (workDir,
                                                       name,
                                                       code,
                                                       type), mode=mode, encoding=encoding)
    # print(file.name)
    file.write(xml)
    file.close()


def getFinanceData(cmd):
    import sys
    import os
    import django
    getConfig()
    sys.path.append(django_path)
    sys.path.append(main_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MainBoard.settings")
    django.setup()
    import detective_app.models as detective_db
    global marketTxt

    yyyymmdd = str(datetime.now())[:10]
    url = "http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp"
    reportType = {
        101: 'snapshot',
        103: 'financeReport',
        104: 'financeRatio'
    }  # 101 : snapshot, 103 : financeReport, 104 : financeRatio
    urlInfo = {
        101: 'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp',
        103: 'http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp',
        104: 'http://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp'
    }

    # reportType = {
    #     # 101: 'snapshot',
    #     103: 'financeReport'
    # }  # 101 : snapshot, 103 : financeReport, 104 : financeRatio
    # urlInfo = {
    #     # 101: 'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp',
    #     103: 'http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp'
    # }

    data = {
        'pGB': 1,
        'gicode': '',
        'cID': '',
        'MenuYn': 'Y',
        'ReportGB': 'D',  # D: 연결, B: 별도
        'NewMenuID': 0,
        'stkGb': 701,
    }

    xmlString = ''

    try:
        '''
        for key in reportType.keys():
            workDir = r'E:\Github\Waver\detective\reports\%s\%s' % (reportType[key], yyyymmdd)
            if not os.path.exists(workDir):
                os.makedirs(workDir)

            data['NewMenuID'] = key
            data['gicode'] = 'A005930'
            response = httpRequest(urlInfo[key], data)
            # ##############################################################Using pandas
            # tables = pd.read_html(response.decode('utf-8'), header=0)
            # for t in tables:
            #     print(t)
            # ##############################################################Using beautifulSoup
            soup = BeautifulSoup(response.decode('utf-8'), "lxml")
            # tables = soup.find_all('table')
            divs = soup.find_all('div')
            for d in divs:
                if len(d.attrs) > 0 and 'class' in d.attrs.keys() and d.attrs['class'] in [['ul_col2wrap', 'pd_t25']]:
                    column_name = []
                    data_header = ''
                    column_data = []
                    data_information = {}
                    report_name = d.find('div').find('div').find('div').get_text().replace('\n', '')
                    for th in d.table.thead.find_all('th'):
                        # print(th.get_text())
                        if th.get_text() == 'IFRS(연결)':
                            continue
                        else:
                            column_name.append(th.get_text())

                    for tr in d.table.tbody.find_all('tr'):
                        data_header = ''
                        if tr.attrs['class'] == ['tbody_tit']:  # 표 이름은 저장하지 않음
                            continue
                        elif 'acd_dep2_sub' in tr.attrs['class']:  # 하위의 BackData 는 저장하지 않음
                            continue
                        elif 'acd_dep_start_close' in tr.attrs['class']:
                            data_header = tr.th.div.div.dl.dt.get_text()
                            column_data = []
                            # print(data_header)
                            # print(tr.th.div.div.dl.dt.get_text(), prev_column)
                            for td in tr.find_all('td'):
                                if len(td.find_all('span')) > 0:
                                    column_data.append(td.span.get_text())
                                else:
                                    column_data.append(td.get_text())
                        data_information[data_header] = column_data
                    print(report_name, column_name)
                    for dh in data_information.keys():
                        print(dh, data_information[dh])
                    # if d.attrs['id'] == 'divSonikY':
                    # dynamic_parse_table(d.attrs['id'], d.table)
                    print('\n\n\n\n\n')
            # for t in tables:
            #     if t
            #     dynamic_parse_table(t)
            #     parse_html_table(t)
            # xml = soup.prettify(encoding='utf-8').replace(b'&', b'&amp;')
            # file = open(r"%s\financeData_%s_%s_%s.txt" % (workDir,
            #                                               '삼성전자',
            #                                               '005930',
            #                                               reportType[key]), "wb")
            # file.write(xml)
            # file.close()
        '''  # FinanceReport 성공
        stockInfo = detective_db.Stocks.objects.filter(listing='Y')
        # stockInfo = detective_db.Stocks.objects.filter(code='005930', listing='Y')
        for key in reportType.keys():
            # print(cmd, cmd and key != cmd)
            if cmd and key != cmd:
                continue
            workDir = r'C:\Github\Waver\detective\reports\%s\%s' % (reportType[key], yyyymmdd)
            if not os.path.exists(workDir):
                os.makedirs(workDir)

            data['NewMenuID'] = key
            for idx, s in enumerate(stockInfo):
                # print(fileCheck(workDir, s.code, s.name, reportType[key]))
                if fileCheck(workDir, s.code, s.name, reportType[key]):
                    print('[%d/%d][%s][%s][%s] File is already exist. Skipped...' % (idx+1, len(stockInfo), reportType[key], s.code, s.name))
                    continue
                print('[%d/%d][%s][%s][%s] File is on process...' % (idx+1, len(stockInfo), reportType[key], s.code, s.name))
                data['gicode'] = 'A%s' % s.code
                response = httpRequest(urlInfo[key], data)
                soup = BeautifulSoup(response.decode('utf-8'), "lxml")
                # File 처리
                xml = soup.prettify(encoding='utf-8').replace(b'&', b'&amp;')
                # p = Process(target=saveFile, args=(workDir, s, reportType[key], xml))
                # p = Process(target=saveFile, args=(workDir, s.code, s.name, reportType[key], xml))
                # p.start()
                # p.join()
                saveFile(workDir, s.code, s.name, reportType[key], xml)

                # File 처리 끝
                # DB 처리
                # marketTxt = select_by_attr(soup, 'span', 'id', 'strMarketTxt').text
                # if marketTxt and key == 'snapshot':
                #     StockMarketTextUpdate(s.code, marketTxt)
                #     marketTxt = None
                # divs = soup.find_all('div')
                # if reportType[key] in ['snapshot', 'financeReport']:
                #     for d in divs:
                #         if 'id' in d.attrs.keys():
                #             # if ('div' in d.attrs['id'] or 'highlight' in d.attrs['id']) and 'um_table' in d.attrs['class']:
                #             if 'div' in d.attrs['id'] and 'um_table' in d.attrs['class']:
                #                 # print(d.attrs['id'], d.attrs['class'])
                #                 # if d.attrs['id'] == 'divSonikY':
                #                 dynamic_parse_table(d.attrs['id'], d.table, s.code, s.name)
                #                 # print('\n\n\n\n\n')
                #             # 20180418
                #             elif 'highlight_D' in d.attrs['id'] and 'um_table' in d.attrs['class']:
                #                 if 'highlight_D_A' == d.attrs['id']:
                #                     continue
                #                 # print(d.attrs['id'], d.attrs['class'])
                #                 dynamic_parse_table(d.attrs['id'], d.table, s.code, s.name)
                #             elif 'svdMainGrid' in d.attrs['id'] and 'um_table' in d.attrs['class']:
                #                 # print(d.attrs['id'], d.attrs['class'])
                #                 dynamic_parse_table(d.attrs['id'], d.table, s.code, s.name)
                #     # DB 처리 끝
                # else:
                #     static_parse_table(divs, s.code, s.name)
        # FinanceReport 성공 끝

        '''
        stockInfo = detective_db.Stocks.objects.all()
        for key in reportType.keys():
            data['NewMenuID'] = key
            for idx, s in enumerate(stockInfo):
                data['gicode'] = 'A%s' % s.code
                response = httpRequest(urlInfo[key], data)
                soup = BeautifulSoup(response.decode('utf-8'), "lxml")
                xml = soup.prettify(encoding='utf-8').replace(b'&', b'&amp;')
                file = open(r"%s\financeData_%s_%s_%s.txt" % (rootDir,
                                                              s.name,
                                                              s.code,
                                                              reportType[key]), "wb")
                file.write(xml)
                file.close()
        '''
        print("FnGuideDataCollection job finished")
    except Exception as e:
        print(e)

    # result = xmltodict.parse(xml)
    # print(result)
    # print(type(tagList), type(tagList[0]), dir(tagList[0]))
    # ll = soup.find_all()
    # for l in ll:
    #     print(type(l))
    # print(xmlString)
    # print(soup.find_all())
    # result = xmltodict.parse(soup.getText())
    # print(result)


def dynamic_parse_table(table_id, table, crp_cd, crp_nm, t_hierarchy=None, c_hierarchy=None):
    n_columns = 0
    n_rows = 0

    prev_column = ''
    prev_column_no = None
    prev_row = ''
    prev_row_no = None

    report_name = ''
    categorizing = ''

    data_information = {}
    column_names = []
    data_pipe = []

    if table_id[-1:] in ['Y', 'Q']:
        if table_id[-1:] == 'Y':
            categorizing = 'YEARLY'
        elif table_id[-1:] == 'Q':
            categorizing = 'QUARTERLY'
        if table_id.find('Sonik') > -1:
            report_name = '포괄손익계산서'
        elif table_id.find('Daecha') > -1:
            report_name = '재무상태표'
        elif table_id.find('Cash') > -1:
            report_name = '현금흐름표'
        elif table_id.find('highlight') > -1:
            report_name = 'FinancialHighlight'

    else:
        if table_id.find('svdMainGrid') > -1:
            report_name = table_id
        else:
            pass
    table_hierarchy = {
        'HorizonHeader': 'thead-tr-th',
        'VerticalHeader': 'tbody-tr-th-div-span',
        'Data': 'tbody-tr-td'
    }
    content_hierarchy = {
        'column': {'TargetTag': 'tr',
                   'Attribute': 'class',
                   'Hierarchy': ['acd_dep_start_close', 'acd_dep2_sub']
                   },
        'row': []
    }

    if t_hierarchy is None:
        pass
    else:
        table_hierarchy = t_hierarchy

    if c_hierarchy is None:
        pass
    else:
        content_hierarchy = t_hierarchy

    tmpHierarchy = table_hierarchy['HorizonHeader'].split('-')

    for tag1 in table.find_all(tmpHierarchy[0]):  # thead
        if tag1.text == '' or tag1.text == '\n':
            pass
        for tag2 in tag1.find_all(tmpHierarchy[1]):  # tr
            for tag3 in tag2.find_all(tmpHierarchy[2]):  # th
                if tag3.text == '전년동기':
                    temp = column_names[-1]
                    period = temp.split('/')
                    column_names.append('%d/%s' % (int(period[0]) - 1, period[1]))
                elif tag3.text in ['Annual', 'Net Quarter']:
                    pass
                elif '(E)' in tag3.text:
                    tmpTag = tag3.text.replace('\n', '').replace('(E) : Estimate컨센서스, 추정치', '')
                    column_names.append(tmpTag)
                elif '(P)' in tag3.text:
                    tmpTag = tag3.text.replace('\n', '').replace('(P) : Provisional잠정실적', '')
                    column_names.append(tmpTag)
                else:
                    column_names.append(tag3.text.replace('\n', '').strip())

    tmpHierarchy = table_hierarchy['VerticalHeader'].split('-')
    dataHierarchy = table_hierarchy['Data'].split('-')

    get_table_row_header(table, tmpHierarchy, dataHierarchy, content_hierarchy, data_information, prev_column,
                         data_pipe)
    if report_name.startswith('svdMainGrid'):
        # print(report_name)
        caption = report_name.replace('svdMainGrid', get_table_contents(table, 'caption')[0])
        column_names, keys, values = setting(get_table_contents(table, 'thead tr th'),
                                             get_table_contents(table, 'tbody tr th'),
                                             get_table_contents(table, 'tbody tr td'))
        if len(keys) == 0:
            # print("[%s][%s][%s] Data is on Processing" % (crp_cd, crp_nm, report_name))
            # if report_name == 'svdMainGrid10D':
            # print(column_names)
            # print(keys)
            # print(values)
            DailySnapShotDataStore(report_name, crp_cd, crp_nm, caption, column_names, '', values)
        else:
            # if report_name == 'svdMainGrid10D':
            # print(column_names)
            # print(keys)
            # print(values)
            # print("[%s][%s][%s] Data is on Processing" % (crp_cd, crp_nm, report_name))
            for idx1, key in enumerate(keys):
                DailySnapShotDataStore(report_name, crp_cd, crp_nm, caption, column_names, key, values[idx1])
    else:
        # print("[%s][%s][%s][%s] Data is on Processing" % (crp_cd, crp_nm, report_name, categorizing))
        return column_names, data_information  # DB저장 빼고 파일에서 직접 읽어오기위해 처리
        # for di in data_information.keys():
        #     # print(categorizing, column_names)
        #     # print(di, data_information[di])
        #     ## 20180504
        #     if report_name == 'FinancialHighlight':
        #         # print(table.text)
        #         # get_table_contents(table, 'tbody tr th')
        #         # get_table_contents(table, 'tbody tr td')
        #         # print("FinancialHighlight")
        #         SnapShotDataStore(report_name, crp_cd, crp_nm, categorizing, column_names, di, data_information[di])
        #     else:
        #         # print(report_name)
        #         # get_table_contents(table, 'tbody tr th')
        #         # get_table_contents(table, 'tbody tr td')
        #         # print("FinancialReportDataStore")
        #         FinancialReportDataStore(report_name, crp_cd, crp_nm, categorizing, column_names, di, data_information[di])
        #     ## 20180504
        #     # for idx, column_name in enumerate(column_names[1:]):
        #     #     period_info = column_name.split('/')
        #     #     if len(period_info) < 2:
        #     #         continue
        #     #     print(report_name, crp_cd, crp_nm, categorizing, period_info[0], period_info[1],
        #     #           str(int(period_info[1])/3)[0]+'Q', di, data_information[di][idx])


def get_table_row_header(rs, hierarchy, hierarchy2, c_hierarchy, data_information, prev_column, data_pipe, level=0):
    # print(('~~~~~~~~~~~~~~~~~~~~~~~' + prev_column) * 1)
    # print(level, '*' * 20)
    # if level > 0:
    #     print(level, len(rs))
    i = level
    isTarget = False
    isUpper = False
    # data = data_pipe
    try:
        if len(hierarchy) < i + 1:
            pass
        else:
            # print(('~~~~~~~~~~~~~~~~~~~~~~~' + prev_column) * 2)
            if hierarchy[i] == c_hierarchy['column']['TargetTag']:
                isTarget = True
            for tag in rs.find_all(hierarchy[i]):
                isUpper = False
                if isTarget and c_hierarchy['column']['Attribute'] in tag.attrs.keys():
                    for attr in tag.attrs[c_hierarchy['column']['Attribute']]:
                        if c_hierarchy['column']['Hierarchy'][0] == attr:
                            isUpper = True
                # print('else4', hierarchy[i+1])
                # if len(tag.find_all(hierarchy[i+1])):
                if hierarchy[i] == 'tr' and len(tag.find_all(hierarchy2[len(hierarchy2) - 1])):
                    data_pipe = get_data_content(tag, hierarchy2, len(hierarchy2) - 1)
                if is_exist_more_information(tag, hierarchy, i + 1):
                    # print(tag)
                    if isTarget and isUpper:
                        # print('if isTarget and isUpper:' * 5)
                        prev_column = get_text_content(tag, hierarchy, prev_column, len(hierarchy) - 1).replace(u'\xa0',
                                                                                                                '')
                        # print('if isTarget and isUpper:' * 5)
                        # print(('~~~~~~~~~~~~~~~~~~~~~~~' + prev_column) * 3)
                    # if 'class' in tag.attrs.keys(): print(tag.attrs['class'])
                    if 'class' in tag.attrs.keys() and \
                            tag.attrs[c_hierarchy['column']['Attribute']] in [['rwf', 'rowBold'], ['rwf', '']]:
                        prev_column = ''
                    get_table_row_header(tag,
                                         hierarchy,
                                         hierarchy2,
                                         c_hierarchy,
                                         data_information,
                                         prev_column,
                                         data_pipe,
                                         i + 1)
                else:
                    # print(tag)
                    # print(get_data_content(tag, hierarchy2, len(hierarchy2)-1))
                    # print(('~~~~~~~~~~~~~~~~~~~~~~~' + prev_column) * 4)
                    if prev_column == '' or tag.text.replace(u'\xa0', '') == prev_column:
                        data_information[tag.text.replace(u'\xa0', '').replace('\n', '').strip()] = data_pipe
                    else:
                        data_information[
                            prev_column + '-' + tag.text.replace(u'\xa0', '').replace('\n', '').strip()] = data_pipe
                    # print(data_information)
                    break
    except Exception as e:
        print(e)


def get_data_content(rs, hierarchy, level):
    retResult = []
    for tag in rs.find_all(hierarchy[level]):
        retResult.append(tag.text.replace(u'\xa0', 'None').replace('\n', '').strip())
    return retResult


def get_text_content(rs, hierarchy, prev_column, level):
    # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n', prev_column, '\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    retStr = prev_column
    if len(hierarchy) < level + 1:
        return None
    for tag in rs.find_all(hierarchy[level]):
        # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n', tag, '\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        if is_exist_more_information(tag, hierarchy, level + 1):
            get_text_content(tag, hierarchy, prev_column, level + 1)
        else:
            # print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%', tag, '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            # print(tag.attrs['class'], tag.attrs)
            if tag.attrs['class'] in [['tcr'], ['blind']]:
                pass
            else:
                if tag.text == retStr:
                    pass
                else:
                    retStr = tag.text.replace('\n', '').strip()
        # print('*'*20)
        # print(retStr)
        # print('*' * 20)
    return retStr


def is_exist_more_information(rs, hierarchy, level):
    if len(hierarchy) < level + 1:
        return 0
    return len(rs.find_all(hierarchy[level]))


def StockMarketTextUpdate(crp_cd, market_text):
    import sys
    import os
    import django
    from datetime import datetime
    # sys.path.append(r'E:\Github\Waver\MainBoard')
    # sys.path.append(r'E:\Github\Waver\MainBoard\MainBoard')
    getConfig()
    sys.path.append(django_path)
    sys.path.append(main_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MainBoard.settings")
    django.setup()
    import detective_app.models as detective_db
    try:
        detective_db.Stocks.objects.filter(code=crp_cd).update(market_text=market_text)
    except Exception as e:
        print('[Error on StockDataUpdate]\n', '*' * 50, e)


def DailySnapShotDataStore(report_name, crp_cd, crp_nm, caption, column_names, key, data_list):
    import sys
    import os
    import django
    from datetime import datetime
    getConfig()
    sys.path.append(django_path)
    sys.path.append(main_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()
    import detective_app.models as detective_db
    try:
        for idx, column_name in enumerate(column_names):
            info = detective_db.FnGuideDailySnapShot.objects.update_or_create(rpt_nm=caption,
                                                                              rpt_tp='',
                                                                              crp_cd=crp_cd,
                                                                              crp_nm=crp_nm,
                                                                              disc_date=datetime.now().strftime(
                                                                                  '%Y-%m-%d'),
                                                                              column_nm=column_name,
                                                                              key=key,
                                                                              defaults={
                                                                                  'value': None
                                                                                  if not is_float(data_list[idx])
                                                                                  else float(
                                                                                      data_list[idx].replace(',', '')),
                                                                                  'value_rmk': ''
                                                                                  if is_float(data_list[idx])
                                                                                  else data_list[idx],
                                                                              }
                                                                              )
            # print(key, column_name, data_list[idx])
        # print("[%s][%s][%s] %s information stored successfully" % (caption, crp_cd, crp_nm, key))
        # print("[%s][%s][%s] information stored successfully" % (report_name, crp_cd, crp_nm))
    except Exception as e:
        print('[Error on DailySnapShotDataStore]\n', '*' * 50, e)


def SnapShotDataStore(report_name, crp_cd, crp_nm, categorizing, column_names, key, data_list):
    import sys
    import os
    import django
    # sys.path.append(r'E:\Github\Waver\MainBoard')
    # sys.path.append(r'E:\Github\Waver\MainBoard\MainBoard')
    getConfig()
    sys.path.append(django_path)
    sys.path.append(main_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MainBoard.settings")
    django.setup()
    import detective_app.models as detective_db
    try:
        for idx, column_name in enumerate(column_names[1:]):

            period_info = column_name.split('/')
            f_p_e = 'F'
            if len(period_info) < 2:
                continue
            elif len(period_info) == 2 and len(period_info[1]) > 2:
                if '(E)' in period_info[1]:
                    f_p_e = 'E'
                    period_info[1] = period_info[1].replace('(E)', '')
                elif '(P)' in period_info[1]:
                    f_p_e = 'P'
                    period_info[1] = period_info[1].replace('(P)', '')
                # print(period_info[1])
            # print(key, column_name, data_list[idx])
            # print(report_name, crp_cd, crp_nm, categorizing, period_info[0], period_info[1])
            #       str(int(period_info[1])/3)[0]+'Q', key, data_list[idx])
            info = detective_db.FnGuideSnapShot.objects.update_or_create(rpt_nm=report_name,
                                                                         rpt_tp=column_names[0],
                                                                         crp_cd=crp_cd,
                                                                         crp_nm=crp_nm,
                                                                         disc_year=period_info[0],
                                                                         disc_month=period_info[1],
                                                                         disc_quarter=int(period_info[1]) / 3,
                                                                         disc_categorizing=categorizing,
                                                                         accnt_nm=key,
                                                                         defaults={
                                                                             'accnt_cd': '',
                                                                             'fix_or_prov_or_estm': f_p_e,
                                                                             'value': None
                                                                             if not is_float(data_list[idx])
                                                                             else float(
                                                                                 data_list[idx].replace(',', '')),
                                                                             'rmk': ''
                                                                             if is_float(data_list[idx])
                                                                             else data_list[idx],
                                                                         }
                                                                         )

        # print("[%s][%s][%s] %s information stored successfully" % (report_name, crp_cd, crp_nm, key))
        # print("[%s][%s][%s] information stored successfully" % (report_name, crp_cd, crp_nm))
    except Exception as e:
        print('[Error on SnapShotDataStore]\n', '*' * 50, e)


def FinancialReportDataStore(report_name, crp_cd, crp_nm, categorizing, column_names, key, data_list):
    import sys
    import os
    import django
    # sys.path.append(r'E:\Github\Waver\MainBoard')
    # sys.path.append(r'E:\Github\Waver\MainBoard\MainBoard')
    getConfig()
    sys.path.append(django_path)
    sys.path.append(main_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MainBoard.settings")
    django.setup()
    import detective_app.models as detective_db
    try:
        for idx, column_name in enumerate(column_names[1:]):
            period_info = column_name.split('/')
            f_p_e = 'F'
            if len(period_info) < 2:
                continue
            elif len(period_info) == 2 and len(period_info[1]) > 2:
                if '(E)' in period_info[1]:
                    f_p_e = 'E'
                    period_info[1] = period_info[1].replace('(E)', '')
                elif '(P)' in period_info[1]:
                    f_p_e = 'P'
                    period_info[1] = period_info[1].replace('(P)', '')

            # print(report_name, crp_cd, crp_nm, categorizing, period_info[0], period_info[1],
            #       str(int(period_info[1])/3)[0]+'Q', key, data_list[idx])
            info = detective_db.FnGuideFinancialReport.objects.update_or_create(rpt_nm=report_name,
                                                                                rpt_tp=column_names[0],
                                                                                crp_cd=crp_cd,
                                                                                crp_nm=crp_nm,
                                                                                disc_year=period_info[0],
                                                                                disc_month=period_info[1],
                                                                                disc_quarter=int(period_info[1]) / 3,
                                                                                disc_categorizing=categorizing,
                                                                                accnt_nm=key,
                                                                                defaults={
                                                                                    'accnt_cd': '',
                                                                                    'fix_or_prov_or_estm': f_p_e,
                                                                                    'value': None
                                                                                    if not is_float(data_list[idx])
                                                                                    else float(
                                                                                        data_list[idx].replace(',',
                                                                                                               '')),
                                                                                    'rmk': ''
                                                                                    if is_float(data_list[idx])
                                                                                    else data_list[idx],
                                                                                }
                                                                                )

        # print("[%s][%s][%s] %s information stored successfully" % (report_name, crp_cd, crp_nm, key))
        # print("[%s][%s][%s] information stored successfully" % (report_name, crp_cd, crp_nm))
    except Exception as e:
        print('[Error on FinancialReportDataStore]\n', '*' * 50, e)


def static_parse_table(divs, itemcode, itemname):
    for d in divs:
        if len(d.attrs) > 0 and 'class' in d.attrs.keys() and d.attrs['class'] in [['ul_col2wrap', 'pd_t25']]:
            column_name = []
            column_data = []
            categorizing = None
            data_information = {}
            report_type = None
            report_name = d.find('div').find('div').find('div').get_text().replace('\n', '')
            if report_name.find('3') > 0:
                categorizing = 'QUARTERLY'
            else:
                categorizing = 'YEARLY'
            for th in d.table.thead.find_all('th'):
                # print(th.get_text())
                if th.get_text().find('IFRS') > -1 or th.get_text().find('GAAP') > -1:
                    report_type = th.get_text()
                    continue
                else:
                    column_name.append(th.get_text())

            for tr in d.table.tbody.find_all('tr'):
                data_header = ''
                if tr.attrs['class'] == ['tbody_tit']:  # 표 이름은 저장하지 않음
                    continue
                elif 'acd_dep2_sub' in tr.attrs['class']:  # 하위의 BackData 는 저장하지 않음
                    # continue
                    if len(tr.th.div.find_all('dl')) > 0:
                        print(tr.th.div.dl.dt.get_text())
                    else:
                        print(tr.th.div.get_text())
                    # print(tr.th)
                elif 'acd_dep_start_close' in tr.attrs['class']:
                    data_header = tr.th.div.div.dl.dt.get_text()
                    column_data = []
                    for td in tr.find_all('td'):
                        if len(td.find_all('span')) > 0:
                            column_data.append(td.span.get_text())
                        else:
                            column_data.append(td.get_text())
                data_information[data_header] = column_data
            print(report_name, column_name)
            for dh in data_information.keys():
                print(dh, data_information[dh])
                # FinancialRatioDataStore(report_name, report_type, itemcode, itemname, categorizing, column_name, dh, data_information[dh])
            print('\n\n')


def is_float(s):
    try:
        float(s.replace(',', ''))
        return True
    except ValueError:
        return False


def get_table_contents(soup, structure):
    retList = []
    if soup:
        for tag in soup.select(structure):
            if tag.div and tag.div.dl and tag.div.dl.dt:
                if '(E) : Estimate' == tag.div.dl.dt.text.replace(u'\xa0', '').replace('\n', '').replace('  ',
                                                                                                         '').replace(
                        '   ', '').strip():
                    retList.append(
                        tag.div.span.text.replace(u'\xa0', '').replace('\n', '').replace('  ', '').replace('   ',
                                                                                                           '').strip())
                elif '(P) : Provisional' == tag.div.dl.dt.text.replace(u'\xa0', '').replace('\n', '').replace('  ',
                                                                                                              '').replace(
                        '   ', '').strip():
                    retList.append(
                        tag.div.span.text.replace(u'\xa0', '').replace('\n', '').replace('  ', '').replace('   ',
                                                                                                           '').strip())
                else:
                    retList.append(
                        tag.div.dl.dt.text.replace(u'\xa0', '').replace('\n', '').replace('  ', '').replace('   ',
                                                                                                            '').strip())
            elif tag.a:
                retList.append('%s(%s)' % (tag.a.text, tag.a['href']))
                continue
            if tag.div and tag.div.dl and tag.div.dl.dd:
                continue
            retList.append(tag.text.replace(u'\xa0', '').replace('\n', '').replace('  ', '').replace('   ', '').strip())
    return retList


def select_by_attr(soup, tagname, attr, condition, all=None):
    retTag = None
    if all:
        if attr == 'id':
            retTag = soup.find_all(tagname, {"id": condition})
        elif attr == 'class':
            retTag = soup.find_all(tagname, {"class": condition})
        elif attr == 'style':
            retTag = soup.find_all(tagname, {"style": condition})
        elif attr == 'scope':
            retTag = soup.find_all(tagname, {"scope": condition})
        elif attr == 'href':
            if condition:
                retTag = soup.find_all(tagname, {"href": condition})
            else:
                retTag = soup.find_all(tagname, href=True)
        else:
            pass
    else:
        if attr == 'id':
            retTag = soup.find(tagname, {"id": condition})
        elif attr == 'class':
            retTag = soup.find(tagname, {"class": condition})
        elif attr == 'style':
            retTag = soup.find(tagname, {"style": condition})
        elif attr == 'scope':
            retTag = soup.find(tagname, {"scope": condition})
        elif attr == 'href':
            retTag = soup.find(tagname, {"href": condition})
        else:
            pass
    return retTag


def setting(header, items, datas):
    retHeader = []
    retKey = []
    retValue = []
    try:
        if len(datas) < len(header) or len(datas) < len(items):
            # print("입력할 데이터 없음!!!")
            pass
        elif len(header) == 0:
            # print(
            #     "::::::::::::::::::::::::::::::::::::::len(header) == 0::::::::::::::::::::::::::::::::::::::::::::::::")
            for idx, item in enumerate(items):
                prev_column = ''
                tmpHeader = []
                tmpData = []
                if item.find('/') > -1:  # 한 컬럼에 여러개의 값이 있는 경우
                    if item.find('(') > -1:  # 여러개의 컬럼의 괄호로 묶인 공통인자가 있는 경우
                        prev_column = item[:item.find('(')].strip().replace('  ', '').replace('   ', '')
                        tmpHeader = [(prev_column + '-' + i.replace(' ', '')) for i in
                                     item[item.find('(') + 1:item.find(')')].strip().replace('  ', '').replace('   ',
                                                                                                               '').split(
                                         '/')]
                    elif item.find('.') > -1:  # 여러개의 컬럼의 마침표로 분리된 공통인자가 있는 경우
                        prev_column = item[:item.find('.')]
                        tmpHeader = [(prev_column + '-' + i.replace(' ', '')) for i in
                                     item[item.find('.') + 1:].strip().replace('  ', '').replace('   ', '').split('/')]
                    else:  # 공통인자 없이 서로 다른 두개의 값이 / 로 묶인 컬럼인 경우
                        tmpHeader = item.strip().replace('  ', '').replace('   ', '').split('/')
                    tmpData = datas[idx].strip().replace('  ', '').replace('   ', '').split('/')
                    retHeader.extend(tmpHeader)
                    retValue.extend(tmpData)
                else:
                    retHeader.append(item.strip().replace('  ', '').replace('   ', ''))
                    retValue.append(datas[idx].strip().replace('  ', '').replace('   ', ''))
        elif len(items) == 0:
            # print(
            #     ":::::::::::::::::::::::::::::::::::::::len(items) == 0::::::::::::::::::::::::::::::::::::::::::::::::")
            for idx, head in enumerate(header):
                retHeader.append(head.replace('  ', '').replace('   ', ''))
                retValue.append(datas[idx].replace('  ', '').replace('   ', ''))
        else:
            # print("::::::::::::::::::::::::::::::::::::::::::::else:::::::::::::::::::::::::::::::::::::::::::::::::")
            for idx, head in enumerate(header[1:]):
                retHeader.append(head.replace('  ', '').replace('   ', ''))
            retKey = items

            for i in range(len(retKey)):
                tmpData = []
                for j in range(len(retHeader)):
                    # print(i, j, len(retHeader)*i+j)
                    tmpData.append(datas[len(retHeader) * i + j].replace('  ', '').replace('   ', ''))
                retValue.append(tmpData)
    except Exception as e:
        print(e)
        # print(header, items, datas)

    return retHeader, retKey, retValue


def FinancialRatioDataStore(report_name, report_type, crp_cd, crp_nm, categorizing, column_names, key, data_list):
    import sys
    import os
    import django
    # sys.path.append(r'E:\Github\Waver\MainBoard')
    # sys.path.append(r'E:\Github\Waver\MainBoard\MainBoard')
    getConfig()
    sys.path.append(django_path)
    sys.path.append(main_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MainBoard.settings")
    django.setup()
    import detective_app.models as detective_db
    try:
        for idx, column_name in enumerate(column_names):
            period_info = column_name.split('/')
            f_p_e = 'F'
            if len(period_info) < 2:
                continue
            elif len(period_info) == 2 and len(period_info[1]) > 2:
                if '(E)' in period_info[1]:
                    f_p_e = 'E'
                    period_info[1] = period_info[1].replace('(E)', '')
                elif '(P)' in period_info[1]:
                    f_p_e = 'P'
                    period_info[1] = period_info[1].replace('(P)', '')
            # print(report_name, crp_cd, crp_nm, categorizing, period_info[0], period_info[1],
            #       str(int(period_info[1])/3)[0]+'Q', key, data_list[idx])
            info = detective_db.FnGuideFinancialRatio.objects.update_or_create(rpt_nm=report_name,
                                                                               rpt_tp=report_type,
                                                                               crp_cd=crp_cd,
                                                                               crp_nm=crp_nm,
                                                                               disc_year=period_info[0],
                                                                               disc_month=period_info[1],
                                                                               disc_quarter=int(period_info[1]) / 3,
                                                                               disc_categorizing=categorizing,
                                                                               ratio_nm=key,
                                                                               defaults={
                                                                                   'ratio_cd': '',
                                                                                   'fix_or_prov_or_estm': f_p_e,
                                                                                   'value': None
                                                                                   if not is_float(data_list[idx])
                                                                                   else float(
                                                                                       data_list[idx].replace(',', '')),
                                                                                   'rmk': ''
                                                                                   if is_float(data_list[idx])
                                                                                   else data_list[idx],
                                                                               }
                                                                               )

        # print("[%s][%s][%s] %s information stored successfully" % (report_name, crp_cd, crp_nm, key))
        # print("[%s][%s][%s] information stored successfully" % (report_name, crp_cd, crp_nm))
    except Exception as e:
        print('[Error on FinancialRatioDataStore]\n', '*' * 50, e)


def parse_html_table(table):
    n_columns = 0
    n_rows = 0
    column_names = []

    # Find number of rows and columns
    # we also find the column titles if we can
    for row in table.find_all('tr'):

        # Determine the number of rows in the table
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            n_rows += 1
            if n_columns == 0:
                # Set the number of columns for our table
                n_columns = len(td_tags)

        # Handle column names if we find them
        th_tags = row.find_all('th')
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text())

    # Safeguard on Column Titles
    print(column_names, n_columns)
    if len(column_names) > 0 and len(column_names) != n_columns:
        raise Exception("Column titles do not match the number of columns")

    columns = column_names if len(column_names) > 0 else range(0, n_columns)
    df = pd.DataFrame(columns=columns,
                      index=range(0, n_rows))
    row_marker = 0
    for row in table.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            df.iat[row_marker, column_marker] = column.get_text()
            column_marker += 1
        if len(columns) > 0:
            row_marker += 1

    # Convert to float if possible
    for col in df:
        try:
            df[col] = df[col].astype(float)
        except ValueError:
            pass

    return df


def httpRequest(url, data, method='POST'):
    try:
        if method == 'POST':
            r = requests.post(url, data)
            # print(method, 'httpRequest error status', r.raise_for_status(), data['gicode'])
            return r.content
        else:
            r = requests.get(url, data)
            # print(method, 'httpRequest error status', r.raise_for_status(), data['gicode'])
            return r.content
    except Exception as e:
        print(e)
        return None


def getUSFinanceData(cmd=None):
    import sys
    import os
    import django
    import edgar
    getConfig()
    sys.path.append(django_path)
    sys.path.append(main_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MainBoard.settings")
    django.setup()
    import detective_app.models as detective_db
    # workDir = r'%s'

    yyyymmdd = str(datetime.now())[:10]
    # url = "http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp"
    reportType = {
        # 101: 'snapshotUS',
        103: 'financeReportUS'
        # 104: 'financeRatioUS'
    }  # 101 : snapshot, 103 : financeReport, 104 : financeRatio
    # urlInfo = {
    #     101: 'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp',
    #     103: 'http://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp',
    #     104: 'http://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp'
    # }
    # url = 'https://finance.yahoo.com/quote/%s/financials?p=%s'

    # stockInfo = detective_db.USStocks.objects.filter(listing='Y')
    stockInfo = detective_db.USStocks.objects.filter(security='Oracle Corp.', listing='Y')
    # stockInfo = detective_db.Stocks.objects.filter(code='005930', listing='Y')
    for key in reportType.keys():
        # print(cmd, cmd and key != cmd)
        if cmd and key != cmd:
            continue
        # workDir = r'%s\%s\%s' % (report_path, reportType[key], yyyymmdd)
        workDir = r'C:\Github\Waver\detective\reports\%s\%s' % (reportType[key], yyyymmdd)
        if not os.path.exists(workDir):
            os.makedirs(workDir)
        for s in stockInfo:
            company = edgar.Company(s.security, s.cik)
            tree = company.getAllFilings(filingType="10-K")
            docs = edgar.getXMLDocuments(tree, noOfDocuments=1)
            # print(docs)
            for xml in docs:
                saveFile(workDir, s.cik, s.security.replace(' ', '_'), reportType[key], xml, 'w')


if __name__ == '__main__':
    # getFinanceData(101)
    getFinanceData(103)
    # getFinanceData(104)
