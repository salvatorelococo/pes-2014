import os

CHARSET = 'utf-8'


def main(keyword: str):
    files = os.listdir()

    for file in files:
        if not os.path.isfile(file):
            continue

        with open(file, 'rb') as f:
            if keyword.encode(CHARSET) in f.read():
                print(file)


if __name__ == '__main__':
    while True:
        keyword = input('Inserisci frase da cercare: ')
        if keyword == 'EXIT':
            break
        main(keyword)
