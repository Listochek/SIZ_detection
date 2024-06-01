from multiprocessing import Process

def print_word(word):
    print('hello,', word)

if __name__ == '__main__':
    p1 = Process(target=print_word, args=('bob',), daemon=True)
    p2 = Process(target=print_word, args=('alice',), daemon=True)
    p1.start()
    p2.start()
    p1.join()
    p2.join()