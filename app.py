from viktor.core import ViktorController
from viktor.geometry import SquareBeam, Group, Material
from viktor.parametrization import ViktorParametrization, Text, IntegerField, OptionField, DynamicArray
from viktor.views import SVGView, SVGResult, GeometryResult, GeometryView
from viktor import Color
from io import StringIO
from matplotlib.patches import Rectangle

from solver import solver
import pandas as pd
import numpy as np
from rectpack import newPacker
import rectpack.packer as packer
import matplotlib.pyplot as plt
import random

# Tipos de veículos 

class Parametrization(ViktorParametrization):
    title = Text('# Otimização de carregamento')

    bin_type = OptionField('Qual tipo de veículo?', options=["carreta_bau", "carreta_sider","truck"], default="carreta_bau", flex=90)

# Definindo os tipos de Pallets 

    array = DynamicArray('Escolha os tipos de Pallets e Quantidade')
    array.pallet_dim = OptionField('Tipo de Pallet', options =['121.9 x 101.6 cm: Pallet USA', '120 x 100 cm: Pallet PBR', '116.5 x 116.5 cm: Pallet Australiano','120 x 80 cm: Pallet Europeu','110 x 110 cm: Pallet Asiático'], flex=70, default='120 x 100 cm: Pallet PBR')
    array.pallet_quantity = IntegerField('Quantidade', default = 1, flex = 25)

#


class Controller(ViktorController):
    label = 'Veículo'
    parametrization = Parametrization(width=35)
        
    @SVGView("Baú", duration_guess=1)
    def create_svg_result(self, params,**kwargs):
        '''Essa função cria a visualização dos pallets dentro dos veicuos.'''

        #initialize figure
        
        fig = plt.figure(figsize = (4,12))

        # Dimensões dos veículos 
        
        carreta_bau = [(270, 1600)] # Carreta Bau'
        truck = [(270, 1000)] # Truck'
        carreta_sider = [(270, 1400)] # carreta sider'

        # Dimensões dos pallets (Acrescentando 5cm em cada eixo de folga)
        bx = 5 # buffer x
        by = 5 # buffer y

        pal_12101 = [121.9 + bx, 101.6 + by] # Pallet USA
        pal_1210 = [120 + bx, 100 + by]      # Pallet PBR
        pal_1111 = [116.5 + bx, 116.5 + by]  # Pallet Austrália
        pal_128 = [120 + bx, 80 + by]        # Pallet Europeu
        pal_11 = [110 + bx, 110 + by]        # Pallet Asiático
        
        # Quantos de cada tipo de pallet são selecionados
        n_12101, n_1210, n_1111, n_128, n_11 = 0, 0, 0, 0, 0

        for pallet in params.array:
            if pallet.pallet_dim == '121.9 x 101.6 cm: Pallet USA':
                n_12101 += pallet.pallet_quantity
            if pallet.pallet_dim == '120 x 100 cm: Pallet PBR':
                n_1210 += pallet.pallet_quantity
            if pallet.pallet_dim == '116.5 x 116.5 cm: Pallet Australiano':
                n_1111 += pallet.pallet_quantity
            if pallet.pallet_dim == '120 x 80 cm: Pallet Europeu':
                n_128 += pallet.pallet_quantity
            if pallet.pallet_dim == '110 x 110 cm: Pallet Asiático':
                n_11 += pallet.pallet_quantity
            

        # Plot Container
        if params.bin_type == "carreta_bau":
            bin_type = carreta_bau
            plt.plot([0,270,270,0,0],[0,0,1600,1600,0], linewidth = 2.5, color = "k" )
        
        elif params.bin_type == "carreta_sider":
            bin_type = carreta_sider
            plt.plot([0,270,270,0,0],[0,0,1400,1400,0], linewidth = 2.5, color = "k" )

        else:
            bin_type = truck
            plt.plot([0,270,270,0,0],[0,0,1000,1000,0], linewidth = 2.5, color = "k")

        #all_rects, all_pals = solver(params.n_812, params.n_1012, bin_type)
        all_rects, all_pals = solver(n_12101, n_1210, n_1111, n_128, n_11 , bin_type)

        # Loop all rect
        for rect in all_rects:
            b, x, y, w, h, rid = rect
            # Pallet type colours. If included also add color in plot below.
            if [w, h] == pal_12101 or [h, w] == pal_12101:
                color = 'pink'
            if [w, h] == pal_1210 or [h, w] == pal_1210:
                color = 'brown'
            if [w, h] == pal_1111 or [h, w] == pal_1111:
                color = 'olive'
            if [w, h] == pal_128 or [h, w] == pal_128:
                color = 'orange'
            if [w, h] == pal_11 or [h, w] == pal_11:
                color = 'blue'
                
            plt.gca().add_patch(Rectangle((x,y),w,h, facecolor = color, edgecolor='k', fill=True, lw=2))
        
        plt.axis('equal')
        plt.axis('off')
        fig.tight_layout()

        #save figure
        
        svg_data = StringIO()
        fig.savefig(svg_data, format='svg')
        plt.close()

        return SVGResult(svg_data)

    @GeometryView("3D Baú", duration_guess=1)
    
    def visualize_container(self, params, **kwargs):
        
        #carreta_padrão
        
        length_x = 2.7
        length_z = 2.6
        
        if params.bin_type == "carreta_bau":
            length_y= 16
            bin_type = [(270, 1600)]
            
        elif params.bin_type == "carreta_sider":
            length_y= 14
            bin_type = [(270, 1400)]
            
        else:
            length_y=10
            bin_type = [(270, 1000)]
                
        container = SquareBeam(length_x, length_y, length_z)
        container.material = Material('iron', threejs_opacity=0.5)
        container.translate([(length_x/2),(length_y/2),(length_z/2)])

        # Set Pallet Dimensions
        bx = 5 # buffer x
        by = 5 # buffer y

        pal_12101 = [121.9 + bx, 101.6 + by] # Pallet USA
        pal_1210 = [120 + bx, 100 + by]      # Pallet PBR
        pal_1111 = [116.5 + bx, 116.5 + by]  # Pallet Austrália
        pal_128 = [120 + bx, 80 + by]        # Pallet Europeu
        pal_11 = [110 + bx, 110 + by]         # Pallet Asiático

        # How many of each pallet type is selected
        
        n_12101, n_1210, n_1111, n_128, n_11 = 0, 0, 0, 0, 0

        for pallet in params.array:
             if pallet.pallet_dim == '121.9 x 101.6 cm: Pallet USA':
                n_12101 += pallet.pallet_quantity
             if pallet.pallet_dim == '120 x 100 cm: Pallet PBR':
                n_1210 += pallet.pallet_quantity
             if pallet.pallet_dim == '116.5 x 116.5 cm: Pallet Australiano':
                n_1111 += pallet.pallet_quantity
             if pallet.pallet_dim == '120 x 80 cm: Pallet Europeu':
                n_128 += pallet.pallet_quantity
             if pallet.pallet_dim == '110 x 110 cm: Pallet Asiático':
                n_11 += pallet.pallet_quantity

        #all_rects, all_pals = solver(params.n_812, params.n_1012, bin_type)
        all_rects, all_pals = solver(n_12101, n_1210, n_1111, n_128, n_11, bin_type)

        pallets = []
        for i, pallet in enumerate(all_rects):
            b, x, y, w, h, rid = pallet
            length_x = w/100
            length_y = h/100
            length_z = random.uniform(1,2) #random pallet heights

            #create pallet
            pallet_box = SquareBeam(length_x=length_x-0.1, length_y=length_y-0.1, length_z=length_z) #add 0.1 loose space between pallets

            #move pallet to right location (defining the center of the pallet)
            pallet_box.translate([(x/100+0.5*length_x),(y/100+0.5*length_y),(0.5*length_z)])
            
            #set Material
            
            if [w, h] == pal_12101 or [h, w] == pal_12101:
                color = Color(227,119,194) #pink
            if [w, h] == pal_1210 or [h, w] == pal_1210:
                color = Color(140,86,75) #brown
            if [w, h] == pal_1111 or [h, w] == pal_1111:
                color = Color(188,189,34) #olive
            if [w, h] == pal_128 or [h, w] == pal_128:
                color = Color(255,127,14) #orange
            if [w, h] == pal_11 or [h, w] == pal_11:
                color = Color(31,119,180) # blue
            pallet_box.material = Material('plastic', color=color)
            #add to pallet list
            pallets.append(pallet_box)
        pallets = Group(pallets)

        container_system = Group([container, pallets])
                
        return GeometryResult(container_system)