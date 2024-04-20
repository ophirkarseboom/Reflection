import time
from functools import partial
import threading
def a1(val):
    # threading.Thread(target=a2, daemon=False).start()
    global nice
    while True:
        print(nice)
def a2():
    while True:
        print('hi')

if __name__ == '__main__':
    nice = True
    threading.Thread(target=a1, args=(nice,), daemon=True).start()
    time.sleep(2)
    nice = False
    time.sleep(1)



