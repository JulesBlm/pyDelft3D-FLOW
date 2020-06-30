# pyDelft3D-FLOW

pyDelft3D-FLOW is a small Python package that were developed to help with 1) reading and writing of several input files of a [Delft3D4-FLOW model](https://oss.deltares.nl/documents/183920/185723/Delft3D-FLOW_User_Manual.pdf), 2) auto-generating multiple successive runs, 3) (interactive) plotting of the Delft3D-FLOW output (NetCDF format only) as and 4) overwriting values in NetCDF output. 

These were developed to view the output of modelling turbidity currents in Delft3D(4)-FLOW, which means 3D models that are entirely submerged. I will attempt to make [everything I developed for my thesis](https://github.com/JulesBlm/Delft3D-Python-Thesis) to a clean and reusable package here. Check out the Jupyter notebooks to get up-and-running. If there's sufficient interest, I'll document and expand it a bit more.

## Installation

Clone this repository: `git clone https://github.com/JulesBlm/pyDelft3D-FLOW.git`

Install pyDelft3D-FLOW with [Poetry](https://python-poetry.org/docs/) (preferred), Conda or pip.

#### Python Poetry

[Why poetry?](https://hackersandslackers.com/python-poetry-package-manager/)

Run `poetry install`.

#### Conda

Make a Python environment with [Anaconda](https://www.anaconda.com/products/individual), [Miniconda](https://docs.conda.io/en/latest/miniconda.html), [Poetry](https://python-poetry.org/) or whatever you like.

### Post-installation

There are three commands to run after installation to get the widgets and plot figures to play nicely with JupyterLab

### JupyterLab

1. To get [ipywidgets](https://ipywidgets.readthedocs.io/en/latest/user_install.html) working run the following two commands

```bash
jupyter nbextension enable --py widgetsnbextension

jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyter-matplotlib@
```

2. To get matplotlib plots working nicely in JupyterLab run the following command after installing

```bash
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

3. To get [HoloViews](http://holoviews.org/) widgets working properly in JupyterLab, run

```bash
jupyter labextension install @pyviz/jupyterlab_pyviz
```

4. (Optional) to get [ITKwidgets](https://github.com/InsightSoftwareConsortium/itkwidgets#installation) working, run the following command after the previous ones

```bash
jupyter labextension install jupyterlab-datawidgets itkwidgets
```

## Viewing Output

The scripts were developed with a focus on modelling sequential turbidity currents in Delft3D-FLOW, so the focus is on 3D models and cross-section of the 3D output. However, the scripts are valuable for any type of Delft3D(4)-FLOW output.

### xarray
The core functionality is provided by [xarray](https://xarray.pydata.org/). Delft3D-FLOW writes output in the NetCDF3 64-bit format with metadata following the [Climate & Forecast Conventions](http://cfconventions.org/).
xarray is Python package for opening and analysing multidimensional gridded data sets. xarray is particularly tailored to working with self-describing NetCDF files and has native support for CF convention metadata, like that written by Delft3D-FLOW.
xarray introduces labels in the form of dimensions, coordinates and attributes on top of raw multidimensional arrays, which allows for a more intuitive, more concise, and less error-prone developer experience.

xarray integrates tightly with [Dask](https://dask.org/) under the hood to facilitate out-of-memory and parallel computations on large datasets that do not fit into memory. Dask arrays allow handling very large array operations using many small arrays known as *chunks*. This enables many successive simulations to be combined and opened as one dataset.

### HoloViews/hvPlot
[HoloViews](http://holoviews.org/) is a a Python library that enables visual exploration of multi-dimensional parameter spaces using auto-generated widgets that read the datasets metadata. Thanks to built-in Dask and Datashader integration HoloViews scales easily to millions of datapoints. hvPlot is a convenience wrapper around xarray for plotting data with HoloViews for more advanced, interactive visualizations.


### Three-dimensional

[PyVista](https://www.pyvista.org/) is a pure Python library wrapping the [VTK library](https://vtk.org)'s Python bindings for a streamlined and intuitive toolset for 3D Visualization and mesh analysis and processing. PyVista can be used across platforms, has extensive documentation and is open-source with a permissive MIT Licence. Structures created in PyVista are immediately interoperable with any VTK-based software.

Optionally, install [ITKwidgets](https://docs.pyvista.org/plotting/itk_plotting.html) to interactively visualize a PyVista mesh within a Jupyter notebook

`poetry install --extras "itk"`


# Prior Work

* [https://github.com/Carlisle345748/Delft3D-Toolbox](Delft3D-Toolbox)
* [https://github.com/spmls/pydelft](pydelft)
* [https://svn.oss.deltares.nl/repos/openearthtools/trunk/python/OpenEarthTools/openearthtools/io/delft3d/](Deltares Python OpenEarthTools)


# To Do

I'd like to get to these

* Move colorcet and imageio-ffmpeg to extras
* Code formatting with [Black](https://black.readthedocs.io/en/stable/)
* Proper package with correct imports and all that
* Documentation with [Sphinx](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html) with [RST](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)


# Ideas

I have plenty of ideas for improvement that I most likely won't get to, here's some

## Input
* Automatically read parameters into right types (float, int). For example in Sed.py and Mor.py, now everthing is read as a string
* Tighter integration with xarray
* Match read file contents against dict of description so you know what the keywords are for.
    * Check if selected options are valid
* Expand D3Dmodel class to include all model's information.
    * Plot all model times in one chart, discharge time, spin-up time, smoothing time
* Better handling of ensembles of models, ie multiple scenarios.
* Visualise vertical grid of input files (in 3D).
    * Visualise 3D vertical boundary profile in 3D
* Testing
* Support for unit-aware arrays with [pint](https://pint.readthedocs.io) to define, operate and manipulate physical quantities. Pint is already integrated in xarray, this would be very useful in calculating sediment volumes of in-flow boundary conditions for example.


## Output
* Support for plotting non-uniform grids with enclosures in HoloViews.
* Out-of-core (lazy) operations for summing vector components like velocity and bottom stress.
* Efficiently plotting vector fields (quiver plots) without loading the all required data into memory at once.
* Interactive 3D plotting with [Panel](https://panel.holoviz.org/reference/panes/VTK.html) or [itkwidgets](https://github.com/InsightSoftwareConsortium/itkwidgets)

