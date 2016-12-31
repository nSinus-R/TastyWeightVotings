# TastyWeightVotings
Some python scripts to analyze ctftime votings, brought to you by Tasteless.

This repository is currently WIP, and an analysis with text and explanations will be posted on tasteless.eu somewhen in the future.

To give you a headstart, there are currently 3 scripts:

- fetcher.py:  fetches data from ctftime. As some of the data which we want to analyze are not given by the ctftime-api, we use a mix of api-calls and html-parsing to get our dataset, stored in the tastyWeighting.json file. The dataset itself is actually stored in a [tinydb](http://tinydb.readthedocs.io/en/latest/), as it was an easy way to save and retrieve fetched data.
- analyser.py, provides several functions for analysing the dataset and drops you in an IPython shell for further analyses per default.
- plotter.py, plots various nice figures, as visualization of data can be quite useful - the generated output can be found in figs-subdirectory

The dataset uploaded in this repository was generated at 1483183201. 
