import os
from PyPDF2 import PdfReader
import pytesseract
from multiprocessing import Pool
import pdf2image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def search_page(file, page_n, target):

   # сохранить страницу как изображение
   image = pdf2image.convert_from_path(f'files/{file}', last_page=page_n)[-1]

   # распознать текст с изображения
   text = pytesseract.image_to_string(image, lang='rus').lower()

   # сохранить все найденные фразы в строку и вернуть её с названием файла и номером страницы
   found_phrases = ''

   for phrase in target:
       if phrase in text:
           found_phrases += phrase + '", "'

   if found_phrases != '':
       return f'{found_phrases[:-4]}:{file}:{page_n}'

   return ''


if __name__ == '__main__':

   print('Введите фразы, которые необходимо найти (нажмите enter два раза когда закончите)')

   # Ввод первой фразы
   target_phrases = []
   user_input = input()

   # Ввод дальнейших фраз пока пользователь не введет пустую строку
   while user_input != '':
       target_phrases.append(user_input.lower())
       user_input = input()

   processes_n = int(input('Сколько необходимо запустить подпроцессов? '))

   print('Обработка запущена')

   fin = []

   # Пройти по всем файлам в папке files
   for filename in os.listdir('files'):
       # Для каждого файла создать reader
       reader = PdfReader(f'files/{filename}')
       # Сгенерировать список списков для применения функции на него
       values = [(filename, reader.get_page_number(page)+1, target_phrases) for page in reader.pages]

       # Запустить подпроцессы, выполняющие поиск
       with Pool(processes_n) as p:
           fin += p.starmap(search_page, values)

   # Убрать все пустые результаты
   fin = [i for i in fin if i != '']

   # Вывести данные пользователю
   print('Обработка завершена. Результаты:')

   for i in fin:
       out = i.split(':')
       print(f'Фразы \"{out[0]}\" найдены в файле {out[1]} на странице {out[2]}')
