import re
import sys
from termcolor import colored
from datetime import datetime

import pandas as pd

import db_utils
import test


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
    r1, r2 = s1, s2
    count, weight, model_weight = 0, 0, 0
    if s2 == 'Canon imageRUNNER Advance C2020i':
        s2 += ''
    ss1_weight = r1.replace('-', ' ').replace('/', ' ')
    ss2_weight = r2.replace('-', ' ').replace('/', ' ')
    ss1_weight = len(ss1_weight.split())
    ss2_weight = len(ss2_weight.split())

    ss1 = s1.split()
    ss2 = s2.split()
    for i in ss1:
        model_numb_i = re.sub(r'.*-', '', i)
        model_class = re.sub('-.*', '', i)

        if re.search(rf"{model_numb_i}", r2) and re.search(f"\d", model_numb_i):
            res = re.search(rf'\w+{model_numb_i}\w+|\w+{model_numb_i}|{model_numb_i}\w+|{model_numb_i}', r2).group(
                0).strip()
            if re.sub(r'[^\d]', '', model_numb_i) == re.sub(r'[^\d]', '', res):
                model_numb_j = res
                res = re.sub(rf"{model_class}", '', res)
                if res:
                    r1 = str.replace(r1, model_numb_i, colored(model_numb_i, 'yellow'))
                    r2 = str.replace(r2, res, colored(res, 'yellow'))

                    if model_numb_j:
                        if model_numb_i == model_numb_j:
                            model_weight += 1
                        elif re.search(rf"{model_numb_i}\w", r2):
                            model_weight += 0.8
                        else:
                            model_weight += 0.5

        if len(model_class) >= 2 and \
                (re.search(rf"{model_class.lower()}", r2.lower()) or re.search(r"Colour", r2.lower())):
            if re.search(r'\w', model_class):
                model_class_lower = model_class.lower()
                model_class_upper = model_class.upper()
                model_class_title = model_class.title()

                r1 = str.replace(r1, model_class, colored(model_class, 'yellow'))
                r2 = str.replace(r2, model_class, colored(model_class, 'yellow'))
                r2 = str.replace(r2, model_class_lower, colored(model_class_lower, 'yellow'))
                r2 = str.replace(r2, model_class_upper, colored(model_class_upper, 'yellow'))
                r2 = str.replace(r2, model_class_title, colored(model_class_title, 'yellow'))

                if re.search(r"Colour", r2):
                    r2 = str.replace(r2, 'Colour', colored('Colour', 'yellow'))
                weight += 1

    count = weight + model_weight
    return count, ss1_weight, ss2_weight, weight, model_weight, r1, r2


def start():
    try:
        dont_analogs = pd.read_csv('dont_analogs.csv', sep=';', header=None)
    except:
        dont_analogs = []

    cartridge_analog_model = db_utils.get_all_analog_models()
    analog2 = None
    for analog in cartridge_analog_model:
        try:
            analog2 = db_utils.select_model(analog[1], re.sub('.*-', '', analog[2]))
        except:
            print("ERROR: ", analog[2])

        if analog2:
            # brand_name = db_utils.get_brand_name(analog[1])

            model = re.sub('.*-', '', analog[2])
            # lmodel = re.sub(r'[^.*\s]', '', model)
            # lmodel = re.sub(r'\s.*', '', lmodel)
            for a in analog2:
                if analog[1] == a[2]:
                    # amodel = re.search(rf'\s{model}', '', a[1])
                    amodel = re.search(rf'\w+{model}\w+|\w+{model}|{model}\w+|{model}', a[1])
                    lamodel = ''
                    if amodel:
                        lamodel = amodel.group(0).strip()
                    # if lamodel and amodel:
                    #     lamodel = lamodel.group(0).strip()
                    if re.search(f'{model}', lamodel):
                        # count, weight, model_weight, r1, r2 = text_highlighting(analog[2], a[1], model)
                        count, ss1_weight, ss2_weight, weight, model_weight, r1, r2 = \
                            text_highlighting(analog[2], a[1])
                        percent = round(int(count / ss1_weight * 100))
                        if percent > 55 and weight > 0 and model_weight > 0 or \
                                percent == 50 and count == 1 and ss1_weight == 2 and ss2_weight == 2 and model_weight >= 0.8:

                            percent = colored(percent, 'green')
                            print(f"{percent}%, {float(count)}, {ss1_weight}, {ss2_weight}, {weight}, "
                                  f"{float(model_weight)}: {r1} = {r2}", colored('Ok', 'green'))
                            cartridge_id = db_utils.get_link_cartridge_model_analog(analog[0])
                            db_utils.update_model_image(analog[0], 1)
                            for cart in cartridge_id:
                                db_utils.link_model_cartridge(a[0], cart[0])
                            """Пропускаем все что меньше 55% вероятности совпадений"""
                        elif percent < 55:
                            if not dont_analogs.loc[dont_analogs[0] == f"{analog[2]} <> {a[1]}"].empty:
                                print(colored(f"{analog[2]} <> {a[1]}", 'red'))
                                continue
                            if 55 > percent > 40:
                                percent = colored(percent, 'blue')
                                print(f"{percent}%, {float(count)}, {ss1_weight}, {ss2_weight}, {weight}, "
                                      f"{float(model_weight)}: {r1} <> {r2}")
                                continue
                            else:
                                if percent < 10:
                                    percent = ' ' + colored(str(percent), 'red')
                                print(f"{percent}%, {float(count)}, {ss1_weight}, {ss2_weight}, {weight}, "
                                      f"{float(model_weight)}: {r1} <> {r2}")
                                continue

                        elif percent < 40 and model_weight == 0:
                            if percent < 10:
                                percent = ' ' + colored(str(percent), 'red')
                            print(f"{percent}%, {float(count)}, {ss1_weight}, {ss2_weight}, {weight}, "
                                  f"{float(model_weight)}: {r1} <> {r2}")
                            continue

                        elif 55 > percent > 40 and model_weight > 0 or \
                                percent == 25 and ss1_weight == 2 and model_weight > 0:
                            percent = colored(percent, 'blue')
                            if not dont_analogs.loc[dont_analogs[0] == f"{analog[2]} <> {a[1]}"].empty:
                                print(colored(f"{analog[2]} <> {a[1]}", 'red'))
                                continue

                            if query_yes_no(f"{percent}%, {float(count)}, {ss1_weight}, {ss2_weight}, {weight}, "
                                            f"{float(model_weight)}: {r1} <> {r2}", None):
                                cartridge_id = db_utils.get_link_cartridge_model_analog(analog[0])
                                db_utils.update_model_image(analog[0], 1)
                                for cart in cartridge_id:
                                    db_utils.link_model_cartridge(a[0], cart[0])
                            else:
                                df = pd.DataFrame([f"{analog[2]} <> {a[1]}"], )
                                df.to_csv('dont_analogs.csv', index=False, mode='a', header=False, sep=";")

                    else:
                        print(analog[2], a[1])


def main():
    start_time = datetime.now()
    print(start_time)
    # start

    # test.test()
    start()

    # end
    print(datetime.now() - start_time)


if __name__ == '__main__':
    main()
