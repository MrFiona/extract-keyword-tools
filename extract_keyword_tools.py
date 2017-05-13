#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-04-11 10:12
# Author  : MrFiona
# File    : extract-keyword-tools.py
# Software: PyCharm Community Edition

import os
import re
import sys
import glob
import time
import shutil
import getopt
from create_xml import create_xml

try:
    from pyh import PyH, h1, table, td, tr, th

except ImportError:
    pwd_dir = os.getcwd()
    os.chdir(os.getcwd() + os.sep + 'PyH-0.1.1')
    os.system('python setup.py install')
    os.chdir(pwd_dir)
    from pyh import PyH, h1, table, td, tr, th

__file_name = os.path.split(__file__)[1]

try:
  import cPickle as pickle
except ImportError:
  import pickle

#命令行参数help帮助显示的信息
def usage():
    print "\033[36m************************************** 用法举例：*************************************\033[0m"
    print
    print "\033[31m****\033[0m  \033[32mpython %s -f filename or --file=filename\033[0m                   \033[31m****\033[0m" % __file_name
    print "\033[31m****\033[0m  \033[32mpython %s --help\033[0m                                           \033[31m****\033[0m" % __file_name
    print "\033[31m****\033[0m  \033[32mpython %s -f filename -r range_line or --range=range_line\033[0m  \033[31m****\033[0m" % __file_name
    print "\033[31m****\033[0m  \033[32mpython %s -f filename -k keywords or --keyword=keywords\033[0m    \033[31m****\033[0m" % __file_name
    print "\033[31m****\033[0m  \033[32mpython %s -f filename -k keywords  --print\033[0m                 \033[31m****\033[0m" % __file_name
    print
    print "\033[36m************************************** 用法举例：*************************************\033[0m"

#获取命令行参数：文件名，行区间，关键字
def main(file=None, range=None, key=None, help=None, combine_flag=False):
    print_flag = False
    parameters = sys.argv[1:]
    # print parameters
    if not parameters:
        raise UserWarning('\033[31m请输入命令行参数!!!\033[0m')
    if '--combine' in sys.argv[1:] or '-combine' in sys.argv[1:]:
        combine_flag = True
        try:
            parameters.remove('--combine')
        except ValueError:
            pass

        try:
            parameters.remove('-combine')
        except ValueError:
            pass

    else:
        combine_flag = False

    try:
        opts, args = getopt.getopt(parameters, "f:r:k:h:p",["file=", "range=", "keyword=", "help", "print"])
        #args为无法解析的字符串
        if len(args) != 0:
            raise UserWarning('\033[31m请检查参数 %s 是否正确!!!\033[0m' % args)
        # print 'opts',opts
        # print 'args',args
    except getopt.GetoptError, error:
        sys.exit(str(error))
    # print opts,args
    for o, a in opts:
        if o in ("--file", "-f"):
            file = a
        elif o in ("--range", "-r"):
            range = a
        elif o in ("--keyword", '-k'):
            key = a
        elif o in ("--help", '-h'):
            usage()
        elif o in ("--print", '-p'):
            print_flag = True
        # elif o in ("--combine", '-c'):
        #     combine_flag = True
        else:
            sys.exit("Unknown option %s" % o)
    return file, range, key, combine_flag, print_flag

#获取行区间的信息并作处理
def get_range_line(range_lineno):
    #对行区间进行合法性检查，返回合法性行区间列表
    def check_range_lineno(range_lineno):
        #不为None的时候
        if range_lineno:
            #对range_lineno判断分类
            pre_range_lineno_list = range_lineno.split(';')
            # print '6666',pre_range_lineno_list
            final_range_lineno_list = []
            #去除无效的空行号区间
            for element in pre_range_lineno_list:
                if len(element) == 0:
                    continue
                final_range_lineno_list.append(element)
            # print '666777',final_range_lineno_list
            #去除不符合规范的行号区间
            legal_range_lineno_list = []
            for ele in final_range_lineno_list:
                temp_list = ele.split(',')
                # print 'hhh',temp_list
                if len(temp_list) != 2:
                    raise UserWarning('\033[31m您输入行区间的部分 [ %s ]不合法!!!\033[0m' % ele)
                try:
                    if int(temp_list[0]) > int(temp_list[-1]):
                        raise UserWarning('\033[31m您输入的行区间号 [ %s ]不合法， 不允许左边大于右边!!!\033[0m' % ele)
                    if int(temp_list[0]) < 0 or int(temp_list[-1]) < 0:
                        raise UserWarning('\033[31m你输入的行区间号 [ %s ]不合法，不允许输入负数!!!\033[0m' % ele)
                    legal_range_lineno_list.append([int(temp_list[0]), int(temp_list[-1])])
                except ValueError as e:
                    raise UserWarning('\033[31m您输入的行区间部分 [ %s ]不合法!!!\033[0m' % ele)
            # print '77777',legal_range_lineno_list
            return legal_range_lineno_list

    #判断两个行区间是否存在交集 改善：更有效率，不会出现内存错误
    def is_list_mix(list1, list2):
        if (list1[0] <= list2[0] and list1[1] >= list2[0]) or \
                (list1[0] >= list2[0] and list1[1] <= list2[1]) or \
                (list1[0] >= list2[0] and list1[1] >= list2[1]) or \
                (list1[0] <= list2[0] and list1[1] >= list2[1]):
            return True
        return False

    # 完善过后的处理多个行区间交集情况的函数
    def mix_index_list(legal_range_lineno_list):
        # temp_mix_flag_list用来标记行区间列表中的行区间下标
        temp_mix_flag_list = []
        # 临时存放符合要求的行区间
        temp_legal_rang_list = []
        legal_range_lineno_list.sort()
        range_length = len(legal_range_lineno_list)
        # print '1000',range_length

        for i in range(range_length):
            temp_mix_flag_list.append(True)

        # 对legal_range_lineno_list中行区间交集非重复比较
        for i in range(range_length):
            for j in range(i + 1, range_length):
                mix = is_list_mix(legal_range_lineno_list[i], legal_range_lineno_list[j])
                # 若出现交集，则将较大的下标对应的行区间置为两者的并集
                if mix:
                    link = [min(legal_range_lineno_list[i][0], legal_range_lineno_list[j][0]),
                            max(legal_range_lineno_list[i][1], legal_range_lineno_list[j][1])]
                    legal_range_lineno_list[j] = link
                    temp_mix_flag_list[i] = False
        # print '1111',temp_mix_flag_list
        for i in range(range_length):
            # 此处不能遍历的同时删除元素， for i循环是通过list中的下标有顺序的循环输出，
            # 移除的同时右边的元素下标会左移!!!
            # print ' i = %d \t%s' % (i, legal_range_lineno_list[i])
            if temp_mix_flag_list[i] != False:
                temp_legal_rang_list.append(legal_range_lineno_list[i])
        # print '122222',temp_legal_rang_list
        legal_range_lineno_list = temp_legal_rang_list

        #此时行区间均互为非交集，但是如果出现像[1,12],[13,34]这样的情况则处理如下
        legal_range_lineno_list.sort()
        temp_length = len(legal_range_lineno_list)
        temp_flag_list = []
        temp = []
        for k in range(temp_length):
            temp_flag_list.append(True)

        for i in range(temp_length):
            i_value_list = legal_range_lineno_list[i]
            for j in range(i+1, temp_length):
                j_value_list = legal_range_lineno_list[j]
                if i_value_list[1] + 1 == j_value_list[0]:
                    legal_range_lineno_list[j] = [ i_value_list[0], j_value_list[1] ]
                    temp_flag_list[i] = False
                    break
        # print '13333',temp_flag_list
        for m in range(temp_length-1,-1,-1):
            if temp_flag_list[m] != True:
                legal_range_lineno_list.remove(legal_range_lineno_list[m])

        # print 'final14444',legal_range_lineno_list
        return legal_range_lineno_list

    temp = []
    legal_range_lineno_list = check_range_lineno(range_lineno)
    # print '88888',legal_range_lineno_list
    if legal_range_lineno_list:
        #去除刚开始就出现完全相同的行区间
        legal_range_lineno_temp_list = []
        for i in legal_range_lineno_list:
            if i in legal_range_lineno_temp_list:
                continue
            legal_range_lineno_temp_list.append(i)

        legal_range_lineno_list = legal_range_lineno_temp_list
        # print '9999',legal_range_lineno_list
        legal_range_lineno_list = mix_index_list(legal_range_lineno_list)
        # print '15555',legal_range_lineno_list

    return legal_range_lineno_list

#获取关键字信息并处理
def get_keyword(keyword=None):
    if not keyword:
        return None
        # raise UserWarning('在设置了keyword的情况下，keyword不能为空!!!')
    if not isinstance(keyword, str):
        raise UserWarning('\033[31mkeyword必选是非空字符串!!!\033[0m')
    if keyword.isspace():
        raise UserWarning('\033[31mkeyword必选是非空字符串!!!\033[0m')
    keyword_list = keyword.split(';')
    for key in keyword_list:
        if key.isspace():
            raise UserWarning('\033[31mkeyword必选是非空字符串!!!\033[0m')
        if len(key) == 0:
            raise UserWarning('\033[31m在设置了keyword的情况下，keyword不能为空!!!\033[0m')
    return keyword_list

#根据行列表和关键字从原始文件提取数据
def range_remove(actual_file_name, pre_dir_name, range_lineno_list, keyword_list, combine_flag=False, multi_file_flag=False, first_file_flag=False):
    def judge_line_valid(line_lfet, line_right, orignal_file_max_length):
        # 判断行区间左右下标有效性
        # 若不处理则当超过文件长度时提取的内容为空

        # if line_lfet > orignal_file_max_length:
        #     for file in os.listdir(os.getcwd() + os.sep + 'resultfile'):
        #         if file == filename.split('.')[0]:
        #             f = open(os.getcwd() + os.sep + 'resultfile' + os.sep + file, 'w+')
        #             f.truncate(0)
            # line_lfet = 0
            # if line_right >= orignal_file_max_length:
            #     line_right = 0

        if (line_lfet <= orignal_file_max_length) and (line_right >= orignal_file_max_length):
            line_right = orignal_file_max_length
        # print 'rrrrr',[line_lfet, line_right]
        return line_lfet, line_right

    def signal_remove(actual_file_name, pre_dir_name, max_file_length, num_list=None, keyword_list=None, continue_add_flag=True, is_exist_key_word=False):
        #行区间存在则处理原文件将提取的数据存储在临时文件中
        if num_list:
            left = num_list[0]
            right = num_list[1]
            #区间的有效性处理
            left, right = judge_line_valid(left, right, max_file_length)
            # print 'left', left
            if left > max_file_length:
                print '大于'
                return

            # print 'qqqqqqq', left, right

            # 移除文件中的某一行数据并回写进文件
            fro = open(pre_dir_name + os.sep + actual_file_name, "rb")

            current_line = 0
            while current_line < left - 1:
                fro.readline()
                current_line += 1

            temp_path = os.getcwd() + os.sep + 'tempfile'
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)

            time_str = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
            temp_file_path = temp_path + os.sep + actual_file_name.split('.')[0]
            #
            if continue_add_flag:
                # print 'eeee'
                fdest = open(temp_file_path, 'a+')
            else:
                # print 'eeeeeeeeee'
                fdest = open(temp_file_path, 'w')

            for i in range(0, right - left + 1):
                line = fro.readline()
                fdest.write(line)
                #****** 注意：此处容易产生一个bug就是去掉换行的时候整个文件就变成了一行，当
                #****** 你想对文件按行来操作的话会出现bug  3/14/2017 出现的bug
                # fdest.write(line.strip('\n'))
            fro.close()
            fdest.close()

            #如果未设置关键字则拷贝临时文件到结果目录下（默认是将行区间提取的数据存放在临时目录下）
            if not keyword_list:
                #去掉多余的换行符增加文件可读性，与原文件格式保持一致
                f = open(temp_file_path, 'r')
                if not os.path.exists(os.getcwd() + os.sep + 'resultfile'):
                    os.makedirs(os.getcwd() + os.sep + 'resultfile')
                d = open(os.getcwd() + os.sep + 'resultfile' + os.sep + actual_file_name.split('.')[0], 'wb')
                for line in f:
                    d.write(line)
                    # d.write(line.strip('\n'))

            elif keyword_list:
                # 判断是否有keyword_list，存在则进一步提取数据，在临时文件的基础上
                result_path = os.getcwd() + os.sep + 'resultfile'
                result_file = result_path + os.sep + actual_file_name.split('.')[0]
                if not os.path.exists(result_path):
                    os.makedirs(result_path)

                final = open(result_file, 'wb+')
                ftemp = open(temp_file_path, 'r')
                # print temp_file_path
                #如果不能在并且combine无连接标记时清零文件，防止之前的结果保留
                for line in ftemp:
                    for key in keyword_list:
                        is_exist_key_word = False
                        if key in line:
                            final.write(line)
                            is_exist_key_word = True
                            # final.write(line.strip('\n'))
                            break
                ftemp.close()
                final.close()
        #行区间不存在的情况下
        elif not num_list:
            if keyword_list:
                # 判断是否有keyword_list，存在则进一步提取数据，在临时文件的基础上
                result_path = os.getcwd() + os.sep + 'resultfile'
                result_file = result_path + os.sep + actual_file_name.split('.')[0]
                if not os.path.exists(result_path):
                    os.makedirs(result_path)

                final = open(result_file, 'wb+')
                ftemp = open(pre_dir_name+os.sep+actual_file_name, 'r')

                # 如果不能在并且combine无连接标记时清零文件，防止之前的结果保留
                #支持特殊字符扩展  如：^|表示开头,$表示结尾  需要考虑关键词含有这两个特殊字符的处理  2017-04-10
                for line in ftemp:
                    for key in keyword_list:
                        write_file_flag = False
                        is_exist_key_word = False
                        # 匹配的关键字是否整体包含在line
                        if key in line:
                            write_file_flag = True
                        #2、含有^特殊字符
                        elif key.startswith('^') and not key.endswith('$'):
                            effective_key = key[1:]
                            #匹配的除去^的关键字是否是line的开头
                            if effective_key in line:
                                if (not line.strip().startswith('"') and line.strip().startswith(effective_key)) or \
                                        (line.strip().startswith('"') and line.strip()[1:].startswith(effective_key)):
                                    write_file_flag = True
                        #3、含有$字符
                        elif not key.startswith('^') and key.endswith('$'):
                            effective_key = key[:-1]
                            # 匹配的除去$的关键字是否是line的结尾
                            if effective_key in line:
                                if (not line.strip().endswith('"') and line.strip().endswith(effective_key)) or \
                                        (line.strip().endswith('"') and line.strip()[:-1].endswith(effective_key)):
                                    write_file_flag = True
                        #4、既含有^又含有$则是匹配整个字符串
                        elif key.startswith('^') and key.endswith('$'):
                            effective_key = key[1:-1]
                            # 匹配的除去^和$的关键字是否是line  除去引号换行空格等的影响
                            if effective_key in line:
                                line = re.sub('["|\n| ]', '', line)
                                if id(line) == id(effective_key):
                                    write_file_flag = True

                        if write_file_flag:
                            final.write(line)
                            is_exist_key_word = True
                            break

                ftemp.close()
                final.close()
        return is_exist_key_word

    #求文件最大长度
    judge = open(pre_dir_name + os.sep + actual_file_name, 'r')
    judge_lines = judge.readlines()
    orignal_file_max_length = len(judge_lines)

    #行区间不为空则执行该部分代码
    is_exist_key_word = False
    if range_lineno_list:
        range_lineno_list.sort()
        # print 'gggggggg',range_lineno_list
        for num_list in range_lineno_list:
            if len(range_lineno_list) != 1 and num_list == range_lineno_list[-1]:
                # print 'num_list', num_list
                is_exist_key_word = signal_remove(actual_file_name, pre_dir_name, orignal_file_max_length, num_list,
                                                  keyword_list, False, is_exist_key_word)
                continue
            is_exist_key_word = signal_remove(actual_file_name, pre_dir_name, orignal_file_max_length, num_list,
                                              keyword_list, True, is_exist_key_word)
    #行区间不存在则执行这部分代码
    if not range_lineno_list:
        is_exist_key_word = signal_remove(actual_file_name, pre_dir_name, orignal_file_max_length, None,
                                          keyword_list, True, is_exist_key_word)
    #如果keyword找不到并且连接标志未开启则清零文件
    if not is_exist_key_word and (not combine_flag and (not multi_file_flag or (multi_file_flag and first_file_flag))):
        dir_path = os.getcwd() + os.sep + 'result_text'
        if os.path.exists(dir_path):
            f = open(dir_path + os.sep + 'result_data.txt', 'w')
            f.truncate(0)
            f.close()

    if not combine_flag and (not multi_file_flag or (multi_file_flag and first_file_flag)):
        if os.path.exists(os.getcwd() + os.sep + 'resultfile'):
            for file in os.listdir(os.getcwd()+os.sep+'resultfile'):
                # print filename.split('.')[0]
                if file != actual_file_name.split('.')[0]:
                    os.remove(os.getcwd()+os.sep+'resultfile'+os.sep+file)
    # 如果不能在并且combine无连接标记时清零文件，防止之前的结果保留

#检测参数，根据参数作出相应动作，分类操作
def classify_parameters(actual_file_name, pre_dir_name, range_lineno_list=None, keyword_list=None, combine_flag=False, multi_file_flag=False,
                        first_file_flag=False):
    #分类操作处理参数
    # print 'swe', range_lineno_list
    is_exist_range_lineno = range_lineno_list and len(range_lineno_list) and len(range_lineno_list[0]) != 0
    is_exist_keyword = keyword_list

    #1、行区间和关键字至少有一个存在
    if is_exist_range_lineno or is_exist_keyword:
        #读取文件中对应行号的信息
        range_remove(actual_file_name, pre_dir_name, range_lineno_list, keyword_list, combine_flag, multi_file_flag, first_file_flag)

    #2、行区间和关键字都不存在，则默认拷贝全部内容
    if not is_exist_range_lineno and not keyword_list:
        if not os.path.exists(os.getcwd()+os.sep+'resultfile'):
            os.makedirs(os.getcwd()+os.sep+'resultfile')
        regex = actual_file_name.split('.')[0]
        shutil.copy2(pre_dir_name+os.sep+actual_file_name, os.getcwd()+os.sep+'resultfile'+os.sep+regex)

#将目标数据显示在html
class objectHtmlDataList:

    def __init__(self, actual_file_name, dest_path=os.getcwd()+os.sep+'resultfile', combine_flag=False, multi_file_flag=False, first_file_flag=False):
        self.dest_path = dest_path
        self.actual_file_name = actual_file_name
        self.first_file_flag = first_file_flag
        self.multi_file_flag = multi_file_flag
        self.combine_flag = combine_flag
        self.object_path = os.getcwd() + os.sep + 'result_text'
        self.throw = []
        self.attribute_value_list_key = []
        self.attribute_value_list_value = []

    def commonTableFunction(self, filename, attribute_value_list_key, attribute_value_list_value, throw_list):
        #tr 元素定义表格行，th 元素定义表头，td 元素定义表格单元
        t = table(border="1", cl="table1", cellpadding="0", cellspacing="0")
        t << tr(td('%s' % (filename), bgColor='#E9DEDE', colspan=2))
        for attribute, value in zip(attribute_value_list_key, attribute_value_list_value):
            t << tr(td(attribute) + td(value))
        t << th() + th()
        throw_list.append(t)

        return throw_list

    # 生成html并显示数据
    def generateTable(self):
        if not os.path.exists(self.dest_path):
            os.makedirs(self.dest_path)
        dir_file_list = os.listdir(self.dest_path)
        for file in range(len(dir_file_list)):
            file_path = self.dest_path + os.sep + dir_file_list[file]
            # 提取目标文本中的属性值
            with open(file_path, 'r') as f:
                lines = f.readlines()
                line_list = ''.join(lines).splitlines()
                for line in range(len(line_list)):
                    if ',' in line_list[line]:
                        if self.actual_file_name.split('.')[0] == dir_file_list[file]:
                            attribute_value_list = line_list[line].split(',')
                            if len(attribute_value_list) != 0:
                                self.attribute_value_list_key.append(attribute_value_list[0].replace("\"""", ""))
                                self.attribute_value_list_value.append(attribute_value_list[-1].replace("\"""", ""))

        for file in range(len(dir_file_list)):
            if self.actual_file_name.split('.')[0] == dir_file_list[file]:
                self.throw = self.commonTableFunction(dir_file_list[file], self.attribute_value_list_key,
                                                  self.attribute_value_list_value, self.throw)
        page = PyH('Intel Compute Data report')
        page << h1('Intel Compute Data report', style="font-family:arial;color:red;font-size:35px;text-align:center")

        tab = table(cellpadding="0", cellspacing="0", cl="table0")
        for t in range(0, len(self.throw), 2):
            tab << tr(td(self.throw[t - 1], cl="table0_td"))

        #判断dump文件夹是否存在
        temp_file_path = os.getcwd()+os.sep+'result_text'+os.sep+'dump'
        if not os.path.exists(temp_file_path):
            os.makedirs(temp_file_path)

        #连接标记未开启，dump原始文件清除
        if not self.combine_flag and (not self.multi_file_flag or (self.multi_file_flag and self.first_file_flag)):
            for file in glob.glob(temp_file_path + os.sep + '*.dump'):
                os.remove(file)

        #将tab对象序列化存储在文件中
        if os.path.exists(temp_file_path+os.sep+self.actual_file_name.split('.')[0]+'.dump'):
            os.remove(temp_file_path+os.sep+self.actual_file_name.split('.')[0]+'.dump')
        f = open(temp_file_path+os.sep+self.actual_file_name.split('.')[0]+'.dump', 'ab+')
        pickle.dump(tab, f)
        f.close()

        #将dump目录下的所以文件反序列化出tab对象，添加到page中
        for file in glob.glob(temp_file_path+os.sep+'*.dump'):
            f = open(file, 'rb')
            d = pickle.load(f)
            page << d
            f.close()


        if not os.path.exists(self.object_path):
            os.makedirs(self.object_path)
        page.printOut(self.object_path + os.sep + 'result_show.html')
        return self.attribute_value_list_key, self.attribute_value_list_value

#生成text文档
def create_text_info(actual_file_name, pre_dir_name, attribute_value_list_key, attribute_value_list_value
                     ,combine_flag=False, print_flag=False, multi_file_flag=False, first_file_flag=False):
    key_value_flag = True
    if not attribute_value_list_key or not attribute_value_list_value:
        key_value_flag = False
    result_text_path = os.getcwd() + os.sep + 'result_text'
    #如果不加参数--combine则默认移除历史记录的text结果
    # print 'gggggg:\t', not combine_flag and (not multi_file_flag or (multi_file_flag and first_file_flag))
    if not combine_flag and (not multi_file_flag or (multi_file_flag and first_file_flag)):
        if not os.path.exists(result_text_path):
            os.makedirs(result_text_path)
        #如果用glob中的file删除的话会报权限问题
        # print '\nssssssssss:\t', os.listdir(result_text_path)
        for file in os.listdir(result_text_path):
            if file == 'result_data.txt' or file == 'result_show.html' or file == 'dump' or file == 'tab_num_dir':
                continue
            os.remove(result_text_path + os.sep + file)
            # print '移除file:\t', file
    if not os.path.exists(result_text_path):
        os.makedirs(result_text_path)

    if key_value_flag:
        line = attribute_value_list_key[0]
        max_line_length = len(line)

        legth_list = []
        #key的最大长度
        for line in attribute_value_list_key:
            legth = len(line.strip())
            if legth >= max_line_length:
                max_line_length = legth
            # print '%s, %d' % (line, len(line))
        # print 'max_line\t:', max_line_length

        #key对应的value应移动的长度
        for line in attribute_value_list_key:
            legth = max_line_length - len(line)
            legth_list.append(legth)
        # print 'legth_list\t:', legth_list

        #打印标记开启则执行如下代码
        i = 0
        if print_flag:
            print '\033[42m%s\033[0m' % actual_file_name
        obj = open(result_text_path + os.sep + 'result' + '_' + actual_file_name, 'wb')
        #增加获取key和value之间空格的个数列表
        if not os.path.exists(result_text_path + os.sep + 'tab_num_dir'):
            os.makedirs(result_text_path + os.sep + 'tab_num_dir')

        write_tab_num_obj = open(result_text_path + os.sep + 'tab_num_dir' + os.sep + 'tab_num_' + actual_file_name, 'wb')
        key_value_tab_num_list = []
        for key, value in zip(attribute_value_list_key, attribute_value_list_value):
            tab_num = ' ' * (legth_list[i] + 2)
            key_value_tab_num_list.append(str(legth_list[i] + 2))
            obj.write(key + tab_num + value + '\n')
            if print_flag:
                print key, '\t', value
            i = i+1
        write_tab_num_obj.write(' '.join(key_value_tab_num_list) + '\n')
        obj.close()

        #如果存在则将文件清零
        if os.path.exists(os.getcwd() + os.sep + 'result_text' + os.sep + 'result_data.txt'):
            f = open(os.getcwd() + os.sep + 'result_text' + os.sep + 'result_data.txt', 'w')
            #如果是当前结果为空并且连接标记未开启，如果开启则应该保留
            if not combine_flag and (not multi_file_flag or (multi_file_flag and first_file_flag)):
                f.truncate(0)
            f.close()


        #将结果写到一个文件
        file_list = os.listdir(result_text_path)
        file1_list = [ file for file in file_list if 'result_data.txt' != file and 'result_show.html' != file and file != 'dump' and file != 'tab_num_dir' and 'result_report.xml' not in file ]
        # print '\nfile1_list:\t', file1_list
        for file in file_list:
            if 'result_data.txt' == file or 'result_show.html' == file or file == 'dump' or file == 'tab_num_dir' or 'result_report.xml' in file:
                continue

            read_obj = open(result_text_path + os.sep + file, 'rb')
            write_obj = open(os.getcwd() + os.sep + 'result_text' + os.sep + 'result_data.txt', 'ab+')
            #对文件名进行处理
            split_file_string_list = re.split('[.]', file)
            #默认取开头
            write_file_string = split_file_string_list[0]
            #文件名含有不止一个.时默认取列表的开头
            if len(split_file_string_list) >= 2:
                write_file_string = split_file_string_list[0]
            if len(split_file_string_list) == 1:
                write_file_string = file

            write_obj.write('[ %s ]' % write_file_string + '\n')
            write_obj.writelines( read_obj.readlines())
            write_obj.write('\n')
            read_obj.close()
            write_obj.close()

    else:
        if os.path.exists(os.getcwd() + os.sep + 'result_text' + os.sep + 'result_data.txt'):
            f = open(os.getcwd() + os.sep + 'result_text' + os.sep + 'result_data.txt', 'w')
            f.write('[ %s ]' %actual_file_name.split('.')[0] + '\n' + '\n')
            f.close()

def clear_temp_file():
    # 移除临时文件
    for file in os.listdir(os.getcwd()):
        if 'tempfile' == file:
            shutil.rmtree(os.getcwd() + os.sep + 'tempfile')
        if 'resultfile' == file:
            shutil.rmtree(os.getcwd() + os.sep + 'resultfile')

    # print 'global_actual_file_list:\t', global_actual_file_list
    for file in os.listdir(os.getcwd() + os.sep + 'result_text'):
        if 'dump' == file:
            shutil.rmtree(os.getcwd() + os.sep + 'result_text' + os.sep + 'dump')

    # 清理无用文件
    result_path = os.getcwd() + os.sep + 'result_text'
    remove_dir_path = result_path + os.sep + 'tab_num_dir'

    if os.path.exists(remove_dir_path):
        for file in os.listdir(remove_dir_path):
            os.remove(remove_dir_path + os.sep + file)
        shutil.rmtree(remove_dir_path)


#判断输入文件的有效性，支持多个文件
def judge_input_file(file):
    # file必须要有值
    contion = (len(sys.argv[1:]) == 1) and (sys.argv[1:] in [['--help'], ['-help'], ['-p'], ['--print'], ['-print']])
    # print contion
    # print 'ddddd:\t', sys.argv[1:]
    # 如果未输入文件名当且仅上在只有输出帮助信息的时候成立
    if not file:
        # 文件名必须放在在任何条件之前，否则执行警告
        if not contion:
            raise UserWarning('\033[31m请您输入需要处理的文件名!!!\033[0m')
    if contion:
        quit()

    file_info_list = []
    file_list = file.split(';')
    # print file_list
    for signal_file in file_list:
        #默认值
        actual_file_name = signal_file
        pre_dir_name = os.getcwd()
        # print 'signal_file:\t', signal_file
        # print os.path.split(signal_file)[0]
        #判断文件是否是有效的路径
        if os.path.isdir(os.path.split(signal_file)[0]):
            # print '是路径'
            actual_file_name = os.path.split(signal_file)[1]
            pre_dir_name = os.path.split(signal_file)[0]
            #是路径则判断文件是否存在
            if not actual_file_name in os.listdir(pre_dir_name):
                # print '文件在对应目录中不存在'
                raise UserWarning('\033[31m文件 [ %s ] 是路径但是在对应目录中不存在\033[0m' %signal_file)
        #非路径则默认在当前目录下
        else:
            if not signal_file in os.listdir(os.getcwd()):
                raise UserWarning('\033[31m文件 [ %s ] 不是路径并且在当前目录中不存在\033[0m' %signal_file)
        file_info_list.append([actual_file_name, pre_dir_name])
        # print 'actual_file_name:\t', actual_file_name
        # print 'pre_dir_name:\t', pre_dir_name
    return file_info_list

#处理将html文件拷贝到另一台机器后造成的格式问题bug
def deal_html_data():
    object_path = os.getcwd() + os.sep + 'result_text'
    read_file = open(object_path + os.sep + 'result_show.html', 'r')
    write_file = open(object_path + os.sep + 'final_result.html', 'w')

    line = read_file.readline()
    write_file.write(line)
    while len(line) != 0:
        line = read_file.readline()
        if '</head>' == line.strip('\n'):
            write_file.write('<style type="text/css">tr{ white-space:0;}\n.table0{border:none;width:100%;}\n'
                             '.table0_td{padding:0 0px 0px 0;}\n.table1 {border-collapse:collapse;width:100%;}\n'
                             '.table1 td{ height:30px;border:#333333 solid 1px;text-align:center;width:25%}\n'
                             '</style></head>\n')
            continue
        write_file.write(line)
    read_file.close()
    write_file.close()
    os.remove(object_path + os.sep + 'result_show.html')
    shutil.copy(object_path + os.sep + 'final_result.html', object_path + os.sep + 'result_show.html')
    os.remove(object_path + os.sep + 'final_result.html')

if __name__ == '__main__':
    time_start = time.time()
    global_actual_file_list = []
    multi_file_flag = False

    #命令行参数设置
    orignal_file, range_lineno_string, keyword, combine_flag, print_flag= main()
    # print orignal_file,range_lineno_string, keyword, combine_flag, print_flag
    #判断输入的文件是否带有（绝对,相对）路径，如不带则默认是当前目录
    file_info_list = judge_input_file(orignal_file)
    # print 'file_info_list:\t', file_info_list
    #获取行区间range
    legal_lineno_list = get_range_line(range_lineno_string)
    # print '4444',legal_lineno_list
    #获取keword
    keyword_list = get_keyword(keyword)
    for file in file_info_list:
        first_file_flag = False
        if file == file_info_list[0]:
            first_file_flag = True
        # print 'first_file_flag:\t', first_file_flag

        #同一次输入多个文件，之间默认是连接的，连接标志置为True
        if len(file_info_list) > 1:
            # combine_flag = True
            multi_file_flag = True

        actual_file_name, pre_dir_name = file[0], file[1]
        global_actual_file_list.append(actual_file_name)
        #根据命令行参数分类进行处理
        classify_parameters(actual_file_name, pre_dir_name, legal_lineno_list, keyword_list, combine_flag=combine_flag,
                            multi_file_flag=multi_file_flag, first_file_flag=first_file_flag)
        #生成html
        object = objectHtmlDataList(actual_file_name, combine_flag=combine_flag, multi_file_flag=multi_file_flag, first_file_flag=first_file_flag)
        attribute_value_list_key, attribute_value_list_value = object.generateTable()
        # 生成txt文档
        create_text_info(actual_file_name, pre_dir_name, attribute_value_list_key, attribute_value_list_value, combine_flag, print_flag,
                         multi_file_flag=multi_file_flag, first_file_flag=first_file_flag)

    # 生成xml文件
    create_xml(global_actual_file_list, combine_flag=combine_flag)
    # 处理生成的html文件
    deal_html_data()
    # 清理临时文件
    clear_temp_file()
    time_end = time.time()
    # print time_end - time_start
