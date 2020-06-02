from rule import Rule
from coroutine import coroutine

LINESEP = "\n"


@coroutine
def file_writer(lif_file):
    line_length = 0

    while True:
        tag = yield

        if line_length + len(tag) >= 70:
            lif_file.write(LINESEP)
            line_length = 0
        lif_file.write(tag)
        line_length += len(tag)


def save_file(model, filename):
    with open(filename, "w") as lif_file:
        square = save_headers(lif_file, model)
        save_rle(lif_file, model.state, square)
    
        pass

def save_rle(lif_file, state, square):

    writer = file_writer(lif_file)

    for y in range(square[1], square[3]+1):
        run_count = 0
        life = (square[0], y) in state
        for x in range(square[0], square[2]+1):
            if life == ((x, y) in state):
                run_count += 1
            else:
                encoding = str(run_count)
                if life:
                    encoding += "o"
                else:
                    encoding += "b"
                writer.send(encoding)
                run_count = 1
                life = not life
            if x == square[2]:  # Last cell in row
                # Only write if cells are alive
                if life:
                    writer.send(str(run_count) + "o")
                # Write end of line marker - or end of file marker
                if y < square[3]:
                    writer.send("$")
                else:
                    writer.send("!"+LINESEP)



def number_sequence_to_string(sequence):
    result = list(sequence)
    result.sort()
    result = "".join(str(item) for item in sequence)
    return result


def save_headers(lif_file, model):
    # Name
    if model.name:
        name = "#N "+str(model.name.strip())
        lif_file.write(name + LINESEP)

    # Comments/Description
    if len(model.description) > 0:
        for comment in model.description:
            comment = "#C " + comment
            lif_file.write(comment + LINESEP)

    # Size (saved with rules)
    for sample_x, sample_y in model.state:
        break
    min_x = max_x = sample_x
    min_y = max_y = sample_y
    for x, y in model.state:
        max_x = max(x, max_x)
        max_y = max(y, max_y)
        min_x = min(x, min_x)
        min_y = min(y, min_y)
    width = 1 + max_x - min_x
    height = 1 + max_y - min_y
    header = "x = " + str(width) + ", y = " + str(height)

    # Rules (saved with size). Not needed if Conway rules
    survival_count = number_sequence_to_string(model.rule.survival)
    birth_count = number_sequence_to_string(model.rule.birth)
    if survival_count != "23" or birth_count != "3":
        rule = survival_count + "/" + birth_count
        header += ", r = " + rule

    lif_file.write(header + LINESEP)

    return (min_x, min_y, max_x, max_y)
