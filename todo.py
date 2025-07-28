tasks = []  # Пустой список задач

def show_tasks():
    if not tasks:
        print("Список задач пуст.")
    else:
        print("Задачи:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")

def main():
    while True:
        command = input("Введите команду (add, show, remove, exit): ").lower()

        if command == "add":
            task = input("Введите задачу: ")
            tasks.append(task)
            print("Задача добавлена.")
        elif command == "show":
            show_tasks()
        elif command == "remove":
            show_tasks()
            try:
                index = int(input("Введите номер задачи для удаления: ")) - 1
                if 0 <= index < len(tasks):
                    removed = tasks.pop(index)
                    print(f"Удалена задача: {removed}")
                else:
                    print("Такой задачи нет.")
            except ValueError:
                print("Введите корректный номер.")
        elif command == "exit":
            print("До встречи!")
            break
        else:
            print("Неизвестная команда.")

main()