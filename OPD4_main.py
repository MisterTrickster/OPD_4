# Улучшить программу таким образом, чтобы она при запуске делала все пункты предыдущих заданий и рисовала график
# средней дневной температуры с начала текущего месяца по текущий день

import datetime  # библиотека для отслеживания даты и времени
import requests  # http библиотека для запросов.
import pickle  # для записи и чтении в файл/из файла объектов в неизменном виде
import xlsxwriter  # библиотека для того, чтобы записывать данные в файл фомрамата excel
# import re
from bs4 import BeautifulSoup


# вывод словаря столбиком
def print_dict(river_temp):
    for item in river_temp:
        print(item, ":\t", river_temp[item])


# вывод двумерного словаря столбиком
def print_2d_dict(any_dict):
    for item in any_dict:
        if item != 'дата':
            print(any_dict['дата'].year, '.', any_dict['дата'].month, '.', item, ' ------')
            print_dict(any_dict[item])


# Запись в файл.
def write(data_struction, file_name):
    with open(file_name, 'wb') as f_write:
        pickle.dump(data_struction, f_write)
    f_write.close()


# Чтение из файла.
def read(file_name):
    with open(file_name, 'rb') as f_read:
        data_struction = pickle.load(f_read)
    f_read.close()
    return data_struction


# функция, возвразающая словарь, в котором ключ 'река river_name' и значение 'temperature'
def rivers_day_temp():
    # ссылка на сайт с погодой
    url = 'https://pogoda1.ru/katalog/sverdlovsk-oblast/temperatura-vody/'
    r = requests.get(url)

    # открытие страницы, которая сохранена в файле
    with open('test.html', 'w') as output_file:
        output_file.write(r.text)

    # используем конструктор BeautifulSoup(), чтобы поместить текст ответа в переменную
    soup = BeautifulSoup(r.text, features="html.parser")

    # словарь с информацией о водоемах
    rivers_temp_dict = {}

    # поиск строчек в файле навзания рек и их температура,  с последующей записью в файл
    river_data = soup.find_all('div', class_="x-row")
    for item in river_data:
        rivers_temp_dict[item.find('a').text] = float(item.find('div', class_="x-cell x-cell-water-temp").text.strip())

    return rivers_temp_dict


# функция выводящая(и записывающая в файл) значения средней температуры за день
def medial_day_temp():
    new_dict = rivers_day_temp()  # прочтенный с сайта словарь

    # читаем словарь с файла, если файл пуст, то устанавливаем дату в new_dict и записываем
    try:
        old_dict = read('day_data.pickle')
    except EOFError:
        new_dict['дата'] = datetime.date.today()
        write(new_dict, 'day_data.pickle')
        return new_dict

    # сравниваем дату, если дни не сходиться, то устанавливаем дату в new_dict и записываем в файл
    if old_dict['дата'].day != datetime.date.today().day:
        new_dict['дата'] = datetime.date.today()
        write(new_dict, 'day_data.pickle')
        return new_dict
    else:
        # цилк, который пробегает по ключам словаря и слкадывает температуру и делит на два, чтобы получить среднее
        # арифметическое
        for item in old_dict:
            # пропускаем ключ 'дата'
            if item != 'дата':
                old_dict[item] = round(((old_dict[item] + new_dict[item]) / 2.0),
                                       1)  # складываем старые значние с новым и делим на два, округляем
        write(old_dict, 'day_data.pickle')
        return old_dict


# фунция, которая подсчитывает среднюю температуру за месяц.
def medial_month_temp():
    new_dict = medial_day_temp()  # 'Новый' словарь, который содержит средние данные за день

    # читаем из файла, если он пустой, то записываем в файл новый массив с новыми данными
    try:
        old_dict = read('medial_month_data.pickle')
    except EOFError:
        new_dict['дата'] = datetime.date.today()
        write(new_dict, 'medial_month_data.pickle')
        return new_dict

    # если месяц не сопаадет, то перезаписываем
    if old_dict['дата'].month != datetime.date.today().month:
        new_dict['дата'] = datetime.date.today()
        write(new_dict, 'medial_month_data.pickle')
        return new_dict

    # если месяц совпадает, а день нет, то считаем среднее значение и записываем
    elif (old_dict['дата'].day != datetime.date.today().day) and (
            old_dict['дата'].month == datetime.date.today().month):
        # цикл, который пробегает по всем рекам и вычсчитываем среднее значение для соответсвующих рек
        for item in old_dict:
            # пропускаем ключ 'дата'
            if item != 'дата':
                old_dict[item] = round(((old_dict[item] + new_dict[item]) / 2.0), 1)
        write(old_dict, 'medial_month_data.pickle')
        return old_dict

    # если месяц и день соответсвенно совпадают, то просто возвращаем прочитанный список, оставляя файл без изменений
    else:
        return old_dict


# функция выводящая(и записывающая в файл) значения средней температуры за месяц
def medial_day_temp_by_month():
    new_dict = {}  # словарь, который содержит ключ 'номер_дня', а значение список со средней температурой за день.

    # читаем из файла, если файл пустой то записываем новый словарь со словаряит в файл
    try:
        old_dict = read('month_data.pickle')
    except EOFError:
        new_dict['дата'] = datetime.date.today()
        new_dict[datetime.date.today().day] = medial_day_temp()
        write(new_dict, 'month_data.pickle')
        return new_dict

    # проверяем дату, если месяц не совпадает, то перезаписываем
    if old_dict['дата'].month != datetime.date.today().month:
        old_dict.clear()
        new_dict['дата'] = datetime.date.today()
        new_dict[datetime.date.today().day] = medial_day_temp()
        write(new_dict, 'month_data.pickle')
        return new_dict
    # если совпадает, то перезаписываем средную температуру за день, в ячейку этого дня.
    else:
        old_dict[datetime.date.today().day] = medial_day_temp()
        write(old_dict, 'month_data.pickle')
        return old_dict


# Запись в xlsx файл
# открываем новый файл на запись
workbook = xlsxwriter.Workbook('rivers_data.xlsx')

# создаем там "лист1" и "лист2"
worksheet_1 = workbook.add_worksheet()
worksheet_2 = workbook.add_worksheet()

# делаем шаблон на Лист1
worksheet_1.write('B2', 'Дата:')
worksheet_1.write('C2', str(datetime.date.today()))  # Дата

worksheet_1.write('B4', 'Название')
worksheet_1.write('C4', 'Текущ.темп')

worksheet_1.write('E4', 'Ср.темп:')
worksheet_1.write('F4', 'за день')
worksheet_1.write('G4', 'за месяц')

# делаем шаблон на Лист2
worksheet_2.write('B2', 'Средняя температура за месяц по дням')
worksheet_2.write('B4', 'Даты:')

# работа над листом_1

# вспомогательные переменные, колонка и столбик
col = 1
row = 4

# словарь с текущей температурой
current_temp_dict = rivers_day_temp()

# записываем навзание рек в строчку 'B' с 5 строки
for item in current_temp_dict:
    worksheet_1.write(row, col, item)
    worksheet_1.write(row, col + 1, current_temp_dict[item])
    row += 1

# средняя температура за день
medial_day_temp_dict = medial_day_temp()

# средняя температура за месяц
medial_month_temp_dict = medial_month_temp()

row = 4
col = 5

# записываем средную температуру за день в колонку F начиная с 4 строки
for item in medial_day_temp_dict:
    if item != 'дата':
        worksheet_1.write(row, col, medial_day_temp_dict[item])
        row += 1

row = 4
col = 6

# записываем средную температуру за месяц в колонку G начиная с 4 строки
for item in medial_month_temp_dict:
    if item != 'дата':
        worksheet_1.write(row, col, medial_month_temp_dict[item])
        row += 1

# работа над листом_2

# вспомогательные переменные, колонка и столбик
col = 2
row = 3

# вспомогательные переменные для температуры и навзаний рек
col_1 = 1
row_1 = 4

# флажок
f = True

# словарь, в который сохранены данные по дням
rivers_days_data = medial_day_temp_by_month()

# записываем даты, в которые сохранены  данные по дням
for item in rivers_days_data:
    if item != 'дата':
        worksheet_2.write(row, col, str(item)+'.'+str(rivers_days_data['дата'].month))
        col += 1

        # col_1 = 1
        row_1 = 4

        # запишем для каждой даты данные по температурам водоемах

        if f:
            for sub_item in rivers_days_data[item]:
                if sub_item != 'дата':
                    worksheet_2.write(row_1, col_1, sub_item)
                    worksheet_2.write(row_1, col_1 + 1, rivers_days_data[item][sub_item])
                    row_1 += 1
                    f = False
            col_1 += 2

        else:
            for sub_item in rivers_days_data[item]:
                if sub_item != 'дата':
                    worksheet_2.write(row_1, col_1, rivers_days_data[item][sub_item])
                    row_1 += 1
            col_1 += 1

# создадим объект типа диаграмма
line_chart = workbook.add_chart({'type': 'line'})

# зводим данные в диаграмму

# добавляем имена значение и категории в диаграмму
for i in range(4, 21):
    line_chart.add_series({'values': ['Sheet2', i, 2, i, col_1 - 1],
                           'name': ['Sheet2', i, 1],
                           'categories': ['Sheet2', 3, 2, 3, col_1-1]})

# Устанавливаем наименования осей
line_chart.set_x_axis({'name': 'Дата'})    # Ось OX
line_chart.set_y_axis({'name': 'Температура(°C)'})    # Ось OY

line_chart.set_title({
    'name': 'Средняя температура за день в месяце',
    'overlay': True
})

# вставляем на лист_2 линейную диаграмму
worksheet_2.insert_chart('B26', line_chart)


print(col_1)

workbook.close()
