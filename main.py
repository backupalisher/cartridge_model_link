import re
import sys
from termcolor import colored

import db_utils


def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:

        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def text_highlighting(s1, s2):
    ss1 = s1.split()
    ss2 = s2.split()
    r1 = ''
    r2 = ''
    line = []
    line2 = []

    for i in ss1:
        for j in ss2:
            model_numb_i = re.sub(r'.*-', '', i)
            model_class = re.sub('-.*', '', i)
            try:
                res = re.search(r'\d.+', j).group(0)
            except:
                res = j
            if i == j or re.sub(r'[^\d]', '', model_numb_i) == res or model_class == j:
                if i in line:
                    r1 = str.replace(r1, i, colored(i, 'yellow'))
                else:
                    r1 += colored(i, 'yellow') + ' '
                    line.append(i)
                if j in line2:
                    r2 = str.replace(r2, j, colored(j, 'yellow'))
                else:
                    r2 += colored(j, 'yellow') + ' '
                    line2.append(j)
            else:
                if i in line:
                    pass
                else:
                    r1 += i + ' '
                    line.append(i)
                if j in line2:
                    pass
                else:
                    r2 += j + ' '
                    line2.append(j)
    return r1, r2


def main():
    cartridge_analog_model = db_utils.get_all_analog_models()
    for analog in cartridge_analog_model:
        try:
            analog2 = db_utils.select_model(analog[1], re.sub('.*-', '', analog[2]))
        except:
            print("ERROR: ", analog[2])

        if analog2:
            # brand_name = db_utils.get_brand_name(analog[1])
            model = re.sub('.*-', '', analog[2])
            lmodel = re.sub(r'[^\d]', '', model)
            for a in analog2:
                amodel = re.sub(rf'[^\w+{model}+\w]', '', a[1])
                lamodel = re.sub(r'[^\d]', '', amodel)
                if int(lmodel) == int(lamodel):
                    r1, r2 = text_highlighting(analog[2], a[1])
                    if query_yes_no(f"{r1}, = {r2}", None):
                        cartridge_id = db_utils.get_link_cartridge_model_analog(analog[0])
                        db_utils.update_model_image(analog[0], 1)
                        for cart in cartridge_id:
                            db_utils.link_model_cartridge(a[0], cart[0])
                    else:
                        db_utils.update_model_image(analog[0], 0)
                else:
                    print(analog[2], a[1])


if __name__ == '__main__':
    main()
