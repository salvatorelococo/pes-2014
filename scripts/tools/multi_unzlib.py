import os
import time
import zlib

MAX_OFFSET = 512


def main():
    files = [x for x in os.listdir() if os.path.isfile(x)]
    timestamp = time.time()
    os.mkdir(str(timestamp))

    for file in files:
        print(file)
        with open(file, 'rb') as f:
            try:
                stream = f.read()
                counter = 0
                offset = 0

                while True:
                    dco = zlib.decompressobj()

                    try:
                        dec = dco.decompress(stream)

                        if not dec:
                            break
                    except:
                        offset += 1

                        if stream == b'' or offset > MAX_OFFSET:
                            break

                        stream = stream[1:]
                        continue

                    offset = 0

                    with open(f'{timestamp}/{file}.unzlib_{counter:03}', 'wb+') as o:
                        o.write(dec)
                        counter += 1

                    stream = dco.unused_data

                    if not stream:
                        break

            except Exception as e:
                print(e.__str__())


if __name__ == '__main__':
    main()
    input()
