class WritableObject(object):
    "dummy output stream for pylint"

    def __init__(self):
        self.content = []

    def write(self, st):
        "dummy write"
        self.content.append(st)

    def read(self):
        "dummy read"
        return self.content


def run_pylint(filename: str) -> list[list]:
    """run pylint on the given file"""
    from pylint import lint
    from pylint.reporters.text import TextReporter
    import re
    list_with_errors = []
    ARGS = ["-r", "n", "--msg-template='{line}, {column}, {end_line}, {end_column}'",
            f"--rcfile={filename}"]  # put your own here
    pylint_output = WritableObject()
    lint.Run([filename] + ARGS, reporter=TextReporter(pylint_output), do_exit=False)
    for l in pylint_output.read():
        if l.isalpha():
            print('here')
            continue
        text = l
        pattern = r"\b[^,]+(?:,[^,]+){3}\b" # r"\d+(?:,\d+)*"

        matches = re.findall(pattern, text)
        if len(matches):
            matches = matches[0].split(', ')
        else: continue
        matches = list(map(int, matches))
        list_with_errors.append(matches) if len(matches) == 4 else ''
    return list_with_errors


if __name__ == "__main__":
    print(run_pylint("Test_file2.py"))
