from ghpythonlib import components as gh
import math
import sys
import rhinoscriptsyntax as rs
from Rhino import Geometry 
"""
A python script for Rhino Grasshopper used to generate fiber strips given input curves and fiber orientation angles.
- Multiple input curves can either be used for boolean difference or to make multiple curves with the same fiber orientation.
-Mattis Koh (August 3rd, 2017)

https://github.com/mattiskoh/GH_fiber-gen
"""

# Constants
line_width = 0.36
line_spacing = line_width + 0.01
layer_height = 0.1

def list_to_tree(input, none_and_holes=True, source=[0]):
    """Transforms nestings of lists or tuples to a Grasshopper DataTree"""
    from Grasshopper import DataTree as Tree
    from Grasshopper.Kernel.Data import GH_Path as Path
    from System import Array
    def proc(input,tree,track):
        path = Path(Array[int](track))
        if len(input) == 0 and none_and_holes: tree.EnsurePath(path); return
        for i,item in enumerate(input):
            if hasattr(item, '__iter__'): #if list or tuple
                track.append(i); proc(item,tree,track); track.pop()
            else:
                if none_and_holes: tree.Insert(item,path,i)
                elif item is not None: tree.Add(item,path)
    if input is not None: t=Tree[object]();proc(input,t,source[:]);return t

def layer_creator(current_geo,fiber_angle):
	layer_vector = Geometry.Vector3d(0,0,layer_height)
	move_vector = Geometry.Vector3d(line_width*math.cos(fiber_angle),line_width*math.sin(fiber_angle),0)
	XYplane = rs.WorldXYPlane()

	fiber_plane = gh.RotatePlane(XYplane,fiber_angle)
	# Generate points along boundary box
	geo_boundary_crvs = gh.BoundarySurfaces(current_geo)
	geo_BB = gh.BoundingBox(geo_boundary_crvs,fiber_plane)[0]
	[BB_u,BB_v] = gh.Dimensions(geo_BB)
	
	points = gh.DivideSurface(geo_BB,BB_u/line_spacing,1)[0]

	strips = []
	for i in range(0,len(points),2):
		strips.append(gh.Rectangle3Pt(points[i],points[i+1],gh.Move(points[i+1],move_vector))[0])
	strips = gh.RegionIntersection(strips,current_geo)
	strips = gh.BoundarySurfaces(strips)
	fibers = gh.Extrude(strips,layer_vector)
	return fibers

def main(layer_angles):
	layers = []
	for crv in range(len(geo)):
	    layer_crv = []
	    for layer_num, layer_angle in enumerate(layer_angles):
	        layer_vector = Geometry.Vector3d(0,0,layer_height*layer_num)
	        layer_crv.append(gh.Move(layer_creator(geo[crv],layer_angle/180*math.pi),layer_vector))
	    layers.append(layer_crv)
	return layers
fibers = list_to_tree(main(layer_angles))