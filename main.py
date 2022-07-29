import cv2
import numpy as np
import time
import sys
from threading import Thread


def array_difference(array1, array2):
    if array1 is None or array2 is None or len(array1) != len(array2):
        return 9999

    return abs(array1[0] - array2[0]) + abs(array1[1] - array2[1]) + abs(array1[2] - array2[2])


def clear_nonetype(array):
    output_1 = list()
    for elem in array:
        if len(elem) != 1:
            output_1.append(elem)
    return output_1


## ARGS
visualize = False
precision = True
debug = True
threads = False

filename = "test3.jpg"
ext = "png"
args = sys.argv
if len(args) == 1 or "-e" not in args:
    print("Usage: main.py <filename> -e <filetype>")
    if not debug:
        quit(1337)
else:
    filename = args[1]
if "-v" in args:
    visualize = True
if "-np" in args:
    precision = False
if "-e" in args:
    indexof_e = args.index("-e")
    if args[indexof_e + 1].lower() == "jpg":
        ext = "jpg"
    elif args[indexof_e + 1].lower() == "png":
        ext = "png"
    else:
        print("Invalid File Type")
        if not debug:
            quit(1337)
if "-t" in args:
    threads = True

output_filename = filename.strip(".\\").split(".")[0] + "_output." + ext
start = time.time()

print("### IMAGES READ ###")
original = cv2.imread(filename, -1)
block_sheet = cv2.imread("blocks.png", -1)
BLOCK_SIZE = 16
SHEET_SIZE = 512
REPRESENTATIVE_HEIGHT = 64
ELEMS = SHEET_SIZE // BLOCK_SIZE
IMAGE_SIZE_H, IMAGE_SIZE_W, _ = original.shape
cropped = None

print("### STARTED AVERAGING ###")
averages = [[0] for i in range(0, ELEMS ** 2)]

averages_index = 0
for i in range(0, ELEMS):
    for j in range(0, ELEMS):
        cropped = block_sheet[i * BLOCK_SIZE: (i + 1) * BLOCK_SIZE, j * BLOCK_SIZE: (j + 1) * BLOCK_SIZE]
        average_color_row = np.average(cropped, axis=0)
        average_color = np.average(average_color_row, axis=0)

        if average_color[3] == 255.0:
            averages[averages_index] = [average_color[0], average_color[1], average_color[2]]
        averages_index += 1

clean_averages = clear_nonetype(averages)
averages_time = time.time()
print("### FINISHED AVERAGING IN " + str(averages_time - start) + " SECONDS ###")

blocks_1 = list()
blocks_2 = list()


def compare1():
    print(f"### STARTED COMPARING{ ' ON THREAD 1' if threads else '' } ###")
    for i_1 in range(0, IMAGE_SIZE_H // 2):
        for j_2 in range(0, IMAGE_SIZE_W):
            if ".png" in filename:
                try:
                    b, g, r, a = (original[i_1, j_2])

                    if a == 0:
                        blocks_1.append(22 * ELEMS + 2)
                        continue
                except ValueError:
                    b, g, r = (original[i_1, j_2])

            else:
                b, g, r = (original[i_1, j_2])

            lowest_difference = 9999
            best_index = 0

            for average in clean_averages:
                diff = array_difference([b, g, r], average)
                if diff < lowest_difference:
                    lowest_difference = diff
                    best_index = averages.index(average)
                    if lowest_difference < 30 and not precision:
                        break
            blocks_1.append(best_index)
    comparison_time = time.time()
    print(f"### FINISHED COMPARING{ ' ON THREAD 1' if threads else '' } IN " + str(comparison_time - averages_time) + " SECONDS ###")


def compare2():
    print(f"### STARTED COMPARING{ ' ON THREAD 2' if threads else '' } ###")
    for i_1 in range(IMAGE_SIZE_H // 2, IMAGE_SIZE_H):
        for j_2 in range(0, IMAGE_SIZE_W):
            if ".png" in filename:
                try:
                    b, g, r, a = (original[i_1, j_2])

                    if a == 0:
                        blocks_2.append(22 * ELEMS + 2)
                        continue
                except ValueError:
                    b, g, r = (original[i_1, j_2])

            else:
                b, g, r = (original[i_1, j_2])

            lowest_difference = 9999
            best_index = 0

            for average in clean_averages:
                diff = array_difference([b, g, r], average)
                if diff < lowest_difference:
                    lowest_difference = diff
                    best_index = averages.index(average)
                    if lowest_difference < 30 and not precision:
                        break
            blocks_2.append(best_index)
    comparison_time = time.time()
    print(f"### FINISHED COMPARING{ ' ON THREAD 2' if threads else '' } IN " + str(comparison_time - averages_time) + " SECONDS ###")


if threads:
    print("### STARTED THREADING ###")
    t1 = Thread(target=compare1)
    t2 = Thread(target=compare2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
else:
    compare1()
    compare2()

blocks = blocks_1 + blocks_2

blocks_index = 0

height = IMAGE_SIZE_H * BLOCK_SIZE
width = IMAGE_SIZE_W * BLOCK_SIZE
output = np.zeros((height, width, 4), np.uint8)

scale_percent = round(REPRESENTATIVE_HEIGHT / IMAGE_SIZE_W * 100)  # percent of original size
width = int(output.shape[1] * scale_percent / 100)
height = int(output.shape[0] * scale_percent / 100)
dim = (width, height)


print("### STARTED CONVERSION ###")
for i in range(0, IMAGE_SIZE_H):
    for j in range(0, IMAGE_SIZE_W):
        if blocks_index == IMAGE_SIZE_H * IMAGE_SIZE_W // 4:
            print("Conversion progress: ****------------")
        elif blocks_index == IMAGE_SIZE_H * IMAGE_SIZE_W // 2:
            print("Conversion progress: ********--------")
        elif blocks_index == round(IMAGE_SIZE_H * IMAGE_SIZE_W * 0.75):
            print("Conversion progress: ************----")

        indexes = [blocks[blocks_index] // ELEMS,
                   blocks[blocks_index] % ELEMS]
        selected_block = block_sheet[indexes[0] * BLOCK_SIZE: (indexes[0] + 1) * BLOCK_SIZE,
                         indexes[1] * BLOCK_SIZE: (indexes[1] + 1) * BLOCK_SIZE]
        output[i * BLOCK_SIZE: (i + 1) * BLOCK_SIZE, j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE] = selected_block
        if visualize:
            cv2.imshow("Progress", cv2.resize(output, dim, interpolation=cv2.INTER_AREA))
            cv2.waitKey(1)
        blocks_index += 1

print("Conversion progress: ****************")
print("CONVERSION DONE!")

scale_percent = 1600  # percent of original size
width = int(original.shape[1] * scale_percent / 100)
height = int(original.shape[0] * scale_percent / 100)
# dim = (width, height)
# cv2.imshow("Original", cv2.resize(original, dim, interpolation=cv2.INTER_AREA))
cv2.imwrite(output_filename, output)
end = time.time()
print("Operation took: " + str(end - start))

cv2.waitKey(0)
