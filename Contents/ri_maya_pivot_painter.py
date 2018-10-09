# -*- coding: utf-8 -*-

"""!
For Maya2015- Maya PivotPainter for UE4  V4.2
     + Make Rotate Pivot with Resetting rotateAxis
     + Separate a Merged Polygon to Polygons
     + Remove Vertex Color (No Animation)
     + Hierarchy PivotPainter
     + Fixed many miss in Y = * -1
     + Fixed When UVSet has "map1" & "UVChannel_1"
     + Add Make X-Up Pivot for Grass will move pivot to lowest face polygon
     + Add Make X-Up Pivot for Branch will move pivot to Lowest or Hightest Bound when Y-up
@file
@author Ritaro

"""

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import sys
import math

def buildMatrix(translate=(0,0,0),xAxis=(1,0,0),yAxis=(0,1,0),zAxis=(0,0,1)):

    # Create transformation matrix from input vectors
    matrix = OpenMaya.MMatrix()
    values = []
    OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 0, xAxis[0])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 1, xAxis[1])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 2, xAxis[2])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 0, yAxis[0])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 1, yAxis[1])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 2, yAxis[2])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 0, zAxis[0])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 1, zAxis[1])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 2, zAxis[2])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 0, translate[0])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 1, translate[1])
    OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 2, translate[2])
    return matrix


def buildRotation(aimVector,upVector=(0,1,0),aimAxis='z',upYAxis='x'):

    # Check negative axis
    negAim = False
    negUp = False
    if aimAxis[0] == '-':
        aimAxis = aimAxis[1]
        negAim = True
    if upYAxis[0] == '-':
        upAxis = upYAxis[1]
        negUp = True

    # Check valid axis
    axisList = ['x','y','z']
    if not axisList.count(aimAxis): raise Exception('Aim axis is not valid!')
    if not axisList.count(upYAxis): raise Exception('Up axis is not valid!')
    if aimAxis == upYAxis: raise Exception('Aim and Up axis must be unique!')
    
    # Determine cross axis
    axisList.remove(aimAxis)
    axisList.remove(upYAxis)
    crossAxis = axisList[0]
    
    # Normaize aimVector
    m_aimVector = OpenMaya.MVector()
    m_aimVector = OpenMaya.MVector(aimVector[0],aimVector[1],aimVector[2]).normal()

    if negAim:
        m_aimVector = (-aimVector[0],-aimVector[1],-aimVector[2])

    # Normaize upVector
    m_upVector = OpenMaya.MVector()
    m_upVector = OpenMaya.MVector(upVector[0],upVector[1],upVector[2]).normal()

    if negUp:
        m_upVector = (-upVector[0],-upVector[1],-upVector[2])

    # Get cross product vector
    o_crossVector = OpenMaya.MVector()
    if (aimAxis == 'x' and upYAxis == 'z') or (aimAxis == 'z' and upYAxis == 'y'):
        o_crossVector = m_upVector ^ m_aimVector
    else:
        o_crossVector = m_aimVector ^ m_upVector

    # Recalculate upVector (orthogonalize)
    o_upVector = OpenMaya.MVector()
    if (aimAxis == 'x' and upYAxis == 'z') or (aimAxis == 'z' and upYAxis == 'y'):
        o_upVector = m_aimVector ^ o_crossVector
    else:
        o_upVector = o_crossVector ^ m_aimVector
    
    # Build axis dictionary
    axisDict={aimAxis: m_aimVector,upYAxis: o_upVector,crossAxis: o_crossVector}
    # Build rotation matrix
    mat = buildMatrix(xAxis=axisDict['x'],yAxis=axisDict['y'],zAxis=axisDict['z'])
    
    # Return rotation matrix
    return mat


def separate_polygon(*args):

    cmds.manipMoveContext("Move",e=True,q=True, mode=0 )
    cmds.selectMode(object=True )

    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    o_selected = cmds.ls(sl=True)[0]

    cmds.makeIdentity(apply=True,translate=False,rotate=True,scale=True,normal=False,preserveNormals=True)
    cmds.manipPivot( o=[0, 0, 90] )
    cmds.delete(o_selected,constructionHistory=True)
    maya.mel.eval('DeleteHistory;')
    o_mesh = []

    try:
        o_shape = cmds.listRelatives(o_selected,path=True)[0]
        if cmds.objectType(o_shape) == 'mesh':
            o_mesh.append(o_selected)
    except:
        pass

    if o_mesh == []:
        cmds.confirmDialog( title='Warnnig', message='No Mesh Polygon Selected  !_! ')
        sys.exit()

    cmds.select(clear=True)
    
    try:
        cmds.polySeparate(o_shape,constructionHistory=True,name=o_mesh[0] )
    except:
        cmds.select(o_mesh[0],r=True)

    o_all_split_list = cmds.ls(sl=True)
    cmds.select(clear=True)
    cmds.select(o_all_split_list,add=True)

def show_polyvtc(*args):

    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    v_all_selected = cmds.ls(sl=True)
    v_all_mesh = []

    for v_obj in v_all_selected:
        try:
            v_shapes = cmds.listRelatives(v_obj,path=True)[0]
            if cmds.objectType(v_shapes) == 'mesh':
                v_all_mesh.append(v_obj)
        except:
            pass

    if v_all_mesh == []:
        cmds.confirmDialog( title='Warnnig', message='No Mesh Polygon Selected  !_! ')
        sys.exit()

    cmds.modelEditor('modelPanel4', e=True, displayAppearance='smoothShaded',activeOnly=False )

    if cmds.getAttr(v_all_mesh[0] + '.displayColors') != 1:
        onoff_vtc = 1
    else:
        onoff_vtc = 0

    for v_obj in v_all_mesh:
        cmds.setAttr(v_obj +'.displayColors',onoff_vtc)

def make_xup(*args):

    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    o_all_selected = cmds.ls(sl=True)
    o_all_mesh = []

    for o_obj in o_all_selected:
        try:
            o_shapes = cmds.listRelatives(o_obj,path=True)[0]
            if cmds.objectType(o_shapes) == 'mesh':
                o_all_mesh.append(o_obj)
        except:
            pass

    if o_all_mesh == []:
        cmds.confirmDialog( title='Warnnig', message='No Mesh Polygon Selected  !_! ')
        sys.exit()

    cmds.manipMoveContext("Move",e=True,q=True, mode=0 )

    for s_mesh in o_all_mesh:
        cmds.select(clear=True)
        cmds.select(s_mesh,r=True)

        cmds.makeIdentity(s_mesh, apply=True, translate=True, rotate=True, scale=False, normal=0, preserveNormals=True)
        mel.eval('ResetTransformations;')

        point_dic = {}
        all_mesh_vtc = cmds.ls((cmds.polyListComponentConversion(s_mesh, toVertex=True)), fl=True)

        for obj_vtc in all_mesh_vtc:
            obj_xyz_data = cmds.xform(obj_vtc,q=True,absolute=True,worldSpace=True,translation=True)
            point_dic.update({obj_vtc:obj_xyz_data})

        y_data_list = []
        for dic_vtc,dic_value in point_dic.items():
            y_data_list.append(dic_value[1])

        min_y_data = min(y_data_list)
        #print point_dic

        min_point_list = []

        for dic_vtc,dic_value in point_dic.items():
            if dic_value[1] == min_y_data:
                min_point_list.append(dic_vtc)

#        print min_point_list[0]

        count = 0
        total_x = 0
        total_z = 0

        if len(min_point_list) == 1:
            min_piv = point_dic[min_point_list[0]]
        else:
            for o_num in min_point_list:
#                print point_dic[o_num][2]
                total_x = total_x + point_dic[o_num][0]
                total_z = total_z + point_dic[o_num][2]
                count = 1 + count
            avg_x = total_x / count
            avg_z = total_z / count
            min_piv = [avg_x,min_y_data,avg_z]

#        print min_piv

        count2 = 0
        total_x2 = 0
        total_y2 = 0
        total_z2 = 0
        for o_num2 in all_mesh_vtc:
            total_x2 = total_x2 + point_dic[o_num2][0]
            total_y2 = total_y2 + point_dic[o_num2][1]
            total_z2 = total_z2 + point_dic[o_num2][2]
            count2 = 1 + count2
        avg_x2 = total_x2 / count2
        avg_y2 = total_y2 / count2
        avg_z2 = total_z2 / count2
        min_piv2 = [avg_x2,avg_y2,avg_z2]

        cmds.selectMode(object=True )

#        print min_piv2

#        *---- Select Lowest Polygon Face *---------

        cmds.select(clear=True)
        cmds.select(s_mesh,r=True)
        cmds.selectMode(object=True )

        inv_min_piv = [min_piv[0]*-1,min_piv[1]*-1,min_piv[2]*-1]
        cmds.xform(s_mesh ,worldSpace=True, translation=inv_min_piv)
        cmds.makeIdentity(s_mesh, apply=True, translate=True, rotate=False, scale=False,preserveNormals=False,normal=0)
        cmds.xform(s_mesh ,worldSpace=True, translation=min_piv)
        cmds.xform(s_mesh ,worldSpace=True, rotatePivot=min_piv)
        cmds.xform(s_mesh ,worldSpace=True, scalePivot=min_piv)

        cmds.selectMode( component=True)
        mel.eval('EnterEditMode;')
        cmds.select(min_point_list[0], r=True)
        maya.mel.eval('PolySelectConvert 1;')
        s_face = cmds.ls(sl=True)

#        print s_face


        if len(s_face) >= 2:
            maya.mel.eval('PolySelectConvert 2;')
            s_edges = cmds.ls(sl=True,fl=True)
            cmds.select(clear=True)

            final_edge_dic = {}
            for o_edge in s_edges:
                cmds.select(clear=True)
                maya.mel.eval('PolySelectConvert 2;')
                cmds.select(o_edge, r=True)
                maya.mel.eval('PolySelectConvert 3;')
                s_points = cmds.ls(sl=True,fl=True)
                point_a_data = cmds.xform(s_points[0],q=True,absolute=True,worldSpace=True,translation=True)
                point_b_data = cmds.xform(s_points[1],q=True,absolute=True,worldSpace=True,translation=True)
                final_edge_dic.update({o_edge: (point_a_data[1] + point_b_data[1]) })

#            print final_edge_dic
            min_t_y_val = min(final_edge_dic.values())
            for dic_edge,dic_value in final_edge_dic.items():
                if dic_value == min_t_y_val:
                    min_t_edge = dic_edge
                    break
            cmds.select(clear=True)
            maya.mel.eval('PolySelectConvert 2;')
            cmds.select(min_t_edge, r=True)
            maya.mel.eval('PolySelectConvert 3;')
            m_points = cmds.ls(sl=True,fl=True)
            point_m_a_data = cmds.xform(m_points[0],q=True,absolute=True,worldSpace=True,translation=True)
            point_m_b_data = cmds.xform(m_points[1],q=True,absolute=True,worldSpace=True,translation=True)
            cmds.select(clear=True)
            cmds.selectMode(object=True)
            min_piv3 = [(point_m_a_data[0]+point_m_b_data[0])/2,(point_m_a_data[1]+point_m_b_data[1])/2,(point_m_a_data[2]+point_m_b_data[2])/2]

            mov_piv = [min_piv3[0]-min_piv[0],min_piv3[1]-min_piv[1],min_piv3[2]-min_piv[2]]
            mov_minus_piv = [mov_piv[0]* -1,mov_piv[1]* -1,mov_piv[2]* -1] 

            cmds.xform(s_mesh ,worldSpace=True, translation=mov_minus_piv)
            cmds.makeIdentity(s_mesh, apply=True, translate=True, rotate=False, scale=False,preserveNormals=False,normal=0)
            cmds.xform(s_mesh ,worldSpace=True, translation=[0,0,0])
            cmds.xform(s_mesh ,worldSpace=True, rotatePivot=[0,0,0])
            cmds.xform(s_mesh ,worldSpace=True, scalePivot=[0,0,0])
            cmds.xform(s_mesh ,worldSpace=True, translation=min_piv3)
            cmds.xform(s_mesh ,worldSpace=True, rotatePivot=min_piv3)
            cmds.xform(s_mesh ,worldSpace=True, rotatePivot=min_piv3)

            min_piv = min_piv3
            cmds.selectMode( component=True)
            mel.eval('EnterEditMode;')
            maya.mel.eval('PolySelectConvert 2;')
            cmds.select(min_t_edge, r=True)
            maya.mel.eval('PolySelectConvert 1;')
            s_face = cmds.ls(sl=True)


#        *---- Get Matrix from Lowest Polygon Face *---------
        normal_info = cmds.polyInfo( fn=True )[0]
        moji_normal= (normal_info[normal_info.index(':')+2:]).rsplit()
        o_normal = [float(moji_normal[0]),float(moji_normal[1]),float(moji_normal[2])]

        cmds.select(clear=True)
        cmds.select(s_mesh,r=True)
        cmds.selectMode(object=True)

        a_upVector = OpenMaya.MVector()
        vec2=[min_piv2[0] - min_piv[0], min_piv2[1] - min_piv[1], min_piv2[2] - min_piv[2]]
        a_upVector = OpenMaya.MVector(vec2[0], vec2[1], vec2[2]).normal()

        mAxisM = buildRotation(o_normal,a_upVector)

        mTransformMtx = OpenMaya.MTransformationMatrix(mAxisM)
        eulerRot_b = mTransformMtx.eulerRotation()
        angles_b = [math.degrees(angle) for angle in (eulerRot_b.x, eulerRot_b.y, eulerRot_b.z)]

        cmds.selectMode(object=True )

        maya.mel.eval('EnterEditMode;')
        cmds.manipPivot(o = (angles_b[0],angles_b[1],angles_b[2]))

        if cmds.currentCtx() != 'moveSuperContext':cmds.setToolTo( 'moveSuperContext' )
        maya.mel.eval('performBakeCustomToolPivot 0;')

    cmds.select(clear=True)
    cmds.select(o_all_mesh,add=True)


def do_parpoly_pp(*args):

    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    p_all_selected = cmds.ls(sl=True)
    p_all_mesh = []

    for p_obj in p_all_selected:
        try:
            p_shapes = cmds.listRelatives(p_obj,path=True)[0]
            if cmds.objectType(p_shapes) == 'mesh':
                p_all_mesh.append(p_obj)
        except:
            pass

    if p_all_mesh == []:
        cmds.confirmDialog( title='Warnnig', message='No Mesh Polygon Selected  !_! ')
        sys.exit()

    leafLengthFalloff=cmds.floatField('per_pivm', q=True,value=True)#　　　　"3D dist to piv multiplier"
#    tooltip:"This multiplies a distance calculation from the pivot to the current vertex."
#    print leafLengthFalloff Default 0.5

    leafLengthFalloffPower=cmds.floatField('per_pivc', q=True,value=True)#　　"3D dist to piv contrast"
#    print leafLengthFalloffPower Default 1.0

    leafWingFalloffPower=10#
    leafWingFalloffX=cmds.floatField('per_xmul', q=True,value=True)#　　　　　"X multiplier"
#    print leafWingFalloffX Default 0.0

    leafWingFalloffPowerX=cmds.floatField('per_xcon', q=True,value=True)#　　"X contrast"
#    print leafWingFalloffPowerX Default 10.0

    leafWingFalloffY=cmds.floatField('per_ymul', q=True,value=True)#　　　　　"Y multiplier"
#    print leafWingFalloffY Default 0.0

    leafWingFalloffPowerY=cmds.floatField('per_xcon', q=True,value=True)#    "Y contrast"
#    print leafWingFalloffPowerY Default 10.0

    leafWingFalloffZ=cmds.floatField('per_zmul', q=True,value=True)#          "Z multiplier"
#    print leafWingFalloffZ Default 0.0

    leafWingFalloffPowerZ=cmds.floatField('per_zcon', q=True,value=True)#     "Z contrast"
#    print leafWingFalloffPowerZ Default 10.0

    cmds.manipMoveContext("Move",e=True,q=True, mode=0 )

    for o_obj in p_all_mesh:
        cmds.select(clear=True)
        cmds.select(o_obj,r=True)
        cmds.delete(o_obj,constructionHistory=True)
        o_obj_shape = cmds.listRelatives(o_obj)[0]

        cmds.selectMode( component=True)
        cmds.selectMode( object=True )

        pre_pivot_pos = cmds.xform(o_obj,q=True,absolute=True,worldSpace=True,matrix=True)
        pre_pivot_pos1 = [round(pre_pivot_pos[12],4),round(pre_pivot_pos[14],4),round(pre_pivot_pos[13],4)]

        pivot_pos = [pre_pivot_pos1[0],pre_pivot_pos1[1],pre_pivot_pos1[2]]

#        print pivot_pos

        pre_pivot_trans = [round(pre_pivot_pos[0],6),round(pre_pivot_pos[2],6)*-1,round(pre_pivot_pos[1],6)]
#        print pre_pivot_trans

        o_r = round((((pre_pivot_trans[0] * 1 ) + 1.0 ) / 2),6)
        o_g = round((((pre_pivot_trans[1] * -1 ) + 1.0 ) / 2),6)
        o_b = round((((pre_pivot_trans[2] * 1 ) + 1.0 ) / 2),6)

        maya_angle_vtc = [o_r,o_g,o_b]
        map3_uv = [pivot_pos[0],pivot_pos[1],pivot_pos[2]]
        map4_uv = [pivot_pos[2],round(maya.mel.eval('rand(0.0,1.0);'),3),0.0]

#        print maya_angle_vtc
#        print map3_uv
#        print map4_uv

        o_obj_all_uv = cmds.polyUVSet( query=True, allUVSets=True )
#        print o_obj_all_uv

        all_obj_vtc = cmds.ls((cmds.polyListComponentConversion((cmds.ls(flatten=True,sl=True)), toVertex=True)), fl=True)
#        print all_obj_vtc

        if 'map1' in o_obj_all_uv:

            if 'UVChannel_1' in o_obj_all_uv:
                cmds.polyUVSet(o_obj_shape,delete=True,uvSet='UVChannel_1')
            if 'UVChannel_3' in o_obj_all_uv:
                cmds.polyUVSet(o_obj_shape,delete=True,uvSet='UVChannel_3')
            if 'UVChannel_4' in o_obj_all_uv:
                cmds.polyUVSet(o_obj_shape,delete=True,uvSet='UVChannel_4')

            cmds.polyUVSet(o_obj_shape,currentUVSet=True,uvSet='map1')
            cmds.polyUVSet(o_obj_shape,perInstance=True,rename=True,newUVSet='UVChannel_1', uvSet='map1')

            cmds.polyUVSet(o_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_3')
            cmds.polyUVSet(o_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_4')


        if 'UVChannel_3' not in o_obj_all_uv:
            cmds.polyUVSet(o_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_3')

        cmds.polyUVSet(o_obj_shape,currentUVSet=True,uvSet='UVChannel_3')
        cmds.polyEditUV(all_obj_vtc,uvSetName="UVChannel_3",relative=False, uValue=map3_uv[0], vValue=map3_uv[1])


        if 'UVChannel_4' not in o_obj_all_uv:
            cmds.polyUVSet(o_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_4')

        cmds.polyUVSet(o_obj_shape,currentUVSet=True,uvSet='UVChannel_4')
        cmds.polyEditUV(all_obj_vtc,uvSetName="UVChannel_4",relative=False, uValue=map4_uv[0], vValue=map4_uv[1])

        if not cmds.checkBoxGrp('optimaze_check',q=True,v1=True):
            count = 0
            for o_vtc in all_obj_vtc:

#                print o_vtc
                o_maya_p0 = cmds.xform(o_obj,q=True,absolute=True,worldSpace=True,matrix=True)
                o_maya_p1 = cmds.xform(o_vtc,q=True,absolute=True,worldSpace=True,translation=True)
                o_maya_p2 = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, o_maya_p1[0], o_maya_p1[1], o_maya_p1[2], 1.0]

#                print o_maya_p2
                o_m0 = OpenMaya.MMatrix()
                o_m1 = OpenMaya.MMatrix()

                mUtil = OpenMaya.MScriptUtil()
                mUtil.createMatrixFromList(o_maya_p0, o_m0)
                mUtil.createMatrixFromList(o_maya_p2, o_m1)

                o_m3 = o_m1 * (o_m0.inverse())

                mList = [
                o_m3(0,0), o_m3(0,1), o_m3(0,2), o_m3(0,3),
                o_m3(1,0), o_m3(1,1), o_m3(1,2), o_m3(1,3),
                o_m3(2,0), o_m3(2,1), o_m3(2,2), o_m3(2,3),
                o_m3(3,0), o_m3(3,1), o_m3(3,2), o_m3(3,3)
                ]

                maya_boundingbox_minmax = [round(o_m3(3,0),5), round(o_m3(3,1),5), round(o_m3(3,2),5)]

                if count == 0: 
                    o_x_min = maya_boundingbox_minmax[0]
                    o_x_max = maya_boundingbox_minmax[0]
                    o_y_min = maya_boundingbox_minmax[1]
                    o_y_max = maya_boundingbox_minmax[1]
                    o_z_min = maya_boundingbox_minmax[2]
                    o_z_max = maya_boundingbox_minmax[2]
                else: 
                    o_x_min = min(o_x_min,maya_boundingbox_minmax[0])
                    o_x_max = max(o_x_max,maya_boundingbox_minmax[0])
                    o_y_min = min(o_y_min,maya_boundingbox_minmax[1])
                    o_y_max = max(o_y_max,maya_boundingbox_minmax[1])
                    o_z_min = min(o_z_min,maya_boundingbox_minmax[2])
                    o_z_max = max(o_z_max,maya_boundingbox_minmax[2])
                count = 1

            maya_bounding_min = [o_x_min,o_y_min,o_z_min]
            maya_bounding_max = [o_x_max,o_y_max,o_z_max]

#            print maya_bounding_min
#            print maya_bounding_max

            gradBBX=[0,maya_bounding_min[0],0]
            gradBBXTwo=[0,maya_bounding_max[0],0]

            gradBBY=[0,maya_bounding_min[1],0]
            gradBBYTwo=[0,maya_bounding_max[1],0]

            gradBBZ=[0,maya_bounding_min[2],0]
            gradBBZTwo=[0,maya_bounding_max[2],0]

            finXScale = maya_bounding_max[0] - maya_bounding_min[0]
            finYScale = maya_bounding_max[1] - maya_bounding_min[1]
            finZScale = maya_bounding_max[2] - maya_bounding_min[2]

#            print gradBBX,gradBBXTwo,finXScale
#            print gradBBY,gradBBYTwo,finYScale 
#            print gradBBZ,gradBBZTwo,finZScale


            for n_vtc in all_obj_vtc:

#                print n_vtc
                n_maya_p0 = cmds.xform(o_obj,q=True,absolute=True,worldSpace=True,matrix=True)
                n_maya_p1 = cmds.xform(n_vtc,q=True,absolute=True,worldSpace=True,translation=True)
                n_maya_p2 = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, n_maya_p1[0], n_maya_p1[1], n_maya_p1[2], 1.0]

#                print o_maya_p2
                n_m0 = OpenMaya.MMatrix()
                n_m1 = OpenMaya.MMatrix()

                mUtil = OpenMaya.MScriptUtil()
                mUtil.createMatrixFromList(n_maya_p0, n_m0)
                mUtil.createMatrixFromList(n_maya_p2, n_m1)

                n_m3 = n_m1 * (n_m0.inverse())

                nList = [
                n_m3(0,0), n_m3(0,1), n_m3(0,2), n_m3(0,3),
                n_m3(1,0), n_m3(1,1), n_m3(1,2), n_m3(1,3),
                n_m3(2,0), n_m3(2,1), n_m3(2,2), n_m3(2,3),
                n_m3(3,0), n_m3(3,1), n_m3(3,2), n_m3(3,3)
                ]

                maya_currVert = [round(n_maya_p1[0],5),(round(n_maya_p1[2],5)) * -1,round(n_maya_p1[1],5)]
#                print maya_currVert

                maya_currMesh_pos = [(n_maya_p0[12]),(n_maya_p0[14]) * -1,(n_maya_p0[13])]
#                print maya_currMesh_pos

                maya_currVertBaseObj = [round(n_m3(3,0),5), round(n_m3(3,1),5), round(n_m3(3,2),5)]
#                print maya_currVertBaseObj

                finXVal = math.pow(((maya_currVertBaseObj[0] - maya_bounding_min[0]) / finXScale), leafWingFalloffPowerX) + math.pow(((maya_bounding_max[0] - maya_currVertBaseObj[0]) / finXScale), leafWingFalloffPowerX)
                finYVal = math.pow(((maya_currVertBaseObj[1] - maya_bounding_min[1]) / finYScale), leafWingFalloffPowerY) + math.pow(((maya_bounding_max[1] - maya_currVertBaseObj[1]) / finYScale), leafWingFalloffPowerY)
                finZVal = math.pow(((maya_currVertBaseObj[2] - maya_bounding_min[2]) / finZScale), leafWingFalloffPowerZ) + math.pow(((maya_bounding_max[2] - maya_currVertBaseObj[2]) / finZScale), leafWingFalloffPowerZ)

#                print finXVal,finYVal,finZVal

                n_dx = maya_currVert[0] - maya_currMesh_pos[0]
                n_dy = maya_currVert[1] - maya_currMesh_pos[1]
                n_dz = maya_currVert[2] - maya_currMesh_pos[2]
                distanceToPivot = round(math.sqrt( n_dx*n_dx + n_dy*n_dy + n_dz*n_dz ) /255,7)

                maya_pre_finalAlpha = round(((math.pow((distanceToPivot * leafLengthFalloff),leafLengthFalloffPower) + (finYVal * leafWingFalloffY) + (finXVal * leafWingFalloffX) + (finZVal * leafWingFalloffZ) ) * 255 ),5)
                maya_finalAlpha = round((max(min(maya_pre_finalAlpha, 255.0), 0.0)) / 255,3)
#                print maya_finalAlpha

                cmds.polyColorPerVertex(n_vtc,rgb=maya_angle_vtc )
                cmds.polyColorPerVertex(n_vtc,alpha=maya_finalAlpha )

            for v_obj in p_all_mesh:
                cmds.setAttr(v_obj +'.displayColors',1)

        cmds.polyUVSet(o_obj_shape,currentUVSet=True,uvSet='UVChannel_1')

    cmds.select(clear=True)
    cmds.select(p_all_mesh,add=True)


def black_polyvtc(*args):

    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    p_all_selected = cmds.ls(sl=True)
    p_all_mesh = []

    for p_obj in p_all_selected:
        try:
            p_shapes = cmds.listRelatives(p_obj,path=True)[0]
            if cmds.objectType(p_shapes) == 'mesh':
                p_all_mesh.append(p_obj)
        except:
            pass

    if p_all_mesh == []:
        cmds.confirmDialog( title='Warnnig', message='No Mesh Polygon Selected  !_! ')
        sys.exit()

    cmds.manipMoveContext("Move",e=True,q=True, mode=0 )

    for o_obj in p_all_mesh:
        cmds.select(clear=True)
        cmds.select(o_obj,r=True)
        cmds.delete(o_obj,constructionHistory=True)
        o_obj_shape = cmds.listRelatives(o_obj)[0]

        cmds.selectMode( component=True)
        cmds.selectMode( object=True )

        o_obj_all_uv = cmds.polyUVSet( query=True, allUVSets=True )
#        print o_obj_all_uv

        all_obj_vtc = cmds.ls((cmds.polyListComponentConversion((cmds.ls(flatten=True,sl=True)), toVertex=True)), fl=True)
#        print all_obj_vtc

        cmds.polyColorPerVertex(all_obj_vtc,rgb=[0.0,0.0,0.0] )
        cmds.polyColorPerVertex(all_obj_vtc,alpha=0.0 )

        if 'map1' in o_obj_all_uv:
            if 'UVChannel_1' in o_obj_all_uv:
                cmds.polyUVSet(o_obj_shape,delete=True,uvSet='UVChannel_1')
            if 'UVChannel_3' in o_obj_all_uv:
                cmds.polyUVSet(o_obj_shape,delete=True,uvSet='UVChannel_3')
            if 'UVChannel_4' in o_obj_all_uv:
                cmds.polyUVSet(o_obj_shape,delete=True,uvSet='UVChannel_4')

            cmds.polyUVSet(o_obj_shape,currentUVSet=True,uvSet='map1')
            cmds.polyUVSet(o_obj_shape,perInstance=True,rename=True,newUVSet='UVChannel_1', uvSet='map1')

            cmds.polyUVSet(o_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_3')
            cmds.polyUVSet(o_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_4')


        if 'UVChannel_3' not in o_obj_all_uv:
            cmds.polyUVSet(o_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_3')

        cmds.polyUVSet(o_obj_shape,currentUVSet=True,uvSet='UVChannel_3')
        cmds.polyEditUV(all_obj_vtc,uvSetName="UVChannel_3",relative=False,uValue=0.0,vValue=0.0)


        if 'UVChannel_4' not in o_obj_all_uv:
            cmds.polyUVSet(o_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_4')

        cmds.polyUVSet(o_obj_shape,currentUVSet=True,uvSet='UVChannel_4')
        cmds.polyEditUV(all_obj_vtc,uvSetName="UVChannel_4",relative=False,uValue=0.0,vValue=0.0)


def set_parent(*args):
    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    p_selected = cmds.ls(sl=True)[0]
    p_mesh = []

    try:
        p_shapes = cmds.listRelatives(p_selected,path=True)[0]
        if cmds.objectType(p_shapes) == 'mesh':
            p_mesh.append(p_selected)
    except:
        cmds.confirmDialog( title='ERROR', message='Polygon is not Selected !_! ')
        sys.exit()

    if p_mesh == []:
        cmds.confirmDialog( title='ERROR', message='Polygon is not Selected !_! ')
        sys.exit()

    cmds.textFieldButtonGrp('setting_parent',edit=True,text=p_mesh[0])

def set_child(*args):
    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    c_all_selected = cmds.ls(sl=True)
    c_all_mesh = []

    for c_obj in c_all_selected:
        try:
            c_shapes = cmds.listRelatives(c_obj,path=True)[0]
            if cmds.objectType(c_shapes) == 'mesh':
                c_all_mesh.append(c_obj)
        except:
            pass
    if c_all_mesh == []:
        cmds.confirmDialog( title='Warnnig', message='No Mesh Polygon Selected  !_! ')
        sys.exit()

    p_selected_obj = cmds.textFieldButtonGrp('setting_parent',q=True,text=True)
    if p_selected_obj != "":
        try:
            if p_selected_obj in c_all_mesh:
                c_all_mesh.remove(p_selected_obj)
        except:
            pass              

    cmds.textScrollList('child_scroll',edit=True,removeAll=True)
    cmds.textScrollList('child_scroll',edit=True,append=c_all_mesh)


def add_child(*args):
    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    new_all_selected = cmds.ls(sl=True)
    new_all_mesh = []

    for new_obj in new_all_selected:
        try:
            new_shapes = cmds.listRelatives(new_obj,path=True)[0]
            if cmds.objectType(new_shapes) == 'mesh':
                new_all_mesh.append(new_obj)
        except:
            pass

    if new_all_mesh == []:
        cmds.confirmDialog( title='Warnnig', message='No Mesh Polygon Selected  !_! ')
        sys.exit()

    r_selected_objs = cmds.textScrollList('child_scroll',q=True,allItems=True)

    if r_selected_objs == [""]:
        r_selected_objs = new_all_mesh
    elif r_selected_objs == None:
        r_selected_objs = new_all_mesh
    else:
        for new_mesh in new_all_mesh:
            if new_mesh not in r_selected_objs:
                r_selected_objs.append(new_mesh)

    p_selected_obj = cmds.textFieldButtonGrp('setting_parent',q=True,text=True)
    if p_selected_obj != "":
        try:
            if p_selected_obj in r_selected_objs:
                r_selected_objs.remove(p_selected_obj)
        except:
            pass

    cmds.textScrollList('child_scroll',edit=True,removeAll=True)
    cmds.textScrollList('child_scroll',edit=True,append=r_selected_objs)

def delete_sel_child(*args):

    d_selected_objs = cmds.textScrollList('child_scroll',q=True,selectItem=True)

    if d_selected_objs == None:
        sys.exit()

    all_selected_objs = cmds.textScrollList('child_scroll',q=True,allItems=True)
    
    if d_selected_objs[0] in all_selected_objs:
        all_selected_objs.remove(d_selected_objs[0])
        cmds.textScrollList('child_scroll',edit=True,removeAll=True)
        cmds.textScrollList('child_scroll',edit=True,append=all_selected_objs)
    else:
        sys.exit()

def reset_scroll(*args):
    cmds.textScrollList('child_scroll',edit=True,removeAll=True) 


def do_hiera_pp(*args):
    p_obj = []
    p_selected_obj =""
    p_selected_obj = cmds.textFieldButtonGrp('setting_parent',q=True,text=True)

    if p_selected_obj == "":
        cmds.confirmDialog( title='ERROR', message='Set Parent Polygon !_! ')
        sys.exit()
    try:
        p_selected_shapes = cmds.listRelatives(p_selected_obj,path=True)[0]
        if cmds.objectType(p_selected_shapes) == 'mesh':
            p_obj.append(p_selected_obj)
    except:
        cmds.confirmDialog( title='ERROR', message='Set Parent Polygon !_! ')
        sys.exit()

    if p_obj == []:
        cmds.confirmDialog( title='Warnnig', message='No Mesh Parent Polygon Selected  !_! ')
        sys.exit()

#    print p_obj
    c_selected_objs = []
    c_selected_objs = cmds.textScrollList('child_scroll',q=True,allItems=True)
#    print c_selected_objs
    if c_selected_objs == None:
        cmds.confirmDialog( title='Warnnig', message='No Child is Selected !_! ')
        sys.exit()

    if p_obj[0] in c_selected_objs:
        cmds.confirmDialog( title='ERROR', message='Same Polygon in Parent and Child !_! ')
        sys.exit()

    shaderWSMultiplier = cmds.intField('max_ppiv', q=True,value=True)
    if shaderWSMultiplier <= 0:
        shaderWSMultiplier = 1
    elif shaderWSMultiplier > 100000000:
        shaderWSMultiplier = 100000000

# Parent

    cmds.select(clear=True)
    cmds.select(p_obj,r=True)
    cmds.delete(p_obj,constructionHistory=True)
    p_obj_shape = cmds.listRelatives(p_obj)[0]


    pre_currbr_transform = cmds.xform(p_obj,q=True,absolute=True,worldSpace=True,matrix=True)
    branch_angle = [round(pre_currbr_transform[0],6),round(pre_currbr_transform[2],6),round(pre_currbr_transform[1],6)]
#    branch_angle = [currbr_transform[0],(currbr_transform[1]*-1),currbr_transform[2]]
#    print branch_angle

    p_obj_all_uv = cmds.polyUVSet( query=True, allUVSets=True )
#    print o_obj_all_uv

    p_obj_vtc = cmds.ls((cmds.polyListComponentConversion((cmds.ls(flatten=True,sl=True)), toVertex=True)), fl=True)
#    print all_obj_vtc

    if branch_angle[2] < 0:
        zSign=-1.0
    else:
        zSign=1.0

    ba_x = round(((branch_angle[0] + 1.0) / 2.0) * 255.0,4)
    ba_y = round(((branch_angle[1] + 1.0) / 2.0) * 255.0,4)
    ba_z = round(((branch_angle[2] + 1.0) / 2.0) * 255.0,4)

    branch_angle2 = [ba_x,ba_y,ba_z]
    clamp_ba_x = round((max(min(branch_angle2[0],255),0)),4)
    branch_angle3 = [clamp_ba_x,branch_angle2[1],branch_angle2[2]]
#    print branch_angle3
    obj_vtc_alpha =  round(branch_angle3[0]/255.0,3)
#   print obj_vtc_alpha

    uv4_green = round((branch_angle3[1] * zSign)/255.0,3)

    curr_branch_pos = [round(pre_currbr_transform[12],4),round(pre_currbr_transform[14],4),round(pre_currbr_transform[13],4)]

    pre_branch_pos_x = curr_branch_pos[0] * 1
    pre_branch_pos_y = curr_branch_pos[1] * -1
    pre_branch_pos_z = curr_branch_pos[2] * 1

    curr_branch_pos2 = [pre_branch_pos_x,pre_branch_pos_y,pre_branch_pos_z]

    pre_temp_x = (curr_branch_pos2[0] / shaderWSMultiplier) * 128 + 128
    pre_temp_y = (curr_branch_pos2[1] / shaderWSMultiplier) * 128 + 128
    pre_temp_z = (curr_branch_pos2[2] / shaderWSMultiplier) * 255 + 0

    pre_temp_x2 = round(max(min(pre_temp_x, 255), 0)/255,4)
    pre_temp_y2 = round(max(min(pre_temp_y, 255), 0)/255,4)
    pre_temp_z2 = round(max(min(pre_temp_z, 255), 0)/255,4)

    branch_pos = [pre_temp_x2,pre_temp_y2,pre_temp_z2]

#    print branch_pos

    cmds.polyColorPerVertex(p_obj_vtc,rgb=branch_pos )
    cmds.polyColorPerVertex(p_obj_vtc,alpha=obj_vtc_alpha )

    map3_uv = [0,0,0]
    map4_uv = [0,uv4_green,0]

    if 'map1' in p_obj_all_uv:
        if 'UVChannel_1' in p_obj_all_uv:
            cmds.polyUVSet(p_obj_shape,delete=True,uvSet='UVChannel_1')
        if 'UVChannel_3' in p_obj_all_uv:
            cmds.polyUVSet(p_obj_shape,delete=True,uvSet='UVChannel_3')
        if 'UVChannel_4' in p_obj_all_uv:
            cmds.polyUVSet(p_obj_shape,delete=True,uvSet='UVChannel_4')
                       
        cmds.polyUVSet(p_obj_shape,currentUVSet=True,uvSet='map1')
        cmds.polyUVSet(p_obj_shape,perInstance=True,rename=True,newUVSet='UVChannel_1', uvSet='map1')
        cmds.polyUVSet(p_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_3')
        cmds.polyUVSet(p_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_4')

    if 'UVChannel_3' not in p_obj_all_uv:
        cmds.polyUVSet(p_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_3')

    cmds.polyUVSet(p_obj_shape,currentUVSet=True,uvSet='UVChannel_3')
    cmds.polyEditUV(p_obj_vtc,uvSetName="UVChannel_3",relative=False, uValue=map3_uv[0], vValue=map3_uv[1])

    if 'UVChannel_4' not in p_obj_all_uv:
        cmds.polyUVSet(p_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_4')

    cmds.polyUVSet(p_obj_shape,currentUVSet=True,uvSet='UVChannel_4')
    cmds.polyEditUV(p_obj_vtc,uvSetName="UVChannel_4",relative=False, uValue=map4_uv[0], vValue=map4_uv[1])

    cmds.polyUVSet(p_obj_shape,currentUVSet=True,uvSet='UVChannel_1')

# Child
    for curr_obj in c_selected_objs:
        cmds.select(clear=True)
        cmds.select(curr_obj,r=True)
        cmds.delete(curr_obj,constructionHistory=True)
        curr_obj_shape = cmds.listRelatives(curr_obj)[0]

        cmds.selectMode( component=True)
        cmds.selectMode( object=True )

        curr_obj_all_uv = cmds.polyUVSet( query=True, allUVSets=True )
#        print o_obj_all_uv

        curr_obj_vtc = cmds.ls((cmds.polyListComponentConversion((cmds.ls(flatten=True,sl=True)), toVertex=True)), fl=True)
#        print all_obj_vtc


        pre_pivot_pos = cmds.xform(curr_obj,q=True,absolute=True,worldSpace=True,translation=True)
        pivot_pos1 =[pre_pivot_pos[0]*255,pre_pivot_pos[2]*255*-1,pre_pivot_pos[1]*255]
#        print pivot_pos

        pivot_pos2=[math.ceil(pivot_pos1[0]),math.ceil(pivot_pos1[1]),math.ceil(pivot_pos1[2])]

        pre_curr_obj_transform = cmds.xform(curr_obj,q=True,absolute=True,worldSpace=True,matrix=True)
        curr_obj_transform = [round(pre_curr_obj_transform[0],6),round(pre_curr_obj_transform[2],6)*-1,round(pre_curr_obj_transform[1],6)]

        x_axis_x = round(((curr_obj_transform[0] * 0.5) + 0.5) * 255,4)
        x_axis_y = round(((curr_obj_transform[1] * 0.5) + 0.5) * 255,4)
        x_axis_z = round(((curr_obj_transform[2] * 0.5) + 0.5) * 255,4)

        x_axis = [x_axis_x,x_axis_y,x_axis_z]

        x_axis2 = [(max(min(x_axis[0], 240), 20)),(max(min(x_axis[1], 240), 20)),(max(min(x_axis[2], 240), 20))]

        if pivot_pos2[0] > 0:
            pivot_pos2[0] = pivot_pos2[0] + x_axis2[0]
        else:
            pivot_pos2[0] = pivot_pos2[0] - x_axis2[0]

        if pivot_pos2[1] > 0:
            pivot_pos2[1] = pivot_pos2[1] + x_axis2[1]
        else:
            pivot_pos2[1] = pivot_pos2[1] - x_axis2[1]

        if pivot_pos2[2] > 0:
            pivot_pos2[2] = pivot_pos2[2] + x_axis2[2]
        else:
            pivot_pos2[2] = pivot_pos2[2] - x_axis2[2]

        pivot_pos3 = [round((pivot_pos2[0] / 255),3),round((pivot_pos2[1] / 255),3),round((pivot_pos2[2] / 255),3)]

        cmds.polyColorPerVertex(curr_obj,rgb=branch_pos )
        cmds.polyColorPerVertex(curr_obj,alpha=obj_vtc_alpha )

        map3_uv2 = pivot_pos3
        map4_uv2 = [pivot_pos3[2],uv4_green,0]

        if 'map1' in curr_obj_all_uv:
            if 'UVChannel_1' in curr_obj_all_uv:
                cmds.polyUVSet(curr_obj_shape,delete=True,uvSet='UVChannel_1')
            if 'UVChannel_3' in curr_obj_all_uv:
                cmds.polyUVSet(curr_obj_shape,delete=True,uvSet='UVChannel_3')
            if 'UVChannel_4' in curr_obj_all_uv:
                cmds.polyUVSet(curr_obj_shape,delete=True,uvSet='UVChannel_4')

            cmds.polyUVSet(curr_obj_shape,currentUVSet=True,uvSet='map1')
            cmds.polyUVSet(curr_obj_shape,perInstance=True,rename=True,newUVSet='UVChannel_1', uvSet='map1')
            cmds.polyUVSet(curr_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_3')
            cmds.polyUVSet(curr_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_4')

        if 'UVChannel_3' not in curr_obj_all_uv:
            cmds.polyUVSet(curr_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_3')

        cmds.polyUVSet(curr_obj_shape,currentUVSet=True,uvSet='UVChannel_3')
        cmds.polyEditUV(curr_obj_vtc,uvSetName="UVChannel_3",relative=False, uValue=map3_uv2[0], vValue=map3_uv2[1])

        if 'UVChannel_4' not in curr_obj_all_uv:
            cmds.polyUVSet(curr_obj_shape,perInstance=True,copy=True,uvSet='UVChannel_1',newUVSet='UVChannel_4')

        cmds.polyUVSet(curr_obj_shape,currentUVSet=True,uvSet='UVChannel_4')
        cmds.polyEditUV(curr_obj_vtc,uvSetName="UVChannel_4",relative=False, uValue=map4_uv2[0], vValue=map4_uv2[1])

        cmds.polyUVSet(curr_obj_shape,currentUVSet=True,uvSet='UVChannel_1')


    cmds.select(clear=True)
    cmds.select(c_selected_objs,add=True)
    cmds.select(p_obj,add=True)

def optimize_on(*args):
    if cmds.floatField('per_pivm', q=True, enable=True):
        cmds.floatField('per_pivm', e=True, enable=False)
        cmds.floatField('per_pivc', e=True, enable=False)
        cmds.floatField('per_xmul', e=True, enable=False)
        cmds.floatField('per_xcon', e=True, enable=False)
        cmds.floatField('per_ymul', e=True, enable=False)
        cmds.floatField('per_ycon', e=True, enable=False)
        cmds.floatField('per_zmul', e=True, enable=False)
        cmds.floatField('per_zcon', e=True, enable=False)
    else:
        cmds.floatField('per_pivm', e=True, enable=True)
        cmds.floatField('per_pivc', e=True, enable=True)
        cmds.floatField('per_xmul', e=True, enable=True)
        cmds.floatField('per_xcon', e=True, enable=True)
        cmds.floatField('per_ymul', e=True, enable=True)
        cmds.floatField('per_ycon', e=True, enable=True)
        cmds.floatField('per_zmul', e=True, enable=True)
        cmds.floatField('per_zcon', e=True, enable=True)

def rotate_pivot(*args):
    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    c_all_selected = cmds.ls(sl=True)
    c_all_mesh = []

    for o_sel in c_all_selected:
        cmds.select(clear=True)
        o_sel_axis = cmds.getAttr(o_sel+'.rotateAxis')[0]
        o_sel_axis_sum = o_sel_axis[0] + o_sel_axis[1] + o_sel_axis[2]

#       Resset rotateAxis to Rotation 
        if o_sel_axis_sum != 0:
            o_piv_pos = cmds.xform(o_sel, q=True,worldSpace=True,pivots=True )
            cmds.setAttr(o_sel+'.rotateAxis',0,0,0)
            maya.mel.eval('PolySelectConvert 3;')
            cmds.rotate(o_sel_axis[0],o_sel_axis[1],o_sel_axis[2],o_sel,r=True,pivot=(o_piv_pos[0],o_piv_pos[1],o_piv_pos[2]),os=True,fo=True)

        cmds.select(o_sel,r=True)
        selList = OpenMaya.MSelectionList()
        selList.add(o_sel)
        mDagPath = OpenMaya.MDagPath()
        selList.getDagPath(0, mDagPath)

        transformFunc = OpenMaya.MFnTransform(mDagPath)
        iu0 = transformFunc.transformation().asMatrix()
        o_up = [0.0, 1.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]

        m1 = OpenMaya.MMatrix()

        mUtil = OpenMaya.MScriptUtil()
        mUtil.createMatrixFromList(o_up, m1)

        final_m = m1 * iu0

        mTransformMtx = OpenMaya.MTransformationMatrix(final_m)
        eulerRot = mTransformMtx.eulerRotation()
        angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]

        cmds.manipPivot(o=[angles[0],angles[1],angles[2]])

        if cmds.currentCtx() != 'moveSuperContext':cmds.setToolTo( 'moveSuperContext' )
        maya.mel.eval('performBakeCustomToolPivot 0;')

    cmds.select(clear=True)
    cmds.select(c_all_selected,r=True)

def make_h_xup(*args):
    if not cmds.ls( sl=True ):
        cmds.confirmDialog( title='ERROR', message='Select Polygon !_! ')
        sys.exit()

    c_all_selected = cmds.ls(sl=True)
    c_all_mesh = []

    for o_sel in c_all_selected:
        cmds.select(clear=True)
        o_sel_axis = cmds.getAttr(o_sel+'.rotateAxis')[0]
        o_sel_axis_sum = o_sel_axis[0] + o_sel_axis[1] + o_sel_axis[2]

#       Resset rotateAxis to Rotation 
        if o_sel_axis_sum != 0:
            o_piv_pos = cmds.xform(o_sel, q=True,worldSpace=True,pivots=True )
            cmds.setAttr(o_sel+'.rotateAxis',0,0,0)
            maya.mel.eval('PolySelectConvert 3;')
            cmds.rotate(o_sel_axis[0],o_sel_axis[1],o_sel_axis[2],o_sel,r=True,pivot=(o_piv_pos[0],o_piv_pos[1],o_piv_pos[2]),os=True,fo=True)

        cmds.select(o_sel,r=True)

        bbox = cmds.exactWorldBoundingBox(o_sel)
        center = [(bbox[0] + bbox[3])/2, (bbox[1] + bbox[4])/2, (bbox[2] + bbox[5])/2]
#        print center

        o_shape = cmds.ls(o_sel,dag=True, shapes=True)[0]
        o_bb_min = cmds.getAttr(o_shape + '.boundingBoxMin')[0]
        o_bb_max = cmds.getAttr(o_shape + '.boundingBoxMax')[0]
#        print o_bb_max

        p_min = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, o_bb_min[1], 0.0, 1.0]
        p_max = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, o_bb_max[1], 0.0, 1.0]
        o_up = [0.0, 1.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        o_up_minus = [0.0,-1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]

        if cmds.radioButtonGrp('up_type',q=True,select=True) != 1:
            p_min = p_max
            o_up = o_up_minus

        m0 = OpenMaya.MMatrix()
        m1 = OpenMaya.MMatrix()

        mUtil = OpenMaya.MScriptUtil()

        mUtil.createMatrixFromList(p_min, m0)
        mUtil.createMatrixFromList(o_up, m1)

        selList = OpenMaya.MSelectionList()
        selList.add(o_sel)
        mDagPath = OpenMaya.MDagPath()
        selList.getDagPath(0, mDagPath)

        transformFunc = OpenMaya.MFnTransform(mDagPath)
        iu0 = transformFunc.transformation().asMatrix()

        min_p0 = m0 * iu0
        min_p1 = m1 * iu0

        mList0 = []
        for x in range(4):
            for n in range(4):
                mList0.append(min_p0(x,n))

        cmds.move(min_p0(3,0),min_p0(3,1),min_p0(3,2),o_sel + '.scalePivot',o_sel + '.rotatePivot')

        mTransformMtx = OpenMaya.MTransformationMatrix(min_p1)
        eulerRot = mTransformMtx.eulerRotation()
        angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]

#        print angles
        cmds.manipPivot(o=[angles[0],angles[1],angles[2]])

        if cmds.currentCtx() != 'moveSuperContext':cmds.setToolTo( 'moveSuperContext' )
        maya.mel.eval('performBakeCustomToolPivot 0;')



def maya_pivot_painter_menu(*args):
    if cmds.window('MayaPivotPainter', exists=True):
        cmds.deleteUI('MayaPivotPainter')

    window = cmds.window('MayaPivotPainter', title='Maya Pivot Painter1  V4.2',sizeable=True, topLeftCorner=[200, 200], widthHeight=(300,170))
    form = cmds.formLayout(numberOfDivisions=100)
    left_space = cmds.text(label='',height=24)
    do_hipiv_button = cmds.button('do_par_child_pp',label='Do!! Hierarchy PivotPainter',width=150,height=25,bgc=[1.0,0.7,0.4],command=do_hiera_pp)
    right_space = cmds.text(label='',height=24)
    text_list = cmds.textScrollList('child_scroll',width=100,allowMultiSelection=True)
    column = cmds.columnLayout()

    cmds.columnLayout('main_column',columnAttach=('both', 5), rowSpacing=8, columnWidth=320, adjustableColumn=True)
    cmds.text(label='Maya PivotPainter1  for UE4    V4.2   @Ritaro',width=300,bgc=[0.0,0.0,0.0],align='center' )
    cmds.frameLayout('set_poly', label='Setup Polygon Tools ',bgc=[0.2,0.2,0.2],collapsable=True,collapse=False,parent="main_column")

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=2,height=18)
    cmds.text(label=' ',width=15)
    cmds.button('sepa_poly',label='Detach Selected Polygon (Separate)',width=150,height=20,bgc=[0.9,0.8,0.6],command=separate_polygon)
    cmds.text(label=' ',width=15)
    cmds.setParent('..',)

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=2,height=18)
    cmds.text(label=' ',width=25)
    cmds.button('rotate_up',label='Rotate Pivot ',width=150,height=16,bgc=[1.0,0.9,0.6],command=rotate_pivot)
    cmds.text(label=' ',width=25)
    cmds.setParent('..',)

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=2,height=18)
    cmds.text(label=' ',width=35)
    cmds.button('show_poly_vtc',label='Show On/Off Vertex Color ',width=130,height=14,bgc=[0.9,0.7,0.45],command=show_polyvtc)
    cmds.text(label=' ',width=35)
    cmds.setParent('..',)
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=2,height=18)
    cmds.text(label=' ',width=35)
    cmds.button('black_poly_vtc',label='Paint Black VertexColor (NoAnimation) ',width=130,height=16,bgc=[0.7,0.5,0.3],command=black_polyvtc)
    cmds.text(label=' ',width=35)
    cmds.setParent('..',)
    cmds.separator(height=3)
    
    cmds.frameLayout('PerPolygon',label='Per Polygon PivotPainter ',bgc=[0.2,0.2,0.2],collapsable=True,collapse=False,parent="main_column")
    cmds.text(label=' ',height=1)

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=2,height=18)
    cmds.text(label=' ',width=25)
    cmds.button('make_x_up',label='Make X-Up Pivot for Grass',width=150,height=16,bgc=[1.0,0.9,0.6],command=make_xup)
    cmds.text(label=' ',width=25)
    cmds.setParent('..',)

    cmds.rowLayout(numberOfColumns=4,adjustableColumn=4,height=18)
    cmds.checkBoxGrp('optimaze_check',columnWidth2=[0, 0],numberOfCheckBoxes=1,label='', v1=False,changeCommand1=optimize_on)
    cmds.text(label='Optimize for Foliage Placement',width=205,align='left',font="boldLabelFont")
    cmds.text(label='(No VertexColor)',width=100)
    cmds.text(label='',width=1)
    cmds.setParent('..',)
    cmds.separator(height=1)
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,height=18)
    cmds.text(label='3D dist to Piv Multiplier',width=180,height=18)
    cmds.floatField('per_pivm', minValue=-1000, maxValue=1000,value=0.5,width=70,height=18,precision=3)
    cmds.text(label=' ',width=30,height=18)
    cmds.setParent('..',)

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,height=18)
    cmds.text(label='  3D dist to Piv Contrast',width=180,height=18)
    cmds.floatField('per_pivc', minValue=-1000, maxValue=1000,value=1.0,width=70,height=18,precision=3)
    cmds.text(label=' ',width=30,height=18)
    cmds.setParent('..',)

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,height=18)
    cmds.text(label='   X Multiplier     ',width=180,align='right',height=18)
    cmds.floatField('per_xmul', minValue=-1000, maxValue=1000,value=0.0,width=70,height=18,precision=3)
    cmds.text(label=' ',width=30,height=18)
    cmds.setParent('..',)
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,height=18)
    cmds.text(label='   X Contrast     ',width=180,align='right',height=18)
    cmds.floatField('per_xcon', minValue=-1000, maxValue=1000,value=10.0,width=70,height=18,precision=3)
    cmds.text(label=' ',width=30,height=18)
    cmds.setParent('..',)

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,height=18)
    cmds.text(label='   Y Multiplier     ',width=180,align='right',height=18)
    cmds.floatField('per_ymul', minValue=-1000, maxValue=1000,value=0.0,width=70,height=18,precision=3)
    cmds.text(label=' ',width=30,height=18)
    cmds.setParent('..',)
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,height=18)
    cmds.text(label='   Y Contrast     ',width=180,align='right',height=18)
    cmds.floatField('per_ycon', minValue=-1000, maxValue=1000,value=10.0,width=70,height=18,precision=3)
    cmds.text(label=' ',width=30,height=18)
    cmds.setParent('..',)

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,height=18)
    cmds.text(label='   Z Multiplier     ',width=180,align='right',height=18)
    cmds.floatField('per_zmul', minValue=-1000, maxValue=1000,value=0.0,width=70,height=18,precision=3)
    cmds.text(label=' ',width=30,height=18)
    cmds.setParent('..',)
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,height=18)
    cmds.text(label='   Z Contrast     ',width=180,align='right',height=18)
    cmds.floatField('per_zcon', minValue=-1000, maxValue=1000,value=10.0,width=70,height=18,precision=3)
    cmds.text(label=' ',width=30,height=18)
    cmds.setParent('..',)

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=2)
    cmds.text(label=' ',width=10)
    cmds.button('do_inf_over',label='Do!! Per Polygon PivotPainter',width=150,height=25,bgc=[1.0,0.8,0.5],command=do_parpoly_pp)
    cmds.text(label=' ',width=10)
    cmds.setParent('..',)
    cmds.separator(height=3)

    cmds.frameLayout('hierarchy_piv',label='Hierarchy PivotPainter ',bgc=[0.2,0.2,0.2],collapsable=True,collapse=False,parent="main_column")

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=2,height=17)
    cmds.text(label=' ',width=50)
    cmds.radioButtonGrp('up_type',labelArray2=['Minimum Side', 'Maximum Side'], numberOfRadioButtons=2,select=1)
    cmds.text(label=' ',width=25)

    cmds.setParent('..',)    
    cmds.rowLayout(numberOfColumns=3,adjustableColumn=2,height=18)
    cmds.text(label=' ',width=25)
    cmds.button('makeh_x_up',label='Make X-Up Pivot for Branch (Use when Y-up)',width=90,height=18,bgc=[1.0,0.9,0.6],command=make_h_xup)
    cmds.text(label=' ',width=25)
    cmds.setParent('..',)
    cmds.rowLayout(numberOfColumns=4,adjustableColumn=4,height=18)
    cmds.checkBoxGrp('optimaze_checkh',columnWidth2=[0, 0],numberOfCheckBoxes=1,label='',v1=False)
    cmds.text(label='Optimize for Foliage Placement',width=205,align='left',font="boldLabelFont")
    cmds.text(label='(No VertexColor)',width=100)
    cmds.text(label='',width=1)
    cmds.setParent('..',)
    cmds.separator(height=1)
    cmds.textFieldButtonGrp('setting_parent',label='> Set A Parent ',text='',buttonLabel='SetParent',adjustableColumn=2,columnWidth3=[91,120,42],buttonCommand=set_parent)

    cmds.text(label='> SetAllChild     ',width=82,align='left' )
    cmds.rowLayout(numberOfColumns=8)
    cmds.text(label=' ',width=7)
    cmds.button('setting_child',label='Set ',width=40,height=20,bgc=[0.4,0.4,0.4],command=set_child)
    cmds.text(label=' ',width=7)
    cmds.button('adding_child',label='Add',width=40,height=20,bgc=[0.4,0.4,0.4],command=add_child)
    cmds.text(label=' ',width=7)
    cmds.button('sel_child_del',label='Delete Selected',width=100,height=20,bgc=[0.4,0.4,0.4],command=delete_sel_child)
    cmds.text(label=' ',width=7)
    cmds.button('setting_child2',label='Claer All',width=60,height=20,bgc=[0.4,0.4,0.4],command=reset_scroll)
    cmds.setParent('..',)

    cmds.rowLayout(numberOfColumns=3,adjustableColumn=3,height=18)
    cmds.text(label='Maximum dist for Parent Piv',width=190,height=18)
    cmds.intField('max_ppiv', minValue=1, maxValue=100000000,value=4096,width=80,height=18)
    cmds.text(label=' ',width=30,height=18)
    cmds.setParent('..',)

    cmds.formLayout( form, edit=True,
         attachForm=[
              (text_list, 'left', 5), (text_list, 'top', 0), (text_list, 'right', 5), (text_list, 'bottom', 10),
              (column, 'top', 5), (column, 'left', 5),
              (left_space, 'left', 0), (left_space, 'bottom', 0),
              (do_hipiv_button, 'bottom', 0), (do_hipiv_button, 'left',0),
              (right_space, 'bottom', 0), (right_space, 'right', 0)
              ],
         attachControl=[(text_list, 'top', 10,column ),(text_list, 'bottom', 0, left_space)],
         attachPosition=[(column, 'right', 0, 100),(left_space, 'right', 0, 10),(do_hipiv_button, 'left', 0, 10),(do_hipiv_button, 'right', 0, 90),(right_space, 'left', 0,100)],
         attachNone=[(left_space, 'top'),(do_hipiv_button, 'top'),(right_space, 'top')])

    cmds.showWindow( window )