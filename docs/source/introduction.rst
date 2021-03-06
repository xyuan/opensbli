Introduction
============

Overview
--------

`OpenSBLI <https://github.com/opensbli/opensbli>`_ is an automatic code generator that expands a set of equations written in Einstein notation, and automatically generates code (in the OPSC language) which performs the finite difference approximation to obtain a solution. This OPSC code can then be targetted with the `OPS library <http://www.oerc.ox.ac.uk/projects/ops>`_ towards specific hardware backends, such as MPI/OpenMP for execution on CPUs, and CUDA/OpenCL for execution on GPUs.

The main focus of OpenSBLI is on the solution of the compressible Navier-Stokes equations with application to shock-boundary layer interactions (SBLI). However, in principle, any set of equations that can be written in Einstein notation may be solved using the code generation framework. This highlights one of the main advantages of such a high-level, abstract approach to computational model development.

From an implementation perspective, the OpenSBLI codebase is written in the Python (2.7.x) language and depends on the SymPy library to process the Einstein formulation of the equations. The code generator will then write out the model code which performs the finite difference approximations in any of the supported languages (currently only OPSC, although the structure of the codebase is such that other languages can be integrated with minimal effort).

The development of OpenSBLI was supported by EPSRC grants EP/K038567/1 ("Future-proof massively-parallel execution of multi-block applications") and EP/L000261/1 ("UK Turbulence Consortium"). It was also supported by the `ExaFLOW project <http://exaflow-project.eu/>`_ (funded by the European Commission Horizon 2020 Framework grant 671571).

Licensing
---------

OpenSBLI is released as an open-source project under the `GNU General Public License <http://www.gnu.org/licenses/gpl-3.0.en.html>`_. See the file called ``LICENSE`` for more information.

Citing
------

If you use OpenSBLI, please consider citing the papers and other resources listed in the `Citing section <citing.html>`_.

Support
-------

The preferred method of reporting bugs and issues with OpenSBLI is to submit an issue via the repository's issue tracker. Users can also email the authors `Satya P. Jammy <mailto:S.P.Jammy@soton.ac.uk>`_ and `Christian T. Jacobs <mailto:C.T.Jacobs@soton.ac.uk>`_ directly.

