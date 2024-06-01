# from multiprocessing import Process

# def print_word(word):
#     print('hello,', word)

# if __name__ == '__main__':
#     p1 = Process(target=print_word, args=('bob',), daemon=True)
#     p2 = Process(target=print_word, args=('alice',), daemon=True)
#     p1.start()
#     p2.start()
#     p1.join()
#     p2.join()
    
from threading import Thread
from time import sleep

counter = 0


def increase(by):
    global counter

    local_counter = counter
    local_counter += by

    sleep(0.1)

    counter = local_counter
    print(f'{counter=}')


t1 = Thread(target=increase, args=(10,))
t2 = Thread(target=increase, args=(20,))

t1.start()
t2.start()

t1.join()
t2.join()
