import configparser


def linear_congruential_generator(m, a, c, x0, n):
    """Функція для генерації псевдовипадкових чисел."""
    sequence = []
    x = x0
    for _ in range(n):
        x = (a * x + c) % m
        sequence.append(x)
    return sequence


def save_to_file(sequence, filename="random_numbers.txt"):
    """Функція для збереження послідовності у файл."""
    with open(filename, "w") as file:
        for number in sequence:
            file.write(f"{number}\n")


def main():
    # Створення об'єкта ConfigParser
    config = configparser.ConfigParser()

    # Зчитування конфігураційного файлу
    config.read("config.ini")

    # Отримання змінних з файлу конфігурації
    m = int(config["LCG"]["m"])
    a = int(config["LCG"]["a"])
    c = int(config["LCG"]["c"])
    x0 = int(config["LCG"]["x0"])

    while True:
        try:
            n = int(input("Введіть кількість псевдовипадкових чисел для генерації: "))
            if n > 1500000:
                print("Надто велике число, введіть менше n: ")
            elif n <= 0:
                print("Число має бути більше нуля. Введіть інше значення.")
            else:
                break
        except ValueError:
            print("Помилка: n має бути цілим числом. Спробуйте ще раз.")

    # Генерація послідовності
    sequence = linear_congruential_generator(m, a, c, x0, n)

    # Виведення результатів на екран
    print("Згенерована послідовність:")
    for number in sequence:
        print(number)

    # Збереження у файл
    save_to_file(sequence)


if __name__ == "__main__":
    main()
