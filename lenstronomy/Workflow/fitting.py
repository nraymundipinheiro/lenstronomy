__author__ = 'sibirrer'

import numpy as np

from lenstronomy.MCMC.mcmc import MCMCSampler
from lenstronomy.MCMC.reinitialize import ReusePositionGenerator
from lenstronomy.Workflow.parameters import Param


class Fitting(object):
    """
    class to find a good estimate of the parameter positions and uncertainties to run a (full) MCMC on
    """

    def __init__(self, multi_band_list, kwargs_model, kwargs_constraints, kwargs_likelihood, kwargs_fixed, kwargs_lower,
                 kwargs_upper):
        """

        :return:
        """
        self.kwargs_fixed = kwargs_fixed
        self.multi_band_list = multi_band_list
        self.kwargs_model = kwargs_model
        self.kwargs_constraints = kwargs_constraints
        self.kwargs_likelihood = kwargs_likelihood
        self.kwargs_lower = kwargs_lower
        self.kwargs_upper = kwargs_upper

    def _set_priors(self, mean_list_kwargs, sigma_list_kwargs):
        """

        :param mean_list_kwargs:
        :param sigma_list_kwargs:
        :return:
        """
        prior_list = []
        for k in range(len(mean_list_kwargs)):
            prior_k = mean_list_kwargs[k].copy()
            prior_k.update(sigma_list_kwargs[k])
            prior_list.append(prior_k)
        return prior_list

    def _run_pso(self, n_particles, n_iterations,
                 kwargs_fixed_lens, kwargs_mean_lens, kwargs_sigma_lens,
                 kwargs_fixed_source, kwargs_mean_source, kwargs_sigma_source,
                 kwargs_fixed_lens_light, kwargs_mean_lens_light, kwargs_sigma_lens_light,
                 kwargs_fixed_ps, kwargs_mean_ps, kwargs_sigma_ps,
                 threadCount=1, mpi=False, print_key='Default', sigma_factor=1, compute_bool=None):

        kwargs_prior_lens = self._set_priors(kwargs_mean_lens, kwargs_sigma_lens)
        kwargs_prior_source = self._set_priors(kwargs_mean_source, kwargs_sigma_source)
        kwargs_prior_lens_light = self._set_priors(kwargs_mean_lens_light, kwargs_sigma_lens_light)
        kwargs_prior_ps = self._set_priors(kwargs_mean_ps, kwargs_sigma_ps)

        # initialise mcmc classes
        param_class = Param(self.kwargs_model, self.kwargs_constraints, kwargs_fixed_lens, kwargs_fixed_source,
                            kwargs_fixed_lens_light, kwargs_fixed_ps, kwargs_lens_init=kwargs_mean_lens)
        mean_start, sigma_start = param_class.param_init(kwargs_prior_lens, kwargs_prior_source,
                                                         kwargs_prior_lens_light, kwargs_prior_ps)
        lowerLimit = np.array(mean_start) - np.array(sigma_start)*sigma_factor
        upperLimit = np.array(mean_start) + np.array(sigma_start)*sigma_factor
        num_param, param_list = param_class.num_param()
        init_pos = param_class.setParams(kwargs_mean_lens, kwargs_mean_source,
                                         kwargs_mean_lens_light, kwargs_mean_ps)
        # run PSO
        kwargs_fixed = [kwargs_fixed_lens, kwargs_fixed_source, kwargs_fixed_lens_light, kwargs_fixed_ps]
        mcmc_class = MCMCSampler(self.multi_band_list, self.kwargs_model, self.kwargs_constraints,
                                 self.kwargs_likelihood, kwargs_fixed, self.kwargs_lower, self.kwargs_upper,
                                 kwargs_lens_init=kwargs_mean_lens, compute_bool=compute_bool)
        lens_result, source_result, lens_light_result, else_result, chain = mcmc_class.pso(n_particles,
                                                                                                       n_iterations,
                                                                                                       lowerLimit,
                                                                                                       upperLimit,
                                                                                                       init_pos=init_pos,
                                                                                                       threadCount=threadCount,
                                                                                                       mpi=mpi,
                                                                                                       print_key=print_key)
        return lens_result, source_result, lens_light_result, else_result, chain, param_list

    def _update_fixed_simple(self, kwargs_lens, kwargs_source, kwargs_lens_light, kwargs_ps, fix_lens=False,
                             fix_source=False, fix_lens_light=False, fix_point_source=False, gamma_fixed=False):
        if fix_lens:
            add_fixed_lens = kwargs_lens
        else:
            add_fixed_lens = None
        if fix_source:
            add_fixed_source = kwargs_source
        else:
            add_fixed_source = None
        if fix_lens_light:
            add_fixed_lens_light = kwargs_lens_light
        else:
            add_fixed_lens_light = None
        if fix_point_source:
            add_fixed_ps = kwargs_ps
        else:
            add_fixed_ps = None
        kwargs_fixed_lens, kwargs_fixed_source, kwargs_fixed_lens_light, kwargs_fixed_ps = self._update_fixed(
            add_fixed_lens=add_fixed_lens, add_fixed_source=add_fixed_source, add_fixed_lens_light=add_fixed_lens_light,
            add_fixed_ps=add_fixed_ps)
        if gamma_fixed:
            if 'gamma' in kwargs_lens[0]:
                kwargs_fixed_lens[0]['gamma'] = kwargs_lens[0]['gamma']
        return kwargs_fixed_lens, kwargs_fixed_source, kwargs_fixed_lens_light, kwargs_fixed_ps

    def _update_fixed(self, add_fixed_lens=None, add_fixed_source=None,
                      add_fixed_lens_light=None, add_fixed_ps=None):

        lens_fix, source_fix, lens_light_fix, ps_fix = self.kwargs_fixed

        if add_fixed_lens is None:
            kwargs_fixed_lens_updated = lens_fix
        else:
            kwargs_fixed_lens_updated = []
            for k in range(len(lens_fix)):
                kwargs_fixed_lens_updated_k = add_fixed_lens[k].copy()
                kwargs_fixed_lens_updated_k.update(lens_fix[k])
                kwargs_fixed_lens_updated.append(kwargs_fixed_lens_updated_k)
        if add_fixed_source is None:
            kwargs_fixed_source_updated = source_fix
        else:
            kwargs_fixed_source_updated = []
            for k in range(len(source_fix)):
                kwargs_fixed_source_updated_k = add_fixed_source[k].copy()
                kwargs_fixed_source_updated_k.update(source_fix[k])
                kwargs_fixed_source_updated.append(kwargs_fixed_source_updated_k)
        if add_fixed_lens_light is None:
            kwargs_fixed_lens_light_updated = lens_light_fix
        else:
            kwargs_fixed_lens_light_updated = []
            for k in range(len(lens_light_fix)):
                kwargs_fixed_lens_light_updated_k = add_fixed_lens_light[k].copy()
                kwargs_fixed_lens_light_updated_k.update(lens_light_fix[k])
                kwargs_fixed_lens_light_updated.append(kwargs_fixed_lens_light_updated_k)
        kwargs_fixed_ps_updated = []
        if add_fixed_ps is None:
            kwargs_fixed_ps_updated = ps_fix
        else:
            for k in range(len(ps_fix)):
                kwargs_fixed_ps_updated_k = add_fixed_ps[k].copy()
                kwargs_fixed_ps_updated_k.update(ps_fix[k])
                kwargs_fixed_ps_updated.append(kwargs_fixed_ps_updated_k)
        return kwargs_fixed_lens_updated, kwargs_fixed_source_updated, kwargs_fixed_lens_light_updated, kwargs_fixed_ps_updated

    def _mcmc_run(self, n_burn, n_run, walkerRatio,
                 kwargs_fixed_lens, kwargs_mean_lens, kwargs_sigma_lens,
                 kwargs_fixed_source, kwargs_mean_source, kwargs_sigma_source,
                 kwargs_fixed_lens_light, kwargs_mean_lens_light, kwargs_sigma_lens_light,
                 kwargs_fixed_else, kwargs_mean_ps, kwargs_sigma_ps,
                 threadCount=1, mpi=False, init_samples=None, sigma_factor=1, compute_bool=None):

        kwargs_prior_lens = self._set_priors(kwargs_mean_lens, kwargs_sigma_lens)
        kwargs_prior_source = self._set_priors(kwargs_mean_source, kwargs_sigma_source)
        kwargs_prior_lens_light = self._set_priors(kwargs_mean_lens_light, kwargs_sigma_lens_light)
        kwargs_prior_ps = self._set_priors(kwargs_mean_ps, kwargs_sigma_ps)
        # initialise mcmc classes

        param_class = Param(self.kwargs_model, self.kwargs_constraints, kwargs_fixed_lens, kwargs_fixed_source,
                            kwargs_fixed_lens_light, kwargs_fixed_else, kwargs_lens_init=kwargs_mean_lens)
        kwargs_fixed = kwargs_fixed_lens, kwargs_fixed_source, kwargs_fixed_lens_light, kwargs_fixed_else
        mcmc_class = MCMCSampler(self.multi_band_list, self.kwargs_model, self.kwargs_constraints,
                                 self.kwargs_likelihood, kwargs_fixed, self.kwargs_lower, self.kwargs_upper,
                                 kwargs_lens_init=kwargs_mean_lens, compute_bool=compute_bool)
        mean_start, sigma_start = param_class.param_init(kwargs_prior_lens, kwargs_prior_source,
                                                         kwargs_prior_lens_light, kwargs_prior_ps)
        num_param, param_list = param_class.num_param()
        # run MCMC
        if not init_samples is None:
            initpos = ReusePositionGenerator(init_samples)
        else:
            initpos = None

        samples, dist = mcmc_class.mcmc_CH(walkerRatio, n_run, n_burn, mean_start, np.array(sigma_start)*sigma_factor, threadCount=threadCount,
                                           mpi=mpi, init_pos=initpos)
        return samples, param_list, dist

    def pso_run(self, kwargs_lens, kwargs_source, kwargs_lens_light, kwargs_ps,
                kwargs_lens_sigma, kwargs_source_sigma, kwargs_lens_light_sigma, kwargs_ps_sigma,
                n_particles, n_iterations, mpi=False, threadCount=1, sigma_factor=1, gamma_fixed=False,
                compute_bool=None, fix_lens=False, fix_source=False, fix_lens_light=False, fix_point_source=False,
                print_key='find_model'):
        """
        finds lens light and lens model combined fit
        :return: constraints of lens model
        """
        kwargs_fixed_lens, kwargs_fixed_source, kwargs_fixed_lens_light, kwargs_fixed_ps = self._update_fixed_simple(
            kwargs_lens, kwargs_source, kwargs_lens_light, kwargs_ps, fix_lens=fix_lens, fix_source=fix_source,
            fix_lens_light=fix_lens_light, fix_point_source=fix_point_source, gamma_fixed=gamma_fixed)
        lens_result, source_result, lens_light_result, else_result, chain, param_list = self._run_pso(
            n_particles, n_iterations,
            kwargs_fixed_lens, kwargs_lens, kwargs_lens_sigma,
            kwargs_fixed_source, kwargs_source, kwargs_source_sigma,
            kwargs_fixed_lens_light, kwargs_lens_light, kwargs_lens_light_sigma,
            kwargs_fixed_ps, kwargs_ps, kwargs_ps_sigma,
            threadCount=threadCount, mpi=mpi, print_key=print_key, sigma_factor=sigma_factor, compute_bool=compute_bool)
        return lens_result, source_result, lens_light_result, else_result, chain, param_list

    def mcmc_run(self, kwargs_lens, kwargs_source, kwargs_lens_light, kwargs_ps,
                 kwargs_lens_sigma, kwargs_source_sigma, kwargs_lens_light_sigma, kwargs_ps_sigma,
                 n_burn, n_run, walkerRatio, threadCount=1, mpi=False, init_samples=None, sigma_factor=1,
                 gamma_fixed=False, compute_bool=None, fix_lens=False, fix_source=False, fix_lens_light=False,
                 fix_point_source=False):
        """
        MCMC
        """
        kwargs_fixed_lens, kwargs_fixed_source, kwargs_fixed_lens_light, kwargs_fixed_ps = self._update_fixed_simple(
            kwargs_lens, kwargs_source, kwargs_lens_light, kwargs_ps, fix_lens=fix_lens, fix_source=fix_source,
            fix_lens_light=fix_lens_light, fix_point_source=fix_point_source, gamma_fixed=gamma_fixed)

        samples, param_list, dist = self._mcmc_run(
            n_burn, n_run, walkerRatio,
            kwargs_fixed_lens, kwargs_lens, kwargs_lens_sigma,
            kwargs_fixed_source, kwargs_source, kwargs_source_sigma,
            kwargs_fixed_lens_light, kwargs_lens_light, kwargs_lens_light_sigma,
            kwargs_fixed_ps, kwargs_ps, kwargs_ps_sigma,
            threadCount=threadCount, mpi=mpi, init_samples=init_samples, sigma_factor=sigma_factor, compute_bool=compute_bool)
        return samples, param_list, dist
