# Aidan DeBrae

# The main topic of my research project is the tidal evolution
# of M33's Dark Matter Halo. The qeustion I'm specifically 
# investigating is  'What is the 3D shape of the dark matter 
# distribution of M33 - how does this change with time? Is it
# elongated/ellipsoid or spherical?' What do terms like prolate, 
# oblate, or triaxial halos mean?' 


#%%
# import modules
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib import cm
import scipy.optimize as so
# my modules from assignments
from ReadFile import Read
from CenterOfMass import CenterOfMass
# generate data from the orbit files written in hw6
M31_data = np.genfromtxt('Orbit_M31.txt', dtype=None, names=True)
M33_data = np.genfromtxt('Orbit_M33.txt', dtype=None, names=True)

# create an easy to use vector difference function
def vector_diff(vector1, vector2):
    diff = vector1 - vector2
    magnitude = np.sqrt(diff[0]**2 + diff[1]**2 + diff[2]**2)
    return magnitude

# I'm going to try and calculate the peri/apo-center approaches
# of the galaxies in an attempt to observe the most dramatic affects.
peri_t = 0
peri_dist = 100000 
apo_t = 0
apo_dist = 0
for i in range(160):
    M33_x = M33_data['x'][i]
    M33_y = M33_data['y'][i]
    M33_z = M33_data['z'][i]
    M33_pos_vector = np.array([M33_x, M33_y, M33_z])
    M31_x = M31_data['x'][i]
    M31_y = M31_data['y'][i]
    M31_z = M31_data['z'][i]
    M31_pos_vector = np.array([M31_x, M31_y, M31_z])
    pos = vector_diff(M31_pos_vector, M33_pos_vector)
    if pos > apo_dist:
        apo_t = M33_data['t'][i]
        apo_dist = pos
    if pos < apo_dist:
        peri_t = M33_data['t'][i]
        peri_dist = pos

# Print the time and position values for pericenter 
# and apocenter to plot the proper snapshat.
print('Pericenter time snapshot: ' + str(peri_t))
print('Pericenter distance: ' + str(peri_dist))
print('Apocenter time snapshot: ' + str(apo_t))
print('Pericenter distance: ' + str(apo_dist))

# I'd like to density contours to analyze the shape of the halo and so 
# I used the code developed in lab 7 to setup the density contours.
def find_confidence_interval(x, pdf, confidence_level):
    return pdf[pdf > x].sum() - confidence_level

def density_contour(xdata, ydata, nbins_x, nbins_y, ax=None, **contour_kwargs):
    """ Create a density contour plot.
    Parameters
    ----------
    xdata : numpy.ndarray
    ydata : numpy.ndarray
    nbins_x : int
        Number of bins along x dimension
    nbins_y : int
        Number of bins along y dimension
    ax : matplotlib.Axes (optional)
        If supplied, plot the contour to this axis. Otherwise, open a new figure
    contour_kwargs : dict
        kwargs to be passed to pyplot.contour()
        
    Example Usage
    -------------
     density_contour(x pos, y pos, contour res, contour res, axis, colors for contours)
     e.g.:
     density_contour(xD, yD, 80, 80, ax=ax, 
         colors=['red','orange', 'yellow', 'orange', 'yellow'])

    """

    H, xedges, yedges = np.histogram2d(xdata, ydata, bins=(nbins_x,nbins_y), normed=True)
    x_bin_sizes = (xedges[1:] - xedges[:-1]).reshape((1,nbins_x))
    y_bin_sizes = (yedges[1:] - yedges[:-1]).reshape((nbins_y,1))

    pdf = (H*(x_bin_sizes*y_bin_sizes))
    
    X, Y = 0.5*(xedges[1:]+xedges[:-1]), 0.5*(yedges[1:]+yedges[:-1])
    Z = pdf.T
    fmt = {}
     
    
    # Contour Levels Definitions
    one_sigma = so.brentq(find_confidence_interval, 0., 1., args=(pdf, 0.60))
    two_sigma = so.brentq(find_confidence_interval, 0., 1., args=(pdf, 0.82))
    three_sigma = so.brentq(find_confidence_interval, 0., 1., args=(pdf, 0.90))

    # Array of Contour levels. Adjust according to the above
    levels = [one_sigma, two_sigma, three_sigma][::-1]
    
    # contour level labels  Adjust accoding to the above.
    strs = ['0.60', '0.80', '0.90'][::-1]

    
    ###### 
    
    if ax == None:
        contour = plt.contour(X, Y, Z, levels=levels, origin="lower", **contour_kwargs)
        for l, s in zip(contour.levels, strs):
            fmt[l] = s
        plt.clabel(contour, contour.levels, inline=True, fmt=fmt, fontsize=12)

    else:
        contour = ax.contour(X, Y, Z, levels=levels, origin="lower", **contour_kwargs)
        for l, s in zip(contour.levels, strs):
            fmt[l] = s
        ax.clabel(contour, contour.levels, inline=True, fmt=fmt, fontsize=12)
    
    return contour

# Rotating the frame of the halo toward the z-axis is useful because I can hopefully
# more easily calaculate the axes of the ellipsoid to understand the shape. 
def RotateFrame(posI,velI):
    """a function that will rotate the position and velocity vectors
    so that the disk angular momentum is aligned with z axis. 
    
    PARAMETERS
    ----------
        posI : `array of floats`
             3D array of positions (x,y,z)
        velI : `array of floats`
             3D array of velocities (vx,vy,vz)
             
    RETURNS
    -------
        pos: `array of floats`
            rotated 3D array of positions (x,y,z) such that disk is in the XY plane
        vel: `array of floats`
            rotated 3D array of velocities (vx,vy,vz) such that disk angular momentum vector
            is in the +z direction 
    """
    
    # compute the angular momentum
    L = np.sum(np.cross(posI,velI), axis=0)
    # normalize the vector
    L_norm = L/np.sqrt(np.sum(L**2))


    # Set up rotation matrix to map L_norm to z unit vector (disk in xy-plane)
    
    # z unit vector
    z_norm = np.array([0, 0, 1])
    
    # cross product between L and z
    vv = np.cross(L_norm, z_norm)
    s = np.sqrt(np.sum(vv**2))
    
    # dot product between L and z 
    c = np.dot(L_norm, z_norm)
    
    # rotation matrix
    I = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    v_x = np.array([[0, -vv[2], vv[1]], [vv[2], 0, -vv[0]], [-vv[1], vv[0], 0]])
    R = I + v_x + np.dot(v_x, v_x)*(1 - c)/s**2

    # Rotate coordinate system
    pos = np.dot(R, posI.T).T
    vel = np.dot(R, velI.T).T
    
    return pos, vel

# Below I've created a function that uses the particle coordinate
# data to plot a "covidence" ellipse which will be used to estimate
# the shape of the halo. The function can scale the horizontal and 
# vertical radii to match the contour lines. This is so that the 
# shape is fitted to the highest density of particles and thus the 
# closest shape of the halo. 

def ellipse(horizontal, vertical, h_scale=1.0, v_scale=1.0):
    """
    The purpose of this function is to create the horizontal
    and vetical radii of an ellipse according to the data points 
    of the halo particles. It will be used to plot and determine
    the shape of the halo.  
    
    PARAMETERS
    ----------
        horizontal : `np.array`
             The horizontal data points of the halo. 
        vertical : `np.array`
             The vertical data points of the halo.
        h_scale: 'float'
            The scale factor by which the horizontal coordinates 
            should be scaled by 
        v_scale: 'float'
            The scale factor by which the vertical coordinates 
            should be scaled by
        n: 'float'
            Size of the ellipse which corresponds to the number
            of desired standard deviations
             
    RETURNS
    -------
        h_coord: `np.array`
            The horizontal coordinates of the ellipse 
        v_coord: 'np.array'
            The vertical coordinates of the ellipse 
    """
    h_mean = sum(horizontal)/len(horizontal)
    v_mean = sum(vertical)/len(vertical)
    N = len(horizontal)
    h_std = np.std(horizontal)
    v_std = np.std(vertical)
    cov = sum((horizontal-h_mean)*(vertical-v_mean))/N
    p = cov/(h_std*v_std)
    h_radii = np.sqrt(1+p)
    v_radii = np.sqrt(1-p)
    h_radii = h_radii*(2*h_scale*h_std)
    v_radii = v_radii*(2*v_scale*v_std)
    angles = np.linspace(0, 2*np.pi, 200)
    h_coord = h_radii*np.cos(angles)
    v_coord = v_radii*np.sin(angles)
    return h_coord, v_coord




# Create a COM of object for M33
# try snapshot 795 for pericenter
# try snapshot 185 for apocenter
M33_COM = CenterOfMass('M33_VLowRes/M33_185.txt', 1.0)

# Compute COM of M33 using halo particles
M33_COM_pos = M33_COM.COM_P(0.1, 4)
M33_COM_vel = M33_COM.COM_V(M33_COM_pos[0],
                            M33_COM_pos[1],
                            M33_COM_pos[2])
# Set up the coordinates to calulate the correct positions
xH = M33_COM.x - M33_COM_pos[0].value 
yH = M33_COM.y - M33_COM_pos[1].value 
zH = M33_COM.z - M33_COM_pos[2].value
r_tot = np.sqrt(xH**2 + yH**2 + zH**2)
vxH = M33_COM.vx - M33_COM_vel[0].value 
vyH = M33_COM.vy - M33_COM_vel[1].value 
vzH = M33_COM.vz - M33_COM_vel[2].value
v_tot = np.sqrt(vxH**2 + vyH**2 + vzH**2)
r = np.array([xH,yH,zH]).T 
v = np.array([vxH,vyH,vzH]).T
# Using the coordinates calculated from the COM, rotate the 
# halo to be centered along the z-axis. 
rn, vn = RotateFrame(r, v)
# Using the ellipse function, define the horizontal and vertical 
# coordinates. Make sure that they are scaled to fit the contour 
# lines. 
x_ellipse, z_ellipse = ellipse(rn[:,0], rn[:,2], 0.40, 0.30)
y_ellipse, z_ellipse = ellipse(rn[:,1], rn[:,2], 0.45, 0.40)

# plot the particle density and contour fitting lines
fig, (ax1, ax2)= plt.subplots(1, 2, figsize=(10, 5))
ax1.set_xlabel('x', fontsize=12)
ax1.set_ylabel('z', fontsize=12)
ax1.hist2d(rn[:,0], rn[:,2], bins=600, norm=LogNorm(), cmap='viridis')
density_contour(rn[:,0], rn[:,2], 80, 80, ax=ax1, colors=['black', 'red', 'white'])
ax1.plot(x_ellipse-100, z_ellipse, color='orange')
ax1.set_ylim(-500,500)
ax1.set_xlim(-500,500)
#######################
ax2.set_xlabel('y', fontsize=12)
ax2.hist2d(rn[:,1], rn[:,2], bins=600, norm=LogNorm(), cmap='viridis')
density_contour(rn[:,1], rn[:,2], 80, 80, ax=ax2, colors=['black', 'red', 'white'])
ax2.plot(y_ellipse, z_ellipse, color='orange')
ax2.set_ylim(-500,500)
ax2.set_xlim(-500,500)

label_size = 12
matplotlib.rcParams['xtick.labelsize'] = label_size 
matplotlib.rcParams['ytick.labelsize'] = label_size

# %%
