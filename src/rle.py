import numpy

#reads pattern files in the "Life 1.05", "Life 1.06", and "Run-Length-Encoded" format
def load_rle(path):
    def get_info(line,info):
        if len(line) < 80:
            info.append(line[3:-1])
        else:
            splitat = line.rfind(" ",3,80)
            if splitat != -1:
                info.append(line[3:splitat])
                info.append(line[1+splitat:-1])
            else:  
                info.append(line[3:80])
                info.append(line[80:-1])
                            
    #parses 'Run-Length-Encoded' pattern files
    block_start = (0,0)
    row         = 0
    col         = 0
    colchar     = ""
    colint      = 0
    done        = False
    info        = []
    with open(path, "r") as lif:
        structure = set()
        for line in lif:
            if line[:2] in ("#P","#R"):
                nums = line[3:].split(" ")
                block_start  = (int(nums[0]),int(nums[1]))
                row = 0
            elif line[:2] in ("#D","#N","#C"):
                get_info(line,info)
            elif line[0] == "x":
                splitat = line.rfind("rule")
                if splitat != -1:
                    info.append("Bounding box: " + line[:splitat-2])
                    info.append("Rule: " + line[splitat+6:-1])
                else:
                    info.append("Bounding box: " + line[:-1])
            elif line[0] != '#' and ("$" in line or "!" in line):
                for char in line:
                    if "0" <= char <= "9":
                        colchar += char
                    elif char == "b":
                        if colchar:
                            col += int(colchar)
                        else:
                            col += 1
                        colchar = ""
                    elif char == "o":
                        if colchar:
                            for i in range(int(colchar)):
                                structure |= set(((block_start[0]+col,block_start[1]+row),))
                                col += 1
                        else:
                            structure |= set(((block_start[0]+col,block_start[1]+row),))
                            col += 1
                        colchar = ""
                    elif char == "$":
                        if colchar:
                            row += int(colchar)
                        else:
                            row += 1
                        colchar = ""
                        col     = 0
                    elif char == "!":
                        done = True
                if done:
                    break

#        return(structure,info)
        return structure

BOARD_LENGTH = 1000
def load(path):
    pattern = load_rle(path)
    x_list, y_list = zip(*pattern)
    size = max(x_list) + 1, max(y_list) + 1
    # we always load a BOARD_LENGTH*BOARD_LENGTH (excluding the empty edges) board
    assert max(size) <= BOARD_LENGTH
    board = numpy.zeros((BOARD_LENGTH + 2, BOARD_LENGTH + 2), dtype=numpy.int)
    for x, y in pattern:
        board[x + 1, y + 1] = 1
    return board
