.. note:: Last update 02/09/2020

.. .. warning:: This guide is still work in progress. New pages are being written
..              and existing ones modified. Once the guide will reach its final
..              version, this box will disappear.

.. _case_studies:

Case studies
============

In this page we propose the model configurations used in publications.

Dal Molin et al., 2020, HESS
----------------------------

This section contains instructions for the implementation of the
semi-distributed hydrological model M02 presented in the article:

Dal Molin, M., Schirmer, M., Zappa, M., and Fenicia, F.: **Understanding**
**dominant controls on streamflow spatial variability to set up a**
**semi-distributed hydrological model: the case study of the Thur catchment**,
Hydrol. Earth Syst. Sci., 24, 1319–1345,
https://doi.org/10.5194/hess-24-1319-2020, 2020.

In this application, the Thur catchment has been divided in 10 subcatchments
and 2 hydrological response units (HRUs). Please refer to the article for the
details; here we propose only the code needed to setup a model that corresponds
to the one used in the publication.

Model structure
...............

The two HRUs are represented using the same model structure represented in the
figure.

.. image:: pics/case_studies/model_structure_thur.png
   :align: center

The structure is similar to the one of :ref:`hymod`; its conversion to
SuperflexPy is presented here

.. image:: pics/case_studies/ThurHESS2020.png
   :align: center

Note that also the temperature has been threated as a flux: this choice is not
forced by the framework but, in this particular case, where it is the first
element that needs it, this is particularly convenient. An alternative solution
would have been designing the snow reservoir in such a way that the temperature
becomes a state of the reservoir; this solution would have been preferable in
the case where the element that needed the flux was not at the beginning of the
structure.

Defining the elements
.....................

We here assume that all the elements are already existing; therefore they just
need to be imported.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 5-6, 10, 11
   :linenos:

After this, all the elements must be initialized, defining the initial state
and the parameters.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 13-15, 17-96
   :linenos:

Defining the HRUs structure
...........................

Once all the elements have been created we can connect them composing the two
HRUs.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 98-124
   :linenos:

Defining the catchments
.......................

Now that the HRUs have been created, we need to assign them to the catchments

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 126-194
   :linenos:

Note that all the catchments incorporate the information about their area that
will then be used by the network.

Not all the catchment must have all the HRUs; if an HRU is not present in a
catchment (e.g. unconsolidated in Mosnang, line 50) it can be simply omitted.

Defining the network
....................

The last step consists in creating the network that connects all the catchments
previously declared.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 196-221
   :linenos:

Running the model
.................

Now that all the components have been initialized, we can run the model.

The first step is to assign the input fluxes to the single elements. For this
we assume that the data is available as a pandas DataFrame and that the
columns are named :code:`P_name_of_the_catchment`,
:code:`T_name_of_the_catchment`, and :code:`PET_name_of_the_catchment`.

The inputs can be set using a for loop

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 253-258
   :linenos:

After this, the last thing to be done before actually running the model is
setting the time step used in the simulations. This can be done directly at
the network level and it will be set to all the components.

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 260
   :linenos:

The only thing left to do is running the model!

.. literalinclude:: model_thur_hess2020.py
   :language: python
   :lines: 262
   :linenos: