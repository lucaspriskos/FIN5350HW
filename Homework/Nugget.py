package = (6, 9, 20)
candidate = package[0]
in_a_row = 0
def is_nug_num(number):
    obtainable = None
    for i in range(15):
        for j in range(15):
            for k in range(15):
                check = package[0] * i + package[1] * j + package[2] * k
                if check == number:
                    obtainable = check
    if obtainable:
        return True
    else:
        return False

while(in_a_row != package[0]):
    if(is_nug_num(candidate)):
        in_a_row += 1
    else:
        largest = candidate
        in_a_row = 0
    candidate += 1

print(largest)
