import pytesseract
from random import randint
from pandas import read_csv
import os
import cv2
from numpy import float32 as np_float32
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from .Prepocessor_Pipeline import preprocess_and_resize_image, duplicate_image
from .ReadingsPostProcessor import result_postprocessor


tk_colors = ['blue', 'dark green', 'cyan2', 'brown1', 'maroon', 'purple',
             'coral2', 'maroon1', 'azure2', 'turquoise1', 'indian red', 'sea green',
             'pink', 'lawn green', 'violet red', 'salmon', 'gray50', 'dark orange',
             'DodgerBlue2', 'coral', 'firebrick2', 'wheat3', 'HotPink2', 'peach puff',
             'SpringGreen2', 'cyan4', 'MediumPurple2', 'LightSalmon3', 'OliveDrab2', 'CadetBlue2',
             'deep pink', 'lime green', 'yellow', 'ivory2', 'SlateGray1',
             'AntiqueWhite2', 'tomato', 'gold']

# BGR color format
cv2_colors = [(0, 0, 255), (0, 100, 0), (0, 238, 238), (255, 64, 64), (176, 48, 96), (160, 32, 240),
              (238, 106, 80), (255, 52, 179), (224, 238, 238), (0, 245, 255), (205, 92, 92), (46, 139, 87),
              (255, 192, 203), (124, 252, 0), (208, 32, 144), (250, 128, 114), (127, 127, 127), (255, 140, 0),
              (28, 134, 238), (255, 127, 80), (238, 44, 44), (205, 186, 150), (238, 106, 167), (255, 218, 185),
              (0, 238, 118), (0, 139, 139), (159, 121, 238), (205, 129, 98), (179, 238, 58), (142, 229, 238),
              (255, 20, 147), (50, 205, 50), (255, 255, 0), (238, 238, 224), (198, 226, 255),
              (238, 223, 204), (255, 99, 71), (255, 215, 0)]


def get_roi(exe_file_path):
    """Function used to get the ROI - region of interest of each template"""
    roi = {}
    all_retailers = read_csv(exe_file_path + r'\bin\Templates\Template_List.csv', sep=',', header=0, encoding='latin')
    for key in all_retailers.keys():
        roi[key] = all_retailers[key].dropna()

    return roi


def existing_keys(results_dict, try_key):
    if try_key not in results_dict.keys():
        return str(try_key)
    else:
        return str(try_key) + str(randint(1, 10000))


def get_current_template_file_path(template_dir_path, template_name):
    """ get the template path from the template directory path"""
    template_path = ""
    for f in os.listdir(template_dir_path):
        file_name = str(os.path.split(f)[1]).split(".")[0].lower()
        if template_name.lower() == file_name:
            template_path = os.path.join(template_dir_path, f)
            break
    return template_path


def get_correct_template(cur_roi, line_y, template_path):
    """ function used to re-calculate the ROI after the user defines the movable line"""
    # find delta from movable line to last list item
    neglect_row = next((k for k, row in enumerate(cur_roi) if row[2] == "neglect"), 0)
    delta_y = cur_roi[neglect_row][0][0]
    item_row_height = cur_roi[neglect_row][1][0]

    # calculate new final list y coordinate (bear in mind it is a scaled (with the image height) variable)
    line_y = float(line_y)
    new_list_end_y = round(line_y - float(delta_y), 6)

    # re-compute the ROI (region of interest) taking into account the user input
    final_roi = []
    after_list = False
    for row in cur_roi:
        if "table" in row[2]:
            final_roi.append([row[0], (row[1][0], new_list_end_y), row[2], row[3]])
            after_list = True
        elif row[2] == "neglect":
            continue
        elif row[0][0] == "0" and row[0][1] == "0" and row[1][0] == "0" and row[1][0] == "0":
            final_roi.append(row)
        elif after_list and row[2] != "neglect":
            old_line_y = float(cur_roi[neglect_row][1][1])
            if old_line_y > line_y:
                new_y1 = round(old_line_y - line_y, 6) + float(row[0][1])
            else:
                new_y1 = round(line_y - old_line_y, 6) + float(row[0][1])
            new_y2 = round(float(row[1][1]) - float(row[0][1]) + new_y1, 6)
            final_roi.append([(row[0][0], new_y1), (row[1][0], new_y2), row[2], row[3]])
        else:
            final_roi.append(row)

    # find height of items list
    list_height = round(next((float(row[1][1]) - float(row[0][1]) for row in final_roi if "list" in row[2]), 0), 6)
    # get an approximated number of articles of the current invoice
    n_lines = int(list_height / float(item_row_height))
    # transform the template name if number of rows larger than 1 (original template definition)
    if n_lines > 1:
        template_name = str(os.path.split(template_path)[1]).split(".")[0].lower()
        template_name_mod = template_name + str(n_lines)
        # get directory path of templates - extra templates should be stored inside a folder with the template name
        template_dir_path = os.path.dirname(template_path) + r'\extra_{}'.format(template_name)
        # if the path of the pretended template exist, then retrieve a new path to be used in the OCR reading
        if len(os.listdir(template_dir_path)) != 0:
            new_template_path = get_current_template_file_path(template_dir_path, template_name_mod)
            template_path = new_template_path if new_template_path != "" else template_path

    return final_roi, template_path


def tesseract_multi_runner(key, imgcrop):
    if key == 'single_number' or key == 'decimal_number':
        # custom_config = r'--psm 12'
        custom_config = r"--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789."  # output base digits
        return (pytesseract.image_to_string(imgcrop, config=custom_config)).strip()

    elif key == 'number' or key == 'ID_number':
        custom_config = r'--oem 3 --psm 8 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-/.'
        return (pytesseract.image_to_string(imgcrop, config=custom_config)).strip()

    elif key == 'date':
        custom_config = r'--oem 3 --psm 8 tessedit_char_whitelist=0123456789-/.'  # output base digits
        return (pytesseract.image_to_string(imgcrop, config=custom_config)).strip()

    elif key == 'text' or key == 'text_table':
        custom_config = r'--oem 3 --psm 6'
        return (pytesseract.image_to_string(imgcrop, lang="por", config=custom_config)).strip()

    elif key == 'list_table':  # quantity and tax
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.,'
        # custom_config = r'--psm 6 --oem 1'
        # custom_config = "digits"
        return (pytesseract.image_to_string(imgcrop, lang="por", config=custom_config)).strip()

    elif key == 'list_table_no':
        custom_config = r'--oem 3 --psm 4 tessedit_char_whitelist=0123456789-/,.'
        return (pytesseract.image_to_string(imgcrop, lang="por", config=custom_config)).strip()

    elif key == 'box':
        # convert image to gray
        imgGray = cv2.cvtColor(imgcrop, cv2.COLOR_BGR2GRAY)
        imgThresh = cv2.threshold(imgGray, 170, 255, cv2.THRESH_BINARY_INV)[1]
        totalPixels = cv2.countNonZero(imgThresh)
        if totalPixels > 500:
            totalPixels = 1
        else:
            totalPixels = 0
        return totalPixels

    else:
        return (pytesseract.image_to_string(imgcrop, lang="por")).strip()


def ocr_tesseract_reader(invoice_path, template, roi):
    """ Function used to find match between loaded_image (invoice) and the selected template
    where: "loaded_image" is of PIL image type,
            "template" is the path of the retailer template
            roi - region of interest matrix
    """

    imgQ = cv2.imread(template, -1)
    # Check if image has len = 3 (color) or 2 (black & white) dimensions
    if len(imgQ.shape) == 3:
        h, w, c = imgQ.shape
    else:
        h, w = imgQ.shape

    # open invoice path as cv2 type image
    img = cv2.imread(invoice_path, -1)
    try:
        cv2.resize(img, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
    except cv2.error as e:
        return "error", """Falha na leitura do ficheiro imagem da fatura! Por favor, converta o ficheiro antes de o
                         correr novamente na ferramenta!"""
    orb = cv2.ORB_create(2500)
    key_points_1, descriptors_1 = orb.detectAndCompute(imgQ, None)
    key_points_2, descriptors_2 = orb.detectAndCompute(img, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING2, True)
    matches = list(bf.match(descriptors_2, descriptors_1))
    matches.sort(key=lambda q: q.distance)
    good = matches[:int(len(matches) * (30 / 100))]

    srcPoints = np_float32([key_points_2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dstPoints = np_float32([key_points_1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    M, _ = cv2.findHomography(srcPoints, dstPoints, method=cv2.RANSAC, ransacReprojThreshold=5.0, mask=None,
                              maxIters=20, confidence=0.99)
    imgScan = cv2.warpPerspective(img, M, (w, h))

    imgCrop = []
    for x, r in enumerate(roi):
        # top_left_corner_X = X1, top_left_corner_Y = Y1, bottom_right_corner_X = X2, bottom_right_corner_Y = Y2
        X1 = int(float(r[0][0]) * w)
        Y1 = int(float(r[0][1]) * h)
        X2 = int(float(r[1][0]) * w)
        Y2 = int(float(r[1][1]) * h)

        if (X1 == 0 and Y1 == 0 and X2 == 0 and Y2 == 0) or Y2 < Y1 or X2 < X1:
            imgCrop.append(imgScan[0:5, 0:5])
        else:
            if r[2] == "list_table":
                imgCrop.append(preprocess_and_resize_image(duplicate_image(imgScan[Y1:Y2, X1:X2]), 1.25, 1))
            else:
                imgCrop.append(preprocess_and_resize_image(imgScan[Y1:Y2, X1:X2], 1.25, 1))
            cv2.rectangle(imgScan, (X1, Y1), (X2, Y2), cv2_colors[x], 2)

    keys = [row[2] for row in roi]
    with ThreadPoolExecutor() as executor:
        results_ocr = executor.map(tesseract_multi_runner, keys, imgCrop)

    # results_ocr = [tesseract_multi_runner(key, img) for key, img in zip(keys, imgCrop)]
    is_makro = True if "makro" in template.lower() else False
    results_out = result_postprocessor(roi, {roi[k][3]: result for k, result in enumerate(results_ocr)}, is_makro)

    return results_out, imgScan


class OcrReaderThread(Thread):
    def __init__(self, queue, queue_stop, list_images, list_fnames, cur_template, template_paths,
                 roi_templates, exe_file_path="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.queueStop = queue_stop
        self.running = True
        self.list_images = list_images
        self.list_fnames = list_fnames
        self.cur_template = cur_template
        self.template_paths = template_paths
        self.roi_templates = roi_templates

        pytesseract.pytesseract.tesseract_cmd = exe_file_path + r'\bin\Tesseract-OCR\tesseract.exe'
        print(exe_file_path + r'\bin\Tesseract-OCR\tesseract.exe')

    def run(self):
        try:
            c = 0
            while self.running:
                # Run OCR Engine
                if c + 1 <= len(self.list_images):
                    results, result_image = ocr_tesseract_reader(self.list_images[c], self.template_paths[c],
                                                                 self.roi_templates[c])
                    self.queue.put((c, results, result_image, self.cur_template, self.list_fnames[c]))
                else:
                    self.running = False
                c += 1
        finally:
            self.running = False
            self.queueStop.put((0, 'DONE'))

    def stop(self):
        self.running = False
