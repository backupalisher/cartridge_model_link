import re
import sys
from datetime import datetime

import pandas as pd
from termcolor import colored

import db_utils


def query_yes_no(question, default=None):
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

                # Берем первые буквы модели для более точного сравнения по классу техники
                try:
                    pres = re.search(rf"[A-Za-z]+[0-9]", model_numb_j).group(0)
                except:
                    pres = None
                try:
                    pres2 = re.search(rf"[A-Za-z]+[0-9]", model_numb_i).group(0)
                except:
                    pres2 = None

                res = re.sub(rf"{model_class}", '', res)
                if res:
                    r1 = str.replace(r1, model_numb_i, colored(model_numb_i, 'yellow'))
                    r2 = str.replace(r2, res, colored(res, 'yellow'))

                    if model_numb_j:
                        if model_numb_i == model_numb_j:
                            model_weight += 1
                        elif re.search(rf"{model_numb_i}\w", r2):
                            if pres == pres2:
                                model_weight += 1
                            else:
                                model_weight += 0.3
                        else:
                            if pres == pres2:
                                model_weight += 0.5
                            else:
                                model_weight += 0.2

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


def search_analog(model, analog, a1, models_list, b):
    b_analog = False

    if re.search(model, a1):
        for da in models_list:
            if re.search(analog, da[0]):
                if re.search(a1, da[0]):
                    b_analog = True
            if b_analog:
                if b:
                    print(colored(f"{da}", 'green'))
                else:
                    print(colored(f"{da}", 'red'))
                break

    return b_analog


def link_supplies():
    try:
        dont_analogs = pd.read_csv('dont_analogs.csv', sep=';', header=None)
        dont_analogs = dont_analogs.values.tolist()
    except:
        dont_analogs = []
    try:
        true_analogs = pd.read_csv('true_analogs.csv', header=None, sep=";")
        true_analogs = true_analogs.values.tolist()
    except:
        true_analogs = []

    # get all supplies id
    supplies_list = db_utils.get_all_supplis_id()
    # get all analog models for supplies
    all_analog_models = db_utils.get_all_analog_models()
    # get all models
    all_models = db_utils.get_all_models()

    for s_id in supplies_list:
        s_id = s_id[0]

        # get all link ids supplies_id and model_analog_id from link_supplies_model_analog
        sm_list = db_utils.get_sm_link(s_id)
        for ids in sm_list:
            for am in all_analog_models:
                if ids[1] == am[0]:
                    model = re.sub('.*-', '', am[2])
                    # get id link model
                    for m in all_models:
                        t_model = False
                        if am[1] == m[1]:
                            if re.search(rf'\w+{model}\w+|\w+{model}|{model}\w+|{model}', m[2]):
                                amodel = re.search(rf'\w+{model}\w+|\w+{model}|{model}\w+|{model}', m[2])
                                lamodel = ''
                                if amodel:
                                    lamodel = amodel.group(0).strip()
                                if re.search(f'{model}', lamodel):
                                    for dm in dont_analogs:
                                        if re.search(am[2], dm[0]) and re.search(m[2], dm[0]):
                                            t_model = True
                                            print(f"{am[2]} <> {m[2]}", '- FALSE')
                                            continue
                                    if t_model:
                                        continue
                                    for tm in true_analogs:
                                        if re.search(am[2], tm[0]) and re.search(m[2], tm[0]):
                                            db_utils.link_model_supplies(m[0], ids[0])
                                            t_model = True
                                            print(f"{am[2]} <> {m[2]}", '- TRUE')
                                            continue
                                    if t_model:
                                        continue

                                    count, ss1_weight, ss2_weight, weight, model_weight, r1, r2 = \
                                        text_highlighting(am[2], m[2])
                                    percent = round(int(count / ss1_weight * 100))

                                    if percent > 70 and weight > 0 and model_weight > 0 or percent >= 50 and \
                                            count >= 1 and ss1_weight >= 1 and ss2_weight >= 2 and model_weight >= 0.8:

                                        percent = colored(percent, 'green')
                                        print(f"{percent}%, {float(count)}, {ss1_weight}, {ss2_weight}, {weight}, "
                                              f"{float(model_weight)}: {r1} = {r2}", colored('Ok', 'green'))
                                        db_utils.link_model_supplies(m[0], ids[0])
                                    elif percent > 40 and weight > 0 and model_weight > 0 or  percent >= 50 and \
                                            count >= 1 and ss1_weight >= 2 and ss2_weight >= 2 and model_weight >= 0.2:
                                        if query_yes_no(
                                                f"{percent}%, {float(count)}, {ss1_weight}, {ss2_weight}, {weight}, "
                                                f"{float(model_weight)}: {r1} <> {r2}", None):

                                            df = pd.DataFrame([f"{am[2]} <> {m[2]}"])
                                            df.to_csv('true_analogs.csv', index=False, mode='a', header=False, sep=";")

                                            db_utils.link_model_supplies(m[0], ids[0])
                                        else:
                                            df = pd.DataFrame([f"{am[2]} <> {m[2]}"])
                                            df.to_csv('dont_analogs.csv', index=False, mode='a', header=False, sep=";")
                                        print(f"{am[2]} <> {m[2]}", '- UNKNOWN')


def main():
    start_time = datetime.now()
    print(start_time)
    link_supplies()
    print(datetime.now() - start_time)


if __name__ == '__main__':
    main()
