import matplotlib.pyplot as plt
f = "full_office.pgm"
with open(f, 'rb') as pgmf:
    im = plt.imread(pgmf)
    plt.imshow(im)
    plt.show()

    # Do something, rasterise for .map file 