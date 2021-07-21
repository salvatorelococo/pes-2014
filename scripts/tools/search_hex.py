import os

encoding_type = 'utf-8'

def main(keyword: str):
    files = os.listdir()

    for file in files:
        if not os.path.isfile(file):
            continue

        with open(file, 'rb') as f:
            content = ''.join([str(hex(c)[2:].zfill(2)) for c in f.read()])

            if keyword in content:
                print(file)


if __name__ == '__main__':
    while True:
        keyword = input('Inserisci sequenza di byte: ').replace(' ', '').lower()

        if keyword == 'exit':
            break

        main(keyword)
