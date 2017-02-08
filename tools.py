import numpy as np
import matplotlib

def compute_cmap(file,colormap):

    '''Read thredds colormaps_<name>.pal file and compute cmap'''

    LinL=np.loadtxt(file)
    if np.max(LinL[:,:]) > 1 :
        LinL[:,:]=LinL[:,:]/255
    b3=LinL[:,2]
    b2=LinL[:,2]
    b1=np.linspace(0,1,len(b2))
    g3=LinL[:,1]
    g2=LinL[:,1]
    g1=np.linspace(0,1,len(g2))
    r3=LinL[:,0]
    r2=LinL[:,0]
    r1=np.linspace(0,1,len(r2))
    # Creating list
    R=zip(r1,r2,r3)
    G=zip(g1,g2,g3)
    B=zip(b1,b2,b3)
    # Transposition list
    RGB=zip(R,G,B)
    rgb=zip(*RGB)
    # Dictionnary
    k=['red','green','blue']
    LinearL=dict(zip(k,rgb))
    return matplotlib.colors.LinearSegmentedColormap(colormap,LinearL)


