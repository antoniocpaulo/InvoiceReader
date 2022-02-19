import cv2
from numpy import concatenate, ones, uint8
# from pi as np_pi, arctan2 as np_arctan2, abs as np_abs
# import math


def duplicate_image(image):
    copy_image = image.copy()
    return concatenate((image, copy_image), axis=1)


def preprocess_and_resize_image(image, resize_val, kernel_size=3):
    # resize image to 150% of original size
    image = cv2.resize(image, None, fx=resize_val, fy=resize_val, interpolation=cv2.INTER_CUBIC)
    # call function to perform remaining preprocessing modifications
    image = preprocess_image(image, kernel_size)

    return image


def preprocess_image(image, kernel_size=5):
    # convert image to gray scale if number of channels is 3 ie 3D (2D array - grayscale image, 3D array - color image)
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # application of dilation and erosion to remove noise (if necessary play with kernel size)
    # apply blurring to smooth out the edges
    kernel = ones((kernel_size, kernel_size), uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.medianBlur(image, 3)

    # direct application of threshold to invert white to black and vice-versa
    # image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)

    # application of blurring to smooth out the edges
    # image = cv2.threshold(cv2.GaussianBlur(image, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # image = cv2.threshold(cv2.bilateralFilter(image, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # image = cv2.threshold(cv2.medianBlur(image, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # before last digit - area pixel size to apply background removal
    # (smaller value -> noise, may fade text characters)
    # last digit - custom value that gets deleted from threshold value (smaller value -> more noise, larger value ->
    # less noise but may remove text information)
    # use only odd values to define the previous two variables

    # image = cv2.adaptiveThreshold(cv2.GaussianBlur(image, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                               cv2.THRESH_BINARY, 31, 2)
    # image = cv2.adaptiveThreshold(cv2.bilateralFilter(image, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                               cv2.THRESH_BINARY, 31, 2)
    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 7)

    return image


# def get_horizontal_lines(image):
#     # Transform source image to gray if it is not already
#     if len(image.shape) != 2:
#         gray = cv2_cvtColor(image, COLOR_BGR2GRAY)
#     else:
#         gray = image
#
#     # Apply adaptiveThreshold at the bitwise_not of gray, notice the ~ symbol
#     # gray = cv2.bitwise_not(gray)
#     # bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
#     # Create the images that will use to extract the horizontal lines
#     # horizontal = np.copy(bw)
#     # # [horiz]
#     # # Specify size on horizontal axis
#     # cols = horizontal.shape[1]
#     # horizontal_size = cols // 30
#     # # Create structure element for extracting horizontal lines through morphology operations
#     # horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
#     # # Apply morphology operations
#     # horizontal = cv2.erode(horizontal, horizontalStructure)
#     # horizontal = cv2.dilate(horizontal, horizontalStructure)
#
#     # thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
#     # horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
#     # horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
#     # cnts = cv2.findContours(horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     # cnts = cnts[0] if len(cnts) == 2 else cnts[1]
#     # for c in cnts:
#     #     cv2.drawContours(image, [c], -1, (36, 255, 12), 2)
#     #     print(c)
#
#     if len(image.shape) == 3:
#         h, w, c = image.shape
#     else:
#         h, w = image.shape
#
#     processed_img = cv2_cvtColor(image, COLOR_BGR2GRAY)
#     processed_img = cv2_Canny(processed_img, threshold1=200, threshold2=300)
#     processed_img = cv2_GaussianBlur(processed_img, (3, 3), 0)
#     lines = cv2_HoughLinesP(processed_img, 5, np_pi / 180, 200, w // 2, 50)
#
#     count = 0
#     for line in lines:
#         line = line[0]
#         x1, y1, x2, y2 = line
#         Angle = math.atan2(y2 - y1, x2 - x1) * 180.0 / np_pi
#         if -5 < Angle < 5 and x1 > 5 and x2 > 5:
#             cv2_line(image, (x1, y1), (x2, y2), [0, 255, 0], 3)
#             count += 1
#
#     cv2_imshow("horizontal lines", image)
#     cv2_waitKey()
#     return image
#
#
# def avg_file_rotation(image):
#     # grab the dimensions of the image and then determine the
#     # center
#     if len(image.shape) == 3:
#         (h, w, _) = image.shape
#     else:
#         (h, w) = image.shape
#
#     (cX, cY) = (w // 2, h // 2)
#
#     grayimg = cv2_cvtColor(image, COLOR_BGR2GRAY)
#     _, binary_thresh = cv2_threshold(grayimg, 200, 255, THRESH_BINARY_INV)
#     lines = cv2_HoughLinesP(binary_thresh, 1, np_pi / 180, 100, minLineLength=300, maxLineGap=20)
#
#     angle = 0
#     for line in lines:
#         x1, y1, x2, y2 = line[0]
#         # r = np.arctan(y2 - y1, x2 - x1)
#         angle += np_arctan2(y2 - y1, x2 - x1)
#
#     avg_radian = angle / len(lines)
#     avg_angle = avg_radian * 180 / np_pi
#
#     # grab the rotation matrix (applying the negative of the
#     # angle to rotate clockwise), then grab the sine and cosine
#     # (i.e., the rotation components of the matrix)
#     M = getRotationMatrix2D((cX, cY), -avg_angle, 1.0)
#     # M = cv2.getRotationMatrix2D((cX, cY), -0.65, 1.0)
#     cos = np_abs(M[0, 0])
#     sin = np_abs(M[0, 0])
#
#     nW = int((h * sin) + (w * cos))
#     nH = int((h * cos) + (w * sin))
#
#     # adjust the rotation matrix to take into account translation
#     M[0, 2] += (nW / 2) - cX
#     M[1, 2] += (nH / 2) - cY
#
#     # perform the actual rotation and return the image
#     return warpAffine(image, M, (nW, nH))
