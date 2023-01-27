
import pandas as pd
import numpy as np
from rectpack import newPacker
import rectpack.packer as packer
import matplotlib.pyplot as plt


# Function Solver
def solver(n_12101, n_1210, n_1111, n_128, n_11, bins):
    ''' For optimizing how pallets should be placed in the container. The inputs are the quantities of each pallet type and the container size.'''

    # Set Pallet Buffer
    bx = 5 # buffer x
    by = 5 # buffer y
    
    pal_12101 = [121.9 + bx, 101.6 + by] # Pallet USA
    pal_1210 = [120 + bx, 100 + by]      # Pallet PBR
    pal_1111 = [116.5 + bx, 116.5 + by]  # Pallet Austrália
    pal_128 = [120 + bx, 80 + by]        # Pallet Europeu
    pal_11 = [110 + bx, 110 + by]         # Pallet Asiático
    
    # Create Rectangles / Pallets to load
    rectangles =[pal_12101 for i in range(n_12101)] + [pal_1210 for i in range(n_1210)] + [pal_1111 for i in range(n_1111)] +\
                [pal_128 for i in range(n_128)] + [pal_11 for i in range(n_11)] 

    # Build the Packer
    pack = newPacker(mode = packer.PackingMode.Offline, bin_algo = packer.PackingBin.Global,
                     rotation=True)

    # Add the rectangles to packing queue
    for r in rectangles:
        pack.add_rect(*r)

    # Add the bins where the rectangles will be placed
    for b in bins:
        pack.add_bin(*b)

    # Start packing
    pack.pack()

    # Full rectangle list
    all_rects = pack.rect_list()

    # Pallets with dimensions
    all_pals = [sorted([p[3], p[4]]) for p in all_rects]

    return all_rects, all_pals

 