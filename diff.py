#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import difflib
import time
# -*- coding: utf-8 -*-

from urllib import request
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
import glob
import os
from collections import defaultdict

class rdict(dict):
    def __getitem__(self, key):
        try:
            return super(rdict, self).__getitem__(key)
        except:
            try:
                ret=[]
                for i in self.keys():
                    m= re.match("^"+key+"$",i)
                    if m:ret.append( super(rdict, self).__getitem__(m.group(0)) )
            except:raise(KeyError(key))
        return ret


def writeHtml():
    file.write('<html>\n')
    file.write('<head>\n')
    file.write('<style type="text/css">\n')
    file.write('body {font-family:Arial}\n')
    file.write('table {background-color:white; border:0px solid white; width:100%; margin-left:auto; margin-right: auto}\n')
    file.write('td {background-color:#ff7e75; padding:10px; border:0px solid white}\n')
    file.write('pre {background-color:white; padding:10px}\n')
    file.write('</style>\n')
    file.write('<title>Test Code Searcher Report</title>\n')
    file.write('<head>\n')
    file.write('<body>\n')
    file.write('<h2>Test Code Searcher Report</h2>\n')
    

#url
url = "file:///Users/ryosuke/Desktop/TCS/NiCad-5.0/projects/systems_functions-blind-clones/systems_functions-blind-clones-0.30-classes-withsource.html"

#get html
html = request.urlopen(url)

#set BueatifulSoup
soup = BeautifulSoup(html, "html.parser")

clint = MongoClient('163.221.190.202')
db = clint['testMapList']

# codeArray = []
# codePathArray = []

startLine = []
stopLine = []

bodyCode = soup.find('body')
# print(bodyCode)

# クローンクラス<h3>の配列を作成し,類似コードが存在するファイルパス<td>を要素として配列に格納する処理

# codePathArray = []
pathToClassDict = defaultdict(list)
classToPathsDict = defaultdict(list)
pathToFragmentDict = defaultdict(list)
pathToCodeInfoDict = defaultdict(list)

try:

    for item in bodyCode.find_all(['h3', 'table']):
        pathArray = []
        if item.name == 'h3':
            cloneclass = item.text.replace('\n','').replace('\r','')
            # print(cloneclass)

        if item.name == 'table':
            # fragmentArray = []      
            tdInfo = item.find_all('td')
            for td in tdInfo:
                codeInfoArray = []
                fragment  = td.find('pre')
                fragmentText = fragment.text
                # print(fragmentText)
                codeInfoArray.append(fragmentText)
                td.find('pre').decompose()
                path = td.text.replace('\n','').replace('\r','')
                pathArray.append(path)

                formalPath = re.sub(r"Lines.*?projects/systems/", "", path)
                codeInfoArray.append(formalPath)
                # print(formalPath)
                path_front = re.sub(r"Lines ", "", path)
                path_line = path_front[:path_front.find('o')]
                path_rmSpace = path_line.replace(' ','')

                startLine = int(path_rmSpace[:path_rmSpace.find('-')])
                endLine = int(path_rmSpace[path_rmSpace.find('-')+1:])
                # print(str(startLine) + ':' + str(endLine))
                codeInfoArray.append(startLine)
                codeInfoArray.append(endLine)
                pathToCodeInfoDict[path] = codeInfoArray
                pathToFragmentDict[path] = fragmentText
                # print(pathArray)
                pathToClassDict[path] = cloneclass

            classToPathsDict[cloneclass] = pathArray

    # for key in pathToFragmentDict:
    #     print(key)
    #     print(pathToFragmentDict[key])
    
    # for key in pathToCodeInfoDict:
    #     print(key)
    #     print(pathToCodeInfoDict[key])
    
    # for key in pathToClassDict:
    #     print(key)
    #     print(pathToClassDict[key])

    # for key in classToPathsDict:
    #     print(key)
    #     print(classToPathsDict[key])

    rePathToClassDict = rdict(pathToClassDict)
    classInfo = rePathToClassDict["^(?=.*" + 'projects/systems/a.java' + ").*$"]
    print(classInfo[0])
    pathInfos = classToPathsDict[classInfo[0]]
    print(pathInfos)
    # for key in pathInfos:
    #     print(pathToCodeInfoDict[key][0])

#     rePathToCodeInfoDict = rdict(pathToCodeInfoDict)
#     for key in pathToCodeInfoDict:
#         print(key)
#         for value in pathToCodeInfoDict[key]:
#             print(value)


    for detected_path in pathInfos:
        if 'projects/systems/a.java' in detected_path:
            input_path = detected_path
            print(input_path)


    # print(pathToCodeInfoDict[input_path][0][1:])
    file = open('diff_result.html','w')
    writeHtml()
    clone_num = 1
    for key_path in pathInfos:
        # print('key_path : ' + key_path)
        if 'projects/systems/a.java' not in key_path:
            code1 = pathToCodeInfoDict[input_path][0][1:].splitlines ()
            code2 = pathToCodeInfoDict[key_path][0][1:].splitlines ()

            diff_lines = difflib.context_diff (code1, code2, 'name-version.orig/test.txt', 'name-version/test.txt', time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime(1212121212)), time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime(1313131313)), 3, '')
            # for文でループさせる
            # print('---------------------------------------------------')
            # for l in g:
            #     print(l)
            twoCodeArray = []
            initLineArray = []
            line_num = 1
            print('-----------------------------------------')
            for diff_line in diff_lines:
                # print(str(line_num) + ' : ' + l)
                if line_num >= 1 and line_num <= 4:
                    pass
                else:
                    # print(str(line_num) + ' : ' + l)
                    line_init = diff_line[:3]
                    initLineArray.append(line_init)
                    # print(line_init)
                    twoCodeArray.append(diff_line)
                line_num += 1
                # print(l[1:])
            if len(initLineArray) != 0:
                print(initLineArray)

                separator_num = initLineArray.index('---')
                print(separator_num)
                print('twoCodeArray : ' + str(len(twoCodeArray)))
                print('initLineArray : ' + str(len(initLineArray)))

                file.write('<TABLE BORDER="0">')
                file.write('<h3>Clone Pairs ' + str(clone_num) +'</h3>\n')
                file.write('<TR>\n')
                file.write('<TD>\n')
                file.write('<table border="1" align="left" cellspacing="0" cellpadding="5" bordercolor="#333333">\n')
                file.write('<tr>\n')
                file.write('<td>\n')
                file.write('Input Code' + '\n')
                file.write('<pre>\n')
                # file.write(pathToCodeInfoDict[input_path][0][1:])
                for line1 in code1:
                    file.write(line1 + '\n')
                    # file.write('<mark>' + line1 + '</mark>' + '\n')
                    # print(line1)

                for line1 in range(0,separator_num):
                    print(twoCodeArray[line1])            
                file.write('</pre>\n')
                file.write('</td>\n')
                file.write('</tr>\n')
                file.write('</table>\n')
                file.write('</TD>\n')
                file.write('<TD>\n')
                file.write('<table border="1"  cellspacing="0" cellpadding="5" bordercolor="#333333">\n')
                file.write('<tr>\n')
                file.write('<td>\n')
                file.write('Lines ' + str(pathToCodeInfoDict[key_path][2]) + ' - ' + str(pathToCodeInfoDict[key_path][3]) + ' of ' + pathToCodeInfoDict[key_path][1] + '\n')
                file.write('<pre>\n')
                # file.write(pathToCodeInfoDict[key_path][0][1:].replace('\n','') + '\n')
                # for line2 in code2:
                #     file.write(line2 + '\n')
                    # print(line2)

                for line2 in range(separator_num+1,len(twoCodeArray)):
                    line_mark = twoCodeArray[line2][:1]
                    # print(line_mark)
                    if line_mark == '!':
                        file.write('<mark>' + twoCodeArray[line2] + '</mark>' + '\n')
                        print(twoCodeArray[line2])
                    else:
                        file.write(twoCodeArray[line2] + '\n')

                file.write('</pre>\n')
                file.write('</td>\n')
                file.write('</tr>\n')
                file.write('</table>\n')
                file.write('</TD>\n')
                file.write('</TR>\n')
                file.write('</TABLE>\n')

            clone_num += 1

except IndexError:
    print('Could not find similar code.')



# text1 = '''	
# 	public void undo(CollectionChangeEvent event)
# 	{
# 		try
# 		{
# 			getValueModel().removeCollectionChangeListener(this.collectionChangeHandler);
# 			getUndoRedoManager().beginTransaction();
# 			CollectionDifference difference = event.getDifference();

# 			ObservableCollection source = getValueModel();
# 			source.unapply(difference);

# 		}
# 		finally
# 		{
# 			getValueModel().addCollectionChangeListener(this.collectionChangeHandler);
# 			getUndoRedoManager().endTransaction();
# 		}
# 	}
# '''.splitlines ()
# text2 = '''	
# 	public void redo(CollectionChangeEvent event)
# 	{
# 		try
# 		{
# 			getValueModel().removeCollectionChangeListener(this.collectionChangeHandler);
# 			getUndoRedoManager().beginTransaction();

# 			CollectionDifference difference = event.getDifference();

# 			// Always use the ValueModel's value since when an entity is reloaded, a new collection
# 			// containing the same objects is recreated
# 			ObservableCollection source = getValueModel();

# 			source.apply(difference);

# 		}
# 		finally
# 		{
# 			getValueModel().addCollectionChangeListener(this.collectionChangeHandler);
# 			getUndoRedoManager().endTransaction();
# 		}
# 	}
# '''.splitlines ()

# print(text1)
# print(len(text1))

# print(text2)
# print(len(text2))
# # 戻り値はジェネレータ型
# # 最初の2つの引数はそれぞれテキストのみを含むリスト型を指定
# g = difflib.unified_diff (text1,
#                           text2,
#                           # 1つ目のファイル名
#                           'name-version.orig/test.txt',
#                           # 2つ目のファイル名
#                           'name-version/test.txt',
#                           # タイムスタンプ部分の文字列(1つ目のファイル)
#                           # 今回は適当なタイムスタンプをフォーマット付けした
#                           time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime(1212121212)),
#                           # タイムスタンプ部分の文字列(2つ目のファイル)
#                           time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime(1313131313)),
#                           # 変更部分周辺をどの程度含めるか(既定値は3)
#                           3,
#                           # 制御行の末尾に付ける文字列
#                           # CR+LFなdiffを書き出したいなら「\r」を記述する
#                           '')
# # for文でループさせる
# # print(g)
# for l in g:
#   print (l)
