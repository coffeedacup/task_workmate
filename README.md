В скрипт можно добавить дополнительный отчёт по новым параметрам, достаточно просто создать новую функцию-обработчик и поместить её в словарь - report-handlers.

В файле launch.json - прописаны необходимые параметры для запуска всех команд напрямую из редактора VSCode.

По умолчанию скрипт запускается со следующими аргументами и в следующей форме: python script.py --files products1.csv products2.csv --report average-rating

После запуска script.py - даст следующий результат для файлов products1.csv и products2.csv:

<img width="225" height="119" alt="image" src="https://github.com/user-attachments/assets/a3fada9e-f12d-4524-b9d8-2fd1f8f8da84" />

Тестирование запускается файлом test_script.py, тестирование в любом случае выдаёт большой объём данных на анализ, для его сжатия можно использовать дополнительные аргументы, например:
pytest -v --tb=line

Результат будет такой:

<img width="1484" height="350" alt="image" src="https://github.com/user-attachments/assets/266db6fa-6705-475c-88c3-aa932d4fbd02" />

Также можно проверить процент покрытия тестами, используем команду pytest --cov=script test_script.py, а на вывод получим: 

<img width="233" height="94" alt="image" src="https://github.com/user-attachments/assets/989a1138-8671-4140-9ffa-35576b02b1f0" />
