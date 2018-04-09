from opensbli.core.grid import Grid
from sympy import pprint, Equality
from opensbli.core.bcs import BoundaryConditionTypes
from opensbli.core.opensbliobjects import ConstantObject, DataObject, DataSetBase, GroupedCondition, GroupedPiecewise, DataSet
from opensbli.core.opensbliequations import ConstituentRelations
from opensbli.core.metrics import MetricsEquation
from sympy import flatten, eye, srepr


class DataSetsToDeclare(object):
    """Remove this we are not using it any more
    """
    datasetbases = []


class KernelCounter():
    """Counter for the kernels
    """

    def __init__(self):
        self.kernel_counter = 0
        self.stored_counter = 0

    @property
    def reset_kernel_counter(self):
        """
        """
        self.kernel_counter = 0
        return

    @property
    def increase_kernel_counter(self):
        """
        """
        self.kernel_counter = self.kernel_counter + 1
        return

    @property
    def store_kernel_counter(self):
        """
        """
        self.stored_counter = self.kernel_counter
        return

    @property
    def reset_kernel_to_stored(self):
        """
        """
        self.kernel_counter = self.stored_counter
        return


class SimulationBlock(Grid, KernelCounter, BoundaryConditionTypes):  # BoundaryConditionTypes add this later
    """
    """

    def __init__(self, ndim, block_number=None):
        if block_number:
            self.__blocknumber = block_number
        else:
            self.__blocknumber = 0
        self.ndim = ndim
        KernelCounter.__init__(self)
        Grid.__init__(self)
        # RationalCounter.__init__(self)
        self.boundary_halos = [[set(), set()] for d in range(self.ndim)]
        self.block_datasets = {}
        self.constants = {}
        self.Rational_constants = {}
        self.block_stencils = {}
        self.InputOutput = []
        return

    @property
    def blockname(self):
        """
        """
        return 'opensbliblock%02d' % self.blocknumber

    @property
    def blocknumber(self):
        return self.__blocknumber

    @blocknumber.setter
    def blocknumber(self, number):
        self.__blocknumber = number
        return

    def set_block_boundaries(self, bclist):
        """
        """
        self.set_boundary_types(bclist, self)
        # Convert the equations into block datasets
        # for b in flatten(self.boundary_types):
        #     if b.equations:
        #         b.equations = self.dataobjects_to_datasets_on_block(b.equations)
                # print srepr(b.equations[0].lhs)
        # for b in bcli
        # for eq in self.list_of_equation_classes:
        #     block_eq = self.dataobjects_to_datasets_on_block(eq.equations)
        #     eq.equations = block_eq
        return

    def set_block_boundary_halos(self, direction, side, types):
        """
        """
        self.boundary_halos[direction][side].add(types)
        return

    def dataobjects_to_datasets_on_block(self, eqs):
        """
        """
        store_equations = flatten(eqs)[:]
        consts = set()

        for no, eq in enumerate(store_equations):
            if isinstance(eq, Equality):
                consts = consts.union(eq.atoms(ConstantObject))
                for d in eq.atoms(DataObject):
                    new = self.location_dataset(d)
                    eq = eq.subs({d: new})
                store_equations[no] = eq
            elif isinstance(eq, GroupedPiecewise):
                # Update equation DataObjects to DataSets
                for index, list_of_eqn in enumerate(eq.grouped_equations):
                    for eqn_no, equation in enumerate(list_of_eqn):
                        consts = consts.union(equation.atoms(ConstantObject))
                        for d in equation.atoms(DataObject):
                            new = self.location_dataset(str(d))
                            equation = equation.subs({d: new})
                        list_of_eqn[eqn_no] = equation
                    eq.grouped_equations[index] = list_of_eqn

                # Update condition DataObjects to DataSets
                for index, condition in enumerate(eq.grouped_conditions):
                    consts = consts.union(condition.atoms(ConstantObject))
                    for d in condition.atoms(DataObject):
                        new = self.location_dataset(str(d))
                        condition = condition.subs(d, new)
                    eq.grouped_conditions[index] = condition
                store_equations[no] = eq
            elif isinstance(eq, DataObject):
                # pprint(eq)
                store_equations[no] = self.location_dataset(str(eq))
            else: # Integers and Floats from Eigensystem entering here
                pass
        # Convert all equations into the format of input equations WARNING crude way
        out = []
        out_loc = 0
        for no, e in enumerate(eqs):
            if isinstance(e, list):
                out += [store_equations[out_loc:out_loc+len(e)]]
                out_loc += len(e)
            else:
                out += [store_equations[out_loc]]
                out_loc += 1
        # Add
        from .kernel import ConstantsToDeclare as CTD
        for c in consts:
            CTD.add_constant(c)
        return out

    def copy_block_attributes(self, otherclass):
        """
        Move this to block
        """
        otherclass.block_number = self.blocknumber
        otherclass.ndim = self.ndim
        otherclass.block_name = self.blockname
        return
    
    @property
    def known_datasets(self):
        known_dsets = set()
        for eq in self.list_of_equation_classes:
            known_dsets = known_dsets.union(eq.evaluated_datasets)
        for io in self.InputOutput:
            known_dsets = known_dsets.union(io.evaluated_datasets)
        return known_dsets

    def discretise(self):
        """
        In this the discretisation of the schemes in the list of equations is applied
        :arg list_of_equations: a list of the type of equations (simulation equations, Constituent relations,
        Metric equations, diagnostic equations etc)
        : ar
        """

        # perform the spatial discretisation of the equations using schemes
        for eq in self.list_of_equation_classes:
            eq.spatial_discretisation(self)
            eq.apply_boundary_conditions(self)
        # Get the classes for the constituent relations
        # for clas in self.list_of_equation_classes:
        # if clas not in crs:
        # print clas, "Exitting"
        # exit()
        # perform the temporal discretisation of the equations for all equation classes
        # Later move TD to equations.td
        temporal = self.get_temporal_schemes
        for t in temporal:
            for eq in self.list_of_equation_classes:
                self.discretisation_schemes[t.name].discretise(eq, self)
        for io in self.InputOutput:
            io.set_read_from_hdf5_arrays(self)
        return

    def create_datasetbase(self, name):
        return DataSetBase(str(name), self.shape, self.blocknumber)

    def location_dataset(self, name):
        if isinstance(name, DataSetBase):
            return name[name.location]
        else:
            base = self.create_datasetbase(name)
            return base[base.location]

    def apply_boundary_conditions(self, arrays):
        """
        """
        kernels = []
        for no, b in enumerate(self.boundary_types):
            for side in [0,1]:
                k = self.apply_bc_direction(no, side, arrays)
                if isinstance(k, list):
                    kernels += k
                else:
                    kernels += [k]
        return kernels

    def apply_bc_direction(self, direction, side, arrays):
        """
        """
        kernel = self.boundary_types[direction][side].apply(arrays, self)
        return kernel

    def set_equations(self, list_of_equations):
        """
        """
        self.list_of_equation_classes = list_of_equations
        # Convert the equations into block datasets
        for eq in self.list_of_equation_classes:
            block_eq = self.dataobjects_to_datasets_on_block(eq.equations)
            eq.equations = block_eq
        self.sort_equation_classes
        return

    @property
    def sort_equation_classes(self):
        for no, eq in enumerate(self.list_of_equation_classes):
            if isinstance(eq, ConstituentRelations):
                cr = self.list_of_equation_classes.pop(no)
                self.list_of_equation_classes.insert(0, cr)
        return

    def set_discretisation_schemes(self, schemes):
        """
        """
        self.discretisation_schemes = schemes
        return

    @property
    def get_constituent_equation_class(self):
        """
        """
        CR_classes = []
        for sc in self.list_of_equation_classes:
            if isinstance(sc, ConstituentRelations):
                CR_classes += [sc]
        return CR_classes

    @property
    def get_temporal_schemes(self):
        """
        """
        temporal = []
        for sc in self.discretisation_schemes:
            if self.discretisation_schemes[sc].schemetype == "Temporal":
                temporal += [self.discretisation_schemes[sc]]
        return temporal

    @property
    def collect_all_spatial_kernels(self):
        """
        """
        all_kernels = []
        for scheme in self.get_temporal_schemes:
            for key, value in scheme.solution.iteritems():  # These are equation classes
                if key.order >= 0 and key.order < 100:  # Checks if the equation classes are part of the time loop
                    all_kernels += key.all_spatial_kernels
                else:
                    print 'NOPE'  # Just checking
        return all_kernels

    def setio(self, list_of_ios):
        """
        """
        self.add_io(list_of_ios)
        return

    def add_io(self, list_of_ios):
        """
        """
        if isinstance(list_of_ios, list):
            self.InputOutput += list_of_ios
        else:
            self.InputOutput += [list_of_ios]
        for io in self.InputOutput:
            io.arrays = self.dataobjects_to_datasets_on_block(io.arrays)
        return

    def add_metric(self, metric_params):
        """
        """
        self.metric_transformations = metric_params
        return

    def get_all_scheme_halos(self):
        """
        """
        spatialschemes = []
        for sc in self.discretisation_schemes:
            if self.discretisation_schemes[sc].schemetype == "Spatial":
                spatialschemes += [self.discretisation_schemes[sc]]
        from opensbli.core.scheme import CentralHalos_defdec
        halos = set([CentralHalos_defdec()])
        # for s in spatialschemes:
        # CentralHalos_defdec()
        # halos.add(s.halotype)
        return halos
    
    @property
    def get_metric_class(self):
        metric_class = []
        for EqClass in self.list_of_equation_classes:
            if isinstance(EqClass, MetricsEquation):
                metric_class += [EqClass]
        if len(metric_class) == 0:
            return None
        if len(metric_class) > 1:
            raise ValueError("more than one metric class found in the equations")
        else:
            return metric_class[0]

    @property
    def fd_metrics(self):
        metric = self.get_metric_class
        if metric:
            fn = lambda x: self.dataobjects_to_datasets_on_block([x])[0]
            return metric.FD_metrics.applyfunc(fn)
        else:
            return eye(self.ndim)

def sort_constants(constants_dictionary):
    """
    """
    known_constants, unknown_constants = [], []
    pprint(constants_dictionary)
    for const in constants_dictionary.values():
        if const.is_input:
            known_constants.append(const)
        else:
            unknown_constants.append(const)
    while len(unknown_constants) != 0:
        set_of_known = set(known_constants)
        for const in unknown_constants:
            requires = const.value.atoms(ConstantObject)
            if requires.issubset(set_of_known):
                print "const: ", const, " has formula: ", const.value, " requires: ", requires
                known_constants.append(const)
                unknown_constants = [x for x in unknown_constants if not const]
            else:
                print const, "is missing", " it requires", requires
    return known_constants
