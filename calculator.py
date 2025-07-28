def calculator():
    print("Добро пожаловать в калькулятор!")
    print("Выберите операцию: +, -, *, /")

    op = input("Операция: ")
    a = float(input("Введите первое число: "))
    b = float(input("Введите второе число: "))

    if op == "+":
        result = a + b
        print(f"Результат: {result}")
    elif op == "-":
        result = a - b
        print(f"Результат: {result}")
    elif op == "*":
        result = a * b
        print(f"Результат: {result}")
    elif op == "/":
        if b != 0:
            result = a / b
            print(f"Результат: {result}")
        else:
            print("Ошибка: деление на ноль!")
    else:
        print("Ошибка: неизвестная операция.")

calculator()