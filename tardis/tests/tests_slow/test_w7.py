import os
import yaml
import pytest
from numpy.testing import assert_allclose
from astropy.tests.helper import assert_quantity_allclose

from tardis.atomic import AtomData
from tardis.simulation.base import Simulation
from tardis.model import Radial1DModel
from tardis.io.config_reader import Configuration


class TestW7(object):
    """
    Slow integration test for Stratified W7 setup.
    """

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def setup(self, reference, data_path, atomic_data_fname):
        """
        This method does initial setup of creating configuration and performing
        a single run of integration test.
        """
        self.config_file = os.path.join(data_path, "config_w7.yml")
        self.abundances = os.path.join(data_path, "abundances_w7.dat")
        self.densities = os.path.join(data_path, "densities_w7.dat")

        # The available config file doesn't have file paths of atom data file,
        # densities and abundances profile files as desired. We load the atom
        # data seperately and provide it to tardis_config later. For rest of
        # the two, we form dictionary from the config file and override those
        # parameters by putting file paths of these two files at proper places.
        config_yaml = yaml.load(open(self.config_file))
        config_yaml['model']['abundances']['filename'] = self.abundances
        config_yaml['model']['structure']['filename'] = self.densities

        # Load atom data file separately, pass it for forming tardis config.
        self.atom_data = AtomData.from_hdf5(atomic_data_fname)

        # Check whether the atom data file in current run and the atom data
        # file used in obtaining the reference data are same.
        # TODO: hard coded UUID for kurucz atom data file, generalize it later.
        kurucz_data_file_uuid1 = "5ca3035ca8b311e3bb684437e69d75d7"
        assert self.atom_data.uuid1 == kurucz_data_file_uuid1

        # Create a Configuration through yaml file and atom data.
        tardis_config = Configuration.from_config_dict(config_yaml, self.atom_data)

        # We now do a run with prepared config and get radial1d model.
        self.obtained_radial1d_model = Radial1DModel(tardis_config)
        simulation = Simulation(tardis_config)
        simulation.legacy_run_simulation(self.obtained_radial1d_model)

        # Get the reference data through the fixture.
        self.reference = reference

    def test_j_estimators(self):
        assert_allclose(
                self.reference['j_estimators'],
                self.obtained_radial1d_model.j_estimators)

    def test_j_blue_estimators(self):
        assert_allclose(
                self.reference['j_blue_estimators'],
                self.obtained_radial1d_model.j_blue_estimators)

        assert_quantity_allclose(
                self.reference['j_blues_norm_factor'],
                self.obtained_radial1d_model.j_blues_norm_factor)

    def test_last_line_interactions(self):
        assert_allclose(
                self.reference['last_line_interaction_in_id'],
                self.obtained_radial1d_model.last_line_interaction_in_id)

        assert_allclose(
                self.reference['last_line_interaction_out_id'],
                self.obtained_radial1d_model.last_line_interaction_out_id)

        assert_allclose(
                self.reference['last_line_interaction_shell_id'],
                self.obtained_radial1d_model.last_line_interaction_shell_id)

        assert_quantity_allclose(
                self.reference['last_line_interaction_angstrom'],
                self.obtained_radial1d_model.last_line_interaction_angstrom)

    def test_nubar_estimators(self):
        assert_allclose(
                self.reference['nubar_estimators'],
                self.obtained_radial1d_model.nubar_estimators)

    def test_ws(self):
        assert_allclose(
                self.reference['ws'],
                self.obtained_radial1d_model.ws)

    def test_luminosity_inner(self):
        assert_quantity_allclose(
                self.reference['luminosity_inner'],
                self.obtained_radial1d_model.luminosity_inner)

    def test_spectrum(self):
        assert_quantity_allclose(
                self.reference['luminosity_density_nu'],
                self.obtained_radial1d_model.spectrum.luminosity_density_nu)

        assert_quantity_allclose(
                self.reference['delta_frequency'],
                self.obtained_radial1d_model.spectrum.delta_frequency)

        assert_quantity_allclose(
                self.reference['wavelength'],
                self.obtained_radial1d_model.spectrum.wavelength)

        assert_quantity_allclose(
                self.reference['luminosity_density_lambda'],
                self.obtained_radial1d_model.spectrum.luminosity_density_lambda)

    def test_montecarlo_properties(self):
        assert_quantity_allclose(
                self.reference['montecarlo_luminosity'],
                self.obtained_radial1d_model.montecarlo_luminosity)

        assert_quantity_allclose(
                self.reference['montecarlo_virtual_luminosity'],
                self.obtained_radial1d_model.montecarlo_virtual_luminosity)

        assert_quantity_allclose(
                self.reference['montecarlo_nu'],
                self.obtained_radial1d_model.montecarlo_nu)

    def test_shell_temperature(self):
        assert_quantity_allclose(
                self.reference['t_rads'],
                self.obtained_radial1d_model.t_rads)