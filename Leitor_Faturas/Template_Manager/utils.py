from PIL import Image

# define font types and sizes to be used by the app
LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)

admissible_var_description = {
    "Adiantamentos/Créditos":   ["decimal_number",  "other_credits"],
    "Custos - Serviços":        ["decimal_number",  "other_services"],
    "Custos - Outros":          ["decimal_number",  "other_costs"],
    "Custos - Portes":          ["decimal_number",  "other_shipping"],
    "Data Fatura":              ["date",            "date_invoice"],
    "Descrição Artigos":        ["text_table",      "Description_items"],
    "Desconto (€) por Item":    ["list_table",      "discount"],
    "Desconto (%) por item":    ["list_table",      "discount_%s"],
    "Desconto Comercial":       ["decimal_number",  "com_discount"],
    "Desconto Financeiro":      ["decimal_number",  "finan_discount"],
    "Desconto Total":           ["decimal_number",  "discount_total"],
    "IVA (€) por Item":         ["list_table",      "tax_per_item"],
    "IVA (%) por Item":         ["list_table",      "tax_%s_per_item"],
    "Morada Empresa":           ["text",            "name_address"],
    "NIF Empresa":              ["ID_number",       "NIF"],
    "Nome Empresa":             ["text",            "name_address"],
    "Número da Fatura":         ["number",          "no_invoice"],
    "Preço por Unidade":        ["list_table",      "unit_price"],
    "Preço Bruto Mercadoria":   ["list_table",      "item_gross_value"],
    "Quantidade":               ["list_table",      "quantity"],
    "Referências Items":        ["list_table_no",   "ID_items"],
    "Subtotal por Item":        ["decimal_number",  "total_per_product"],
    "Subtotal Fatura":          ["decimal_number",  "invoice_subtotal"],
    "Total Fatura (pré-Descontos/Custos)":  ["decimal_number",  "invoice_net_total"],
    "Total Fatura":             ["decimal_number",  "invoice_total"],
    "Total IVA (€) Fatura":     ["decimal_number",  "total_tax"],
    "Total IVA (%) Fatura":     ["decimal_number",  "total_tax_%"],
    "Total IVA (6%) Fatura":    ["decimal_number",  "total_tax_6%"],
    "Total IVA (13%) Fatura":   ["decimal_number",  "total_tax_13%"],
    "Total IVA (23%) Fatura":   ["decimal_number",  "total_tax_23%"],
}


def get_resized_img(image, width, height):
    """ method used to resize image"""
    video_ratio = width / height
    img_ratio = image.size[0] / image.size[1]
    if video_ratio >= 1:  # the video is wide
        if img_ratio <= video_ratio:  # image is not wide enough
            width_new = int(height * img_ratio)
            size_new = width_new, height
        else:  # image is wider than video
            height_new = int(width / img_ratio)
            size_new = width, height_new
    else:  # the video is tall
        if img_ratio >= video_ratio:  # image is not tall enough
            height_new = int(width / img_ratio)
            size_new = width, height_new
        else:  # image is taller than video
            width_new = int(height * img_ratio)
            size_new = width_new, height
    return image.resize(size_new, Image.LANCZOS)
