import argparse
import csv
import os
import sys
from collections import defaultdict
from tabulate import tabulate


def read_csv_files(files):
    """Читает данные из всех переданных CSV-файлов и возвращает объединенный список."""
    data = []
    
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Проверяем наличие обязательных колонок
                if reader.fieldnames is None or not all(field in reader.fieldnames for field in ['brand', 'rating']):
                    print(f"Предупреждение: в файле {file} отсутствуют обязательные колонки 'brand' или 'rating'")
                    continue
                
                rows_processed = 0
                for row_num, row in enumerate(reader, 2):  # начинаем с 2 (заголовок - строка 1)
                    try:
                        # Проверяем, что строка не пустая
                        if not row.get('brand') or not row.get('rating'):
                            continue
                            
                        brand = row['brand'].strip()
                        rating_str = row['rating'].strip()
                        
                        # Пропускаем пустые значения
                        if not brand or not rating_str:
                            continue
                            
                        # Пытаемся преобразовать рейтинг в число
                        rating = float(rating_str)
                        
                        # Проверяем допустимый диапазон рейтинга (0-5)
                        if rating < 0 or rating > 5:
                            print(f"Предупреждение: некорректный рейтинг {rating} в строке {row_num} файла {file}")
                            continue
                            
                        row['brand'] = brand
                        row['rating'] = rating
                        data.append(row)
                        rows_processed += 1
                        
                    except (ValueError, TypeError) as e:
                        print(f"Предупреждение: пропущена строка {row_num} в файле {file} - некорректный формат рейтинга")
                        continue
                        
                if rows_processed == 0:
                    print(f"Предупреждение: в файле {file} не найдено валидных данных")
                    
        except FileNotFoundError:
            print(f"Ошибка: файл {file} не найден")
            sys.exit(1)
        except PermissionError:
            print(f"Ошибка: нет доступа для чтения файла {file}")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка чтения файла {file}: {e}")
            sys.exit(1)
    
    if not data:
        print("Ошибка: не удалось прочитать данные из переданных файлов")
        sys.exit(1)
        
    return data


def calculate_average_rating(data):
    """Вычисляет средний рейтинг для каждого бренда и сортирует результаты."""
    brand_ratings = defaultdict(list)
    skipped_count = 0
    
    for row in data:
        try:
            brand = row['brand']
            rating = row['rating']
            brand_ratings[brand].append(rating)
        except (KeyError, TypeError):
            skipped_count += 1
            continue
    
    if skipped_count > 0:
        print(f"Предупреждение: пропущено {skipped_count} некорректных записей при расчете рейтинга")
    
    if not brand_ratings:
        print("Ошибка: нет данных для расчета рейтингов")
        return []
    
    report = []
    for brand, ratings in brand_ratings.items():
        avg_rating = sum(ratings) / len(ratings)
        report.append({'brand': brand, 'average_rating': round(avg_rating, 2)})
    
    return sorted(report, key=lambda x: x['average_rating'], reverse=True)


def main():
    report_handlers = {
        'average-rating': calculate_average_rating,
    }
    
    parser = argparse.ArgumentParser(description='Generate product reports.')
    parser.add_argument('--files', nargs='+', required=True, help='CSV files to process')
    parser.add_argument('--report', required=True, choices=report_handlers.keys(), help='Report type')
    
    try:
        args = parser.parse_args()
        
        # Проверяем, что файлы существуют и имеют правильное расширение
        valid_files = []
        for file in args.files:
            if not os.path.isfile(file):
                print(f"Ошибка: файл {file} не существует")
                sys.exit(1)
            elif not file.lower().endswith('.csv'):
                print(f"Ошибка: файл {file} не является CSV файлом")
                sys.exit(1)
            elif not os.access(file, os.R_OK):
                print(f"Ошибка: нет доступа для чтения файла {file}")
                sys.exit(1)
            else:
                valid_files.append(file)
        
        if not valid_files:
            print("Ошибка: нет валидных файлов для обработки")
            sys.exit(1)
            
        # Читаем и обрабатываем данные
        data = read_csv_files(valid_files)
        
        # Формируем отчет
        report_data = report_handlers[args.report](data)
        
        if not report_data:
            print("Отчет пуст - нет данных для отображения")
            sys.exit(0)
            
        # Выводим результат
        print(tabulate(report_data, headers='keys', tablefmt='psql'))
        
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()