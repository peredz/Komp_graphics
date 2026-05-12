
import subprocess
import sys

def main():
    print("╔═══════════════════════════════════════════════╗")
    print("║              РЕНДЕРИНГ ЛАНДШАФТА              ║")
    print("╠═══════════════════════════════════════════════╣")
    print("║  1 - Проволочный режим                        ║")
    print("║  2 - Управление камерой                       ║")
    print("║  3 - Сглаживание ландшафта                    ║")
    print("║  4 - Выход                                    ║")
    print("╚═══════════════════════════════════════════════╝")
    
    running = True
    while running:
        answer = input("Введите ответ: ").strip()
        
        if answer == "1":
            subprocess.run([sys.executable, "task_a.py"])
        elif answer == "2":
            subprocess.run([sys.executable, "task_b.py"])
        elif answer == "3":
            subprocess.run([sys.executable, "task_c.py"])
        elif answer == "4":
            running = False
            print("*** ЗАВЕРШЕНИЕ::ПРОГРАММА УСПЕШНО ЗАКОНЧИЛА РАБОТУ ***")
        else:
            print(" *** ОШИБКА::НЕВЕРНЫЙ ВАРИАНТ ОТВЕТА *** ")

if __name__ == "__main__":
    main()
