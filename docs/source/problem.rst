Defining and Running a Problem
==============================

Problem setup
-------------
Essentially, OpenSBLI comprises the following classes and modules (emboldened below), which define the abstraction employed:

* A **Problem** defines the physical problem's dimension, the equations that must be solved, and any accompanying formulas, constants, etc.
* This Problem comprises many **Equations** representing the governing model equations and any constitutive formulas that need to be solved for. The Problem also performs the expansion on these equations and formulas about the Einstein indices.
* Once the equations are expanded, a numerical **Grid** of solution points and numerical **Scheme** s are created in order to discretise the expanded equations. Several Schemes are available, such as **RungeKutta** and **Explicit** for time-stepping schemes, and **Central** for central differencing in space. The spatial and temporal discretisation is handled by the **SpatialDiscretisation** and **TemporalDiscretisation** classes, respectively.
* The setting of any boundary conditions and initial conditions are handled by the **BoundaryConditions** and **GridBasedInitialisation** classes.
* The computational steps performed by the discretisation processes are described by a series of **Kernel** objects.
* All of the above classes come together to form a computational system which is written out as **OPSC** code.
* All LaTeX writing (mainly for debugging purposes) is handled by the **LatexWriter** class.

OpenSBLI will expect all these problem-specific settings and configurations (the governing equations, any constitutive formulas for e.g. temperature-dependent viscosity, what time-stepping scheme is to be used, the boundary conditions, etc.) to be defined in a separate Python script, which will eventually call the various OpenSBLI code generation routines. There are several examples provided in the applications (``apps``) directory of the OpenSBLI package.

Equation specification
----------------------
Although the equations can be specified at a very abstract level in Einstein notation, certain rules are to be followed while writing them:

* All equations are written in the form ``Eq(LHS,RHS)``, where ``LHS`` is the time dependant term in the equation and ``RHS`` are the terms of the equations that are equated to the time dependant governing equation.
* The Einstein indices should be prefixed with an underscore (_) and multiple indices should have multiple underscores. For example, a vector is written as ``f_i`` and a tensor is written as ``f_i_j``.
* Derivatives that do not require special handling (e.g. single functions, chain rule applications for multiple derivatives) should be written in the form ``Der(f,direction)``, where ``f`` is the function and ``direction`` is the direction.
* Derivatives involving more than one function that needs special handling like the conservative or skew-symmetric forms of the Navier-Stokes equations are handled using ``Conservative`` or ``Skew``, respectively.
* OpenSBLI can handle all standard functions in SymPy (i.e. Kronecker Delta and Levi-Civita terms).

Generating and compiling the model code
---------------------------------------
Once defined, users can run the Python script defining the problem's configuration and generate the code for this particular problem:

.. code-block:: bash

    python /path/to/directory/containing/problem_file.py

OpenSBLI will create two files written in the OPSC language: ``simulation_name_here_block_0_kernel.h`` and ``simulation_name_here.cpp``. The latter file will automatically be passed through OPS's translator to target the OPSC code towards different backends, e.g. CUDA, MPI, OpenMP, etc; this yields a new file called ``simulation_name_here_ops.cpp`` and various directories corresponding to the different backends. It is this file that will be compiled to create the model's executable file. Note that, if OPS's translator cannot be called by OpenSBLI, you will need to run it manually using

.. code-block:: bash

    python ~/OPS/translator/python/c/ops.py simulation_name_here.cpp

Finally, copy across the ``Makefile`` from one of the existing ``apps``, and modify the simulation name appropriately so that it will compile the source for your simulation setup. To create a serial executable, run ``make simulation_name_here_seq``. For MPI parallel executution, run ``make simulation_name_here_mpi``. Similar commands can be run for GPU backends.
