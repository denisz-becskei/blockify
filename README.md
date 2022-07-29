# Blockify

Used to turn images into Minecraft Blockified versions of the image.

The way it works, is it has a block palette. At the beginning of the run, every block's average color on the palette gets calculated and stored, then takes every pixel of the input image one by one, and stores it's (R, G, B) values.
Then we check the difference between the pixels' and the palette's (R, G, B) values, and the best match gets selected from the palette. Then we build up the output from the selected blocks.

## Usage

py main.py &lt;input> -e &lt;extension>

## Args
Extension | Effect
--- | ---
-e | The output's extension. Supported PNG and JPEG
-v | Visualize output creation. WARNING! Significantly increases output time
-np | Not Precise, the results are not as precise, but it decreases output time

## Recommendation

We recommend to not use large images. For a 200x200 input image, it needs to place down 40,000 blocks on the output. The bigger the input is, the longer conversion takes, and bigger the output file.
On a bigger image, than 200x200 image, we recommend a JPEG output format. For example, the test image "galaxy.png" (which is of a size of 1000x667), the output file's size is 324MB in PNG format, while it's 82.4MB in JPEG.
