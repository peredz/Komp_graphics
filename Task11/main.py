import sys
from task_a import task_a
from task_b import task_b
from task_c import task_c

def main():
    print("╔════════════════════════════════════════════╗")
    print("║  PARAMETRIC CURVES: SPLINES & INTERPOLATION║")
    print("╠════════════════════════════════════════════╣")
    print("║  1 - Bezier Curve                         ║")
    print("║  2 - Bezier, B-Spline, Catmull-Rom        ║")
    print("║  3 - Rational Curves (NURBS)              ║")
    print("║  4 - Exit                                 ║")
    print("╚════════════════════════════════════════════╝")
    
    while True:
        answer = input("\nEnter choice: ").strip()
        
        if answer == "1":
            task_a()
        elif answer == "2":
            task_b()
        elif answer == "3":
            task_c()
        elif answer == "4":
            print("Exit")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
