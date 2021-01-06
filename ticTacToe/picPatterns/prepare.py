import pickle

from PIL import Image

for name1, name2 in [('image_cross.png', 'cross'),
                     ('image_circle.png', 'circle')]:
    pattern = Image.open(name1)
    pixels = pattern.load()

    values = set()

    for i in range(pattern.size[0]):
        for j in range(pattern.size[1]):
            rgba = pixels[i, j]
            if rgba[3] != 0:
                values.add(rgba[0])

    M = int('a2', 16) if name2 == 'circle.png' else int('90', 16)
    m = min(values)


    def normalize(value):
        value = (value - m) / (M - m)
        value = round(value * (255 - m))
        value += m
        return min(255, value)

    result_pixels = [[[0, 0] for _ in range(pattern.size[1])]
                     for _ in range(pattern.size[0])]

    for i in range(pattern.size[0]):
        for j in range(pattern.size[1]):
            rgba = pixels[i, j]
            if rgba[3] != 0:
                gray = normalize(rgba[0])
                i2 = pattern.size[0] - i - 1
                j2 = pattern.size[1] - j - 1
                result_pixels[i2][j2] = [gray, rgba[3]]

    with open(name2, 'wb') as f:
        pickle.dump(result_pixels, f)
