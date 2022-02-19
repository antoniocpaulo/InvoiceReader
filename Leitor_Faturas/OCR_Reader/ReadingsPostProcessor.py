from re import sub as re_sub, compile as re_compile

is_makro_template = False

def convert_iva_codes(value_in):
    if str(value_in).find("23") != -1:
        return "23"
    elif str(value_in).find("13") != -1:
        return "13"
    elif str(value_in).find("6") != -1:
        return "6"
    else:
        return "23"


def convert_makro_iva_codes(code_in):
    if code_in == "4":
        return "6"
    elif code_in == "2":
        return "23"
    elif code_in == "5":
        return "13"
    else:
        return ""


def fix_text(text_in):
    if not text_in:
        return
    else:
        words = text_in.replace('$', '5').replace('§', '5').replace('!', '1').replace('|', '1').split()
        # known_words = spell.known(words)

        fixed_text = []

        for k, word in enumerate(words):
            if word.lower() in ["r.", "rua", "av.", "avenida", "tv.", "travessa"]:
                lower_word = word.lower()
                fixed_text.append(lower_word.capitalize())
            # elif word in known_words:
            #     if word.islower():
            #         fixed_text.append(word)
            #     else:
            #         fixed_text.append(word.capitalize())
            else:
                if word.islower():
                    fixed_text.append(word)
                else:
                    fixed_text.append(word.capitalize())
                #    word_corrected = spell.correction(word)
                #    fixed_text.append(word_corrected)
                # else:
                #    word_corrected = spell.correction(word).lower()
                #    fixed_text.append(word_corrected.capitalize())

        return ' '.join(fixed_text)


def fix_number(number_in):
    number_fix = number_in.replace('S', '5').replace('$', '5').replace('§', '5').replace('!', '1').replace(
        '|', '1').replace('I', '1').replace('/', '1').replace(',', '.').replace('"', "").replace('“', "").replace(
        "'", "").strip()
    number_fix = re_sub("[^0-9.]", "", number_fix)
    try:
        return format(float(number_fix), ".2f")
    except ValueError:
        return "" if number_fix == "." else number_fix


def fix_nif(nif_in):
    nif = nif_in.replace('S', '5').replace('$', '5').replace('§', '5').replace('!', '1').replace(
        '|', '1').replace('I', '1').replace('/', '1')

    try:
        nif = "5" + nif[1:] if nif[0] == "7" else nif
        nif = re_sub("[^0-9]", "", nif)
        return nif[-9:]
    except IndexError:
        return nif


def fix_date(date_in):
    date_fix = date_in.replace('S', '5').replace('$', '5').replace('§', '5').replace('!', '1').replace(
        '|', '1').replace('I', '1')
    date_fix = date_fix.replace(' ', '').replace(',', '-').replace('.', '-').replace('/', '-')
    date_fix = date_fix.split('-')

    def truncate_n_days(date, idx):
        try:
            if int(date[idx]) > 31 and date[idx][0] in ["8", "9"]:
                date[idx] = "2" + date[idx][1]
            return date
        except ValueError:
            return date

    try:
        if len(date_fix[2]) > 4:
            if str(date_fix[2][0]) == "2":
                date_fix = truncate_n_days(date_fix, 0)
                date_fix = date_fix[2][:4] + "-" + date_fix[1] + "-" + date_fix[0]
            else:
                date_fix = truncate_n_days(date_fix, 0)
                date_fix = date_fix[2] + "-" + date_fix[1] + "-" + date_fix[0]
        elif len(date_fix[2]) == 4:
            date_fix = truncate_n_days(date_fix, 0)
            date_fix = date_fix[2] + "-" + date_fix[1] + "-" + date_fix[0]
        else:
            date_fix = truncate_n_days(date_fix, 2)
            date_fix = date_fix[0] + "-" + date_fix[1] + "-" + date_fix[2]
        return re_sub("[^0-9-]", "", date_fix)
    except (IndexError, TypeError):
        return date_fix


def fix_code(code_in):
    code_out = code_in.replace('$', '5').replace('§', '5').replace('!', '1').replace('|', '1').replace(
        '_', '').replace('--', '').replace('"', "").replace("'", "").replace("“", "").replace(',', '.').strip()
    code_out = code_out.split()
    return ' '.join(code_out)


def split_on_letter(s):
    if s.upper().isupper():
        match = re_compile("[^\W\d]").search(s)
        Out = s[:match.start()], s[match.start():]
    else:
        Out = s
    return Out


def split_duplicated_entries(result_in):
    """Function used to split the duplicated entries on to two separate, equal length, strings"""
    result_in = result_in[0] if len(result_in) == 1 else result_in if type(result_in) is list else result_in
    try:
        first_part, second_part = result_in[:len(result_in) // 2], result_in[len(result_in) // 2:]
        if first_part.strip() == second_part.strip():
            result_out = first_part
        else:
            result_out = result_in
    except TypeError:
        return result_in
    return result_out


def fix_quantity(quantity_in, var_name):
    quantity_in = split_duplicated_entries(quantity_in)
    quantity_in = quantity_in.replace('S', '5').replace('$', '5').replace('§', '5').replace('!', '1').replace(
        '|', '1').replace('I', '1').replace(')', '').replace('(', '').replace(',', '.').strip()
    if is_makro_template and var_name == "tax_%s_per_item":
        quantity_in = convert_makro_iva_codes(quantity_in)
    elif not is_makro_template and var_name == "tax_%s_per_item":
        quantity_in = convert_iva_codes(quantity_in) 
    quantity_out = split_on_letter(quantity_in)

    if isinstance(quantity_out, str):
        return fix_number(quantity_out)
    elif quantity_out == "LUN":
        return "1.00 UN"
    elif not isinstance(quantity_out, str) and quantity_out != "":
        try:
            quantity_num = fix_number(quantity_out[0])
            quantity_unit = fix_code(quantity_out[1]).replace(' ', '')
            return " ".join([quantity_num, quantity_unit])
        except IndexError:
            return quantity_out
    else:
        return quantity_in


def input_fix(var_type, var_name, ocr_result):
    # fix/correct values of each entry by its variable type and/or field name
    if var_type == 'date':
        return fix_date(ocr_result)

    elif var_type == 'ID_number' and var_name == 'NIF':
        return fix_nif(ocr_result)

    elif var_type == 'number' or (var_type == 'ID_number' and var_name != 'NIF'):
        return fix_code(ocr_result)

    elif var_type == 'decimal_number':
        return fix_number(ocr_result)

    elif var_type == 'list_table_no' and (var_name == 'ID_items' or var_name == 'article' or var_name == 'reference'):
        split_entry = ocr_result.strip().split('\n')
        if len(split_entry) > 1:
            split_entry = [item for item in split_entry if item]  # remove empty list items
            return list(map(fix_code, split_entry))
        else:
            return [fix_code(ocr_result)]

    elif var_type == 'list_table_no' and var_name != 'ID_items' and var_name != 'article' and var_name != 'reference':
        split_entry = ocr_result.strip().split('\n')
        if len(split_entry) > 1:
            split_entry = [item for item in split_entry if item]  # remove empty list items
            return list(map(fix_number, split_entry))
        else:
            return fix_number(ocr_result)

    elif var_type == 'list_table':
        split_entry = ocr_result.strip().split('\n')
        if len(split_entry) > 1:
            split_entry = [item for item in split_entry if item]  # remove empty list items
            return list(map(fix_quantity, split_entry, [var_name for _ in range(0, len(split_entry))]))
        elif len(split_entry) == 1:
            return [fix_quantity(ocr_result, var_name)]
        else:
            return [split_duplicated_entries(split_entry)]

    elif var_type == 'text' or var_type == 'text_table':
        split_entry = ocr_result.strip().split('\n')
        if len(split_entry) > 1:
            split_entry = [item for item in split_entry if item]  # remove empty list items
            return list(map(fix_text, split_entry))
        else:
            return [fix_text(ocr_result)]

    else:
        split_entry = ocr_result.strip().split('\n')
        if len(split_entry) > 1:
            split_entry = [item for item in split_entry if item]  # remove empty list items
            return list(map(fix_code, split_entry))
        else:
            return [fix_code(ocr_result)]


def result_postprocessor(roi, results, is_makro=""):
    """ Post Processor initializing function: receives ocr_results and template roi to assess each input in
    a different way"""

    global is_makro_template
    is_makro_template = is_makro

    var_types = []
    var_names = []
    ocr_results = []
    for line in roi:
        var_types.append(line[2])
        var_names.append(line[3])
        ocr_results.append(results[line[3]])

    Results_Out = list(map(input_fix, var_types, var_names, ocr_results))

    return {roi[k][3]: row for k, row in enumerate(Results_Out)}
