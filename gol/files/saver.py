"""Saves game of life to filesystem
"""

# I would have liked to import coroutine like this, but path
# issues with import and packages prevented it from working
# when running this file as __main__ to run tests

#from gol.coroutine import coroutine

# So I had to write it again here:

from functools import wraps

def coroutine(func):
    """Decorator: primes 'func' by advancing to first 'yield'"""
    @wraps(func)
    def primer(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return primer


# The line seperator. Usually \n or \r\n.
LINESEP = "\n"

@coroutine
def file_writer(lif_file):
    """Writes to file making sure no line is longer than 70 characters

    Parameter:
    lif_file: File to write to
    """

    line_length = 0

    while True:
        tag = yield

        if line_length + len(tag) >= 70:
            lif_file.write(LINESEP)
            line_length = 0
        lif_file.write(tag)
        line_length += len(tag)


def save_file(model, filename):
    """Save game of life as an rle file

    Parameters:
    mode (GolModel): The model to save
    filename (str): The name of the file
    """

    with open(filename, "w") as lif_file:
        square = save_headers(lif_file, model)
        save_rle(lif_file, model.state, square)


def save_rle(lif_file, state, square):
    """Write game of life cells to rle file

    Parameters:
    lif_file: File to write to
    state: Set with coordinates for alive cells
    square (x_min, y_min, x_max, y_max): The bound of the cells to write to the file
    """

    # Prepare the file writer coroutine
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


def number_iterable_to_string(iterable):
    """Converts the rules to strings

    Parameter:
    iterable: An iterable data structure (usually a set) containing integers

    Return:
    str: A string containing the integers sorted by size

    >>> number_iterable_to_string((2, 1))
    '12'
    """

    result = list(iterable)
    result.sort()
    result = "".join(str(item) for item in result)
    return result


def save_headers(lif_file, model):
    """Writes headers to the file

    Parameters:
    lif_file: The file to write the headers to
    model: The GolModel to read the information from

    Return:
    (int, int, int, int): Tuple in the form (min_x, min_y, max_x, max_y)
        representing the minimum and maximum grid coordinates for alive
        cells in the model

    """

    # Write name
    if model.name:
        name = "#N "+str(model.name.strip())
        lif_file.write(name + LINESEP)

    # Write xomments/description
    if len(model.description) > 0:
        for comment in model.description:
            comment = "#C " + comment
            lif_file.write(comment + LINESEP)

    # Get any cell in the set as a starting point
    sample_x = sample_y = 0
    for sample_x, sample_y in model.state:
        break

    min_x = max_x = sample_x
    min_y = max_y = sample_y
    
    # Find minimum and maximum
    for x, y in model.state:
        max_x = max(x, max_x)
        max_y = max(y, max_y)
        min_x = min(x, min_x)
        min_y = min(y, min_y)

    # Find width and prepare header
    width = 1 + max_x - min_x
    height = 1 + max_y - min_y
    header = "x = " + str(width) + ", y = " + str(height)

    # Rules (saved with size). 
    survival_count = number_iterable_to_string(model.rule.survival)
    birth_count = number_iterable_to_string(model.rule.birth)

    # Rules are not needed if they are Conway rules
    if survival_count != "23" or birth_count != "3":
        rule = survival_count + "/" + birth_count
        header += ", r = " + rule

    # Write header to the file
    lif_file.write(header + LINESEP)

    return (min_x, min_y, max_x, max_y)


# Does not work due to path issues in the imports
if __name__ == "__main__":
    import doctest
    doctest.testmod()