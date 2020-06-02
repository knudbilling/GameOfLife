from model import GolModel
from rule import Rule


def rle_decoder(rle):
    """Decode RLE (Run Length Encoding)

    Parameters:
    rle (str): the RLE to decode

    Returns:
    set((int,int)): a set containing the coordinates of alive cells
    """
    state = set()
    x = y = count = 0
    for s in rle:
        if s in "0123456789":
            count = count * 10 + int(s)
        elif s == 'b':
            count = 1 if count == 0 else count
            x += count
            count = 0
        elif s == '$':
            x = 0
            y += 1
            count = 0
        elif s == '!':
            return state
        elif s == 'o':
            count = 1 if count == 0 else count
            for _ in range(count):
                state.add((x, y))
                x += 1
            count = 0
    return state


def load_file(filename):
    """Load file containing a state for the Conway Game of Life
        Can read Life1.05 and RLE files

    Parameters:
    filename (str): the file to load

    Returns:
    set((int,int)): a set containing the coordinates of alive cells
    """
    state = set()
    comments = list()

    model = GolModel()

    f = open(filename, "r")
    if f.mode != 'r':
        return {}
    contents = f.readlines()
    f.close()
    if contents[0].startswith("#Life 1.05"):
        coord_x = coord_y = 0
        block_x = 0
        for line in contents[1:]:
            line = line.strip()
            if line.startswith("#C") or line.startswith("#D"):  # Comment
                comments.append(line[2:].strip())
            elif line.startswith("#R"):  # Rule
                split_line = line.split()[1].split("/")
                survival = split_line[0]
                birth = split_line[1]
            elif line.startswith("#P"):  # Position
                split_line = line.split()
                block_x = coord_x = int(split_line[1])
                coord_y = int(split_line[2])
            elif line.startswith("#N"):  # Normal rules = #R 23/3
                survival = (2, 3)
                birth = (3,)
            elif line.startswith("#"):
                print("Unknown # in this line:", line)
            else:
                for cell in line:
                    if cell == '.':
                        pass
                    elif cell == '*':
                        state.add((coord_x, coord_y))
                    else:
                        pass
                    coord_x += 1
                coord_y += 1
                coord_x = block_x
        model.rule = Rule(survival, birth)
        model.state = state

    elif contents[0].startswith("#Life 1.06"):
        for line in contents[1:]:
            split_line = line.split(" ")
            model.state.add((int(split_line[0]), int(split_line[1])))

    # Assume RLE
    else:
        is_rle = False
        rle_string = ""
        for line in contents:
            line = line.strip()
            if line.startswith("#C") or line.startswith("#c"):  # Comment
                print(line[2:])
            elif line.startswith("#N"):  # Name of pattern
                pass
            elif line.startswith("#O"):  # Author
                pass
            elif line.startswith("#P"):  # Top-left coordinates (Life32)
                pass
            elif line.startswith("#R"):  # Top-left coordinated (XLife)
                pass
            elif line.startswith("#r"):  # Rule survcival_counts/birth_counts
                pass
            # Size and optionally rules  x = m, y = n, rule = abc
            elif line.startswith("x ="):
                is_rle = True
                split_line = line.split()
                width = int(split_line[2][:-1])
                height = int(split_line[5][:-1])
                print("Size: ", width, "x", height)
                # also do rules
            else:
                rle_string += line
        if not is_rle:
            raise TypeError

        model.rule = Rule((2, 3), (3,))
        model.state = rle_decoder(rle_string)

    return model
