DEFAULT_BYTES = \
    b'\xB3\x00\x05\x00\x00\x70\x4E\x28\x50\x42\x47\x3E\xC2\x3F\x4B\x41' \
    b'\x44\x3E\x43\x3B\x44\x42\x49\x41\x39\x4C\x40\x43\x4B\x41\x44\x32' \
    b'\x98\x1D\x00\x00\x00\x37\x8E\x10\x20\x50\x70\x77\x01\x00\x00\x00' \
    b'\x3E\x00\x00\x00\x17\x00\x34\x13\x21\x77\x77\x77\x77\x17\x00\x00' \
    b'\x0E\x00\x00\x00\x60\xDB\xB6\x61\x60\xC3\x86\x6D'

CHARSET = 'utf-8'

def main():
    while True:
        name = input('Digita il nome del giocatore (es: Barella) per inserire un nuovo giocatore o EXIT per uscire: ')

        if name.lower() == 'exit':
            break

        shirt = name.upper()

        enc_name = b''.join(n.encode(CHARSET) + b'\x00' for n in name)
        enc_name = enc_name + b'\x00' * (32 - len(enc_name))

        enc_shirt = shirt.encode(CHARSET)[:15]
        enc_shirt = enc_shirt + b'\x00' * (16 - len(enc_shirt))

        try:
            with open('ID00051_000', 'ab') as f:
                f.write(enc_name)
                f.write(enc_shirt)
                f.write(DEFAULT_BYTES)

            print(name + ' aggiunto!\n')
        except Exception as e:
            print(e.__str__())


if __name__ == '__main__':
    main()
