def convert_rub_to_usd():
    print("Конвертер RUB → USD")
    rate = 90  # Фиксированный курс: 1 USD = 90 RUB
    rub = float(input("Введите сумму в рублях: "))
    usd = rub / rate
    print(f"{rub} RUB = {usd:.2f} USD")

convert_rub_to_usd()