#!/bin/sh

fullbeamline
python3 plot.py
rm *.digested* __bmad_data output.gdf
rm -r __fullbeamline
