# Maya_PivotPainter
UnrealEingine4 Maya version PivotPainter1  

This is a Maya Version of UnrealEngine4 Max PivotPainter1.  


## Install

1,
Drag&Drop ri_maya_pivot_painter.py into MayaScriptEditor's Python Window  
and add "maya_pivot_painter_menu()" in the last row,  
than select all to make Shelf button (Python).   

or 

2,
Copy ri_maya_pivot_painter.py to Maya's Pathed script ot python directory  
and call "maya_pivot_painter_menu()" to start up.  


## Infomation

This tool is scripted as like the original Max tool as posible, to know what it's doing.  
Therefore, optimization is lowest in the Max tool part.  
Other parts are using OpenMaya to calculate vectors, specially thanks to the knowledge of  
buildMatrix and buildRotation.  


## Usage

### Setup Polygon Tools  
・[Detach Selected Polygon (Separate)]  
> Detach One Polygon Object to separate Polygons in accordance with UV Shell.  
> Useful when importing FBX Grass polygon.  


・[Rotate Pivot]  
> Rotate Pivot around.  Useful when making X-up, or back to Y-up.  
> When rotateAxis has data, the tool will reset to Zero, and add that data to Rotation.  



・[Show On/Off Vertex Color]  
> Toggle show On or Off Vertex Color, when Vertex Color Data is set.  


・[Paint Black VertexColor (NoAnimation)]  
> Paint Black Vertex Color, to set Animation Off in PivotPoint material animation.  
> Useful when setting Trunk of a Tree.  



### Per Polygon PivotPainter  
・[Make X-Up Pivot for Grass]  
> This tool will set the X-up pivot to the lowest point of a grass, according to lowest Face polygon.  


・[] Optimize for Foliage Placement (No VectorColor)  
> Doesn't set Vector Color when checked.  


  ... See Max Tool for Detale ...  


・[Do!! Per Polygon PivotPaiter]  
> Do PivotPaiter to selected seperate Polygons.  
> Maya Default UVset name "map1" will be renamed to "UVChannel_1".  
> Do care about UVset name when using this tool.  



### Hierachy PivotPainter
・  + Minimum Side - Maximum Side  
・[Make X-Up Pivot for Branch (Use when Y-up)]  
> This tool will set the X-up pivot to the Minimum Side or Maximum Side of a branch polygon.  
> Use when Polygon is Y-Up, if not Rotate the Pivot using [Rotate Pivot] tool and set it to Y-up.  


・[] Optimize for Foliage Placement (No VectorColor)  
> Doesn't set Vector Color when checked.  



・Set a Parent [__]  [SetParent]  
> Select a Polygon to be a Parent and Press [SetParent] Button.  


・SetAllChild  
> [Set]  [Add]  [DeleteSelected]  [Clear All]   

> Select all Polygons to be a Child and Press [Set] Button, will show into lower list.  
> [Add] will add selected Polygons to list,   
> [DeleteSelected] will delete from list what is selected in the list,  
> [Clear All]  will clear the list.  


・[Do!! Hierachy PivotPaiter]  
> Do PivotPaiter to the Polygons that are listed.   
> Maya Default UVset name "map1" will be renamed to "UVChannel_1".  
> Do care about UVset name when using this tool.  

