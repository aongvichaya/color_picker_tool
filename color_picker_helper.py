import maya.cmds as cmds
import pymel.core as pm

from snow.common.lib import code_logging
from snow.maya.tools.assign_shade import assign_shade

logger = code_logging.create_log(__name__)   


def create_shader(shd_name, meshes, trans, node_type,color):
    """_function to create shader with or without transparency and assign it to selected geo_

    Args:
        shd_name (str): _name of shader using for read data from YAML and to use in create and assign shd_
        meshes (_str_): _to get the selected geometry or face_
        trans (bool): _To check if trans true it will set transparency attr but if not it will not set_
        node_type (str, optional): _type of shader to create and assign_. Defaults to "lambert".
    """    
    if not meshes:
        logger.warning('Please Select Geo Before Select Color')
        return
    
    # check have trans or not if trans == true set shadename as transparency shdname
    # check if shd_name already exist if not create and assign
    
    mat_name = '{}_{}_mat'.format(shd_name,node_type)
    if trans:
        mat_name = 'transparency_'+ mat_name
    
    if not cmds.objExists(mat_name):
        material = cmds.shadingNode(node_type, name=mat_name, asShader=True)
        shd_grp = cmds.sets(name='{0}.SG'.format(mat_name), empty=True, renderable=True, noSurfaceShader=True)
        cmds.connectAttr('{0}.outColor'.format(material), '{0}.surfaceShader'.format(shd_grp))
        cmds.setAttr('{0}.color'.format(material), color[0], color[1], color[2], type="double3")
        if trans:
            cmds.setAttr('{0}.transparency'.format(material), 0.5, 0.5, 0.5, type="double3")
        cmds.sets(meshes, forceElement=shd_grp)
        

    else:
    # select exists color shade node and assign to geo
        logger.info('[{}] Color is already created.'.format(shd_name))
        shd_grp = cmds.listConnections(mat_name,d=1,t='shadingEngine')
        cmds.sets(meshes,fe=shd_grp[0])


def delete_unused_nodes():
    """_to delete unused nodes_
    """
    logger.info('Deleting Unused Nodes')
    pm.mel.eval('MLdeleteUnused;')


def return_original_shd(*args):
    """Return to preview shade from reference
    """
    listObj=pm.ls(sl=True)[0]
    if 'Grp' in listObj:
        assign_shade.assign_to_selecting(shd_type="preview")       
    else : 
        assign_shade.assign_to_selecting(only_selected_geo=True, shd_type="preview")
    pass    
