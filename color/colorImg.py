# (2) 영상 처리 및 이미지 기반의 데이터 분석 통합 GUI 툴
#  --> RAW, GIF, JPG, PNG, BMP, TIF 영상 데이터 분석 및 처리
#  --> 영상 데이터와 CSV, SQLite, MySQL, XLS 저장 및 로딩 기능 지원
#  --> Image Processing 알고리즘 (화소점, 화소영역, 기하학 등)
#  --> 히스토그램을 통한 데이터 분석 및 영상 개선 알고리즘
#  --> 대량의 영상 빅데이터 자동변환 기능 (자동화)

## 라이브러리
from tkinter import *
from tkinter.filedialog import *
from tkinter.simpledialog import *
import operator
import os.path
import math
import threading
import numpy
import xlsxwriter
from xlsxwriter import Workbook
import struct
import csv
import sqlite3
import pymysql
import xlwt
import glob
import matplotlib.pyplot as plt
from matplotlib import colors
from wand.color import Color
from wand.drawing import Drawing
from wand.image import *

## 함수선언부

### 파일메뉴
#### 이미지 로딩 및 디스플레이

def loadImage(fname) :  # Gray-scale 이미지 로딩하기
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    fsize = os.path.getsize(fname) # 파일 크기 확인
    inH = inW = int(math.sqrt(fsize))  # 입력메모리 크기 결정! (중요)
    inImage = []; tmpList = []
    for i in range(inH) :  # 입력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(inW) :
            tmpList.append(0)
        inImage.append(tmpList)
    # 파일 --> 메모리로 데이터 로딩
    fp = open(fname, 'rb') # 파일 열기(바이너리 모드)
    for  i  in range(inH) :
        for  k  in  range(inW) :
            inImage[i][k] =  int(ord(fp.read(1)))
    fp.close()

def display_raw() : #Gray-scale 이미지 출력하기
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 기존에 캐버스 있으면 뜯어내기.
    if  canvas != None :
        canvas.destroy()
    # 화면 준비 (고정됨)
    VIEW_X, VIEW_Y = 256, 256
    if VIEW_X >= outW or VIEW_Y >= outH : # 영상이 128미만이면
        VIEW_X = outW
        VIEW_Y = outH
        step = 1  # 건너뛸숫자
    else :
        step = outW / VIEW_X # step을 실수도 인정. 128, 256, 512 단위가 아닌 것 고려.

    window.geometry(str(VIEW_X*2) + 'x' + str(VIEW_Y*2))
    canvas = Canvas(window, width=VIEW_X, height=VIEW_Y)
    paper = PhotoImage(width=VIEW_X, height=VIEW_Y)
    canvas.create_image((VIEW_X/2, VIEW_X/2), image=paper, state='normal')
    # 화면에 출력. 실수 step을 위해서 numpy 사용
    def putPixel() :
        for i in numpy.arange(0, outH,step) :
            for k in numpy.arange(0, outW,step) :
                i = int(i); k = int(k) # 첨자이므로 정수화
                data = outImage[i][k]
                paper.put('#%02x%02x%02x' % (data, data, data),
                          ( int(k/step),int(i/step)))

    threading.Thread(target=putPixel).start()
    canvas.pack(expand=1, anchor =CENTER)
    status.configure(text='이미지 정보:' + str(outW) + 'x' + str(outH) )


def loadColorImage(fname) :  # Color 이미지 로딩하기
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR,outImageG,outImageB , inW, inH, outW, outH

    photo = PhotoImage(file=filename)
    inW = photo.width();   inH = photo.height()

    inImageR, inImageG, inImageB  = [], [],[]; tmpList = []
    for i in range(inH) :  # 입력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(inW) :
            tmpList.append(0)
        inImageR.append(tmpList[:])
    for i in range(inH):  # 입력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(inW):
            tmpList.append(0)
        inImageG.append(tmpList[:])
    for i in range(inH):  # 입력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(inW):
            tmpList.append(0)
        inImageB.append(tmpList[:])

    # 파일 --> 메모리로 데이터 로딩
    for  i  in range(inH) :
        for  k  in  range(inW) :
            r, g, b = photo.get(k,i)
            #print(r,g,b,end='/')
            inImageR[i][k] = r
            inImageG[i][k] = g
            inImageB[i][k] = b
            #print(inImageR[i][k], inImageG[i][k], inImageB[i][k], end='/')
    photo=None

def display_Color() :
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 기존에 캐버스 있으면 뜯어내기.
    if canvas != None:
        canvas.destroy()
    # 화면 준비 (고정됨)
    VIEW_X, VIEW_Y = 256, 256
    if VIEW_X >= outW or VIEW_Y >= outH:  # 영상이 128미만이면
        VIEW_X = outW
        VIEW_Y = outH
        step = 1  # 건너뛸숫자
    else:
        step = outW / VIEW_X  # step을 실수도 인정. 128, 256, 512 단위가 아닌 것 고려.

    window.geometry(str(VIEW_X * 2) + 'x' + str(VIEW_Y * 2))
    canvas = Canvas(window, width=VIEW_X, height=VIEW_Y)
    paper = PhotoImage(width=VIEW_X, height=VIEW_Y)
    canvas.create_image((VIEW_X / 2, VIEW_X / 2), image=paper, state='normal')

    # 화면에 출력. 실수 step을 위해서 numpy 사용
    def putPixel():
        for i in numpy.arange(0, outH, step):
            for k in numpy.arange(0, outW, step):
                i = int(i)
                k = int(k)  # 첨자이므로 정수화
                dataR = outImageR[i][k]
                dataG = outImageG[i][k]
                dataB = outImageB[i][k]
                # print(dataR, dataG, dataB, end='/')
                paper.put('#%02x%02x%02x' % (dataR, dataG, dataB), (int(k / step), int(i / step)))
    threading.Thread(target=putPixel).start()
    canvas.pack(expand=1, anchor=CENTER)
    status.configure(text='이미지 정보:' + str(outW) + 'x' + str(outH))


def display_first_Color():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH, photo, paper_copy
    if canvas != None:
        canvas.destroy()
        # 화면 준비 (고정됨)
    VIEW_X, VIEW_Y = 256, 256
    if VIEW_X >= outW or VIEW_Y >= outH:  # 영상이 128미만이면
        VIEW_X = outW
        VIEW_Y = outH
        step = 1  # 건너뛸숫자
    else:
        step = outW / VIEW_X  # step을 실수도 인정. 128, 256, 512 단위가 아닌 것 고려.

    window.geometry(str(VIEW_X * 2) + 'x' + str(VIEW_Y * 2))
    canvas = Canvas(window, width=VIEW_X, height=VIEW_Y)
    paper = PhotoImage(width=VIEW_X, height=VIEW_Y)
    canvas.create_image((VIEW_X / 2, VIEW_X / 2), image=paper, state='normal')

    # 화면에 출력. 실수 step을 위해서 numpy 사용
    def putPixel():
        for i in numpy.arange(0, outH, step):
            for k in numpy.arange(0, outW, step):
                i = int(i)
                k = int(k)  # 첨자이므로 정수화
                dataR = outImageR[i][k]
                dataG = outImageG[i][k]
                dataB = outImageB[i][k]
                paper.put('#%02x%02x%02x' % (dataR, dataG, dataB), (int(k / step), int(i / step)))
                paper_copy.put('#%02x%02x%02x' % (dataR, dataG, dataB), (int(k / step), int(i / step)))

    threading.Thread(target=putPixel).start()
    canvas.pack()


def display_copy_Color():
    global window, canvas, pLabel, paper, filename, inImage, outImage, inW, inH, outW, outH, photo, paper_copy
    if canvas != None:
        canvas.destroy()
    window.geometry(str(outH * 2) + 'x' + str(outW))
    canvas = Canvas(window, width=outW, height=outH)
    canvas.create_image((outW / 2, outH / 2), image=paper, state='normal')
    canvas.pack(side=RIGHT)
    photo = PhotoImage()
    pLabel = Label(window, image=photo)
    pLabel.pack(side=LEFT)
    pLabel.configure(image=paper_copy)


def rollback_gif():
    global window, canvas, paper, PLabel, filename, inImage, outImage, inW, inH, outW, outH, photo, paper_copy
    if pLabel != None:
        pLabel.destroy()
    loadColorImage(filename)
    equal_Color()


#### 데이터 파일형식 로딩

def loadRawCSV(fname) :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    fsize = -1
    fp = open(fname, 'r')
    for  f  in fp :
        fsize += 1
    fp.close()
    inH = inW = int(math.sqrt(fsize))  # 입력메모리 크기 결정! (중요)
    inImage = []; tmpList = []
    for i in range(inH) :  # 입력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(inW) :
            tmpList.append(0)
        inImage.append(tmpList)
    # 파일 --> 메모리로 데이터 로딩
    fp = open(fname, 'r') # 파일 열기(바이너리 모드)
    csvFP = csv.reader(fp)
    next(csvFP)
    for row_list in csvFP :
        row= int(row_list[0]) ; col = int(row_list[1]) ; value=int(row_list[2])
        inImage[row][col] = value
    fp.close()

#### 열기메뉴

def openRawFile() :    #Gray-scale 이미지 불러오기
    global window, canvas, paper, filename,inImage, outImage,inW, inH, outW, outH
    filename = askopenfilename(parent=window,
                               filetypes=(("RAW파일", "*.raw"), ("모든파일", "*.*")))
    loadImage(filename) # 파일 --> 입력메모리
    equal_raw() # 입력메모리--> 출력메모리


def openColorFile() :    #Color 이미지 불러오기
    global window, canvas, paper, filename,inImageR, inImageG, inImageB, outImageR,outImageG,outImageB ,inW, inH, outW, outH
    filename = askopenfilename(parent=window,
                               filetypes=(("그림파일", "*.gif;*.jpg;*.png;*.tif;*.bmp"), ("모든파일", "*.*")))
    loadColorImage(filename) # 파일 --> 입력메모리
    equal_Color() # 입력메모리--> 출력메모리


def openRawCSV() :
    global window, canvas, paper, filename,inImage, outImage,inW, inH, outW, outH
    filename = askopenfilename(parent=window,
                               filetypes=(("CSV파일", "*.csv"), ("모든파일", "*.*")))
    loadRawCSV(filename) # 파일 --> 입력메모리
    equal_raw() # 입력메모리--> 출력메모리



def openRawSQLite() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    global csvList, input_file
    con = sqlite3.connect('imageDB')  # 데이터베이스 지정(또는 연결)
    cur = con.cursor()  # 연결 통로 생성 (쿼리문을 날릴 통로)
    try :
        sql = "SELECT DISTINCT filename, resolution FROM imageTable"
        cur.execute(sql)
        tableNameList = [] # ['강아지:128', '강아지:512' ....]
        while True :
            row = cur.fetchone()
            if row == None :
                break
            tableNameList.append( row[0] + ':' + str(row[1]) )

        ######## 내부 함수 (Inner Function) : 함수 안의 함수,지역함수 #######
        def selectTable() :
            global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
            selectedIndex = listbox.curselection()[0]
            subWindow.destroy()
            fname, res = tableNameList[selectedIndex].split(':')
            filename = fname
            sql = "SELECT row, col, value FROM imageTable WHERE filename='" + \
                fname + "' AND resolution=" + res
            print(sql)
            cur.execute(sql)

            inH = inW = int(res)
            inImage = [];  tmpList = []
            for i in range(inH):  # 입력메모리 확보(0으로 초기화)
                tmpList = []
                for k in range(inW):
                    tmpList.append(0)
                inImage.append(tmpList)
            while True :
                row_tuple = cur.fetchone()
                if row_tuple == None :
                    break
                row, col, value = row_tuple
                inImage[row][col] = value

            cur.close()
            con.close()
            equal_raw()
            print("Ok.")

        ################################################################

        subWindow = Toplevel(window)
        listbox = Listbox(subWindow)
        button = Button(subWindow, text='선택', command=selectTable)
        listbox.pack(); button.pack()
        for sName in tableNameList :
            listbox.insert(END, sName)
        subWindow.lift()
    except :
        cur.close()
        con.close()
        print("Error.")

def openRawMySQL() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    global csvList, input_file
    con = pymysql.connect(host='192.168.200.131', user='root', password='1234', db='imageDB', charset='utf8')  # 데이터베이스 지정(또는 연결)
    cur = con.cursor()  # 연결 통로 생성 (쿼리문을 날릴 통로)
    try :
        sql = "SELECT DISTINCT filename, resolution FROM imageTable"
        cur.execute(sql)
        tableNameList = [] # ['강아지:128', '강아지:512' ....]
        while True :
            row = cur.fetchone()
            if row == None :
                break
            tableNameList.append( row[0] + ':' + str(row[1]) )

        ######## 내부 함수 (Inner Function) : 함수 안의 함수,지역함수 #######
        def selectTable() :
            global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
            selectedIndex = listbox.curselection()[0]
            subWindow.destroy()
            fname, res = tableNameList[selectedIndex].split(':')
            filename = fname
            sql = "SELECT row, col, value FROM imageTable WHERE filename='" + \
                fname + "' AND resolution=" + res
            print(sql)
            cur.execute(sql)

            inH = inW = int(res)
            inImage = [];  tmpList = []
            for i in range(inH):  # 입력메모리 확보(0으로 초기화)
                tmpList = []
                for k in range(inW):
                    tmpList.append(0)
                inImage.append(tmpList)
            while True :
                row_tuple = cur.fetchone()
                if row_tuple == None :
                    break
                row, col, value = row_tuple
                inImage[row][col] = value

            cur.close()
            con.close()
            equal_raw()
            print("Ok! openMySQL")

        ################################################################

        subWindow = Toplevel(window)
        listbox = Listbox(subWindow)
        button = Button(subWindow, text='선택', command=selectTable)
        listbox.pack(); button.pack()
        for sName in tableNameList :
            listbox.insert(END, sName)
        subWindow.lift()

    except :
        cur.close()
        con.close()
        print("Error! openMySQL")


#### 저장메뉴

def saveRawFile() :
    global window, canvas, paper, filename,inImage, outImage,inW, inH, outW, outH
    saveFp = asksaveasfile(parent=window, mode='wb', defaultextension="*.raw", filetypes=(("RAW파일", "*.raw"), ("모든파일", "*.*")))
    for i in range(outH):
        for k in range(outW):
            saveFp.write(struct.pack('B',outImage[i][k]))
    saveFp.close()

def saveColorFile() :
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    draw = Drawing()  # 빈 판을 준비

    saveFp = asksaveasfile(parent=window, mode='w', defaultextension='.png'
                           , filetypes=(("그림파일", "*.gif;*.jpg;*.png;*.tif;*.bmp"), ("모든파일", "*.*")))

    # 빈 판에 칼라찍기. '#000000~#FFFFFF'
    for i in range(outH):
        for k in range(outW):
            dataR = outImageR[i][k]
            dataG = outImageG[i][k]
            dataB = outImageB[i][k]
            hexStr = '#'
            if dataR > 15:
                hexStr += hex(dataR)[2:]
            else:
                hexStr += ('0' + hex(dataR)[2:])
            if dataG > 15:
                hexStr += hex(dataG)[2:]
            else:
                hexStr += ('0' + hex(dataG)[2:])
            if dataB > 15:
                hexStr += hex(dataB)[2:]
            else:
                hexStr += ('0' + hex(dataB)[2:])
            draw.fill_color = Color(hexStr)
            draw.color(k, i, 'replace')

    with Image(filename=filename) as img:
        draw(img)
        img.save(filename=saveFp.name)

    print('Save... OK!')

def saveRawCSV() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    output_file = asksaveasfile(parent=window, mode='w',
                               defaultextension="*.csv", filetypes=(("CSV파일", "*.csv"), ("모든파일", "*.*")))
    output_file = output_file.name

    header = ['Column', 'Row', 'Value']
    with open(output_file, 'w', newline='') as filewriter:
        csvWriter = csv.writer(filewriter)
        csvWriter.writerow(header)
        for row in range(outW):
            for col in range(outH):
                data = outImage[row][col]
                row_list = [row, col, data]
                csvWriter.writerow(row_list)

def saveRawSQLite() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    global csvList, input_file
    con = sqlite3.connect('imageDB')  # 데이터베이스 지정(또는 연결)
    cur = con.cursor()  # 연결 통로 생성 (쿼리문을 날릴 통로)
    # 열이름 리스트 만들기
    colList = []
    fname = os.path.basename(filename).split(".")[0]
    try:
        sql = "CREATE TABLE imageTable( filename CHAR(20), resolution smallint" + \
            ", row  smallint,  col  smallint, value  smallint)"
        cur.execute(sql)
    except:
        pass

    for i in range(inW) :
        for k in range(inH) :
            sql = "INSERT INTO imageTable VALUES('" + fname + "'," + str(inW) + \
                "," + str(i) + "," + str(k) + "," + str(inImage[i][k]) +")"
            cur.execute(sql)
    con.commit()
    cur.close()
    con.close()  # 데이터베이스 연결 종료
    print('Ok!')

def saveRawMySQL() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    global csvList, input_file
    con = pymysql.connect(host='192.168.200.131', user='root', password='1234', db='imageDB', charset='utf8')  # 데이터베이스 지정(또는 연결)
    cur = con.cursor()  # 연결 통로 생성 (쿼리문을 날릴 통로)
    # 열이름 리스트 만들기
    colList = []
    fname = os.path.basename(filename).split(".")[0]
    try:
        sql = "CREATE TABLE imageTable( filename CHAR(20), resolution smallint" + \
            ", row  smallint,  col  smallint, value  smallint)"
        cur.execute(sql)
    except:
        pass

    try:
        sql = "DELETE FROM imageTable WHERE filename='" + \
              fname + "' AND resolution=" + str(outW)
        cur.execute(sql)
        con.commit()
    except:
        pass

    for i in range(inW) :
        for k in range(inH) :
            sql = "INSERT INTO imageTable VALUES('" + fname + "'," + str(outW) + \
                "," + str(i) + "," + str(k) + "," + str(outImage[i][k]) +")"
            cur.execute(sql)
    con.commit()
    cur.close()
    con.close()  # 데이터베이스 연결 종료
    print('Ok! saveMySQL')


def saveNumExcel():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    output_file = asksaveasfile(parent=window, mode='w',
                               defaultextension="*.xlsx", filetypes=(("EXCEL파일", "*.xls"), ("모든파일", "*.*")))
    output_file = output_file.name

    sheetName = os.path.basename(output_file).split(".")[0]
    wb = xlwt.Workbook()
    ws = wb.add_sheet(sheetName)

    for rowNum in range(outH):
        for colNum in range(outW):
            data = outImage[rowNum][colNum]
            ws.write(rowNum, colNum, data)
    wb.save(output_file)

def saveRawExcel():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    output_file = asksaveasfile(parent=window, mode='w',
                                defaultextension="*.xlsx", filetypes=(("XLSX파일", "*.xls"), ("모든파일", "*.*")))
    output_file = output_file.name

    sheetName = os.path.basename(output_file).split(".")[0]
    wb = xlsxwriter.Workbook(output_file)
    ws = wb.add_worksheet(sheetName)

    # 워크시트의 열 너비 및 행 높이를 지정
    ws.set_column(0, outW, 1.0)  # 약 0.34 열 너비
    for r in range(outH):
        ws.set_row(r, 9.5)  # 약 0.35 행 높이

    for rowNum in range(outW):
        for colNum in range(outH):
            data = outImage[rowNum][colNum]
            # data 값으로 셀의 배경색을 조절 #000000~#FFFFFF
            if data > 15:
                hexStr = '#' + (hex(data)[2:]) * 3
            else:
                hexStr = '#' + ('0' + hex(data)[2:]) * 3

            # 셀의 포맷을 준비
            cell_format = wb.add_format()
            cell_format.set_bg_color(hexStr)
            ws.write(rowNum, colNum, '', cell_format)
    wb.close()


def saveColorNumExcel():
    global window, canvas, paper, filename, inImage, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    output_file = asksaveasfile(parent=window, mode='w',
                               defaultextension="*.xlsx", filetypes=(("EXCEL파일", "*.xls"), ("모든파일", "*.*")))
    output_file = output_file.name

    sheetName = os.path.basename(output_file).split(".")[0]
    wb = xlwt.Workbook()
    ws = wb.add_sheet(sheetName)

    for rowNum in range(outH):
        for colNum in range(outW):
            data = outImageR[rowNum][colNum]
            data += outImageG[rowNum][colNum]
            data += outImageB[rowNum][colNum]
            ws.write(rowNum, colNum, data)
    wb.save(output_file)

def saveColorExcel():
    global window, canvas, paper, filename, inImage, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    output_file = asksaveasfile(parent=window, mode='w',
                                defaultextension="*.xlsx", filetypes=(("XLSX파일", "*.xls"), ("모든파일", "*.*")))
    output_file = output_file.name

    sheetName = os.path.basename(output_file).split(".")[0]
    wb = xlsxwriter.Workbook(output_file)
    ws = wb.add_worksheet(sheetName)

    # 워크시트의 열 너비 및 행 높이를 지정
    ws.set_column(0, outW, 1.0)  # 약 0.34 열 너비
    for r in range(outH):
        ws.set_row(r, 9.5)  # 약 0.35 행 높이

    for rowNum in range(outW):
        for colNum in range(outH):
            dataR = outImageR[rowNum][colNum]
            # data 값으로 셀의 배경색을 조절 #000000~#FFFFFF
            if dataR <= 15: # 15 이하일 경우, 1자리 수이기 때문에 0을 추가
                hexStr = '#' + ('0' + hex(dataR)[2:])
            else:
                hexStr = '#' + (hex(dataR)[2:])  # 16진수 변환 후, R(2자리)

            dataG = outImageG[rowNum][colNum]
            # data 값으로 셀의 배경색을 조절 #000000~#FFFFFF
            if dataG <= 15:
                hexStr += ('0' + hex(dataG)[2:])  # G(2자리)
            else:
                hexStr += hex(dataG)[2:]
            dataB = outImageB[rowNum][colNum]
            # data 값으로 셀의 배경색을 조절 #000000~#FFFFFF
            if dataB <= 15:
                hexStr += ('0' + hex(dataB)[2:])  # B(2자리)
            else:
                hexStr += hex(dataB)[2:]

            # 셀의 포맷을 준비
            cell_format = wb.add_format()  # RGB코드는 #을 앞에
            cell_format.set_bg_color((hexStr))
            ws.write(rowNum, colNum, '', cell_format)

    wb.close()

def saveRawAllMySQL():  #    폴더 안의 raw 파일들을 모두 DB로 저장
    global window, canvas, paper, filename, inImage, inW, inH
    con = pymysql.connect(host='192.168.226.131', user='root', password='1234', db='imagedb',
                          charset='utf8')  # pymySQL 연결
    cur = con.cursor()
    dirName = askdirectory()
    file_list = glob.glob(os.path.join(dirName, "*.raw"))  # 폴더지정
    for input_file in file_list:
        filereader = open(input_file, 'rb')
        fsize = os.path.getsize(input_file)  # raw파일 size
        inH = inW = int(math.sqrt(fsize))
        tableName = os.path.basename(input_file).split(".")[0]  # tablename을 위한 축략
        colList = ["row", "col", "grayscale"]  # table col에 들어갈 리스트
        try:
            sql = "CREATE table " + tableName + "("
            for colname in colList:
                sql += colname + " int(5),"
            sql = sql[:-1]
            sql += ")"
            cur.execute(sql)  # table query (filename, row, col, grayscale)
        except:
            print("error --> ", input_file)
        for i in range(inW):
            for j in range(inH):
                sql = "INSERT into " + tableName + " Values("
                sql += str(i) + ", " + str(j) + ", " + str(int(ord(filereader.read(1))))
                sql += ")"
                try:
                    cur.execute(sql)  # value insert
                except:
                    pass
    filereader.close()

    def saveRAW(): #        DB 안의 RAW(filename / row / col / grayscale) 데이터를 파일로 저장하는 함수
        global window, canvas, paper, filename, inImage, inW, inH
        con = pymysql.connect(host='192.168.226.131', user='root', password='1234', db='imagedb',
                              charset='utf8')  # pymySQL 연결
        cur = con.cursor()
        sql = "SHOW TABLES"  # table description이 담긴 정보를 리턴하는 쿼리
        cur.execute(sql)
        dirName = askdirectory()  # 저장할 폴더 directory ask
        tableNameList = []
        while True:
            row = cur.fetchone()
            if row == None:
                break
            tableNameList.append(row[0])  # tableNameList -> 모든 Table의 이름을 받아 리스트
        for tableName in tableNameList:
            sql = "SELECT * FROM " + tableName
            cur.execute(sql)
            while True:
                row = cur.fetchone()
                if row == None:
                    break
                output_file = dirName + "/" + tableName + ".raw"  # save file 경로
                saveFp = open(output_file, "wb")
                saveFp.write(struct.pack('B', row[2]))
            saveFp.close()
        cur.close()
        con.close()

    con.commit()
    cur.close()
    con.close()
    print("OK")


#### 종료메뉴
def exitFile():
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    window.quit()
    window.destroy()



### 화소점처리

#### 동일영상보기

def equal_raw() :  # Gray-scale사본 영상 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage = [];   tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImage[i][k] = inImage[i][k]
    display_raw()

def equal_Color() :  # Color사본 영상 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])

    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for i in range(inH):
        for k in range(inW):
            outImageR[i][k] = inImageR[i][k]
            outImageG[i][k] = inImageG[i][k]
            outImageB[i][k] = inImageB[i][k]
            # print(outImageR[i][k], outImageG[i][k], outImageB[i][k], end='/')

    display_Color()

#### 밝기 조정

## Gray scale 값
def raw_brightAdd() :  # Gray scale 밝기조정(덧셈)
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage=[]
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    value = askinteger('밝게하기', '밝게할 값-->', minvalue=1, maxvalue=255)
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if inImage[i][k] + value > 255 :
                outImage[i][k] = 255
            else :
                outImage[i][k] = inImage[i][k] + value
    display_raw()

def raw_brightSub() :  # Gray scale 밝기조정(뺄셈)
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage=[]
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    value = askinteger('어둡게하기', '어둡게할 값-->', minvalue=1, maxvalue=255)
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if inImage[i][k] - value < 0 :
                outImage[i][k] = 0
            else :
                outImage[i][k] = inImage[i][k] - value
    display_raw()

def raw_mulitply() :  # Gray scale 밝기조정(곱셈)
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage=[]
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList[:])

    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    value = askinteger('더 밝게하기', '숫자(1~10) 입력:', minvalue=1, maxvalue=10)
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if inImage[i][k] * value > 255 :
                outImage[i][k] = 255
            elif inImage[i][k] * value < 0:
                outImage[i][k] = 0
            else:
                outImage[i][k] = int(inImage[i][k] * value)
    display_raw()

def raw_division() :  # Gray-scale 밝기조정(나눗셈)
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage=[]
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    value = askinteger('어둡게하기', '숫자(1~10) 입력:', minvalue=1, maxvalue=10)
    for i in range(inH):
        for k in range(inW):
            if outImage[i][k] / value < 0:
                outImage[i][k] = 0
            elif outImage[i][k] / value < 0:
                outImage[i][k] = 0
            else:
                outImage[i][k] = int(outImage[i][k] / value)
    display_raw()



## Color 값
def color_brightAdd() :  # Color 밝기조정(덧셈)
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR,outImageG,outImageB, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH

    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])

    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    value = askinteger('밝게하기', '밝게할 값-->', minvalue=1, maxvalue=255)
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if inImageR[i][k] + value > 255 :
                outImageR[i][k] = 255
            else :
                outImageR[i][k] = inImageR[i][k] + value
            if inImageG[i][k] + value > 255 :
                outImageG[i][k] = 255
            else :
                outImageG[i][k] = inImageG[i][k] + value
            if inImageB[i][k] + value > 255 :
                outImageB[i][k] = 255
            else :
                outImageB[i][k] = inImageB[i][k] + value

    display_Color()

def color_brightSub() :  # Color 밝기조정(뺄셈)
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR,outImageG,outImageB, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])

    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    value = askinteger('어둡게하기', '어둡게할 값-->', minvalue=1, maxvalue=255)
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if inImageR[i][k] - value < 0 :
                outImageR[i][k] = 0
            else :
                outImageR[i][k] = inImageR[i][k] - value
            if inImageG[i][k] - value < 0:
                outImageG[i][k] = 0
            else :
                outImageG[i][k] = inImageG[i][k] - value
            if inImageB[i][k] - value < 0 :
                outImageB[i][k] = 0
            else :
                outImageB[i][k] = inImageB[i][k] - value

    display_Color()

def color_mulitply() :  # Color 밝기조정(곱셈)
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR,outImageG,outImageB, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])

    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    value = askinteger('더 밝게하기', '숫자(1~10) 입력:', minvalue=1, maxvalue=10)
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if inImageR[i][k] * value > 255 :
                outImageR[i][k] = 255
            elif inImageR[i][k] * value < 0:
                outImageR[i][k] = 0
            else:
                outImageR[i][k] = int(inImageR[i][k] * value)
            if inImageG[i][k] * value > 255:
                outImageG[i][k] = 255
            elif inImageG[i][k] * value < 0:
                outImageG[i][k] = 0
            else:
                outImageG[i][k] = int(inImageG[i][k] * value)
            if inImageB[i][k] * value > 255 :
                outImageB[i][k] = 255
            elif inImageB[i][k] * value < 0:
                outImageB[i][k] = 0
            else:
                outImageB[i][k] = int(inImageB[i][k] * value)

    display_Color()

def color_division() :  # Color 밝기조정(나눗셈)
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR,outImageG,outImageB, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])

    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    value = askinteger('어둡게하기', '숫자(1~10) 입력:', minvalue=1, maxvalue=10)
    for i in range(inH):
        for k in range(inW):
            if inImageR[i][k] / value < 0:
                outImageR[i][k] = 0
            elif inImageR[i][k] / value < 0:
                outImageR[i][k] = 0
            else:
                outImageR[i][k] = int(inImageR[i][k] / value)
    for i in range(inH):
        for k in range(inW):
            if inImageG[i][k] - value < 0:
                outImageG[i][k] = 0
            elif inImageG[i][k] / value < 0:
                outImageG[i][k] = 0
            else:
                outImageG[i][k] = int(inImageG[i][k] / value)
    for i in range(inH):
        for k in range(inW):
            if inImageB[i][k] - value < 0:
                outImageB[i][k] = 0
            elif inImageB[i][k] / value < 0:
                outImageB[i][k] = 0
            else:
                outImageB[i][k] = int(inImageB[i][k] / value)

    display_Color()



#### 화소값처리

def raw_reverse():  #Gray-scale 화소값 반전
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH

    for i in range(outH):  # 입력 메모리 확보(0으로 초기화)
        tmplist = []
        for k in range(outW):
            tmplist.append(0)  # 0으로 초기화
        outImage.append(tmplist)
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = 255 - inImage[i][k]
    display_raw()

def raw_cap(): #Gray-scale 파라볼라(Cap)
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH

    for i in range(outH):  # 입력 메모리 확보(0으로 초기화)
        tmplist = []
        for k in range(outW):
            tmplist.append(0)  # 0으로 초기화
        outImage.append(tmplist)
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    for i in range(inH):
        for k in range(inW):
            new_value = 255 - 255 * pow((getdouble)(inImage[i][k] / 128.0) - 1.0, 2)
            if new_value < 0:
                outImage[i][k] = 0
            elif new_value > 255:
                outImage[i][k] = 255
            else:
                outImage[i][k] = int(new_value)
    display_raw()

def raw_cup():  #Gray-scale 파라볼라(Cup)
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH

    for i in range(outH):  # 입력 메모리 확보(0으로 초기화)
        tmplist = []
        for k in range(outW):
            tmplist.append(0)  # 0으로 초기화
        outImage.append(tmplist)
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    for i in range(inH):
        for k in range(inW):
            new_value = 255 * pow((getdouble)(inImage[i][k] / 128.0) - 1.0, 2)
            if new_value < 0:
                outImage[i][k] = 0
            elif new_value > 255:
                outImage[i][k] = 255
            else:
                outImage[i][k] = int(new_value)
    display_raw()

def raw_gamma():    #Gray-scale 감마값
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH

    for i in range(outH):  # 입력 메모리 확보(0으로 초기화)
        tmplist = []
        for k in range(outW):
            tmplist.append(0)  # 0으로 초기화
        outImage.append(tmplist)
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    value = askfloat('감마처리', '실수값(0~1)을 입력하세요:', minvalue=0, maxvalue=1)
    for i in range(inH):
        for k in range(inW):
            new_value = pow(inImage[i][k], 1 / value)
            if new_value < 0:
                outImage[i][k] = 0
            elif new_value > 255:
                outImage[i][k] = 255
            else:
                outImage[i][k] = int(new_value)
    display_raw()


def raw_binarAdaptive():    #Gray-scale 적응 이진화
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH

    for i in range(outH):  # 입력 메모리 확보(0으로 초기화)
        tmplist = []
        for k in range(outW):
            tmplist.append(0)  # 0으로 초기화
        outImage.append(tmplist)
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    value = askfloat('이진화 처리', '숫자(1~255)를 입력하세요.', minvalue=1, maxvalue=255)
    for i in range(inH):
        for k in range(inW):
            if inImage[i][k] >= value:
                outImage[i][k] = 255
            else:
                outImage[i][k] = 0
    display_raw()

def raw_spotLight():  #Gray-scale 범위 강조 변환
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH

    for i in range(outH):  # 입력 메모리 확보(0으로 초기화)
        tmplist = []
        for k in range(outW):
            tmplist.append(0)  # 0으로 초기화
        outImage.append(tmplist)
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################

    startPoint = askinteger('강조할 범위 값', '시작 값(0~255):', minvalue=0, maxvalue=255)
    endPoint = askinteger('강조할 범위 값', '마지막 값(0~255):', minvalue=0, maxvalue=255)
    for i in range(inH):
        for k in range(inW):
            if (inImage[i][k] >= startPoint) & (inImage[i][k] <= endPoint):
                outImage[i][k] = 255
            else:
                outImage[i][k] = inImage[i][k]
    display_raw()


def raw_morphing() :  # Gray-scale 모핑(합성) 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH

    #영상파일 선택
    filename2 = askopenfilename(parent=window,filetypes=(("RAW파일", "*.raw"), ("모든파일", "*.*")))
    if filename2 =='' or filename2 ==None:
        return
    inImage2=[]
    fsize2=os.path.getsize(filename2)
    inH2 = inW2 =int(math.sqrt(fsize2))
    if inH2 != inH:
        return
    fp2 = open(filename2, 'rb')
    for i in range(inH2):   # 출력메모리 확보(0으로 초기화)
        tmpList=[]
        for k in range(inW2):
            data = int(ord(fp2.read(1)))
            tmpList.append(data)
        inImage2.append(tmpList)
    fp2.close()

    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)

    ###########################
    # 진짜 영상처리 알고리즘을 구현#
    ###########################
    value = askinteger('합성비율', '두번째 영상의 가중치(%) 값-->', minvalue=1, maxvalue=99)
    w1 = (1-value/100)  #첫번째 영상의 가중치
    w2 = 1-w1 #두번째 영상의 가중치
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data=int(inImage[i][k]*w1 +inImage2[i][k]*w2)
            if data > 255 :
                data = 255
            elif data <0:
                data =0
            outImage[i][k] = data
    display_raw()


def raw_endIn() :  # 엔드-인 검색 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW;  outH = inH;
    outImage = [];   tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    minVal, maxVal, HIGH = 255, 0, 255
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data = inImage[i][k]
            if data > maxVal:
                maxVal = data
            if data < minVal:
                minVal = data
    limit = askinteger('엔드인','상하범위:', minvalue=1, maxvalue=127)
    maxVal -= limit
    minVal += limit

    #히스토그램 스트레칭시키기
    #new = (old - minVal) * HIGH / (maxVal - minVal)
    for i in range(inH):
        for k in range(inW):
            value = int((inImage[i][k] - minVal) * HIGH / (maxVal - minVal))
            if value < 0 :
                value = 0
            if value > 255:
                value = 255
            outImage[i][k] = value
    display_raw()


### Color값
def color_reverse():    #Color 화소값 반전
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], [];
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    for i in range(inH):
        for k in range(inW):
            outImageR[i][k] = 255 - inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            outImageG[i][k] = 255 - inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            outImageB[i][k] = 255 - inImageB[i][k]
    display_Color()


def color_cap():    #color 파라볼라(Cap)
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []

    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    for i in range(inH):
        for k in range(inW):
            new_value = 255 - 255 * pow((getdouble)(inImageR[i][k] / 128.0) - 1.0, 2)
            if new_value < 0:
                outImageR[i][k] = 0
            elif new_value > 255:
                outImageR[i][k] = 255
            else:
                outImageR[i][k] = int(new_value)
    for i in range(inH):
        for k in range(inW):
            new_value = 255 - 255 * pow((getdouble)(inImageG[i][k] / 128.0) - 1.0, 2)
            if new_value < 0:
                outImageG[i][k] = 0
            elif new_value > 255:
                outImageG[i][k] = 255
            else:
                outImageG[i][k] = int(new_value)
    for i in range(inH):
        for k in range(inW):
            new_value = 255 - 255 * pow((getdouble)(inImageB[i][k] / 128.0) - 1.0, 2)
            if new_value < 0:
                outImageB[i][k] = 0
            elif new_value > 255:
                outImageB[i][k] = 255
            else:
                outImageB[i][k] = int(new_value)

    display_Color()

def color_cup():  #color 파라볼라(Cup)
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    for i in range(inH):
        for k in range(inW):
            new_value = 255 * pow((getdouble)(inImageR[i][k] / 128.0) - 1.0, 2)
            if new_value < 0:
                outImageR[i][k] = 0
            elif new_value > 255:
                outImageR[i][k] = 255
            else:
                outImageR[i][k] = int(new_value)
    for i in range(inH):
        for k in range(inW):
            new_value = 255 * pow((getdouble)(inImageG[i][k] / 128.0) - 1.0, 2)
            if new_value < 0:
                outImageG[i][k] = 0
            elif new_value > 255:
                outImageG[i][k] = 255
            else:
                outImageG[i][k] = int(new_value)
    for i in range(inH):
        for k in range(inW):
            new_value = 255 * pow((getdouble)(inImageB[i][k] / 128.0) - 1.0, 2)
            if new_value < 0:
                outImageB[i][k] = 0
            elif new_value > 255:
                outImageB[i][k] = 255
            else:
                outImageB[i][k] = int(new_value)
    display_Color()


def color_gamma():    #Color 감마값
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    value = askfloat('감마처리R', '실수값(0~1)을 입력하세요:', minvalue=0, maxvalue=1)
    for i in range(inH):
        for k in range(inW):
            new_valueR = pow(inImageR[i][k], 1 / value)
            if new_valueR < 0:
                outImageR[i][k] = 0
            elif new_valueR > 255:
                outImageR[i][k] = 255
            else:
                outImageR[i][k] = int(new_valueR)
    for i in range(inH):
        for k in range(inW):
            new_valueG = pow(inImageG[i][k], 1 / value)
            if new_valueG < 0:
                outImageG[i][k] = 0
            elif new_valueG > 255:
                outImageG[i][k] = 255
            else:
                outImageG[i][k] = int(new_valueG)
    for i in range(inH):
        for k in range(inW):
            new_valueB = pow(inImageB[i][k], 1 / value)
            if new_valueB < 0:
                outImageB[i][k] = 0
            elif new_valueB > 255:
                outImageB[i][k] = 255
            else:
                outImageB[i][k] = int(new_valueB)
    display_Color()


def color_binarAdaptive():    #Color 적응 이진화
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################
    value = askfloat('이진화 처리', '숫자(1~255)를 입력하세요.', minvalue=1, maxvalue=255)
    for i in range(inH):
        for k in range(inW):
            if inImageR[i][k] >= value:
                outImageR[i][k] = 255
            else:
                outImageR[i][k] = 0
    for i in range(inH):
        for k in range(inW):
            if inImageG[i][k] >= value:
                outImageG[i][k] = 255
            else:
                outImageG[i][k] = 0
    for i in range(inH):
        for k in range(inW):
            if inImageB[i][k] >= value:
                outImageB[i][k] = 255
            else:
                outImageB[i][k] = 0
    display_Color()

def color_spotLight():  #Color 범위 강조 변환
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #####################################
    ##  이제부터 진짜 영상처리 알고리즘 구현 ##
    ####################################

    startPoint = askinteger('강조할 범위 값', '시작 값(0~255):', minvalue=0, maxvalue=255)
    endPoint = askinteger('강조할 범위 값', '마지막 값(0~255):', minvalue=0, maxvalue=255)
    startPointR = startPoint
    startPointG = startPoint
    startPointB = startPoint
    endPointR = endPoint
    endPointG = endPoint
    endPointB = endPoint

    for i in range(inH):
        for k in range(inW):
            if (inImageR[i][k] >= startPointR) & (inImageR[i][k] <= endPointR):
                outImageR[i][k] = 255
            else:
                outImageR[i][k] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            if (inImageG[i][k] >= startPointG) & (inImageG[i][k] <= endPointG):
                outImageG[i][k] = 255
            else:
                outImageG[i][k] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            if (inImageB[i][k] >= startPointB) & (inImageB[i][k] <= endPointB):
                outImageB[i][k] = 255
            else:
                outImageB[i][k] = inImageB[i][k]
    display_Color()


def color_morphing() :  # Color 모핑(합성) 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH

    #영상파일 선택
    filename2 = askopenfilename(parent=window,filetypes=(("그림파일", "*.gif;*.png;*.jpg;*.tif"), ("모든파일", "*.*")))
    photo = PhotoImage(file=filename2)
    inW2 = photo.width()
    inH2 = photo.height()
    if filename2 =='' or filename2 ==None:
        return

    # 중요!! 출력메모리 크기 결정
    inImageR2,inImageG2,inImageB2=[],[],[]
    for i in range(inH2):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(inW2):
            tmpList.append(0)
        inImageR2.append(tmpList[:])
    for i in range(inH2):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(inW2):
            tmpList.append(0)
        inImageG2.append(tmpList[:])
    for i in range(inH2):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(inW2):
            tmpList.append(0)
        inImageB2.append(tmpList[:])

    ## r,g,b 값 가져오기
    outW, outH = inW, inH
    if inH2 != inH:
        return
    fp2 = open(filename2, 'rb')
    for i in range(inH2):
        for k in range(inW2):
            r, g, b = photo.get(k, i)
            # print(r,g,b,end='/')
            inImageR2[i][k] = r
            inImageG2[i][k] = g
            inImageB2[i][k] = b
            # print(inImageR[i][k], inImageG[i][k], inImageB[i][k], end='/')
    photo = None

    ###########################
    # 진짜 영상처리 알고리즘을 구현#
    ###########################
    value = askinteger('합성비율', '두번째 영상의 가중치(%) 값-->', minvalue=1, maxvalue=99)
    wR1 = (1-value/100)  #첫번째 영상의 가중치
    wR2 = 1-wR1 #두번째 영상의 가중치
    wG1 = (1-value/100)  #첫번째 영상의 가중치
    wG2 = 1-wG1 #두번째 영상의 가중치
    wB1 = (1-value/100)  #첫번째 영상의 가중치
    wB2 = 1-wB1 #두번째 영상의 가중치
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            dataR=int(inImageR[i][k]*wR1 +inImageR2[i][k]*wR2)
            if dataR > 255 :
                dataR = 255
            elif dataR <0:
                dataR =0
            outImageR[i][k] = dataR
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            dataG=int(inImageG[i][k]*wG1 +inImageG2[i][k]*wG2)
            if dataG > 255 :
                dataG = 255
            elif dataG <0:
                dataG =0
            outImageG[i][k] = dataG
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            dataB=int(inImageB[i][k]*wB1 +inImageB2[i][k]*wB2)
            if dataB > 255 :
                dataB = 255
            elif dataB <0:
                dataB =0
            outImageB[i][k] = dataB
    fp2.close()
    display_Color()

### 기하학처리

#### Gray-scale

def raw_zoomIn():# Gray-scale 화면확대
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    scale = askinteger('확대하기', '값(2~32)을 입력하세요:', minvalue=2, maxvalue=32)
    outW = int(inW * scale)
    outH = int(inH * scale)
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for i in range(outH):
        for k in range(outW):
            outImage[i][k] = inImage[int(i / scale)][int(k / scale)]
    display_raw()

def raw_zoomOut():  # Gray-scale 화면축소
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    scale = askinteger('축소하기', '값(2~32)을 입력하세요:', minvalue=2, maxvalue=32)
    outW = int(inW / scale)
    outH = int(inH / scale)
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for i in range(inH):
        for k in range(inW):
            outImage[int(i / scale)][int(k / scale)] = inImage[i][k]
    display_raw()


def raw_upDown() :  # Gray-scale 상하반전
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImage[outW-1-i][k] = inImage[i][k]
    display_raw()

def raw_rightLeft():    #Gray-scale 좌우반전
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImage[i][outH-1-k] = inImage[i][k]
    display_raw()



## 화면이동 서브 기능 함수

def raw_panImage() :
    global raw_panYN
    raw_panYN = True

def raw_mouseClick(event) :  # Gray-scale 마우스 이벤트 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    global sx, sy, ex, ey, raw_panYN
    if not raw_panYN :
        return
    sx = event.x;  sy = event.y

def raw_mouseDrop(event):  # Gray-scale 마우스 이벤트 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    global sx, sy, ex, ey, raw_panYN
    if not raw_panYN:
        return
    ex = event.x; ey = event.y
    my = sx - ex ; mx = sy - ey

    # 중요! 출력메모리의 크기를 결정
    outW = inW;  outH = inH
    outImage = [];   tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if 0<= i-mx <outH and 0<= k-my < outW :
                outImage[i-mx][k-my] = inImage[i][k]
    raw_panYN = False
    display_raw()


## 영상 회전
def raw_rotate1():  #영상회전(포워딩)
    global inImage, outImage, inH, inW, outH, outW, window, canvas, paper, filename
    degree = askinteger('각도', '값 입력', minvalue=0, maxvalue=360)
    # 출력 파일의 크기 결정.
    outW = inW;
    outH = inH
    # 출력 영상 메모리 확보
    outImage = []
    for i in range(0, inW):
        tmpList = []
        for k in range(0, inH):
            tmpList.append(0)
        outImage.append(tmpList)
    ### 진짜 영상 처리 알고리즘 ###
    radian = degree * 3.141592 / 180.0
    for i in range(0, inW):
        for k in range(0, inH):
            xs = i;
            ys = k
            xd = int(math.cos(radian) * xs - math.sin(radian) * ys)
            yd = int(math.sin(radian) * xs + math.cos(radian) * ys)
            if 0 <= xd < outW and 0 <= yd < outH:
                outImage[xd][yd] = inImage[xs][ys]
    ###############################
    display_raw()


def raw_rotate2():  #영상회전(백워딩 및 중앙)
    global inImage, outImage, inH, inW, outH, outW, window, canvas, paper, filename
    degree = askinteger('각도', '값 입력', minvalue=0, maxvalue=360)
    # 출력 파일의 크기 결정.
    outW = inW;
    outH = inH
    # 출력 영상 메모리 확보
    outImage = []
    for i in range(0, inW):
        tmpList = []
        for k in range(0, inH):
            tmpList.append(0)
        outImage.append(tmpList)
    ### 진짜 영상 처리 알고리즘 ###
    radian = degree * 3.141592 / 180.0
    cx = int(inW / 2);
    cy = int(inH / 2)
    for i in range(0, outW):
        for k in range(0, outH):
            xs = i;
            ys = k
            xd = int(math.cos(radian) * (xs - cx)
                     - math.sin(radian) * (ys - cy)) + cx
            yd = int(math.sin(radian) * (xs - cx)
                     + math.cos(radian) * (ys - cy)) + cy
            if 0 <= xd < outW and 0 <= yd < outH:
                outImage[xs][ys] = inImage[xd][yd]
            else:
                outImage[xs][ys] = 255
    ###############################
    display_raw()


def raw_rotate3(): # 영상회전(확대)
    global inImage, outImage, inH, inW, outH, outW, window, canvas, paper, filename
    degree = askinteger('각도', '값 입력', minvalue=0, maxvalue=360)
    # 출력 파일의 크기 결정.
    radian90 = (90 - degree) * 3.141592 / 180.0
    radian = degree * 3.141592 / 180.0

    outW = int(inH * math.cos(radian90) + inW * math.cos(radian))
    outH = int(inH * math.cos(radian) + inW * math.cos(radian90))

    # outW = inW; outH = inH
    # 출력 영상 메모리 확보
    outImage = []
    for i in range(0, outW):
        tmpList = []
        for k in range(0, outH):
            tmpList.append(0)
        outImage.append(tmpList)
    ### 진짜 영상 처리 알고리즘 ###

    # inImage2 크기를 outImage와 동일하게
    inImage2 = []
    for i in range(0, outW):
        tmpList = []
        for k in range(0, outH):
            tmpList.append(255)
        inImage2.append(tmpList)

    # inImage --> inImage2의 중앙으로
    gap = int((outW - inW) / 2)
    for i in range(0, inW):
        for k in range(0, inH):
            inImage2[i + gap][k + gap] = inImage[i][k]

    ### 진짜 영상 처리 알고리즘 ###
    cx = int(outW / 2);
    cy = int(outH / 2)

    for i in range(0, outW):
        for k in range(0, outH):
            xs = i;
            ys = k
            xd = int(math.cos(radian) * (xs - cx)
                     - math.sin(radian) * (ys - cy)) + cx
            yd = int(math.sin(radian) * (xs - cx)
                     + math.cos(radian) * (ys - cy)) + cy
            # if 0 <= xd < outW and 0 <= yd < outH :
            if 0 <= xd < outW and 0 <= yd < outH:
                outImage[xs][ys] = inImage2[xd][yd]
            else:
                outImage[xs][ys] = 255
    ###############################
    display_raw()



#### Color값

def color_zoomIn():# Color 화면확대
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    scale = askinteger('축소하기', '값(2~32)을 입력하세요:', minvalue=2, maxvalue=32)
    outW = int(inW * scale)
    outH = int(inH * scale)
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for i in range(outH):
        for k in range(outW):
            outImageR[i][k] = inImageR[int(i / scale)][int(k / scale)]
    for i in range(outH):
        for k in range(outW):
            outImageG[i][k] = inImageG[int(i / scale)][int(k / scale)]
    for i in range(outH):
        for k in range(outW):
            outImageB[i][k] = inImageB[int(i / scale)][int(k / scale)]
    display_Color()

def color_zoomOut():  # Color 화면축소
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    scale = askinteger('축소하기', '값(2~32)을 입력하세요:', minvalue=2, maxvalue=32)
    outW = int(inW / scale)
    outH = int(inH / scale)
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for i in range(inH):
        for k in range(inW):
            outImageR[int(i / scale)][int(k / scale)] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            outImageG[int(i / scale)][int(k / scale)] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            outImageB[int(i / scale)][int(k / scale)] = inImageB[i][k]
    display_Color()

def color_upDown() :  # Color 상하반전
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImage[outW-1-i][k] = inImage[i][k]
    display_Color()

def color_rightLeft():    # Color 좌우반전
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImage[i][outH-1-k] = inImage[i][k]
    display_Color()



def color_upDown() :  # Color 상하반전
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImageR[outW-1-i][k] = inImageR[i][k]
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImageG[outW-1-i][k] = inImageG[i][k]
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImageB[outW-1-i][k] = inImageB[i][k]
    display_Color()

def color_rightLeft():    # Color 좌우반전
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImageR[i][outH-1-k] = inImageR[i][k]
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImageG[i][outH-1-k] = inImageG[i][k]
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImageB[i][outH-1-k] = inImageB[i][k]
    display_Color()


## 화면이동 서브 기능 함수

def color_panImage() :
    global color_panYN
    color_panYN = True

def color_mouseClick(event) :  # color 마우스 이벤트 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    global sx, sy, ex, ey, color_panYN
    if not color_panYN :
        return
    sx = event.x;  sy = event.y

def color_mouseDrop(event):  # color 마우스 이벤트 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    global sx, sy, ex, ey, color_panYN
    if not color_panYN:
        return
    ex = event.x; ey = event.y
    my = sx - ex ; mx = sy - ey

    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if 0<= i-mx <outH and 0<= k-my < outW :
                outImageR[i-mx][k-my] = inImageR[i][k]

    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if 0<= i-mx <outH and 0<= k-my < outW :
                outImageG[i-mx][k-my] = inImageG[i][k]

    for  i  in  range(inH) :
        for  k  in  range(inW) :
            if 0<= i-mx <outH and 0<= k-my < outW :
                outImageB[i-mx][k-my] = inImageB[i][k]
    color_panYN = False
    display_Color()

## 영상 회전
def color_rotate1():    #영상회전(포워딩)
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    degree = askinteger('각도', '값 입력', minvalue=0, maxvalue=360)
    # 출력 파일의 크기 결정.
    outW = inW
    outH = inH
    # 출력 영상 메모리 확보
    outImageR, outImageG, outImageB = [], [], []

    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    ### 진짜 영상 처리 알고리즘 ###
    radian = degree * 3.141592 / 180.0
    for i in range(0, inW):
        for k in range(0, inH):
            xs = i
            ys = k
            xd = int(math.cos(radian) * xs - math.sin(radian) * ys)
            yd = int(math.sin(radian) * xs + math.cos(radian) * ys)
            if 0 <= xd < outW and 0 <= yd < outH:
                outImageR[xd][yd] = inImageR[xs][ys]
    for i in range(0, inW):
        for k in range(0, inH):
            xs = i
            ys = k
            xd = int(math.cos(radian) * xs - math.sin(radian) * ys)
            yd = int(math.sin(radian) * xs + math.cos(radian) * ys)
            if 0 <= xd < outW and 0 <= yd < outH:
                outImageG[xd][yd] = inImageG[xs][ys]
    for i in range(0, inW):
        for k in range(0, inH):
            xs = i
            ys = k
            xd = int(math.cos(radian) * xs - math.sin(radian) * ys)
            yd = int(math.sin(radian) * xs + math.cos(radian) * ys)
            if 0 <= xd < outW and 0 <= yd < outH:
                outImageB[xd][yd] = inImageB[xs][ys]
    ###############################
    display_Color()


def color_rotate2():  #영상회전(백워딩 및 중앙)
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    degree = askinteger('각도', '값 입력', minvalue=0, maxvalue=360)
    # 출력 파일의 크기 결정.
    outW = inW
    outH = inH
    # 출력 영상 메모리 확보
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    ### 진짜 영상 처리 알고리즘 ###
    radian = degree * 3.141592 / 180.0
    cx = int(inW / 2);
    cy = int(inH / 2)
    for i in range(0, outW):
        for k in range(0, outH):
            xs = i
            ys = k
            xd = int(math.cos(radian) * (xs - cx)
                     - math.sin(radian) * (ys - cy)) + cx
            yd = int(math.sin(radian) * (xs - cx)
                     + math.cos(radian) * (ys - cy)) + cy
            if 0 <= xd < outW and 0 <= yd < outH:
                outImageR[xs][ys] = inImageR[xd][yd]
            else:
                outImageR[xs][ys] = 255
    for i in range(0, outW):
        for k in range(0, outH):
            xs = i
            ys = k
            xd = int(math.cos(radian) * (xs - cx)
                     - math.sin(radian) * (ys - cy)) + cx
            yd = int(math.sin(radian) * (xs - cx)
                     + math.cos(radian) * (ys - cy)) + cy
            if 0 <= xd < outW and 0 <= yd < outH:
                outImageG[xs][ys] = inImageG[xd][yd]
            else:
                outImageG[xs][ys] = 255
    for i in range(0, outW):
        for k in range(0, outH):
            xs = i
            ys = k
            xd = int(math.cos(radian) * (xs - cx)
                     - math.sin(radian) * (ys - cy)) + cx
            yd = int(math.sin(radian) * (xs - cx)
                     + math.cos(radian) * (ys - cy)) + cy
            if 0 <= xd < outW and 0 <= yd < outH:
                outImageB[xs][ys] = inImageB[xd][yd]
            else:
                outImageB[xs][ys] = 255
    ###############################
    display_Color()


def color_rotate3(): # 영상회전(확대)
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    degree = askinteger('각도', '값 입력', minvalue=0, maxvalue=360)
    # 출력 파일의 크기 결정.
    radian90 = (90 - degree) * 3.141592 / 180.0
    radian = degree * 3.141592 / 180.0

    outW = int(inH * math.cos(radian90) + inW * math.cos(radian))
    outH = int(inH * math.cos(radian) + inW * math.cos(radian90))

    # outW = inW; outH = inH
    # 출력 영상 메모리 확보
    outImageR = []
    outImageG = []
    outImageB = []
    for i in range(0, outW):
        tmpList = []
        for k in range(0, outH):
            tmpList.append(0)
        outImageR.append(tmpList)
    for i in range(0, outW):
        tmpList = []
        for k in range(0, outH):
            tmpList.append(0)
        outImageG.append(tmpList)
    for i in range(0, outW):
        tmpList = []
        for k in range(0, outH):
            tmpList.append(0)
        outImageB.append(tmpList)
    ### 진짜 영상 처리 알고리즘 ###

    # inImage2 크기를 outImage와 동일하게
    inImageR2 = []
    inImageG2 = []
    inImageB2 = []
    for i in range(0, outW):
        tmpList = []
        for k in range(0, outH):
            tmpList.append(255)
        inImageR2.append(tmpList)
    for i in range(0, outW):
        tmpList = []
        for k in range(0, outH):
            tmpList.append(255)
        inImageG2.append(tmpList)
    for i in range(0, outW):
        tmpList = []
        for k in range(0, outH):
            tmpList.append(255)
        inImageB2.append(tmpList)

    # inImage --> inImage2의 중앙으로
    gap = int((outW - inW) / 2)
    for i in range(0, inW):
        for k in range(0, inH):
            inImageR2[i + gap][k + gap] = inImageR[i][k]
    for i in range(0, inW):
        for k in range(0, inH):
            inImageG2[i + gap][k + gap] = inImageG[i][k]
    for i in range(0, inW):
        for k in range(0, inH):
            inImageB2[i + gap][k + gap] = inImageB[i][k]

    ### 진짜 영상 처리 알고리즘 ###
    cx = int(outW / 2)
    cy = int(outH / 2)

    for i in range(0, outW):
        for k in range(0, outH):
            xs = i
            ys = k
            xd = int(math.cos(radian) * (xs - cx)
                     - math.sin(radian) * (ys - cy)) + cx
            yd = int(math.sin(radian) * (xs - cx)
                     + math.cos(radian) * (ys - cy)) + cy
            # if 0 <= xd < outW and 0 <= yd < outH :
            if 0 <= xd < outW and 0 <= yd < outH:
                outImageR[xs][ys] = inImageR2[xd][yd]
            else:
                outImageR[xs][ys] = 255
    for i in range(0, outW):
        for k in range(0, outH):
            xs = i
            ys = k
            xd = int(math.cos(radian) * (xs - cx)
                     - math.sin(radian) * (ys - cy)) + cx
            yd = int(math.sin(radian) * (xs - cx)
                     + math.cos(radian) * (ys - cy)) + cy
            # if 0 <= xd < outW and 0 <= yd < outH :
            if 0 <= xd < outW and 0 <= yd < outH:
                outImageG[xs][ys] = inImageG2[xd][yd]
            else:
                outImageG[xs][ys] = 255
    for i in range(0, outW):
        for k in range(0, outH):
            xs = i
            ys = k
            xd = int(math.cos(radian) * (xs - cx)
                     - math.sin(radian) * (ys - cy)) + cx
            yd = int(math.sin(radian) * (xs - cx)
                     + math.cos(radian) * (ys - cy)) + cy
            # if 0 <= xd < outW and 0 <= yd < outH :
            if 0 <= xd < outW and 0 <= yd < outH:
                outImageB[xs][ys] = inImageB2[xd][yd]
            else:
                outImageB[xs][ys] = 255
    ###############################
    display_Color()




### 화소영역처리

#### Gray scale

def raw_embossing() :  # Gray scale 마스크 활용 엠보싱 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    mask = [[-1,0,0],[0,0,0],[0,0,1]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImage =[]
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImage.append(tmpList)
    tmpOutImage = []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImage.append(tmpList)
    print(tmpOutImage)
    print(tmpInImage)
    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImage[i+1][k+1] = inImage[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += mask[m][n] *tmpInImage[i+(m-1)][k+(n-1)]
            tmpOutImage[i-1][k-1] = s

    #127 더해주기(마스크의 합계가 0인 경우)
    for i in range(outW):
        for k in range(outH):
            tmpOutImage[i][k] +=127

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImage[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImage[i][k] = value
    display_raw()


def raw_bluring() :  # Gray scale 마스크 활용 블러링 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    mask = [[1./9,1./9,1./9],[1./9,1./9,1./9],[1./9,1./9,1./9]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImage =[]
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImage.append(tmpList)
    tmpOutImage = []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImage.append(tmpList)
    print(tmpOutImage)
    print(tmpInImage)
    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImage[i+1][k+1] = inImage[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += mask[m][n] *tmpInImage[i+(m-1)][k+(n-1)]
            tmpOutImage[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImage[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImage[i][k] = value
    display_raw()


def raw_GaussianFilter() :  # Gray scale 마스크 활용 가우시안필터 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    mask = [[1./16., 1./8., 1./16.],[1./8., 1./4., 1./8.],[1./16., 1./8., 1./16.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImage =[]
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImage.append(tmpList)
    tmpOutImage = []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImage.append(tmpList)
    print(tmpOutImage)
    print(tmpInImage)
    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImage[i+1][k+1] = inImage[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += mask[m][n] *tmpInImage[i+(m-1)][k+(n-1)]
            tmpOutImage[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImage[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImage[i][k] = value
    display_raw()

def raw_Sharpening() :  # Gray scale 마스크 활용 샤프닝 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    mask = [[0., -1., 0.],[-1., 5., -1.],[0., -1., 0.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImage =[]
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImage.append(tmpList)
    tmpOutImage = []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImage.append(tmpList)
    print(tmpOutImage)
    print(tmpInImage)
    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImage[i+1][k+1] = inImage[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += mask[m][n] *tmpInImage[i+(m-1)][k+(n-1)]
            tmpOutImage[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImage[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImage[i][k] = value
    display_raw()

def raw_HpfSharpening() :  # Gray scale 마스크 활용 고주파 샤프닝 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    mask = [[-1./9., -1./9., -1.],[-1./9., 8./9., -1./9.],[-1./9., -1./9., -1./9.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImage =[]
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImage.append(tmpList)
    tmpOutImage = []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImage.append(tmpList)
    print(tmpOutImage)
    print(tmpInImage)
    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImage[i+1][k+1] = inImage[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += mask[m][n] *tmpInImage[i+(m-1)][k+(n-1)]
            tmpOutImage[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImage[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImage[i][k] = value
    display_raw()


def raw_LpfSharpening() :  # Gray scale 마스크 활용 저주파 샤프닝 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    mask = [[1./9., 1./9., 1./9.],[1./9., 1./9., 1./9.],[1./9., 1./9., 1./9.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImage =[]
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImage.append(tmpList)
    tmpOutImage = []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImage.append(tmpList)
    print(tmpOutImage)
    print(tmpInImage)
    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImage[i+1][k+1] = inImage[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += mask[m][n] *tmpInImage[i+(m-1)][k+(n-1)]
            tmpOutImage[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImage[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImage[i][k] = value
    display_raw()


def raw_HomogenOperator() :  # Gray scale 유사 연산자 에지 검출 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    print(inW, inH)
    outImage= []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################

    tmpInImage =[]
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImage.append(tmpList)

    tmpOutImage = []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImage.append(tmpList)

    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImage[i+1][k+1] = inImage[i][k]

    # 회선연산하기.
    MSIZE =3
    for i in range(1, inH):
        for k in range(1, inW):
            max = 0.0   #블록이 이동할 때마다 최대값 초기화
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    if (tmpInImage[i+1][k+1] - tmpInImage[i+n][k+m]) >= max:  #블록의 가운데 값 - 블록의 주변 픽셀 값의 절대 값 중 최대값 찾기
                        max = abs(tmpInImage[i+1][k+1] - tmpInImage[i+(m-1)][k+(n-1)])
                        tmpOutImage[i-1][k-1] = max

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImage[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImage[i][k] = value
    display_Color()





#### Color

def color_embossing() :  # Color 마스크 활용 엠보싱 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    maskR = [[-1,0,0],[0,0,0],[0,0,1]]
    maskG = [[-1,0,0],[0,0,0],[0,0,1]]
    maskB = [[-1,0,0],[0,0,0],[0,0,1]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImageR, tmpInImageG, tmpInImageB =[],[],[]

    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageR.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageG.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageB.append(tmpList)

    tmpOutImageR, tmpOutImageG, tmpOutImageB = [], [], []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageR.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageG.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageB.append(tmpList)

    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImageR[i+1][k+1] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageG[i+1][k+1] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageB[i+1][k+1] = inImageB[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskR[m][n] *tmpInImageR[i+(m-1)][k+(n-1)]
            tmpOutImageR[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskG[m][n] *tmpInImageG[i+(m-1)][k+(n-1)]
            tmpOutImageG[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskB[m][n] *tmpInImageB[i+(m-1)][k+(n-1)]
            tmpOutImageB[i-1][k-1] = s

    #127 더해주기(마스크의 합계가 0인 경우)
    for i in range(outW):
        for k in range(outH):
            tmpOutImageR[i][k] +=127
    for i in range(outW):
        for k in range(outH):
            tmpOutImageG[i][k] +=127
    for i in range(outW):
        for k in range(outH):
            tmpOutImageB[i][k] +=127

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageR[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageR[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageG[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageG[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageB[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageB[i][k] = value
    display_Color()


def color_bluring() :  # Color 마스크 활용 블러링 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    maskR = [[1./9., 1./9.,1./9.],[1./9.,1./9.,1./9.],[1./9.,1./9.,1./9.]]
    maskG = [[1./9., 1./9.,1./9.],[1./9.,1./9.,1./9.],[1./9.,1./9.,1./9.]]
    maskB = [[1./9., 1./9.,1./9.],[1./9.,1./9.,1./9.],[1./9.,1./9.,1./9.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImageR, tmpInImageG, tmpInImageB =[],[],[]

    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageR.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageG.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageB.append(tmpList)

    tmpOutImageR, tmpOutImageG, tmpOutImageB = [], [], []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageR.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageG.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageB.append(tmpList)

    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImageR[i+1][k+1] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageG[i+1][k+1] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageB[i+1][k+1] = inImageB[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskR[m][n] *tmpInImageR[i+(m-1)][k+(n-1)]
            tmpOutImageR[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskG[m][n] *tmpInImageG[i+(m-1)][k+(n-1)]
            tmpOutImageG[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskB[m][n] *tmpInImageB[i+(m-1)][k+(n-1)]
            tmpOutImageB[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageR[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageR[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageG[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageG[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageB[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageB[i][k] = value
    display_Color()


def color_GaussianFilter() :  # Color 마스크 활용 가우시안필터 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    maskR = [[1./16., 1./8., 1./16.],[1./8., 1./4., 1./8.],[1./16., 1./8., 1./16.]]
    maskG = [[1./16., 1./8., 1./16.],[1./8., 1./4., 1./8.],[1./16., 1./8., 1./16.]]
    maskB = [[1./16., 1./8., 1./16.],[1./8., 1./4., 1./8.],[1./16., 1./8., 1./16.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImageR, tmpInImageG, tmpInImageB =[],[],[]

    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageR.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageG.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageB.append(tmpList)

    tmpOutImageR, tmpOutImageG, tmpOutImageB = [], [], []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageR.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageG.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageB.append(tmpList)

    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImageR[i+1][k+1] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageG[i+1][k+1] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageB[i+1][k+1] = inImageB[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskR[m][n] *tmpInImageR[i+(m-1)][k+(n-1)]
            tmpOutImageR[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskG[m][n] *tmpInImageG[i+(m-1)][k+(n-1)]
            tmpOutImageG[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskB[m][n] *tmpInImageB[i+(m-1)][k+(n-1)]
            tmpOutImageB[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageR[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageR[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageG[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageG[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageB[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageB[i][k] = value
    display_Color()


def color_Sharpening() :  # Color 마스크 활용 샤프닝 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    maskR = [[0., -1., 0.],[-1., 5., -1.],[0., -1., 0.]]
    maskG = [[0., -1., 0.],[-1., 5., -1.],[0., -1., 0.]]
    maskB = [[0., -1., 0.],[-1., 5., -1.],[0., -1., 0.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImageR, tmpInImageG, tmpInImageB =[],[],[]

    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageR.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageG.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageB.append(tmpList)

    tmpOutImageR, tmpOutImageG, tmpOutImageB = [], [], []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageR.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageG.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageB.append(tmpList)

    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImageR[i+1][k+1] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageG[i+1][k+1] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageB[i+1][k+1] = inImageB[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskR[m][n] *tmpInImageR[i+(m-1)][k+(n-1)]
            tmpOutImageR[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskG[m][n] *tmpInImageG[i+(m-1)][k+(n-1)]
            tmpOutImageG[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskB[m][n] *tmpInImageB[i+(m-1)][k+(n-1)]
            tmpOutImageB[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageR[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageR[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageG[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageG[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageB[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageB[i][k] = value
    display_Color()


def color_HpfSharpening() :  # Color 마스크 활용 고주파 샤프닝 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    maskR = [[-1./9., -1./9., -1.],[-1./9., 8./9., -1./9.],[-1./9., -1./9., -1./9.]]
    maskG = [[-1./9., -1./9., -1.],[-1./9., 8./9., -1./9.],[-1./9., -1./9., -1./9.]]
    maskB = [[-1./9., -1./9., -1.],[-1./9., 8./9., -1./9.],[-1./9., -1./9., -1./9.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImageR, tmpInImageG, tmpInImageB =[],[],[]

    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageR.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageG.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageB.append(tmpList)

    tmpOutImageR, tmpOutImageG, tmpOutImageB = [], [], []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageR.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageG.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageB.append(tmpList)

    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImageR[i+1][k+1] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageG[i+1][k+1] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageB[i+1][k+1] = inImageB[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskR[m][n] *tmpInImageR[i+(m-1)][k+(n-1)]
            tmpOutImageR[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskG[m][n] *tmpInImageG[i+(m-1)][k+(n-1)]
            tmpOutImageG[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskB[m][n] *tmpInImageB[i+(m-1)][k+(n-1)]
            tmpOutImageB[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageR[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageR[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageG[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageG[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageB[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageB[i][k] = value
    display_Color()

def color_LpfSharpening() :  # Color 마스크 활용 저주파 샤프닝 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []

    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    maskR = [[1./9., 1./9., 1./9.],[1./9., 1./9., 1./9.],[1./9., 1./9., 1./9.]]
    maskG = [[1./9., 1./9., 1./9.],[1./9., 1./9., 1./9.],[1./9., 1./9., 1./9.]]
    maskB = [[1./9., 1./9., 1./9.],[1./9., 1./9., 1./9.],[1./9., 1./9., 1./9.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImageR, tmpInImageG, tmpInImageB =[],[],[]

    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageR.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageG.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageB.append(tmpList)

    tmpOutImageR, tmpOutImageG, tmpOutImageB = [], [], []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageR.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageG.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageB.append(tmpList)

    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImageR[i+1][k+1] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageG[i+1][k+1] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageB[i+1][k+1] = inImageB[i][k]

    # 회선연산하기. 마스크로 쭉 긁으면서 계산하기
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskR[m][n] *tmpInImageR[i+(m-1)][k+(n-1)]
            tmpOutImageR[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskG[m][n] *tmpInImageG[i+(m-1)][k+(n-1)]
            tmpOutImageG[i-1][k-1] = s
    for i in range(1, inH):
        for k in range(1, inW):
            #1개 점을 처리하되 3x3 반복해서 처리: 마스크 연산은 모두 곱해서 더함.
            s = 0.0
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    s += maskB[m][n] *tmpInImageB[i+(m-1)][k+(n-1)]
            tmpOutImageB[i-1][k-1] = s

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageR[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageR[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageG[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageG[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageB[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageB[i][k] = value
    display_Color()


def color_DiffOperatorHor() :  # Color 마스크 활용 수평이동과 차분처리 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    MSIZE=3 #마스크 사이즈
    maskR = [[0., -1., 0.],[0., 1., 0.],[0.,0.,0.]]
    maskG = [[0., -1., 0.],[0., 1., 0.],[0.,0.,0.]]
    maskB = [[0., -1., 0.],[0., 1., 0.],[0.,0.,0.]]
    #임시 입력 영상 = inImage보다 2개열이 큼
    tmpInImageR, tmpInImageG, tmpInImageB =[],[],[]

    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageR.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageG.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageB.append(tmpList)

    tmpOutImageR, tmpOutImageG, tmpOutImageB = [], [], []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageR.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageG.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageB.append(tmpList)

    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImageR[i+1][k+1] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageG[i+1][k+1] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageB[i+1][k+1] = inImageB[i][k]

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageR[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageR[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageG[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageG[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageB[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageB[i][k] = value
    display_Color()



def color_HomogenOperator() :  # Color 유사 연산자 에지 검출 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    print(inW, inH)
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################

    tmpInImageR, tmpInImageG, tmpInImageB =[],[],[]

    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageR.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageG.append(tmpList)
    for i in range(inH +2):
        tmpList=[]
        for k in range(inW +2):
            tmpList.append(128)
        tmpInImageB.append(tmpList)

    tmpOutImageR, tmpOutImageG, tmpOutImageB = [], [], []
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageR.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageG.append(tmpList)
    for i in range(outH):
        tmpList=[]
        for k in range(outW):
            tmpList.append(0)
        tmpOutImageB.append(tmpList)

    #원래 입력--> 임시 입력
    for i in range(inH):
        for k in range(inW):
            print(i*inW+k)
            tmpInImageR[i+1][k+1] = inImageR[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageG[i+1][k+1] = inImageG[i][k]
    for i in range(inH):
        for k in range(inW):
            tmpInImageB[i+1][k+1] = inImageB[i][k]

    # 회선연산하기.
    MSIZE =3
    for i in range(1, inH):
        for k in range(1, inW):
            max = 0.0   #블록이 이동할 때마다 최대값 초기화
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    if (tmpInImageR[i+1][k+1] - tmpInImageR[i+n][k+m]) >= max:  #블록의 가운데 값 - 블록의 주변 픽셀 값의 절대 값 중 최대값 찾기
                        max = abs(tmpInImageR[i+1][k+1] - tmpInImageR[i+(m-1)][k+(n-1)])
                        tmpOutImageR[i-1][k-1] = max
    for i in range(1, inH):
        for k in range(1, inW):
            max = 0.0   #블록이 이동할 때마다 최대값 초기화
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    if (tmpInImageG[i+1][k+1] - tmpInImageG[i+n][k+m]) >= max:  #블록의 가운데 값 - 블록의 주변 픽셀 값의 절대 값 중 최대값 찾기
                         max = abs(tmpInImageG[i+1][k+1] - tmpInImageG[i+(m-1)][k+(n-1)])
                         tmpOutImageG[i-1][k-1] = max
    for i in range(1, inH):
        for k in range(1, inW):
            max = 0.0   #블록이 이동할 때마다 최대값 초기화
            for m in range(0,MSIZE):
                for n in range(0,MSIZE):
                    if (tmpInImageB[i+1][k+1] - tmpInImageB[i+n][k+m]) >= max:  #블록의 가운데 값 - 블록의 주변 픽셀 값의 절대 값 중 최대값 찾기
                        max = abs(tmpInImageB[i+1][k+1] - tmpInImageB[i+(m-1)][k+(n-1)])
                        tmpOutImageB[i-1][k-1] = max

    #임시출력 -> 원래 출력
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageR[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageR[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageG[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageG[i][k] = value
    for i in range(outW):
        for k in range(outH):
            value = int(tmpOutImageB[i][k])
            if value > 255:
                value = 255
            if value < 0 :
                value = 0
            outImageB[i][k] = value
    display_Color()



### 데이터 분석

def raw_data():   #Gray-scale 데이터값 분석
    rawDic= {}  # 색상:갯수
    XSIZE = outImage.width()
    YSIZE = outImage.height()
    for i in range(XSIZE):
        for k in range(YSIZE):
            rawData = outImage.get(i, k)
            if rawData in rawDic:
                rawDic[rawData] += 1
            else:
                rawDic[rawData] = 1

    rawDataList = sorted(rawDic.items(), key=operator.itemgetter(1))
    minCount= rawDataList[0]
    maxCount= rawDataList[-1]
    rawSum = 0
    for item in rawDataList:
        rawSum += item[0] * item[1]
    rawAvg = rawSum / (XSIZE * YSIZE)

    rawDataList = sorted(rawDic.items(), key=operator.itemgetter(0))
    rawStream = []
    for item in rawDataList:
        for i in range(item[1]):
            rawStream.append(item[0])
    upperPos = int((XSIZE * YSIZE) / 10 / 100)
    lowerPos = int((XSIZE * YSIZE) / -10 / 100)
    midPos = int((XSIZE * YSIZE) / 2)
    raw_upper= rawStream[upperPos]
    raw_lower= rawStream[lowerPos]
    raw_mid= rawStream[midPos]

    subWindow = Toplevel(window)  # 부모(window)에 종속된 서브윈도
    subWindow.geometry('200x100')
    label1 = Label(subWindow, text='픽셀 합계:' + rawSum)
    label1.pack()
    label2 = Label(subWindow, text='픽셀 평균값:' + rawAvg)
    label2.pack()
    label3 = Label(subWindow, text='최소출현 픽셀값:' + minCount)
    label3.pack()
    label4 = Label(subWindow, text='최다출현 픽셀값:' + maxCount)
    label4.pack()
    label5 = Label(subWindow, text='픽셀 상위수:' + raw_upper)
    label5.pack()
    label6 = Label(subWindow, text='픽셀 하위수:' + raw_lower)
    label6.pack()
    label6 = Label(subWindow, text='픽셀 중위수:' + raw_mid)
    label6.pack()
    subWindow.mainloop()


def raw_histogram() :  # 히스토 그램
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    countList = [0] * 256;  normalList = [0] * 256

    for i in range(outH) :
        for k in range(outW) :
            value = outImage[i][k]
            countList[value] += 1

    # 정규화된값 =  (카운트값 - 최소값) * High  /  (최대값 - 최소값)
    maxVal  = max (countList);  minVal = min(countList)
    for i in range(len(countList)) :
        normalList[i] = (countList[i] - minVal) * 256 / (maxVal - minVal)

    # 화면 출력
    subWindow = Toplevel(window)
    subWindow.geometry('256x256')
    subCanvas = Canvas(subWindow, width=256, height=256)
    subPaper = PhotoImage(width=256, height=256)
    subCanvas.create_image((256/2,256/2), image=subPaper, state='normal')

    for i in range(0, 256) :
        for k in range(0, int(normalList[i])) :
            data = 0
            subPaper.put('#%02x%02x%02x' % (data, data, data), (i, 255-k))
    subCanvas.pack(expand=1, anchor=CENTER)
    subWindow.mainloop()


def raw_histo_plt() :  # 히스토 그램
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    countList = [0] * 256

    for i in range(outH) :
        for k in range(outW) :
            value = outImage[i][k]
            countList[value] += 1
    plt.plot(countList)
    plt.show()


def raw_histoStretch() :  # 히스토그램 스트레칭 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW;  outH = inH;
    outImage = [];   tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    minVal, maxVal, HIGH = 255, 0, 255
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data = inImage[i][k]
            if data > maxVal:
                maxVal = data
            if data < minVal:
                minVal = data

    #히스토그램 스트레칭시키기
    #new = (old - minVal) * HIGH / (maxVal - minVal)
    for i in range(inH):
        for k in range(inW):
            value = int((inImage[i][k] - minVal) * HIGH / (maxVal - minVal))
            if value < 0 :
                value = 0
            if value > 255:
                value = 255
            outImage[i][k] = value
    display_raw()

def raw_endIn() :  # 엔드-인 검색 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW;  outH = inH;
    outImage = [];   tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    minVal, maxVal, HIGH = 255, 0, 255
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data = inImage[i][k]
            if data > maxVal:
                maxVal = data
            if data < minVal:
                minVal = data
    limit = askinteger('엔드인','상하범위:', minvalue=1, maxvalue=127)
    maxVal -= limit
    minVal += limit

    #히스토그램 스트레칭시키기
    #new = (old - minVal) * HIGH / (maxVal - minVal)
    for i in range(inH):
        for k in range(inW):
            value = int((inImage[i][k] - minVal) * HIGH / (maxVal - minVal))
            if value < 0 :
                value = 0
            if value > 255:
                value = 255
            outImage[i][k] = value
    display_raw()


def raw_histoEqual() :  # 히스토그램 평활화 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 중요! 출력메모리의 크기를 결정
    outW = inW;  outH = inH;
    outImage = [];   tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImage.append(tmpList)
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    histo = [0]*255
    sumHisto = [0]*255
    normalHisto= [0]*255
    minVal, maxVal, HIGH = 255, 0, 255
    #히스토그램 작성
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            value = inImage[i][k]
            histo[value]+=1

    #누적 히스토그램 작성
    sumVal = 0
    for  i  in  range(len(histo)) :
        sumVal += histo[i]
        sumHisto[i] = sumVal

    #정규화된 누적 히스토그램: (누적의 합/(행개수*열개수)) * HIGH
    for i in range(len(sumHisto)):
        normalHisto[i] = int(sumHisto[i] / (outW * outH) * HIGH)

    #정규화된 값으로 출력하기
    for i in range(inH):
        for k in range(inW):
            index = inImage[i][k]
            outImage[i][k] =normalHisto[index]
    display_raw()



## Color 값
def color_data():   #Color 데이터값 분석
    global window, canvas, paper, filename, outImage, inImage, inImageR, inImageG, inImageB,outImageR, outImageG, outImageB, inW, inH, outW, outH
    rDic, bDic, gDic = {}, {}, {}  # 색상:갯수
    photo = PhotoImage(file=filename)
    YSIZE = photo.height()
    XSIZE = photo.width()
    for i in range(XSIZE):
        for k in range(YSIZE):
            r, g, b = photo.get(i, k)
            if r in rDic:
                rDic[r] += 1
            else:
                rDic[r] = 1
            if g in gDic:
                gDic[g] += 1
            else:
                gDic[g] = 1
            if b in bDic:
                bDic[b] += 1
            else:
                bDic[b] = 1
    rcountList = sorted(rDic.items(), key=operator.itemgetter(1))
    gcountList = sorted(gDic.items(), key=operator.itemgetter(1))
    bcountList = sorted(bDic.items(), key=operator.itemgetter(1))
    minCount= rcountList[0]+gcountList[0]+bcountList[0]
    maxCount= rcountList[-1]+ gcountList[-1]+bcountList[-1]
    rSum = 0
    for item in rcountList:
        rSum += item[0] * item[1]
    rAvg = rSum / (XSIZE * YSIZE)
    gSum = 0
    for item in gcountList:
        gSum += item[0] * item[1]
    gAvg = gSum / (XSIZE * YSIZE)
    bSum = 0
    for item in bcountList:
        bSum += item[0] * item[1]
    bAvg = bSum / (XSIZE * YSIZE)
    rgb_avg= rAvg+ gAvg+ bAvg
    rgb_sum= rSum+ gSum+ bSum

    rcountList = sorted(rDic.items(), key=operator.itemgetter(0))
    gcountList = sorted(gDic.items(), key=operator.itemgetter(0))
    bcountList = sorted(bDic.items(), key=operator.itemgetter(0))
    rStream, gStream, bStream = [], [], []
    for item in rcountList:
        for i in range(item[1]):
            rStream.append(item[0])
    for item in gcountList:
        for i in range(item[1]):
            gStream.append(item[0])
    for item in bcountList:
        for i in range(item[1]):
            bStream.append(item[0])
    upperPos = int((XSIZE * YSIZE) / 10 / 100)
    lowerPos = int((XSIZE * YSIZE) / -10 / 100)
    midPos = int((XSIZE * YSIZE) / 2)
    rgb_upper= rStream[upperPos]+ gStream[upperPos]+ bStream[upperPos]
    rgb_lower= rStream[lowerPos]+ gStream[lowerPos]+bStream[lowerPos]
    rgb_mid= rStream[midPos]+ gStream[midPos]+ bStream[midPos]

    subWindow = Toplevel(window)  # 부모(window)에 종속된 서브윈도
    subWindow.geometry('500x500')
    label1 = Label(subWindow, text='r,g,b픽셀 합계:' + str(rSum)+','+ str(gSum) +','+ str(bSum))
    label1.pack()
    label2 = Label(subWindow, text='r,g,b 픽셀 평균값:' + str(rAvg)+','+ str(gAvg)+','+str(bAvg))
    label2.pack()
    label3 = Label(subWindow, text='최소출현 r,g,b픽셀값:' +str(rcountList[0])+','+str(gcountList[0])+','+str(bcountList[0]))
    label3.pack()
    label4 = Label(subWindow, text='최다출현 r,g,b픽셀값:' + str(rcountList[-1])+','+str(gcountList[-1])+','+str(bcountList[-1]))
    label4.pack()
    label5 = Label(subWindow, text='r,g,b픽셀 상위수:' +str(rStream[upperPos])+','+str(gStream[upperPos])+ ','+str(bStream[upperPos]))
    label5.pack()
    label6 = Label(subWindow, text='r,g,b픽셀 하위수:' +str(rStream[lowerPos])+','+ str(gStream[lowerPos])+','+str(bStream[lowerPos]))
    label6.pack()
    label6 = Label(subWindow, text='r,g,b픽셀 중위수:' + str(rStream[midPos])+','+ str(gStream[midPos])+ ','+str(bStream[midPos]))
    label6.pack()
    subWindow.mainloop()


def color_histo_normal() :  # 정규화 히스토그램
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    countListR,countListG,countListB = [0] * 256,[0] * 256,[0] * 256
    normalListR,normalListG,normalListB = [0] * 256,[0] * 256,[0] * 256

    for i in range(outH) :
        for k in range(outW) :
            valueR = outImageR[i][k]
            countListR[valueR] += 1
    for i in range(outH) :
        for k in range(outW) :
            valueG = outImageG[i][k]
            countListG[valueG] += 1
    for i in range(outH) :
        for k in range(outW) :
            valueB = outImageB[i][k]
            countListB[valueB] += 1

    # 정규화된값 =  (카운트값 - 최소값) * High  /  (최대값 - 최소값)
    maxValR = max(countListR)
    maxValG = max(countListG)
    maxValB = max(countListB)
    minValR = min(countListR)
    minValG = min(countListG)
    minValB = min(countListB)
    normalList = [0] * 256
    for i in range(len(countListR)) :
        normalListR = int((countListR[i] - minValR) * 256 / (maxValR - minValR))
        normalList[0] += normalListR
    for i in range(len(countListG)) :
        normalListG = int((countListG[i] - minValG) * 256 / (maxValG - minValG))
        normalList[1] += normalListG
    for i in range(len(countListB)) :
        normalListB = int((countListB[i] - minValB) * 256 / (maxValB - minValB))
        normalList[2] += normalListB

    n_bins = 200
    fig, axs = plt.subplots(3, tight_layout=True)
    axs[0].hist(normalList[0], color='r', bins=n_bins)
    axs[1].hist(normalList[1], color='g', bins=n_bins)
    axs[2].hist(normalList[2], color='b', bins=n_bins)
    plt.show()

    # 화면 출력
    # subWindow = Toplevel(window)
    # subWindow.geometry('256x256')
    # subCanvasR = Canvas(subWindow, width=256, height=256)
    # subCanvasG = Canvas(subWindow, width=256, height=256)
    # subCanvasB = Canvas(subWindow, width=256, height=256)
    # subPaperR = PhotoImage(width=256, height=256)
    # subPaperG = PhotoImage(width=256, height=256)
    # subPaperB = PhotoImage(width=256, height=256)
    # canvasR = subCanvasR.create_image((256/2,256/2), image=subPaperR, state='normal')
    # canvasG = subCanvasG.create_image((256/2,256/2), image=subPaperG, state='normal')
    # canvasB = subCanvasB.create_image((256/2,256/2), image=subPaperB, state='normal')

    # for i in range(0, 256) :
    #     for k in range(0, int(normalListR[i])) :
    #         dataR, dataG, dataB = normalListR[i], normalListB[i], normalListG[i]
    #         resR = subPaperR.put('#%02x%02x%02x' % (dataR, dataR, dataR), (i, 255-k))
    #         resG = subPaperG.put('#%02x%02x%02x' % (dataG, dataG, dataG), (i, 255-k))
    #         resB = subPaperB.put('#%02x%02x%02x' % (dataB, dataB, dataB), (i, 255-k))
    # for i in range(0, 256) :
    #     for k in range(0, int(normalListG[i])) :
    #         dataG = 0
    #         subPaper.put('#%02x%02x%02x' % (dataG, dataG, dataG), (i, 255-k))
    # for i in range(0, 256) :
    #     for k in range(0, int(normalListB[i])) :
    #         dataB = 0
    #         subPaper.put('#%02x%02x%02x' % (dataB, dataB, dataB), (i, 255-k))
    # subCanvasR.pack(expand=1, anchor=CENTER)
    # subCanvasG.pack(expand=1, anchor=CENTER)
    # subCanvasB.pack(expand=1, anchor=CENTER)
    # subWindow.mainloop()



def color_histo_plt() :  # 히스토 그램
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    countListR = [0] * 256
    countListG = [0] * 256
    countListB = [0] * 256

    for i in range(outH) :
        for k in range(outW) :
            value = outImageR[i][k]
            countListR[value] += 1
    for i in range(outH) :
        for k in range(outW) :
            value = outImageG[i][k]
            countListG[value] += 1
    for i in range(outH) :
        for k in range(outW) :
            value = outImageB[i][k]
            countListB[value] += 1

    n_bins = 200
    fig, axs = plt.subplots(3, tight_layout=True)
    axs[0].hist(countListR, color='r', bins=n_bins)
    axs[1].hist(countListG, color='g', bins=n_bins)
    axs[2].hist(countListB, color='b', bins=n_bins)
    plt.show()


def color_histoStretch() :  # 히스토그램 스트레칭 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    minValR, maxValR, HIGHR = 255, 0, 255
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data = inImageR[i][k]
            if data > maxValR:
                maxValR = data
            if data < minValR:
                minValR = data
    minValG, maxValG, HIGHG = 255, 0, 255
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data = inImageG[i][k]
            if data > maxValG:
                maxValG = data
            if data < minValG:
                minValG = data
    minValB, maxValB, HIGHB = 255, 0, 255
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data = inImageB[i][k]
            if data > maxValB:
                maxValB = data
            if data < minValB:
                minValB = data

    #히스토그램 스트레칭시키기
    #new = (old - minVal) * HIGH / (maxVal - minVal)
    for i in range(inH):
        for k in range(inW):
            value = int((inImageR[i][k] - minValR) * HIGHR / (maxValR - minValR))
            if value < 0 :
                value = 0
            if value > 255:
                value = 255
            outImageR[i][k] = value
    for i in range(inH):
        for k in range(inW):
            value = int((inImageG[i][k] - minValG) * HIGHG / (maxValG - minValG))
            if value < 0 :
                value = 0
            if value > 255:
                value = 255
            outImageG[i][k] = value
    for i in range(inH):
        for k in range(inW):
            value = int((inImageB[i][k] - minValB) * HIGHB / (maxValB - minValB))
            if value < 0 :
                value = 0
            if value > 255:
                value = 255
            outImageB[i][k] = value
    display_Color()

def color_endIn() :  # 엔드-인 검색 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    tmpList = []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    minVal, maxVal, HIGH = 255, 0, 255
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data = inImageR[i][k]
            if data > maxVal:
                maxVal = data
            if data < minVal:
                minVal = data
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data = inImageG[i][k]
            if data > maxVal:
                maxVal = data
            if data < minVal:
                minVal = data
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            data = inImageB[i][k]
            if data > maxVal:
                maxVal = data
            if data < minVal:
                minVal = data
    limit = askinteger('엔드인','상하범위:', minvalue=1, maxvalue=127)
    maxVal -= limit
    minVal += limit

    #히스토그램 스트레칭시키기
    #new = (old - minVal) * HIGH / (maxVal - minVal)
    for i in range(inH):
        for k in range(inW):
            value = int((inImageR[i][k] - minVal) * HIGH / (maxVal - minVal))
            if value < 0 :
                value = 0
            if value > 255:
                value = 255
            outImageR[i][k] = value
    for i in range(inH):
        for k in range(inW):
            value = int((inImageG[i][k] - minVal) * HIGH / (maxVal - minVal))
            if value < 0 :
                value = 0
            if value > 255:
                value = 255
            outImageG[i][k] = value
    for i in range(inH):
        for k in range(inW):
            value = int((inImageB[i][k] - minVal) * HIGH / (maxVal - minVal))
            if value < 0 :
                value = 0
            if value > 255:
                value = 255
            outImageB[i][k] = value
    display_Color()


def color_histoEqual() :  # 히스토그램 평활화 알고리즘
    global window, canvas, paper, filename, inImageR, inImageG, inImageB, outImageR, outImageG, outImageB, inW, inH, outW, outH
    # 중요!! 출력메모리 크기 결정
    outW = inW
    outH = inH
    outImageR, outImageG, outImageB = [], [], []
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageR.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageG.append(tmpList[:])
    for i in range(outH):  # 출력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(outW):
            tmpList.append(0)
        outImageB.append(tmpList[:])
    #############################
    # 진짜 영상처리 알고리즘을 구현
    ############################
    histoR = []
    histoG = [0]*255
    histoB = [0]*255
    sumHistoR = [0]*255
    sumHistoG = [0]*255
    sumHistoB = [0]*255
    normalHistoR = [0]*255
    normalHistoG = [0]*255
    normalHistoB = [0]*255
    minVal, maxVal, HIGH = 255, 0, 255
    #히스토그램 작성
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            value = inImageR[i][k]
            histoR[value]+=1
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            value = inImageG[i][k]
            histoG[value]+=1
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            value = inImageB[i][k]
            histoB[value]+=1

    #누적 히스토그램 작성
    sumVal = 0
    for  i  in  range(len(histoR)) :
        sumVal += histoR[i]
        sumHistoR[i] = sumVal
    for  i  in  range(len(histoG)) :
        sumVal += histoG[i]
        sumHistoG[i] = sumVal
    for  i  in  range(len(histoB)) :
        sumVal += histoB[i]
        sumHistoB[i] = sumVal

    #정규화된 누적 히스토그램: (누적의 합/(행개수*열개수)) * HIGH
    for i in range(len(sumHistoR)):
        normalHistoR[i] = int(sumHistoR[i] / (outW * outH) * HIGH)
    for i in range(len(sumHistoG)):
        normalHistoG[i] = int(sumHistoG[i] / (outW * outH) * HIGH)
    for i in range(len(sumHistoB)):
        normalHistoB[i] = int(sumHistoB[i] / (outW * outH) * HIGH)

    #정규화된 값으로 출력하기
    for i in range(inH):
        for k in range(inW):
            index = inImageR[i][k]
            outImageR[i][k] =normalHistoR[index]
    for i in range(inH):
        for k in range(inW):
            index = inImageG[i][k]
            outImageG[i][k] =normalHistoG[index]
    for i in range(inH):
        for k in range(inW):
            index = inImageB[i][k]
            outImageB[i][k] =normalHistoB[index]
    display_Color()



## 전역 변수부
window, canvas, paper, filename = [None] * 4
inImage, outImage = [], []; inW, inH, outW, outH = [0] * 4
color_panYN = False
raw_panYN = False
sx, sy, ex, ey = [0] * 4
VIEW_X, VIEW_Y = 128, 128
status = None

## 메인 코드부
window = Tk();  window.geometry('400x400');
window.title('DATS(Digital Image Analysis & Processing Total Solution) Ver 0.91')
window.bind("<Button-1>", raw_mouseClick)
window.bind("<ButtonRelease-1>", raw_mouseDrop)
window.bind("<Button-1>", color_mouseClick)
window.bind("<ButtonRelease-1>", color_mouseDrop)

status = Label(window, text='이미지 정보:', bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM, fill=X)


# 위젯 메뉴
mainMenu = Menu(window)
window.config(menu=mainMenu)

### 파일메뉴
fileMenu = Menu(mainMenu)
mainMenu.add_cascade(label='파일', menu=fileMenu)

openMenu = Menu(fileMenu)
fileMenu.add_cascade(label='열기', menu=openMenu)
openMenu.add_command(label='Gray-scale image 가져오기', command=openRawFile)
openMenu.add_command(label='Color image 가져오기', command=openColorFile)
openMenu.add_command(label='CSV형식 가져오기', command=openRawCSV)
openMenu.add_command(label='SQLite에서 가져오기', command=openRawSQLite)
openMenu.add_command(label='MySQL에서 가져오기', command=openRawMySQL)

saveMenu = Menu(fileMenu)
fileMenu.add_cascade(label='저장', menu=saveMenu)
saveMenu.add_command(label='Gray-scale image 저장', command=saveRawFile)
saveMenu.add_command(label='Color image 저장', command=saveColorFile)
saveMenu.add_command(label='Excel(숫자)형식으로 저장', command=saveNumExcel)
saveMenu.add_command(label='Excel(음영)형식으로 저장', command=saveRawExcel)
saveMenu.add_command(label='Excel(RGB숫자)형식으로 저장', command=saveColorNumExcel)
saveMenu.add_command(label='Excel(컬러)형식으로 저장', command=saveColorExcel)
saveMenu.add_command(label='CSV형식으로 저장', command=saveRawCSV)
# saveMenu.add_command(label='CSV(셔플)형식으로 저장', command=saveShuffleCSV)

sendMenu = Menu(fileMenu)
fileMenu.add_cascade(label='DB에 내보내기', menu=sendMenu)
sendMenu.add_command(label='SQLite에 내보내기', command=saveRawSQLite)
sendMenu.add_command(label='MySQL에 내보내기', command=saveRawMySQL)
sendMenu.add_separator()
sendMenu.add_command(label='RAW폴더-MySQL에 내보내기', command=saveRawAllMySQL)

fileMenu.add_separator()
fileMenu.add_command(label='종료', command=exitFile)


### 화소점처리
pixelMenu = Menu(mainMenu)
mainMenu.add_cascade(label='화소점처리', menu=pixelMenu)

equalMenu = Menu(pixelMenu)
pixelMenu.add_cascade(label='동일영상보기', menu=equalMenu)
equalMenu.add_command(label='Gray-동일영상', command=equal_raw)
equalMenu.add_command(label='Color-동일영상', command=equal_Color)

raw_brightnessMenu = Menu(pixelMenu)
pixelMenu.add_cascade(label='Gray scale-밝기조정', menu=raw_brightnessMenu)
raw_brightnessMenu.add_command(label='밝게(덧셈)', command=raw_brightAdd)
raw_brightnessMenu.add_command(label='어둡게(뺄셈)', command=raw_brightSub)
raw_brightnessMenu.add_command(label='더 밝게(곱셈)', command=raw_mulitply)
raw_brightnessMenu.add_command(label='더 어둡게(나눗셈)', command=raw_division)

color_brightnessMenu = Menu(pixelMenu)
pixelMenu.add_cascade(label='Color-밝기조정', menu=color_brightnessMenu)
color_brightnessMenu.add_command(label='밝게(덧셈)', command=color_brightAdd)
color_brightnessMenu.add_command(label='어둡게(뺄셈)', command=color_brightSub)
color_brightnessMenu.add_command(label='더 밝게(곱셈)', command=color_mulitply)
color_brightnessMenu.add_command(label='더 어둡게(나눗셈)', command=color_division)

raw_pixelMenu = Menu(pixelMenu)
pixelMenu.add_cascade(label='Gray scale-화소값처리',menu=raw_pixelMenu)
raw_pixelMenu.add_command(label='화소값반전', command=raw_reverse)
raw_pixelMenu.add_command(label='파라볼라(Cap)', command=raw_cap)
raw_pixelMenu.add_command(label='파라볼라(Cup)', command=raw_cup)
raw_pixelMenu.add_command(label='감마', command=raw_gamma)
raw_pixelMenu.add_command(label='적응이진화', command=raw_binarAdaptive)
raw_pixelMenu.add_command(label='범위강조변환', command=raw_spotLight)
raw_pixelMenu.add_command(label='합성', command=raw_morphing)

color_pixelMenu = Menu(pixelMenu)
pixelMenu.add_cascade(label='Color-화소값처리',menu=color_pixelMenu)
color_pixelMenu.add_command(label='화소값반전', command=color_reverse)
color_pixelMenu.add_command(label='파라볼라(Cap)', command=color_cap)
color_pixelMenu.add_command(label='파라볼라(Cup)', command=color_cup)
color_pixelMenu.add_command(label='감마', command=color_gamma)
color_pixelMenu.add_command(label='적응이진화', command=color_binarAdaptive)
color_pixelMenu.add_command(label='범위강조변환', command=color_spotLight)
color_pixelMenu.add_command(label='합성', command=color_morphing)


### 기하학처리
geoMenu = Menu(mainMenu)
mainMenu.add_cascade(label='기하학 처리', menu=geoMenu)

raw_geoMenu = Menu(geoMenu)
geoMenu.add_cascade(label='Gray scale-기하학 처리', menu=raw_geoMenu)
raw_geoMenu.add_command(label='화면확대', command=raw_zoomIn)
raw_geoMenu.add_command(label='화면축소', command=raw_zoomOut)
raw_geoMenu.add_command(label='상하반전', command=raw_upDown)
raw_geoMenu.add_command(label='좌우반전', command=raw_rightLeft)
raw_geoMenu.add_command(label='화면이동', command=raw_panImage)
raw_geoMenu.add_separator()
raw_geoMenu.add_command(label='영상회전(포워딩)', command=raw_rotate1)
raw_geoMenu.add_command(label='영상회전(백워딩 및 중앙)', command=raw_rotate2)
raw_geoMenu.add_command(label='영상회전(확대)', command=raw_rotate3)

color_geoMenu = Menu(geoMenu)
geoMenu.add_cascade(label='Color-기하학 처리', menu=color_geoMenu)
color_geoMenu.add_command(label='화면확대', command=color_zoomIn)
color_geoMenu.add_command(label='화면축소', command=color_zoomOut)
color_geoMenu.add_command(label='상하반전', command=color_upDown)
color_geoMenu.add_command(label='좌우반전', command=color_rightLeft)
color_geoMenu.add_command(label='화면이동', command=color_panImage)
color_geoMenu.add_separator()
color_geoMenu.add_command(label='영상회전(포워딩)', command=color_rotate1)
color_geoMenu.add_command(label='영상회전(백워딩 및 중앙)', command=color_rotate2)
color_geoMenu.add_command(label='영상회전(확대)', command=color_rotate3)

### 화소영역처리
areaMenu = Menu(mainMenu)
mainMenu.add_cascade(label='화소영역처리', menu=areaMenu)

raw_areaMenu = Menu(areaMenu)
areaMenu.add_cascade(label='Gray scale-화소영역처리', menu=raw_areaMenu)
raw_areaMenu.add_command(label='엠보싱', command=raw_embossing)
raw_areaMenu.add_command(label='블러링', command=raw_bluring)
raw_areaMenu.add_command(label='가우시안필터', command=raw_GaussianFilter)
raw_areaMenu.add_command(label='샤프닝', command=raw_Sharpening)
raw_areaMenu.add_command(label='고주파 샤프닝', command=raw_HpfSharpening)
raw_areaMenu.add_command(label='저주파 샤프닝', command=raw_LpfSharpening)
raw_areaMenu.add_command(label='유사 연산자 에지 검출', command=raw_HomogenOperator)


color_areaMenu = Menu(areaMenu)
areaMenu.add_cascade(label='Color-화소영역처리', menu=color_areaMenu)
color_areaMenu.add_command(label='엠보싱', command=color_embossing)
color_areaMenu.add_command(label='블러링', command=color_bluring)
color_areaMenu.add_command(label='가우시안필터', command=color_GaussianFilter)
color_areaMenu.add_command(label='샤프닝', command=color_Sharpening)
color_areaMenu.add_command(label='고주파 샤프닝', command=color_HpfSharpening)
color_areaMenu.add_command(label='저주파 샤프닝', command=color_LpfSharpening)
color_areaMenu.add_command(label='유사 연산자 에지 검출', command=color_HomogenOperator)



### 데이터 분석
analyzeMenu = Menu(mainMenu)
mainMenu.add_cascade(label='데이터분석', menu=analyzeMenu)

raw_analyzeMenu = Menu(analyzeMenu)
analyzeMenu.add_cascade(label='Gray scale-데이터분석', menu=raw_analyzeMenu)
raw_analyzeMenu.add_command(label='데이터값 분석', command=raw_data)
raw_analyzeMenu.add_command(label='히스토그램', command=raw_histogram)
raw_analyzeMenu.add_command(label='히스토그램(matplotlib)', command=raw_histo_plt)
raw_analyzeMenu.add_separator()
raw_analyzeMenu.add_command(label='히스토그램 평활화', command=raw_histoEqual)
raw_analyzeMenu.add_command(label='히스토그램 스트레칭', command=raw_histoStretch)
raw_analyzeMenu.add_command(label='히스토그램 엔드-인 탐색', command=raw_endIn)

color_analyzeMenu = Menu(analyzeMenu)
analyzeMenu.add_cascade(label='Color-데이터분석', menu=color_analyzeMenu)
color_analyzeMenu.add_command(label='테이터값 분석', command=color_data)
color_analyzeMenu.add_command(label='히스토그램', command=color_histo_normal)
color_analyzeMenu.add_command(label='히스토그램(matplotlib)', command=color_histo_plt)
color_analyzeMenu.add_separator()
color_analyzeMenu.add_command(label='히스토그램 평활화', command=color_histoEqual)
color_analyzeMenu.add_command(label='히스토그램 스트레칭', command=color_histoStretch)
color_analyzeMenu.add_command(label='히스토그램 엔드-인 탐색', command=color_endIn)

window.mainloop()
