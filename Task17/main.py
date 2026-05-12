import sys
from task_a import task_a
from task_b import task_b
from task_c import task_c


def main():
    print("╔══════════════════════════════════════════════╗")
    print("║                СИСТЕМА ЧАСТИЦ                ║")
    print("╠══════════════════════════════════════════════╣")
    print("║  1 - Фейерверк                               ║")
    print("║  2 - Дождь/снегопад                          ║")
    print("║  3 - Огонь                                   ║")
    print("║  4 - Выход                                   ║")
    print("╚══════════════════════════════════════════════╝")
    
    while True:
        answer = input("Введите ответ: ").strip()
        
        if answer == "1":
            task_a()
        elif answer == "2":
            task_b()
        elif answer == "3":
            task_c()
        elif answer == "4":
            print("*** ЗАВЕРЕШЕНИЕ::ПРОГРАММА УСПЕШНО ЗАКОНЧИЛА РАБОТУ ***")
            sys.exit(0)
        else:
            print(" *** ОШИБКА::НЕВЕРНЫЙ ВАРИАНТ ОТВЕТА *** \n")


if __name__ == "__main__":
    main()
