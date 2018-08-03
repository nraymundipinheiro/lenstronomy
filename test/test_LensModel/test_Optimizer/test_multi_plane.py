from lenstronomy.LensModel.Optimizer.optimizer import Optimizer
from lenstronomy.Util.util import sort_image_index
import numpy.testing as npt
import numpy as np
from astropy.cosmology import FlatLambdaCDM
import pytest
from time import time
from lenstronomy.LensModel.Optimizer.split_multiplane import SplitMultiplane
from lenstronomy.LensModel.lens_model import LensModel

class TestMultiPlaneOptimizer(object):

    cosmo = FlatLambdaCDM(H0=70,Om0=0.3)

    x_pos_simple,y_pos_simple = np.array([-0.45328229,  0.57461556,  0.53757501, -0.42312438]),\
                                np.array([ 0.69582971, -0.51226356,  0.37577509, -0.40245467])
    magnification_simple = np.array([2.79394452,3.28101725,2.29495699,1.63409843])*3.28101725**-1

    redshift_list_simple = [0.5,0.5]
    lens_model_list_simple = ['SPEP', 'SHEAR']
    kwargs_lens_simple = [{'theta_E': 0.7, 'center_x': 0.0, 'center_y': 0, 'e1': 0.0185665252864011, 'gamma': 2.,
                           'e2': 0.08890716633399057}, {'e1': 0.00418890660015825, 'e2': -0.02908846518073248}]

    front_halos = ['NFW', 'NFW', 'NFW', 'NFW', 'NFW','NFW']
    front_redshifts = [0.4, 0.4, 0.4, 0.44, 0.44, 0.44]
    front_args = [{'theta_Rs': 0.001, 'center_y': 0.2, 'center_x': 1.2, 'Rs': 0.13},
                  {'theta_Rs': 0.002, 'center_y': -0.2, 'center_x': 1, 'Rs': 0.11},
                  {'theta_Rs': 0.004, 'center_y': 0.12, 'center_x': -1.2, 'Rs': 0.13},
                  {'theta_Rs': 0.0001, 'center_y': 0.32, 'center_x': -0.2, 'Rs': 0.13},
                  {'theta_Rs': 0.003, 'center_y': 0.82, 'center_x': 0.78, 'Rs': 0.13},
                  {'theta_Rs': 0.008, 'center_y': 1, 'center_x': 0.75, 'Rs': 0.16}]

    main_halos = ['NFW', 'NFW', 'NFW', 'NFW', 'NFW','NFW']
    main_redshifts = [0.5]*6
    main_args = [{'theta_Rs': 0.001, 'center_y': 1.2, 'center_x': 0.2, 'Rs': 0.13},
                  {'theta_Rs': 0.002, 'center_y': -0.1, 'center_x': 0.91, 'Rs': 0.11},
                  {'theta_Rs': 0.009, 'center_y': 0.18, 'center_x': -0.42, 'Rs': 0.13},
                  {'theta_Rs': 0.0001, 'center_y': 0.42, 'center_x': -0.92, 'Rs': 0.13},
                  {'theta_Rs': 0.005, 'center_y': 0.9, 'center_x': 0.48, 'Rs': 0.13},
                  {'theta_Rs': 0.008, 'center_y': -1, 'center_x': 0.95, 'Rs': 0.16}]

    back_halos = ['NFW', 'NFW', 'NFW', 'NFW', 'NFW', 'NFW']
    back_redshifts = [0.55, 0.6, 0.6, 0.74, 0.74, 0.8]
    back_args = [{'theta_Rs': 0.004, 'center_y': 0.1, 'center_x': 1, 'Rs': 0.13},
                  {'theta_Rs': 0.001, 'center_y': 0.2, 'center_x': 0.7, 'Rs': 0.11},
                  {'theta_Rs': 0.003, 'center_y': -0.1, 'center_x': -1, 'Rs': 0.13},
                  {'theta_Rs': 0.0008, 'center_y': 0.42, 'center_x': 0.1, 'Rs': 0.13},
                  {'theta_Rs': 0.0014, 'center_y': 0.42, 'center_x': 1.08, 'Rs': 0.13},
                  {'theta_Rs': 0.006, 'center_y': 0.5, 'center_x': 0.75, 'Rs': 0.16}]

    lens_model_list_full = lens_model_list_simple + front_halos + main_halos+ back_halos
    redshift_list_full = redshift_list_simple + front_redshifts + main_redshifts + back_redshifts
    kwargs_lens_full = kwargs_lens_simple + front_args + main_args + back_args

    lens_model_simple = LensModel(lens_model_list_simple,z_source=1.5, redshift_list=redshift_list_simple, cosmo=cosmo,
                           multi_plane=True)

    lens_model_full = LensModel(lens_model_list_full, z_source=1.5, redshift_list=redshift_list_full, cosmo=cosmo,
                           multi_plane=True)

    optimizer_simple = Optimizer(x_pos_simple, y_pos_simple, magnification_target=magnification_simple, redshift_list=redshift_list_simple,
                                 lens_model_list=lens_model_list_simple, kwargs_lens=kwargs_lens_simple, multiplane=True, verbose=True,
                                 z_source=1.5,z_main=0.5,astropy_instance=cosmo,optimizer_routine='optimize_SPEP_shear')

    optimizer_subs = Optimizer(x_pos_simple, y_pos_simple, magnification_target=magnification_simple, redshift_list=redshift_list_full,
                               lens_model_list=lens_model_list_full, kwargs_lens=kwargs_lens_full, multiplane=True, verbose=True,
                               z_source=1.5,z_main=0.5,astropy_instance=cosmo,optimizer_routine='optimize_SPEP_shear')

    lensmodel_kwargs = {'z_source':1.5,'cosmo':cosmo,'multi_plane':True}


    def test_split_multi_plane_lensmodels(self):

        split = SplitMultiplane(x_pos=self.x_pos_simple, y_pos=self.y_pos_simple, full_lensmodel=self.lens_model_full,
                                lensmodel_params=self.kwargs_lens_full, interpolated=False, z_source=1.5, z_macro=0.5,
                                astropy_instance=self.cosmo, verbose=True, macro_indicies=[0,1])

        macromodel_lensmodel, macro_args, halos_lensmodel, halos_args,_ = \
            split._split_lensmodel(self.lens_model_full, self.kwargs_lens_full, z_break=0.5, macro_indicies=[0, 1])

        assert macro_args == self.kwargs_lens_simple

        assert halos_args == self.front_args+self.main_args+self.back_args

    def test_split_multiplane_rayshooting(self):

        model = self.lens_model_full

        kwargs = self.kwargs_lens_full

        split = SplitMultiplane(x_pos=self.x_pos_simple, y_pos=self.y_pos_simple, full_lensmodel=model,
                                lensmodel_params=kwargs, interpolated=False, z_source=1.5, z_macro=0.5,
                                astropy_instance=self.cosmo, verbose=True, macro_indicies=[0,1])

        betax_true, betay_true = model.ray_shooting(self.x_pos_simple, self.y_pos_simple,
                                                    kwargs)

        betax, betay = split.ray_shooting(self.x_pos_simple, self.y_pos_simple,
                                          macromodel_args=split.macro_args)
        betax_fast, betay_fast = split.ray_shooting_fast(split.macro_args)

        npt.assert_almost_equal(betax, betax_fast)
        npt.assert_almost_equal(betax_true, betax)
        npt.assert_almost_equal(betay_true, betay)
        npt.assert_almost_equal(betax_true, betax_fast)
        npt.assert_almost_equal(betay_true, betay_fast)

    def test_split_multi_plane_magnification(self):

        split = SplitMultiplane(x_pos=self.x_pos_simple, y_pos=self.y_pos_simple, full_lensmodel=self.lens_model_full,
                                lensmodel_params=self.kwargs_lens_full, interpolated=False, z_source=1.5, z_macro=0.5,
                                astropy_instance=self.cosmo, verbose=True,macro_indicies=[0,1])

        magnification_true = np.absolute(self.lens_model_full.magnification(self.x_pos_simple,
                                                                            self.y_pos_simple,self.kwargs_lens_full))
        magnification_split = split.magnification_fast(self.kwargs_lens_simple)

        npt.assert_almost_equal(magnification_true*max(magnification_true)**-1,
                                magnification_split*max(magnification_split)**-1,2)


    def test_multi_plane_simple(self):
        """

        :param tol: image position tolerance
        :return:
        """
        kwargs_lens, source, [x_image,y_image] = self.optimizer_simple.optimize(n_particles=50,n_iterations=200, restart = 2)
        index = sort_image_index(x_image, y_image, self.x_pos_simple, self.y_pos_simple)

        x_image = x_image[index]
        y_image = y_image[index]
        mags = self.optimizer_simple.optimizer_amoeba.lensModel.magnification(x_image, y_image, kwargs_lens)
        mags = np.absolute(mags)
        mags *= max(mags) ** -1

        npt.assert_almost_equal(x_image, self.x_pos_simple, decimal=3)
        npt.assert_almost_equal(y_image, self.y_pos_simple, decimal=3)
        npt.assert_array_less(np.absolute(self.magnification_simple - mags) * 0.2 ** -1, [1, 1, 1, 1])

    def test_multi_plane_subs(self,tol=0.004):
        """
        Should be a near perfect fit since the LOS model is the same used to create the data.
        :return:
        """
        t0 = time()
        kwargs_lens, source, [x_image,y_image] = self.optimizer_subs.optimize(n_particles=50,n_iterations=200, restart = 1)

        index = sort_image_index(x_image, y_image, self.x_pos_simple, self.y_pos_simple)
        x_image = x_image[index]
        y_image = y_image[index]

        mags = self.optimizer_subs.optimizer_amoeba.lensModel.magnification(x_image, y_image, kwargs_lens)
        mags = np.absolute(mags)
        mags *= max(mags) ** -1

        dx = np.absolute(x_image - self.x_pos_simple)
        dy = np.absolute(y_image - self.y_pos_simple)

        npt.assert_array_less(dx, [tol] * len(dx))
        npt.assert_array_less(dy, [tol] * len(dy))
        npt.assert_array_less(np.absolute(self.magnification_simple - mags) * 0.2 ** -1, [1, 1, 1, 1])

        t_end = time()
        T = t_end - t0
        t0 = time()

        reopt = Optimizer(self.x_pos_simple,self.y_pos_simple, magnification_target=self.magnification_simple, redshift_list=self.redshift_list_full,
                               lens_model_list=self.lens_model_list_full, kwargs_lens=self.kwargs_lens_full, multiplane=True, verbose=True,
                               z_source=1.5,z_main=0.5,astropy_instance=self.cosmo,optimizer_routine='optimize_SPEP_shear',re_optimize=True,
                          optimizer_start=self.optimizer_subs)


        kwargs_lens, source, [x_image, y_image] = reopt.optimize(n_particles=50, n_iterations=200,
                                                                               restart=1)

        index = sort_image_index(x_image, y_image, self.x_pos_simple, self.y_pos_simple)
        x_image = x_image[index]
        y_image = y_image[index]

        mags = reopt.optimizer_amoeba.lensModel.magnification(x_image, y_image, kwargs_lens)
        mags = np.absolute(mags)
        mags *= max(mags) ** -1

        dx = np.absolute(x_image - self.x_pos_simple)
        dy = np.absolute(y_image - self.y_pos_simple)

        npt.assert_array_less(dx, [tol] * len(dx))
        npt.assert_array_less(dy, [tol] * len(dy))
        npt.assert_array_less(np.absolute(self.magnification_simple - mags) * 0.2 ** -1, [1, 1, 1, 1])

        t_end = time()
        T_reopt = t_end - t0

        assert T_reopt < T

if __name__ == '__main__':
    pytest.main()

