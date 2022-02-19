import tkinter as tk
from math import floor as math_floor
from PIL import Image, ImageTk
from pandas import read_csv
from ..Tkinter_Addins.TooltipHover import CreateToolTip

# define font types and sizes to be used by the app
LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)


# CHECK INPUT VARIABLES
def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math_floor(n * multiplier + 0.55) / multiplier


def check_is_float_and_convert(check_input):
    """function used to check if the variable or its items (if is list) can be converted to type float"""
    try:
        if type(check_input) is list:
            check_input = list(map(lambda s: s.replace(",", "."), check_input))
            checked_input = list(map(float, check_input))
        else:
            checked_input = float(check_input.replace(",", "."))
    except (TypeError, AttributeError):
        return False
    except ValueError:
        return 0
    else:
        return checked_input


def check_if_not_none(check_input):
    """function used to check if input is not none"""
    try:
        if type(check_input) is list and check_input:
            if not check_input[0]:
                return None
            else:
                return check_input
        else:
            if not check_input and check_input != 0:
                return None
            else:
                return check_input
    except TypeError:
        return None


# PROVIDE INITIAL POSSIBLE TOTALS - SUBTOTAL, TAX TOTAL AND INVOICE TOTAL
# ONLY IF OCR READINGS ARE NULL
def provide_initial_subtotal(total_per_product_no_tax):
    if check_if_not_none(total_per_product_no_tax) is None:
        return [False, "Verificar formato do total dos artigos, devem ser números!"]

    if type(total_per_product_no_tax) is list:
        return round(sum(total_per_product_no_tax), 2)
    else:
        return 0


def provide_initial_tax_total(tax_per_item):
    if check_if_not_none(tax_per_item) is None:
        return [False, "Verificar formato do imposto total da fatura, deve ser um número!"]

    if type(tax_per_item) is list:
        return round(sum(tax_per_item), 2)
    else:
        return 0


def provide_initial_invoice_total(invoice_subtotal, invoice_total_tax):
    if check_if_not_none(invoice_subtotal) is None:
        return [False, "Verificar formato do subtotal, deve ser um número!"]
    if check_if_not_none(invoice_total_tax) is None:
        return [False, "Verificar formato do imposto total da fatura, deve ser um número!"]

    return round(invoice_subtotal + invoice_total_tax, 2)


# PERFORM CHECKS ON INPUTS PROVIDED BY THE READINGS OR THE USER

def calculate_gross_total_per_item(quantities, unit_prices):
    # calculate the net value of each item with the product of the quantity times the item unit price
    if type(quantities) is list:
        item_quantities = []
        for item_qty in quantities:
            if type(item_qty) is float:
                item_quantities.append(item_qty)
            else:
                try:
                    item_quantities.append([item_qty.split()][0])
                except IndexError:
                    item_quantities.append(item_qty)
    else:
        item_quantities = quantities

    if check_if_not_none(item_quantities) is None:
        return [False, "Verificar formato das quantidades por artigo, devem ser números!"]
    if check_if_not_none(unit_prices) is None:
        return [False, "Verificar formato dos preços unitários por artigo, devem ser números!"]

    if type(item_quantities) is list and type(unit_prices) is list:
        return [round(a * b, 2) for a, b in zip(item_quantities, unit_prices)] if len(
            list(item_quantities)) == len(list(unit_prices)) else False
    else:
        return [False, "Verificar formato dos preços unitários por artigo, devem ser números!"]


def convert_percentage_tax_to_amount(items_net_value, tax_percentages):
    # Convert tax percentages per item to tax amounts taking into account the products net value = quantity x unit price
    if check_if_not_none(items_net_value) is None:
        return [False, "Verificar formato dos totais por artigo, devem ser números!"]
    if check_if_not_none(tax_percentages) is None:
        return [False, "Verificar formato das taxas de imposto por artigo, devem ser percentagens!"]

    if type(tax_percentages) is list and type(items_net_value) is list:
        if len(list(tax_percentages)) == len(list(items_net_value)):
            # calculate the tax per item: if "a" or "b" is odd, then use round_half_up function to round the number
            # else, use normal round function
            tax_per_item = [round_half_up(a / 100 * b, 2) if a // 2 != 0 or b // 2 != 0 else round(a / 100 * b, 2)
                            for a, b in zip(tax_percentages, items_net_value)]
            return tax_per_item
        else:
            return False
    else:
        return False


def calculate_total_item_cost(total_per_product_no_tax, tax_per_item, discount_per_item=None):
    # if the total amount paid for an item is not available, then calculate it using: net amount + tax amount
    if check_if_not_none(total_per_product_no_tax) is None:
        return False
    if check_if_not_none(tax_per_item) is None:
        return False

    if not discount_per_item:
        if type(total_per_product_no_tax) is list and type(tax_per_item) is list:
            return [round(a + b, 2) for a, b in zip(total_per_product_no_tax, tax_per_item)] if len(
                list(total_per_product_no_tax)) == len(list(tax_per_item)) else False
        else:
            return False
    else:
        if type(total_per_product_no_tax) is list and type(tax_per_item) is list and type(discount_per_item) is list:
            return [round(a - b + c, 2) for a, b, c in zip(total_per_product_no_tax, discount_per_item, tax_per_item)] \
                if len(list(total_per_product_no_tax)) == len(list(tax_per_item)) == len(list(discount_per_item)) \
                else False
        else:
            return False


def check_unit_price_times_quantity(quantity, unit_price, total_per_product_no_tax=None):
    # Check if the product between item's quantity and unit price is equal to net total
    items_net_value = calculate_gross_total_per_item(quantity, unit_price)
    if check_if_not_none(items_net_value) is None:
        return [False, "Verificar formato do total dos artigos, devem ser um números!"]
    else:
        if total_per_product_no_tax is not None:
            if type(total_per_product_no_tax) is list and type(items_net_value) is list:
                total_per_product_no_tax = round(sum(total_per_product_no_tax), 2)
                items_net_value = round(sum(items_net_value), 2)

                return [False, "Verificar subtotal dos artigos ({}€) vs soma dos produtos sem IVA ({}€)!".format(
                    items_net_value, total_per_product_no_tax)] if total_per_product_no_tax != items_net_value \
                    else [True, ""]
            else:
                return [False, "Verificar formato das entradas deste check!"]

        else:
            return [False, "Verificar subtotal dos artigos!"]


def check_gross_total_plus_tax_is_total_per_item(total_per_product_no_tax, tax_per_item, total_per_product):
    # Check if sum of net total and tax equals sum of totals per item
    if check_if_not_none(total_per_product_no_tax) is None:
        return [False, "Verificar formato do total dos artigos, devem ser um números!"]
    if check_if_not_none(tax_per_item) is None:
        return [False, "Verificar formato do imposto total da fatura, deve ser um número!"]
    if check_if_not_none(total_per_product) is None:
        return [False, "Verificar formato do total dos artigos, devem ser um números!"]

    if type(total_per_product_no_tax) is list and type(tax_per_item) is list and type(total_per_product) is list:
        if len(total_per_product_no_tax) == len(tax_per_item) == len(total_per_product):
            total_items = round(sum([a + b for a, b in zip(total_per_product_no_tax, tax_per_item)]), 2)
            return [False, "Verificar valor líquido mais IVA por produto ({}€) vs subtotal ({}€)!".format(
                round(sum(total_per_product), 2), total_items)] if total_items != round(sum(total_per_product), 2) \
                else [True, ""]
        else:
            return [False, "Diferente número de entradas na coluna imposto por artigo e total por artigo!"]
    else:
        return [False, "Verificar formato do subtotal (decimal), taxa de IVA (%) e do total (decimal) por produto!"]


def check_if_sum_per_item_total_is_invoice_total(total_per_product, invoice_total):
    # Check if sum of total per product is equal to invoice total
    if check_if_not_none(total_per_product) is None:
        return [False, "Verificar formato do subtotal por artigo, devem ser um números!"]
    if check_if_not_none(invoice_total) is None:
        return [False, "Verificar formato do total da fatura, deve ser um número!"]

    if type(total_per_product) is list:
        return [False, "Verificar soma dos valores por artigo ({}€) vs total fatura ({}€)!".format(
            round(sum(total_per_product), 2), invoice_total)] if round(sum(total_per_product), 2) != invoice_total \
            else [True, ""]
    else:
        return [False, "Verificar formato do subtotal por artigo, devem ser um números!"]


def check_net_sum_is_subtotal(total_per_product_no_tax, invoice_subtotal):
    # Check if sum of net total is equal to invoice's subtotal
    if check_if_not_none(total_per_product_no_tax) is None:
        return [False, "Verificar formato do total líquido da fatura, deve ser um número!"]
    if check_if_not_none(invoice_subtotal) is None:
        return [False, "Verificar formato do imposto total da fatura, deve ser um número!"]

    if type(total_per_product_no_tax) is list:
        total_per_product_no_tax = round(sum(total_per_product_no_tax), 2)
        return [False, "Verificar SubTotal Fatura ({}€) vs Total Produtos sem IVA ({}€)!".format(
            invoice_subtotal, total_per_product_no_tax)] if total_per_product_no_tax != invoice_subtotal else [True, ""]
    else:
        return [False, "Verificar formato do total líquido da fatura, deve ser um número!"]


def check_tax_sum_is_total_tax(tax_per_item, invoice_total_tax):
    # Check if sum of taxes yields total tax
    if check_if_not_none(tax_per_item) is None:
        return [False, "Verificar formato do imposto por artigo, deve ser um número!"]
    if check_if_not_none(invoice_total_tax) is None:
        return [False, "Verificar formato do imposto total da fatura, deve ser um número!"]

    if type(tax_per_item) is list:
        return [False, "Verificar Imposto Total ({}€) vs Soma Impostos por produto ({}€)!".format(
            invoice_total_tax, round(sum(tax_per_item), 2))] if round(sum(tax_per_item), 2) != invoice_total_tax\
            else [True, ""]
    else:
        return [False, "Verificar formato do imposto por artigo, deve ser um número!"]


def check_subtotal_plus_tax_is_total(invoice_subtotal, invoice_total_tax, discount_total, other_costs,
                                     invoice_net_total, invoice_total):
    # Check if sum of subtotal and tax total yields total of invoice
    if check_if_not_none(invoice_subtotal) is None:
        return [False, "Verificar formato do subtotal, deve ser um número!"]
    if check_if_not_none(invoice_total_tax) is None:
        return [False, "Verificar formato do imposto total da fatura, deve ser um número!"]
    if check_if_not_none(invoice_net_total) is None:
        return [False, "Verificar formato do total líquido da fatura, deve ser um número!"]
    if check_if_not_none(invoice_total) is None:
        return [False, "Verificar formato do total da fatura, deve ser um número!"]

    if invoice_net_total == 0:
        subtotal_sum = round(invoice_subtotal - discount_total + other_costs + invoice_total_tax, 2)
        return [False, "Verificar Total da Fatura ({}€) vs soma de subtotais ({}€)!".format(
            invoice_total, subtotal_sum)] if subtotal_sum != invoice_total else [True, ""]
    else:
        subtotal_sum = round(invoice_net_total + other_costs + invoice_total_tax, 2)
        return [False, "Verificar Total da Fatura ({}€) vs soma de subtotais ({}€)!".format(
            invoice_total, subtotal_sum)] if subtotal_sum != invoice_total else [True, ""]


# RETRIEVE DATA FROM OCR RESULTS

def find_max_length(OCR_Results):
    """function used to determine the max length of the item's sub lists"""
    max_length = 0
    for item in OCR_Results:
        if type(OCR_Results[item]) is list:
            max_length = len(OCR_Results[item]) if len(OCR_Results[item]) > max_length else max_length
    return max_length


def get_input_from_OCR_results(OCR_Results, input_var, max_length, is_list):
    try:
        result = OCR_Results[input_var]
        if input_var == "quantity":
            result = get_quantity_sorted(result)
        result = check_is_float_and_convert(result)
        exists = True
    except KeyError:
        result = [0 for _ in range(0, max_length)] if is_list else 0
        exists = False

    return result, exists


def get_quantity_sorted(input_var):
    """ function used to split the information between quantity value and unit"""
    result = []
    if type(input_var) is list:
        for quant in input_var:
            quant = quant.split()
            try:
                result.append(quant[0]) if type(quant) is list else result.append(quant)
            except IndexError:
                result.append(quant)
        return result
    else:
        return input_var


def get_invoice_other_costs(OCR_Results):
    # function used calculate with the determination of the total tax
    # it should deal with most of the known cases - total tax (one value), or separated in multiple % values
    try:  # Special cases other costs are further described
        other_shipping = OCR_Results["other_shipping"]
    except KeyError:
        other_shipping = 0
    try:
        other_services = OCR_Results["other_services"]
    except KeyError:
        other_services = 0
    try:
        other_credits = OCR_Results["other_credits"]
    except KeyError:
        other_credits = 0
    try:
        other_costs = OCR_Results["other_costs"]
    except KeyError:
        other_costs = 0

    if other_shipping != 0:
        other_shipping = check_is_float_and_convert(other_shipping)
        other_shipping = 0 if not other_shipping else other_shipping
    if other_services != 0:
        other_services = check_is_float_and_convert(other_services)
        other_services = 0 if not other_services else other_services
    if other_credits != 0:
        other_credits = check_is_float_and_convert(other_credits)
        other_credits = 0 if not other_credits else other_credits
    if other_costs != 0:
        other_costs = check_is_float_and_convert(other_costs)
        other_costs = 0 if not other_costs else other_costs

    return other_shipping + other_services + other_credits + other_costs


def get_invoice_total_tax(OCR_Results):
    # function used calculate with the determination of the total tax
    # it should deal with most of the known cases - total tax (one value), or separated in multiple % values
    try:
        invoice_total_tax = OCR_Results["total_tax"]  # sum of all taxes per item
        invoice_total_tax = check_is_float_and_convert(invoice_total_tax)
    except KeyError:
        try:  # Special cases where total tax is provided by percentage
            invoice_total_tax_per = OCR_Results["total_tax_%"]
        except KeyError:
            invoice_total_tax_per = 0
        try:
            invoice_total_tax_6 = OCR_Results["total_tax_6%"]
        except KeyError:
            invoice_total_tax_6 = 0
        try:
            invoice_total_tax_13 = OCR_Results["total_tax_13%"]
        except KeyError:
            invoice_total_tax_13 = 0
        try:
            invoice_total_tax_23 = OCR_Results["total_tax_23%"]
        except KeyError:
            invoice_total_tax_23 = 0

        if invoice_total_tax_per != 0:
            invoice_total_tax_per = check_is_float_and_convert(invoice_total_tax_per)
            invoice_total_tax_per = 0 if not invoice_total_tax_per else invoice_total_tax_per
        if invoice_total_tax_6 != 0:
            invoice_total_tax_6 = check_is_float_and_convert(invoice_total_tax_6)
            invoice_total_tax_6 = 0 if not invoice_total_tax_6 else invoice_total_tax_6
        if invoice_total_tax_13 != 0:
            invoice_total_tax_13 = check_is_float_and_convert(invoice_total_tax_13)
            invoice_total_tax_13 = 0 if not invoice_total_tax_13 else invoice_total_tax_13
        if invoice_total_tax_23 != 0:
            invoice_total_tax_23 = check_is_float_and_convert(invoice_total_tax_23)
            invoice_total_tax_23 = 0 if not invoice_total_tax_23 else invoice_total_tax_23

        invoice_total_tax = invoice_total_tax_per + invoice_total_tax_6 + invoice_total_tax_13 + invoice_total_tax_23

    return invoice_total_tax


def get_invoice_total_discount(OCR_Results):
    # function used calculate with the determination of the total discount
    # it should deal with most of the known cases - total discount (one value), or separated in multiple values
    try:
        invoice_total_discount = OCR_Results["discount_total"]  # sum of all taxes per item
        invoice_total_discount = check_is_float_and_convert(invoice_total_discount)
    except KeyError:
        try:  # Special cases where total tax is provided by percentage
            commercial_discount = OCR_Results["com_discount%"]
        except KeyError:
            commercial_discount = 0
        try:
            financial_discount = OCR_Results["finan_discount"]
        except KeyError:
            financial_discount = 0

        if commercial_discount != 0:
            commercial_discount = check_is_float_and_convert(commercial_discount)
            commercial_discount = 0 if not commercial_discount else commercial_discount
        if financial_discount != 0:
            financial_discount = check_is_float_and_convert(financial_discount)
            financial_discount = 0 if not financial_discount else financial_discount

        invoice_total_discount = commercial_discount + financial_discount

    return invoice_total_discount


class TrafficLightCheck(tk.Frame):
    """ Class used to assess the validation checks on the read invoice"""

    def __init__(self, parent=None, main_file_path="", **kwargs):
        tk.Frame.__init__(self, parent, background="white", **kwargs)
        self.columnconfigure((0, 1), weight=1)
        path_green = main_file_path + r"\bin\aux_img\green.png"
        path_yellow = main_file_path + r"\bin\aux_img\yellow.png"
        path_red = main_file_path + r"\bin\aux_img\red.png"

        # load images to compile traffic light - green, yellow, red
        self.green_img = ImageTk.PhotoImage(Image.open(path_green).resize((20, 20), Image.LANCZOS))
        self.yellow_img = ImageTk.PhotoImage(Image.open(path_yellow).resize((20, 20), Image.LANCZOS))
        self.red_img = ImageTk.PhotoImage(Image.open(path_red).resize((20, 20), Image.LANCZOS))

        labelframe = tk.LabelFrame(self, text="Por Artigo", background="white", font=SMALL_FONT, labelanchor="n")
        labelframe.columnconfigure(1, weight=1)
        labelframe.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        labelframe_1 = tk.LabelFrame(self, text="Fatura", background="white", font=SMALL_FONT, labelanchor="n")
        labelframe.columnconfigure(1, weight=1)
        labelframe_1.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        label1 = tk.Label(labelframe, text="Subtotal = Quantidade x Preço Unitário", background="white",
                          font=NORM_FONT)
        self.check_1_img = tk.Label(labelframe, image=self.yellow_img, background="white")
        self.check_1_img.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        label1.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        label2 = tk.Label(labelframe, text="Subtotal + Imposto = Total Fatura",
                          background="white", font=NORM_FONT)
        self.check_2_img = tk.Label(labelframe, image=self.yellow_img, background="white")
        self.check_2_img.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        label2.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        label3 = tk.Label(labelframe, text="Soma dos subtotais = Total Fatura",
                          background="white", font=NORM_FONT)
        self.check_3_img = tk.Label(labelframe, image=self.yellow_img, background="white")
        self.check_3_img.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        label3.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        label4 = tk.Label(labelframe_1, text="Soma de total líquido por artigo = Subtotal",
                          background="white", font=NORM_FONT)
        self.check_4_img = tk.Label(labelframe_1, image=self.yellow_img, background="white")
        self.check_4_img.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        label4.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        label5 = tk.Label(labelframe_1, text="Soma de imposto por artigo = Total Imposto",
                          background="white", font=NORM_FONT)
        self.check_5_img = tk.Label(labelframe_1, image=self.yellow_img, background="white")
        self.check_5_img.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        label5.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        label6 = tk.Label(labelframe_1, text="Subtotal + Imposto = Total", background="white", font=NORM_FONT)
        self.check_6_img = tk.Label(labelframe_1, image=self.yellow_img, background="white")
        self.check_6_img.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        label6.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    def load_initial_status(self):
        """Method used to re-load all traffic light images to yellow"""
        self.check_1_img.configure(image=self.yellow_img)
        self.check_2_img.configure(image=self.yellow_img)
        self.check_3_img.configure(image=self.yellow_img)
        self.check_4_img.configure(image=self.yellow_img)
        self.check_5_img.configure(image=self.yellow_img)
        self.check_6_img.configure(image=self.yellow_img)

    def _assess_check(self, widget, check, msg):
        """Method used to attach error/ok message to traffic light image"""
        if check:
            widget.configure(image=self.green_img)
            CreateToolTip(widget, text="OK!")
        else:
            widget.configure(image=self.red_img)
            CreateToolTip(widget, text=msg)

    def do_checks(self, OCR_results):
        """method used to perform the defined invoice checks"""
        max_length = find_max_length(OCR_results)

        # ITEM QUANTITIES
        quantity, _ = get_input_from_OCR_results(OCR_results, "quantity", max_length, True)
        unit_price, _ = get_input_from_OCR_results(OCR_results, "unit_price", max_length, True)
        discount_per_item, discount = get_input_from_OCR_results(OCR_results, "discount", max_length, True)

        # item's: quantity x unit price - first try to get it from OCR readings, or compute using existing variables
        try:
            total_per_product_no_tax = OCR_results["item_gross_value"]
            total_per_product_no_tax = check_is_float_and_convert(total_per_product_no_tax)
        except KeyError:
            total_per_product_no_tax = calculate_gross_total_per_item(quantity, unit_price)
        # tax paid per item - first try to get it from OCR readings, else compute it using existing variables
        try:
            tax_per_item = OCR_results["tax_per_item"]
            tax_per_item = check_is_float_and_convert(tax_per_item)
        except KeyError:
            tax_percentages_per_item, _ = get_input_from_OCR_results(OCR_results, "tax_%s_per_item", max_length, True)
            tax_per_item = convert_percentage_tax_to_amount(total_per_product_no_tax, tax_percentages_per_item)
        # item's: quantity x unit price + tax
        try:
            total_per_product = OCR_results["total_per_product"]
            total_per_product = check_is_float_and_convert(total_per_product)
        except KeyError:
            # item's net value (=quantity x unit price) + tax (in amount, not percentage)
            # if a discount was made, include it in calculations
            if discount:
                total_per_product = calculate_total_item_cost(total_per_product_no_tax, tax_per_item, discount_per_item)
            else:
                total_per_product = calculate_total_item_cost(total_per_product_no_tax, tax_per_item)

        # INVOICE TOTALS
        invoice_subtotal, _ = get_input_from_OCR_results(OCR_results, "invoice_subtotal", max_length, False)
        calc_subtotal = False
        if not invoice_subtotal:
            invoice_subtotal, calc_subtotal = provide_initial_subtotal(total_per_product_no_tax), True

        invoice_net_total, _ = get_input_from_OCR_results(OCR_results, "invoice_net_total", max_length, False)
        discount_total = get_invoice_total_discount(OCR_results)
        other_costs = get_invoice_other_costs(OCR_results)

        invoice_total_tax = get_invoice_total_tax(OCR_results)
        calc_tax_total = False
        if not invoice_total_tax:
            invoice_total_tax, calc_tax_total = provide_initial_tax_total(tax_per_item), True

        invoice_total, _ = get_input_from_OCR_results(OCR_results, "invoice_total", max_length, False)
        calc_total = False
        if not invoice_total:
            invoice_total, calc_total = provide_initial_invoice_total(invoice_subtotal, invoice_total_tax), True

        # Check if the product between item's quantity and unit price is equal to net total
        check_1, message_error_1 = check_unit_price_times_quantity(quantity, unit_price, total_per_product_no_tax)
        # Check if sum of net total and tax equals sum of totals per item
        check_2, message_error_2 = check_gross_total_plus_tax_is_total_per_item(total_per_product_no_tax, tax_per_item,
                                                                                total_per_product)
        # Check if sum of total per product is equal to invoice total
        check_3, message_error_3 = check_if_sum_per_item_total_is_invoice_total(total_per_product, invoice_total)
        # Check if sum of net total is equal to invoice's subtotal
        check_4, message_error_4 = check_net_sum_is_subtotal(total_per_product_no_tax, invoice_subtotal)
        # Check if sum of taxes yields total tax
        check_5, message_error_5 = check_tax_sum_is_total_tax(tax_per_item, invoice_total_tax)
        # Check if sum of subtotal and tax total yields total of invoice
        check_6, message_error_6 = check_subtotal_plus_tax_is_total(invoice_subtotal, invoice_total_tax,
                                                                    discount_total, other_costs, invoice_net_total,
                                                                    invoice_total)

        self._assess_check(self.check_1_img, check_1, message_error_1)
        self._assess_check(self.check_2_img, check_2, message_error_2)
        if not calc_total:
            self._assess_check(self.check_3_img, check_3, message_error_3)
        if not calc_subtotal:
            self._assess_check(self.check_4_img, check_4, message_error_4)
        if not calc_tax_total:
            self._assess_check(self.check_5_img, check_5, message_error_5)
        if not calc_total:
            self._assess_check(self.check_6_img, check_6, message_error_6)

        return [invoice_subtotal, calc_subtotal, invoice_total_tax, calc_tax_total, invoice_total, calc_total]


class ProductUnitPrices():

    def __init__(self, template, dir_path, allowed_variation=0.1):
        self.template = template
        self.allowed_variation = allowed_variation
        self.template_item_table = {}
        self.get_template_reference_table(dir_path)

    def get_template_reference_table(self, dir_path):
        """Function used to get the ROI - region of interest of each template"""
        all_retailers_items = read_csv(dir_path, sep=',', header=0, encoding='latin')
        for key in all_retailers_items.keys():
            self.template_item_table[key] = all_retailers_items[key].dropna()

    def check_unit_price(self, cur_item_ref, cur_item_unit_price, permission_level):
        """method used to assess if unit price above or below expected price"""
        if cur_item_ref in self.template_item_table.keys():
            ref_price = self.template_item_table[cur_item_ref]
            if cur_item_unit_price <= ref_price * (1 + self.allowed_variation):
                return [True, "OK"]
            else:
                if permission_level == "admin":
                    return [False, "admin", "Preço acima do máximo esperado, deseja aceitar a faturação?"]
                else:
                    return [False, "user", "Preço acima do máximo esperado, por favor requisite a aprovação" +
                            " de um utilizador com permissões de administrador"]
        else:
            return [False, "Referência {} não existe na lista de produtos.".format(str(cur_item_ref))]
