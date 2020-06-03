from gol.model import GolModel
from gol.rule import Rule
from gol.coroutine import coroutine


@coroutine
def rle_decoder(state):
    x = y = count = 0

    while True:
        s = yield

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
            # This is the end marker
            break
        elif s == 'o':
            count = 1 if count == 0 else count
            for _ in range(count):
                state.add((x, y))
                x += 1
            count = 0

    # End marker was reached.
    # Do nothing for eternity
    while True:
        black_hole = yield


@coroutine
def life_105(model):
    coord_x = coord_y = 0
    block_x = 0
    while True:
        line = yield
        if line.startswith("#C") or line.startswith("#D"):  # Comment
            model.description.append(line[2:].strip())
        elif line.startswith("#R"):  # Rule
            split_line = line.split()[1].split("/")
            survival = (a for a in split_line[0])
            birth = (a for a in split_line[1])
            model.rule = Rule(survival, birth)
        elif line.startswith("#P"):  # Position
            split_line = line.split()
            block_x = coord_x = int(split_line[1])
            coord_y = int(split_line[2])
        elif line.startswith("#N"):  # Normal rules = #R 23/3
            model.rule = Rule((2, 3), (3,))
        elif not line.startswith("#"):
            for cell in line:
                if cell == '*':
                    model.state.add((coord_x, coord_y))
                coord_x += 1
            coord_y += 1
            coord_x = block_x


@coroutine
def life_106(model):
    while True:
        line = yield
        split_line = line.split(" ")
        model.state.add((int(split_line[0]), int(split_line[1])))


@coroutine
def life_rle(model):
    decoder = rle_decoder(model.state)
    line = ""
    while not line.startswith("x ="):
        line = yield
    # x = m, y = n, rule = abc/def
    split_line = line.split(",")
    width = int(split_line[0].split("=")[1])
    height = int(split_line[1].split("=")[1])
    if len(split_line) > 2:
        rules = split_line[2].split("=")[1].split("/")
        survival_count = set( int(a) for a in rules[0].strip())
        birth_count = set(int(a) for a in rules[1].strip())
        model.rule = Rule(survival_count, birth_count)
    else:
        model.rule = Rule((2, 3), (3,))
    while True:
        line = yield
        for c in line:
            decoder.send(c)


@coroutine
def life_plaintext(model):
    y_pos = 0
    while True:
        line = yield
        if line.startswith("!Name:"):
            model.name = line[7:] if len(line) >= 7 else ""
            model.name = model.name.strip()
        elif line == "!":
            model.comment.description.add("")
        elif line.startswith("!"):
            comment = line[1:].strip()
            model.description.add(comment)
        else:
            x_pos = 0
            for c in line:
                if c in "O*":
                    model.state.add((x_pos, y_pos))
                x_pos += 1
            y_pos += 1


@coroutine
def life_unknown(model):
    while True:
        line = yield
        if line.startswith("#C") or line.startswith("#c"):  # Comment
            model.description.append(line[2:].strip())
        elif line.startswith("#N"):  # Name of pattern
            model.name = line[3:]
        elif line.startswith("#O"):  # Author
            model.author = line[3:]
        elif line.startswith("#P"):  # Top-left coordinates (Life32)
            pass
        elif line.startswith("#R"):  # Top-left coordinated (XLife)
            pass
        elif line.startswith("#r"):  # Rule survival_counts/birth_counts
            pass


@coroutine
def read_line(model):
    decoder = None
    model.state = set()

    generic_decoder = life_unknown(model)

    while True:
        line = yield
        line = line.strip()

        if decoder:
            decoder.send(line)
        else:
            # Check for "magic numbers/markers"
            if line.startswith("#Life 1.05"):
                decoder = life_105(model)
            elif line.startswith("#Life 1.06"):
                decoder = life_106(model)
            elif line.startswith("x ="):
                decoder = life_rle(model)
                decoder.send(line)
            elif line.startswith("!Name:"):
                decoder = life_plaintext(model)
                decoder.send(line)
            # File-type not yet known. Send line to the generic decoder
            else:
                generic_decoder.send(line)


def load_file(filename):
    """Load file containing a state for the Conway Game of Life
        Can read Life1.05 and RLE files

    Parameters:
    filename (str): the file to load

    Returns:
    set((int, int)): a set containing the coordinates of alive cells
    """

    model = GolModel()
    reader = read_line(model)

    lif_file = open(filename, "r")

    if lif_file.mode != 'r':
        return None

    for line in lif_file:
        reader.send(line)

    lif_file.close()

    return model
