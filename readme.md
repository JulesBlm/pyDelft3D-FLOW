# pyDelft3D-FLOW

Some Python tools to manipulate Delft3D-FLOW input files and netCDF output.

## Installation

Make a Python environment with [Anaconda](https://www.anaconda.com/products/individual), [Miniconda](https://docs.conda.io/en/latest/miniconda.html), [Poetry](https://python-poetry.org/) or whatever you like.

There are three commands to run after installation to get the widgets and plot figures to play nicely with JupyterLab

### JupyterLab

1. To get [ipywidgets](https://ipywidgets.readthedocs.io/en/latest/user_install.html) working run the following two commands

```bash
jupyter nbextension enable --py widgetsnbextension

jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyter-matplotlib@0.7.0
```

2. To get matplotlib plots working nicely in JupyterLab run the following command after installing

```bash
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

3. To get HoloViews working properly, run this after installing

```bash
jupyter labextension install @pyviz/jupyterlab_pyviz
```

# Prior Work

* [https://github.com/Carlisle345748/Delft3D-Toolbox](Delft3D-Toolbox)
* [https://github.com/spmls/pydelft](pydelft)
* [https://svn.oss.deltares.nl/repos/openearthtools/trunk/python/OpenEarthTools/openearthtools/io/delft3d/](Deltares Python OpenEarthTool)


# To-do

I'd like to get to these

* Move colorcet and imageio-ffmpeg to extras
* Black
* Proper package with correct imports and all that
* [Sphinx docs](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html) with [RST](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)


# Ideas

I have plenty of ideas for improvement that I won't get to.

## Input
* Read parameters into right types (float, int). For example in SedMor.py, everthing is read as a string.
* Expand D3Dmodel class to include all model's information.
    * Plot all model times in one chart, discharge time, spin-up time, smoothing time
* Better handling of ensembles of models, ie multiple scenarios.
* Visualise vertical grid of input files (in 3D).
    * Visualise 3D vertical boundary profile in 3D
* Match read file contents against dict of description so you know what the keywords are for.
    * Check if selected options are valid
* Testing

## Interactive 3D plotting
* Use [Panel](https://panel.holoviz.org/reference/panes/VTK.html) or [itkwidgets](https://github.com/InsightSoftwareConsortium/itkwidgets) for interactive 3D plotting and widgets

