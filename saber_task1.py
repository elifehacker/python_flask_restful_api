for i in range(1, 76):
    words = ''
    if i % 4 == 0:
        words += 'Mission'
    
    if i % 5 == 0:
        if words != '':
            words += ' '
        words += 'Control'

    if words != '':
        print(words)
    else:
        print(i)