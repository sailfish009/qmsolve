import numpy as np
from scipy.sparse import diags
from scipy.sparse import kron
from scipy.sparse import eye
from .particle_system import ParticleSystem
from ..util.constants import *
from .. import Eigenstates

class SingleParticle(ParticleSystem):
    def __init__(self, m = m_e, spin = None):
        """
        N: number of grid points
        extent: spacial extent, measured in angstroms
        """
        self.m = m
        self.spin = spin


    def get_observables(self, H):

        if H.spatial_ndim ==1:
            self.x = np.linspace(-H.extent/2, H.extent/2, H.N)
            H.ndim = 1

        elif H.spatial_ndim ==2:
            x = np.linspace(-H.extent/2, H.extent/2, H.N)
            y = np.linspace(-H.extent/2, H.extent/2, H.N)
            self.x, self.y = np.meshgrid(x,y)
            H.ndim = 2


        elif H.spatial_ndim ==3:
            self.x, self.y, self.z  = np.mgrid[ -H.extent/2: H.extent/2:H.N*1j, -H.extent/2: H.extent/2:H.N*1j, -H.extent/2: H.extent/2:H.N*1j]
            H.ndim = 3

    def build_matrix_operators(self, H):

        if H.spatial_ndim == 1:
            self.x = np.linspace(-H.extent/2, H.extent/2, H.N)
            diff_x =  diags([-1., 0., 1.], [-1, 0, 1] , shape=(H.N, H.N))*1/(2*H.dx)
            self.px = - hbar *1j * diff_x
            H.ndim = 1
            self.I = eye(H.N)


        elif H.spatial_ndim == 2:
            x = diags([np.linspace(-H.extent/2, H.extent/2, H.N)], [0])
            y = diags([np.linspace(-H.extent/2, H.extent/2, H.N)], [0])
            I = eye(H.N)

            self.x = kron(I,x)
            self.y = kron(y,I)

            diff_x =  diags([-1., 0., 1.], [-1, 0, 1] , shape=(H.N, H.N))*1/(2*H.dx)
            diff_y = diags([-1., 0., 1.], [-1, 0, 1] , shape=(H.N, H.N))*1/(2*H.dx)

            self.px = kron(I, - hbar *1j * diff_y)
            self.py = kron(- hbar *1j * diff_x, I)
            H.ndim = 2
            self.I = kron(I,I)

        elif H.spatial_ndim == 3:
            raise NotImplementedError()

    def get_kinetic_matrix(self, H):

        I = eye(H.N)
        T_ =  diags([-2., 1., 1.], [0,-1, 1] , shape=(H.N, H.N))*-k/(self.m*H.dx**2)
        if H.spatial_ndim ==1:
            T = T_

        elif H.spatial_ndim ==2:
            T =  kron(T_,I) + kron(I,T_)

        elif H.spatial_ndim ==3:
            T =  kron(T_, kron(I, I)) + kron(I, kron(T_, I)) + kron(I, kron(I, T_))

        return T

    def get_eigenstates(self, H, max_states, eigenvalues, eigenvectors):

        energies = eigenvalues
        eigenstates_array = np.moveaxis(eigenvectors.reshape(  *[H.N]*H.ndim , max_states), -1, 0)

        # Finish the normalization of the eigenstates
        eigenstates_array = eigenstates_array/np.sqrt(H.dx**H.ndim)

        if H.spatial_ndim == 1:
            type = "SingleParticle1D"
        elif H.spatial_ndim == 2:
            type = "SingleParticle2D"
        elif H.spatial_ndim == 3:
            type = "SingleParticle3D"

        eigenstates = Eigenstates(energies/eV, eigenstates_array, H.extent, H.N, type)
        return eigenstates