import csv
from collections import Counter
import matplotlib.pyplot as plt
import os

def adder_stat():
    name_csv_file = 'summary.csv'

    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, '..', 'warns', name_csv_file)
    print(current_directory)
    print(file_path)


    warnings = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if row['warn']:
                warnings.extend(eval(row['warn']))

    warning_counts = Counter(warnings)
    labels = [f"{label} - {count}" for label, count in warning_counts.items()]
    sizes = warning_counts.values()


    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  

    plt.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5))

    # Сохранение диаграммы в файл
    output_path = os.path.join(current_directory, 'stat.png')
    plt.savefig(output_path, bbox_inches="tight")

    print(f"Диаграмма сохранена по пути: {output_path}")


if __name__ == '__main__':
    adder_stat()