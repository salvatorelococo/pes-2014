import os

filenames = os.listdir()

for filename in filenames:
    buffer_size = 8
    try:
        if '.' in filename:
            fn_s = filename.split('.')
            copy_filename = '.'.join(fn_s[:-1]) + ' - Copia.' + fn_s[-1]
        else:
            copy_filename = filename + ' - Copia'
        
        with open(filename, 'rb') as f, open(copy_filename, 'rb') as c:
            curr_pos = 0
            while True:
                b1 = f.read(buffer_size)
                b2 = c.read(buffer_size)

                if b1 != b2:
                    print(f'{filename:32} {hex(curr_pos)[2:].zfill(8):16}', " ".join(hex(c1)[2:].zfill(2) for c1 in b1))
                    print(f'{copy_filename:32} {hex(curr_pos)[2:].zfill(8):16}', " ".join(hex(c2)[2:].zfill(2) for c2 in b2))
                    print()

                curr_pos += buffer_size

                if not b1 and not b2:
                    break
    except FileNotFoundError:
        pass

input('FINE. Premi INVIO per terminare')

