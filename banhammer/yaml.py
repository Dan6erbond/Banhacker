def strip(str):
    return str.strip(" \t\r\n")

def eval_value(str):
    str = strip(str)

    number = True
    for c in str:
        if c not in "0123456789":
            number = False
            break

    if number:
        return int(str)

    true = ["true"]
    false = ["false"]

    if str.lower() in true:
        return True
    elif str.lower() in false:
        return False

    return str

def get_dict(str):
    dict = {}

    active_key = ""
    active_value = ""

    lines = str.splitlines()
    lines.append("1:1")

    for line in lines:
        partitions = line.split(":")
        if ":" in line and len(line.split(":")) >= 2 and len(partitions[0].split(" ")) == 1:
            if active_key != "" and active_value != "":
                if type(active_value) is str:
                    active_value = strip(active_value)
                dict[active_key] = active_value
                active_key = ""
                active_value = ""

            active_key = strip(partitions[0])
            value = strip(":".join(partitions[1:]))
            if active_key != "":
                if value == "|":
                    continue
                active_value = eval_value(value)
        elif active_key != "":
            active_value += strip(line) + "\n"

    return dict

def get_list(str):
    str += "\n--"
    lines = str.splitlines()

    dicts = list()
    s = ""
    for line in str.splitlines():
        if line.startswith("-"):
            dicts.append(get_dict(s))
            s = ""
        elif strip(line).startswith("#"):
            continue
        else:
            s += "\n" + line

    return dicts