#!/usr/bin/env python
"""
This script runs multiple simulations to check sensitivity to parameters.

"""
from subprocess import call
import foampy
import os
import processing
import pandas as pd
from processing import get_yplus

def set_blockmesh_resolution(nx, ny, nz):
    resline = "({} {} {})".format(nx, ny, nz)
    blocks = """blocks
(
    hex (0 1 2 3 4 5 6 7)
    {}
    simpleGrading (1 1 1)
);
""".format(resline)
    foampy.dictionaries.replace_value("constant/polyMesh/blockMeshDict", 
                                      "blocks", blocks)
                                      
def set_timestep(dt):
    dt = str(dt)
    foampy.dictionaries.replace_value("system/controlDict", "deltaT", dt)
    
def set_maxco(maxco):
    maxco = str(maxco)
    foampy.dictionaries.replace_value("system/controlDict", "maxCo", maxco)

def spatial_grid_dep(newfile=True):
    if newfile:
        try:
            os.remove("processed/spatial_grid_dep.csv")
        except OSError:
            pass
    nx_list = [42, 48, 58, 68, 78, 88, 98]
    for nx in nx_list:
        call("./Allclean")
        print("Setting blockMesh nX to {}".format(nx))
        set_blockmesh_resolution(nx)
        call("./Allrun")
        processing.log_perf("spatial_grid_dep.csv", verbose=False)
        
def timestep_dep(newfile=True):
    if newfile:
        try:
            os.remove("processed/timestep_dep.csv")
        except OSError:
            pass
    dt_list = [4e-3, 3e-3, 2.5e-3, 2e-3, 1.8e-3, 1.5e-3, 1e-3, 9e-4, 8e-4]
    call("./Allrun.pre")
    for dt in dt_list:
        call("./Allclean.nomesh")
        print("Setting timestep to {}".format(dt))
        set_timestep(dt)
        call("./Allrun.postmesh")
        processing.log_perf("timestep_dep.csv", verbose=False)
        
def maxco_dep(newfile=True):
    if newfile:
        try:
            os.remove("processed/maxco_dep.csv")
        except OSError:
            pass
    maxco_list = [40, 20, 10, 5, 2, 0.9, 0.5]
    call("./Allrun.pre")
    for maxco in maxco_list:
        call("./Allclean.nomesh")
        print("Setting maxCo to {}".format(maxco))
        set_maxco(maxco)
        call("./Allrun.postmesh")
        processing.log_perf("maxco_dep.csv", verbose=False)

def tsr_dep(newfile=True):
    if newfile:
        try:
            os.remove("processed/tsr_dep.csv")
        except OSError:
            pass
    tsr_list = [3.5, 3.0, 2.5, 2.0, 1.5, 1.0]
    call("./Allrun.pre")
    for tsr in tsr_list:
        call("./Allclean.nomesh")
        print("Setting tip speed ratio to {}".format(tsr))
        call("./Allrun.postmesh {}".format(tsr), shell=True)
        processing.log_perf("tsr_dep.csv", verbose=False)

def automesh(yplus_thresh=5.0):
    yplus_mean = 10.0
    reslist = [(70, 70, 25),
               (71, 71, 26),
               (72, 72, 27),
               (70, 69, 25),
               (69, 70, 25),
               (81, 81, 27)]
    for nx, ny, nz in reslist:
        if yplus_mean > yplus_thresh:
            call("./Allclean")
            set_blockmesh_resolution(nx, ny, nz)
            call("./Allrun.pre")
            yplus_mean = get_yplus()["mean"]
                            
if __name__ == "__main__":
    automesh()
