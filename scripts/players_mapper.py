BLOCK_LENGTH = 0x7C
CHARSET = 'utf-16'


def main():
    with open('ID00051_000', 'rb') as f:
        _id = 1

        with open('files/players.csv', 'w+', encoding=CHARSET) as o:
            while True:
                f.seek(BLOCK_LENGTH * _id)
                name = f.read(32)

                if name == b'':
                    break

                name = name.replace(b'\x00\x00', b'')
                print(f'{_id},{name.decode(CHARSET)}')
                o.write(f'{_id},{name.decode(CHARSET)}\n')
                _id += 1


if __name__ == '__main__':
    main()
