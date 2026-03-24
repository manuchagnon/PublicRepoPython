# switch ik fk
######
#
#    Switch IK/FK
#
#    ce sript permet de créer un switch ik/ fk sur une chaine de bones et de créer les controler, les contraintes dans le node editor, etc
#
#    19/09/2025
#    v 003
#
######
from maya import cmds


###########################################################################


###########################################################################

class ribbon:
    def __init__(self, my_chain, my_name):

        ribbon.create_ribbon(my_chain, my_name)

    def create_surface(name, lenght):

        # créer une surface
        surface = cmds.nurbsPlane(name=f'{name}_srf', ax=[0, 1, 0], w=1, lr=lenght, d=3, u=1, v=1, ch=1)

        return surface[0]

    def create_flc(surface, flc_number):

        surface_name = surface

        flc_created = []

        flc_grp = cmds.group(name=f'flc_{surface_name}_grp', empty=1)

        # créer les follicules
        for flc_index in range(int(flc_number)):
            # parameterU
            parameter_u = 0.5
            # parameterV
            parameter_v = flc_index / (int(flc_number) - 1)  # espacement équidistant sur V

            # Créer le follicle node avec sa shape et son transform
            follicle_shape = cmds.createNode("follicle", name=f"flc_{surface_name}_{flc_index}Shape")

            follicle_transform = cmds.listRelatives(follicle_shape, parent=1)[0]
            cmds.rename(follicle_transform, f"flc_{surface_name}_{flc_index}")
            follicle_transform = f"flc_{surface_name}_{flc_index}"

            cmds.connectAttr(f"{surface}.local", f"{follicle_shape}.inputSurface", f=1)
            cmds.connectAttr(f"{surface}.worldMatrix[0]", f"{follicle_shape}.inputWorldMatrix", f=1)
            cmds.connectAttr(f"{follicle_shape}.outRotate", f"{follicle_transform}.rotate", f=1)
            cmds.connectAttr(f"{follicle_shape}.outTranslate", f"{follicle_transform}.translate", f=1)

            cmds.setAttr(f"{follicle_shape}.parameterU", parameter_u)
            cmds.setAttr(f"{follicle_shape}.parameterV", parameter_v)

            cmds.parent(follicle_transform, flc_grp)
            flc_created.append(follicle_transform)

        flc_joint_set = cmds.sets(name=f'{surface}_bind_set', empty=1)
        flc_joint_created = []

        for flc in flc_created:
            my_joint = cmds.joint(n=f'{flc}_bind_jnt')
            cmds.parent(my_joint, flc)
            cmds.xform(my_joint, os=1, t=[0, 0, 0])
            cmds.select(clear=1)
            cmds.sets(my_joint, add=flc_joint_set)
            flc_joint_created.append(my_joint)

        # group
        cmds.group(flc_created, n=f'{surface}_flc_grp')

        return flc_created, flc_joint_created

    def create_controler(list, scale, with_joint, my_name, parent):

        controler_created = []
        controler_grp_created = []
        joint_created = []

        for element_list in list:

            if my_name == []:
                controler_name = element_list
            else:
                controler_name = my_name + "list.index(element_list)-1"

            # créer un controler
            controler = cmds.circle(n=f'{element_list}_ctl', r=scale * .5, normal=[0, 0, 1], ch=0)
            cmds.select(clear=1)

            if with_joint == 1:
                joint = cmds.joint(n=f'{controler}_bind_jnt', r=scale * .2)
                cmds.parent(joint, controler)
                cmds.select(clear=1)
                joint_created.append(joint.split('|')[-1])

            # group
            controler_ZRO_group = cmds.group(controler, n=f'{controler}_ZRO_grp')

            # parenter et déplacer
            if parent == 1:
                cmds.parent(controler_ZRO_group, element_list)
                cmds.xform(controler_ZRO_group, os=1, t=[0, 0, 0])
            # ou juste déplacer
            elif parent == 0:
                pos = cmds.xform(element_list, q=1, ws=1, t=1)
                print(pos, " c'est la pos de la element_list dans world")
                cmds.xform(controler_ZRO_group, ws=1, t=pos)

            controler_created.append(controler[0])
            controler_grp_created.append(controler_ZRO_group)

        # group
        cmds.group(controler_grp_created, n=f'{controler}_grp')

        return controler_created, controler_grp_created, joint_created

    def create_ribbon(my_chain, my_name):

        if my_chain == []:
            articulations_number = int(cmds.textField("articulations_number_textfield", q=1, text=1))  #####
            ribbon_scale = int(cmds.textField("ctl_scale", q=1, text=1)) or 1
            my_range = articulations_number + 2
        else:
            my_range = len(my_chain)
            articulations_number = 1
            ribbon_scale = 2
        print(my_range)

        # on crée des locators qui créent une chain
        locator_chain = []
        for locator_index in range(0, my_range):
            locator_pos = [0, 0, locator_index * 2 * ribbon_scale]
            locator = cmds.spaceLocator(n=f"surface_locator_{locator_index + 1}", p=[0, 0, 0])
            cmds.xform(locator, ws=1, t=locator_pos)
            # cmds.CenterPivot(locator, apply = 1)
            locator_chain.append(locator)
            if locator_index >= 1:
                cmds.parent(locator, locator_chain[locator_index - 1])

        # créer plusieurs surfaces et les attacher
        # surface créées
        surface_created = []

        for locator_index in range(0, len(locator_chain)):
            # index
            locator = locator_chain[locator_index]

            # si ce n'est pas le bout de la locator_chain
            if locator_index < len(locator_chain) - 1:

                length = 2 * ribbon_scale

                my_surface = ribbon.create_surface(my_name, length)

                surface_created.append(my_surface)

                # pos_middle = locator_duo_index*0.5*(surface_scale*2)
                # pos_middle = [0,0,0]

                # déplacer la surface
                cmds.delete(cmds.pointConstraint(locator, locator_chain[locator_index + 1], my_surface))
                cmds.delete(cmds.orientConstraint(locator, my_surface))

                print(surface_created)

                if locator_index >= 1:
                    surface_attached = cmds.attachSurface(my_surface, surface_created[locator_index - 1], ch=1, rpo=1,
                                                          kmk=1, m=1, bb=1, bki=1, p=0.1)
                    cmds.delete(surface_attached, ch=1)

        # supprimer les surfaces inutiles
        for surface_index in range(0, len(surface_created) - 1):
            cmds.delete(surface_created[surface_index])
            print(f'la surface {surface_created[surface_index]} est supprimée')
        # inverser la direction de la surface
        cmds.reverseSurface(my_surface, d=1, ch=1, rpo=1)
        print(my_surface, " is my_surface")

        # deformers sur la surface
        deformer_grp = cmds.group(em=1, n=f'{my_surface}_deformer')

        if int(cmds.checkBox("sine_toggle", q=1, value=1)) == 1:
            print("sine deformer : ON")
            sine, sine_handle = cmds.nonLinear(my_surface, type="sine")
            cmds.rotate(90, 0, 90, sine_handle, r=1, os=1, cp=1)
            cmds.parent(sine_handle, deformer_grp)
        '''    
        if cmds.checkBox(wave_checkbox, q=1, value=1) == 1 :
            print("wave deformer : ON")
            wave, wave_handle = cmds.nonLinear(my_surface, type = "wave")
            cmds.rotate(90,0,90, wave_handle, r=1, os=1, cp=1)
            cmds.parent(wave_handle, deformer_grp)
        '''

        if not cmds.listRelatives(deformer_grp, children=1, ad=1):
            cmds.delete(deformer_grp)

        # créer les follicules sur la surface
        flc_number = int(cmds.textField("flc_number_textfield", q=1, text=1))
        articulations_number = len(my_chain) - 2
        # articulations_number = int(cmds.textField(articulations_number_textfield, q=1, text=1))

        flc_amount = articulations_number * 2 + 3

        flc_amount = flc_amount + (flc_amount - 1) * (flc_number - 1)

        # fonction crée les follicles
        flc_created, flc_joint_created = ribbon.create_flc(my_surface, flc_amount)

        # créer les controlers principaux de l'articulation
        # controler_main_created, controler_main_grp_created, no_joint_created = create_controler(locator_chain, ribbon_scale*1.5, 0, my_name, parent = 0)

        # créer les controler_offset et les joints de la surface aux endroits des follicules / flc_number
        controler_offset_pos = []
        for i in range(0, len(flc_created)):
            if i % flc_number == 0:
                controler_offset_pos.append(flc_created[i])

        controler_offset_created, controler_offset_grp_created, joint_surface_created = ribbon.create_controler(
            controler_offset_pos, ribbon_scale, with_joint=1, my_name=[], parent=0)
        print(joint_surface_created, " est la liste des joints a bind sur la ruface")

        # skinner le ribbon
        skin_cluster = cmds.skinCluster(joint_surface_created, my_surface, n=f'{my_surface}_skin', maximumInfluences=4,
                                        dropoffRate=3.0, obeyMaxInfluences=1)[0]

        '''
        #version avec les controler main
        for controler_offset, controler_offset_grp in zip(controler_offset_created, controler_offset_grp_created) :
            #créer les contraintes matrix entre les controler main et les controler offset

            if controler_offset_created.index(controler_offset) % 2 == 0 :
                print(controler_offset, "pair")
                main_controler = controler_main_created[ int( controler_offset_grp_created.index(controler_offset_grp) * 0.5 ) ]
                #créer les nodes matrix
                mult_matrix = cmds.createNode("multMatrix", n=f'{controler_offset_grp}_mult')
                decompose_matrix = cmds.createNode("decomposeMatrix", n=f'{controler_offset_grp}_decompose')

                #connecter les contraintes matrix
                cmds.connectAttr(f'{main_controler}.worldMatrix[0]', f'{mult_matrix}.matrixIn[0]', f=1)
                cmds.connectAttr(f'{controler_offset_grp}.parentInverseMatrix[0]', f'{mult_matrix}.matrixIn[1]', f=1)

                cmds.connectAttr(f'{mult_matrix}.matrixSum', f'{decompose_matrix}.inputMatrix')

                cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{controler_offset_grp}.translate')
                cmds.connectAttr(f'{decompose_matrix}.outputRotate', f'{controler_offset_grp}.rotate')

            #créer les contraintes matrix entre les controler offset et ses voisins            
            else :
                print(controler_offset, "impair")
                controler_offset_start = f"{controler_offset_created[controler_offset_created.index(controler_offset)-1]}"
                print(controler_offset_start,"is start")
                controler_offset_end = f"{controler_offset_created[controler_offset_created.index(controler_offset)+1]}"
                print(controler_offset_end,"is end")

                #créer les nodes pour point matrix
                mult_matrix_start = cmds.createNode("multMatrix", n=f'{controler_offset}_mult_start')
                mult_matrix_end = cmds.createNode("multMatrix", n=f'{controler_offset}_mult_end')
                decompose_matrix = cmds.createNode("decomposeMatrix", n=f'{controler_offset}_decompose')
                blend_matrix = cmds.createNode("blendMatrix", n=f'{controler_offset}_blend')

                #connecter les contraintes point matrix
                cmds.connectAttr(f'{controler_offset_start}.worldMatrix[0]', f'{blend_matrix}.inputMatrix', f=1)
                cmds.connectAttr(f'{controler_offset_end}.worldMatrix[0]', f'{blend_matrix}.target[0].targetMatrix', f=1) 
                cmds.setAttr(f'{blend_matrix}.envelope', 0.5)
                cmds.connectAttr(f'{blend_matrix}.outputMatrix', f'{decompose_matrix}.inputMatrix')
                cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{controler_offset_grp}.translate')

                #aim constraint
                aim_matrix_target = controler_offset_start
                cmds.aimConstraint(aim_matrix_target, controler_offset_grp, mo = 1, weight = 1, aimVector =[0, 0,-1], upVector = [0, 1, 0], worldUpType = "none")
        '''
        for controler_offset, controler_offset_grp in zip(controler_offset_created, controler_offset_grp_created):
            # créer les contraintes matrix entre les joints et les controler offset grp
            if controler_offset_created.index(controler_offset) % 2 == 0:

                print(controler_offset, "pair")
                joint = my_chain[int(controler_offset_grp_created.index(
                    controler_offset_grp) * 0.5)]  # va chercher le joint dans la list des joints
                # créer les nodes matrix
                mult_matrix = cmds.createNode("multMatrix", n=f'{controler_offset}_mult')
                decompose_matrix = cmds.createNode("decomposeMatrix", n=f'{controler_offset_grp}_decompose')

                # connecter les contraintes matrix
                cmds.connectAttr(f'{joint}.worldMatrix[0]', f'{mult_matrix}.matrixIn[0]', f=1)
                cmds.connectAttr(f'{controler_offset_grp}.parentInverseMatrix[0]', f'{mult_matrix}.matrixIn[1]', f=1)

                cmds.connectAttr(f'{mult_matrix}.matrixSum', f'{decompose_matrix}.inputMatrix')

                cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{controler_offset_grp}.translate')
                cmds.connectAttr(f'{decompose_matrix}.outputRotate', f'{controler_offset_grp}.rotate')

            # créer les contraintes matrix entre les controler offset et ses voisins avec blend matrix
            else:
                print(controler_offset, "impair")
                controler_offset_start = f"{controler_offset_created[controler_offset_created.index(controler_offset) - 1]}"
                print(controler_offset_start, "is start")
                controler_offset_end = f"{controler_offset_created[controler_offset_created.index(controler_offset) + 1]}"
                print(controler_offset_end, "is end")

                # créer les nodes pour point matrix
                mult_matrix_start = cmds.createNode("multMatrix", n=f'{controler_offset}_mult_start')
                mult_matrix_end = cmds.createNode("multMatrix", n=f'{controler_offset}_mult_end')
                decompose_matrix = cmds.createNode("decomposeMatrix", n=f'{controler_offset}_decompose')
                blend_matrix = cmds.createNode("blendMatrix", n=f'{controler_offset}_blend')

                # connecter les contraintes point matrix
                cmds.connectAttr(f'{controler_offset_start}.worldMatrix[0]', f'{blend_matrix}.inputMatrix', f=1)
                cmds.connectAttr(f'{controler_offset_end}.worldMatrix[0]', f'{blend_matrix}.target[0].targetMatrix',
                                 f=1)
                cmds.setAttr(f'{blend_matrix}.envelope', 0.5)
                cmds.connectAttr(f'{blend_matrix}.outputMatrix', f'{decompose_matrix}.inputMatrix')
                cmds.connectAttr(f'{decompose_matrix}.outputTranslate', f'{controler_offset_grp}.translate')

                # aim constraint
                aim_matrix_target = controler_offset_start
                # cmds.aimConstraint(aim_matrix_target, controler_offset_grp, mo = 1, weight = 1, aimVector =[0, 0,-1], upVector = [0, 1, 0], worldUpType = "none")
                cmds.aimConstraint(aim_matrix_target, controler_offset_grp, weight=1, aimVector=[0, 0, -1],
                                   upVector=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0],
                                   worldUpObject=f'{aim_matrix_target}')

        # mettre des groupes constraints sur les controlers offsets qui sont au niveau des articulations

        # parent constraints avec les joints de la joint_chain

        return flc_created, my_surface


###########################################################################

class ik_fk:
    def __init__(self, joint_chain, ribbon):
        created = []

        symetrize = 0

        ik_fk.create_IK_FK_switch(joint_chain, ribbon)

    def duplicate_chain(chain, type):

        duplicated_list = []

        for chain_element in chain:
            # index
            element_index = chain.index(chain_element)

            chain_element_pos = cmds.xform(chain_element, ws=1, q=1, t=1)
            chain_element_rot = cmds.xform(chain_element, ws=1, q=1, ro=1)

            if cmds.objectType(chain_element) == "joint":
                cmds.select(clear=True)
                duplicated_element = cmds.joint(name=f'{chain_element}_{type}')
                cmds.delete(cmds.parentConstraint(chain_element, duplicated_element))
                cmds.makeIdentity(duplicated_element, apply=1, t=1, r=1, s=1)
            else:
                print("pas joint")

            duplicated_list.append(duplicated_element)

            # parenter
            if element_index > 0:
                print(f'je veux parenter {duplicated_list[element_index]} à {duplicated_list[element_index - 1]}')
                cmds.parent(duplicated_list[element_index], duplicated_list[element_index - 1])

        return duplicated_list

    def duplicate_joint_chain(joint_chain, type):

        duplicated_joint_chain = ik_fk.duplicate_chain(joint_chain, type)

        for duplicated_joint, joint in zip(duplicated_joint_chain, joint_chain):
            # index
            joint_index = duplicated_joint_chain.index(duplicated_joint)
            # nouveau nom avec le type IK ou Fk
            new_name = cmds.rename(duplicated_joint, f'{joint}_{type}')
            # j'enlève l'ancien de la list et je le remet avec le nouveau nom
            duplicated_joint_chain.pop(joint_index)
            duplicated_joint_chain.insert(joint_index, new_name)

        duplicated_group = cmds.group(duplicated_joint_chain[0], name=f'{joint_chain[0]}_{type}_grp')
        # si le groupe IK ou FK est dans une hiérarchie, l'enlever
        if cmds.listRelatives(duplicated_group, parent=1):
            cmds.parent(duplicated_group, world=1)

        cmds.setAttr(f'{duplicated_group}.visibility', 0)

        # liste retournée
        print(f'la liste joint_chain_{type} : {duplicated_joint_chain}')

        return duplicated_joint_chain, duplicated_group

    def create_FK(joint_chain, offset_pos, controler_normal):
        if cmds.textField("ctl_scale", q=1, text=1):
            radius = int(cmds.textField("ctl_scale", q=1, text=1)) or 1
        else:
            radius = 1

            # dupliquer la joint_chain de base
        joint_chain_FK, FK_group = ik_fk.duplicate_joint_chain(joint_chain, type="FK")

        controler_created = []
        controler_ZRO_grp_created = []

        # créer le set de selection
        FK_set = cmds.sets(name=f'{joint_chain_FK[0]}_set', empty=1)

        # créer les controler et leur group
        for joint in joint_chain_FK:

            # créer le controler et son ZRO_grp au dessus
            controler = cmds.circle(name=f"ctl_{joint}", normal=controler_normal, radius=radius)
            cmds.delete(controler, constructionHistory=True)
            controler_ZRO_grp = cmds.group(controler[0], name=f"{joint}_ZRO_grp")

            # ajout dans les listes des controler et controler ZRO_grp
            controler_created.append(controler[0])
            controler_ZRO_grp_created.append(controler_ZRO_grp)

            # ajouter le controler au set de selection
            cmds.sets(controler[0], add=FK_set)

            cmds.delete(cmds.parentConstraint(joint, controler_ZRO_grp))

            """
            #positionner
            joint_pos = cmds.xform(joint, q=1, ws=1, t=1)
            #additionnezr la pos du joint et un offset
            controler_offset_pos = [joint_pos[0] + offset_pos[0], joint_pos[1] + offset_pos[1], joint_pos[2] + offset_pos[2]]

            #orienter
            joint_rot = cmds.xform(joint, q=1, ws=1, ro=1)

            print(f'le controler {controler[0]} a pos = {joint_pos} et rot = {joint_rot}')

            #appliquer la pos et la rot au ZRO_grp du controler
            cmds.xform(controler_ZRO_grp, ws=1, t = controler_offset_pos, ro = joint_rot)
            """
            # index
            controler_index = joint_chain_FK.index(joint)

            # parenter
            if controler_index > 0:
                print(
                    f'je veux parenter {controler_ZRO_grp_created[controler_index]} à {controler_created[controler_index - 1]}')
                cmds.parent(controler_ZRO_grp_created[controler_index], controler_created[controler_index - 1])

            # contraindre les joints
            cmds.connectAttr(f'{controler_created[controler_index]}.rotate', f'{joint}.rotate')

        return controler_created, controler_ZRO_grp_created, joint_chain_FK, FK_group

    def create_IK(joint_chain, IK_handle_name, pole_vector):
        if cmds.textField("ctl_scale", q=1, text=1):
            radius = int(cmds.textField("ctl_scale", q=1, text=1)) or 1
        else:
            radius = 1
        joint_chain_IK, IK_group = ik_fk.duplicate_joint_chain(joint_chain, type="IK")

        IK_handle = cmds.ikHandle(name=IK_handle_name, sj=joint_chain_IK[0], ee=joint_chain_IK[-1], sol='ikRPsolver')
        cmds.setAttr(f'{IK_handle[0]}.visibility', 0)

        # controler en forme de cube
        # cube_points = [0.5, 0.5, 0.5],[0.5, 0.5, -0.5],[-0.5, 0.5, -0.5],[-0.5, -0.5, -0.5],[0.5, -0.5, -0.5],[0.5, 0.5, -0.5],[-0.5, 0.5, -0.5],[-0.5, 0.5, 0.5],[0.5, 0.5, 0.5],[0.5, -0.5, 0.5],[0.5, -0.5, -0.5],[-0.5, -0.5, -0.5],[-0.5, -0.5, 0.5],[0.5, -0.5, 0.5],[-0.5, -0.5, 0.5],[-0.5, 0.5, 0.5]
        cube_points = [0.5 * radius, 0.5 * radius, 0.5 * radius], [0.5 * radius, 0.5 * radius, -0.5 * radius], [
            -0.5 * radius, 0.5 * radius, -0.5 * radius], [-0.5 * radius, -0.5 * radius, -0.5 * radius], [0.5 * radius,
                                                                                                         -0.5 * radius,
                                                                                                         -0.5 * radius], [
            0.5 * radius, 0.5 * radius, -0.5 * radius], [-0.5 * radius, 0.5 * radius, -0.5 * radius], [-0.5 * radius,
                                                                                                       0.5 * radius,
                                                                                                       0.5 * radius], [
            0.5 * radius, 0.5 * radius, 0.5 * radius], [0.5 * radius, -0.5 * radius, 0.5 * radius], [0.5 * radius,
                                                                                                     -0.5 * radius,
                                                                                                     -0.5 * radius], [
            -0.5 * radius, -0.5 * radius, -0.5 * radius], [-0.5 * radius, -0.5 * radius, 0.5 * radius], [0.5 * radius,
                                                                                                         -0.5 * radius,
                                                                                                         0.5 * radius], [
            -0.5 * radius, -0.5 * radius, 0.5 * radius], [-0.5 * radius, 0.5 * radius, 0.5 * radius]
        IK_controler = cmds.curve(d=1, p=cube_points, name=f'{IK_handle_name}_controler')
        IK_controler_ZRO_grp = cmds.group(IK_controler, name=f'{IK_controler}_ZRO_grp')

        # déplacer le ZRO_grp du controler sur la ik_handle
        IK_handle_pos = cmds.xform(IK_handle[0], ws=1, q=1, t=1)
        IK_handle_rot = cmds.xform(IK_handle[0], ws=1, q=1, ro=1)
        cmds.xform(IK_controler_ZRO_grp, ws=1, t=IK_handle_pos, ro=IK_handle_rot)

        cmds.parent(IK_handle[0], IK_controler)

        if cmds.checkBox("opposite_ik_controler", q=1, value=1):
            cmds.setAttr(f'{IK_controler_ZRO_grp}.scaleX', -1)
        '''    
        #pole vector
        pole_vector_amount = len(joint_chain) % 3
        for i in range(1, pole_vector_amount)
            ctl_pole = cmds.circle(n= f'{joint_chain[i-1]}_pole_vector', radius = radius*0.5)
            ctl_pole_grp = cmds.group(n=f'{ctl_pole}_ZRO_grp', e=1)
            cmds.parent(ctl_pole, ctl_pole_grp)
        '''

        return IK_handle, IK_controler, IK_controler_ZRO_grp, joint_chain_IK, IK_group

    def create_switch_IK_FK(joint_chain, joint_chain_IK, joint_chain_FK, IK_group, FK_group, IK_controler_ZRO_grp):
        if cmds.textField("ctl_scale", q=1, text=1):
            offset_pos = int(cmds.textField("ctl_scale", q=1, text=1))
        else:
            offset_pos = 1

            # créer le controler contenant l'attribut switch IK/FK
        switch_controler = cmds.circle(name=f'{joint_chain[0]}_switch_IK_FK', radius=offset_pos, normal=[1, 0, 0])
        cmds.delete(switch_controler, constructionHistory=True)
        switch_controler.remove(switch_controler[1])

        switch_controler_ZRO_grp = cmds.group(switch_controler, name=f'{switch_controler}_ZRO_grp')
        switch_controler_pos = cmds.xform(joint_chain[0], ws=1, q=1, t=1)

        switch_controler_offset_pos = [switch_controler_pos[0], switch_controler_pos[1] + offset_pos * offset_pos,
                                       switch_controler_pos[2]]

        cmds.xform(switch_controler_ZRO_grp, ws=1, t=switch_controler_offset_pos)

        # vérouiller les transform du switch_controler
        cmds.setAttr(f'{switch_controler[0]}.tx', lock=1)
        cmds.setAttr(f'{switch_controler[0]}.ty', lock=1)
        cmds.setAttr(f'{switch_controler[0]}.tz', lock=1)
        cmds.setAttr(f'{switch_controler[0]}.rx', lock=1)
        cmds.setAttr(f'{switch_controler[0]}.ry', lock=1)
        cmds.setAttr(f'{switch_controler[0]}.rz', lock=1)
        cmds.setAttr(f'{switch_controler[0]}.sx', lock=1)
        cmds.setAttr(f'{switch_controler[0]}.sy', lock=1)
        cmds.setAttr(f'{switch_controler[0]}.sz', lock=1)

        # créer un nouveau attribut switch_IK_FK
        cmds.addAttr(switch_controler[0], ln="switch_IK_FK", at="float", keyable=1, min=0, max=1, dv=0)

        node_created = []

        # connecter les attributs
        for joint_IK, joint_FK, joint in zip(joint_chain_IK, joint_chain_FK, joint_chain):
            print(f"le joint IK '{joint_IK}' et le joint FK '{joint_FK}' vont influencer le joint {joint}")
            # créer le pair_blend
            pair_blend = cmds.shadingNode("pairBlend", asUtility=1, name=f'{joint}_pairBlend')

            # connect les rotates au pair_blend
            cmds.connectAttr(f'{joint_FK}.rotate', f'{pair_blend}.inRotate1')
            cmds.connectAttr(f'{joint_IK}.rotate', f'{pair_blend}.inRotate2')
            cmds.connectAttr(f'{pair_blend}.outRotate', f'{joint}.rotate')

            # connect l'attribut du switch_IK_FK à la weight du pairblend
            cmds.connectAttr(f'{switch_controler[0]}.switch_IK_FK', f'{pair_blend}.weight')

            node_created.append(pair_blend)

        # créer node condition pour interpréter l'attribut du switch_IK_FK
        inverse_attribut = cmds.shadingNode("condition", asUtility=1, name=f'{switch_controler}_condition')
        cmds.connectAttr(f'{switch_controler[0]}.switch_IK_FK', f'{inverse_attribut}.firstTerm')
        cmds.setAttr(f'{inverse_attribut}.operation', 5)
        cmds.setAttr(f'{inverse_attribut}.secondTerm', 0.5)
        cmds.setAttr(f'{inverse_attribut}.colorIfTrueR', 1)
        cmds.setAttr(f'{inverse_attribut}.colorIfFalseR', 0)

        # connecter l'attribut visibility des objets FK
        cmds.connectAttr(f'{inverse_attribut}.outColorR', f'{joint_chain[0]}_FK_ZRO_grp.visibility')

        # connecter l'attribut visibility des objets IK
        cmds.connectAttr(f'{inverse_attribut}.outColorG', f'{IK_controler_ZRO_grp}.visibility')

        return node_created, switch_controler, switch_controler_ZRO_grp

    def create_IK_FK_switch(joint_chain, ribbon_toggle):
        if not joint_chain:
            print("please select a joint chain before executing the script")

            return

        # enlève la sélection
        cmds.select(clear=1)

        # la FK chain
        controler_created, controler_ZRO_grp_created, joint_chain_FK, FK_group = ik_fk.create_FK(joint_chain,
                                                                                                 offset_pos=[0, 0, 0],
                                                                                                 controler_normal=[1, 0,
                                                                                                                   0])

        # la IK_chain
        IK_handle, IK_controler, IK_controler_ZRO_grp, joint_chain_IK, IK_group = ik_fk.create_IK(joint_chain,
                                                                                                  IK_handle_name=f'{joint_chain[-1]}_IK_handle',
                                                                                                  pole_vector=0)

        # le controler switch et relier les attributs
        node_created, switch_controler, switch_controler_ZRO_grp = ik_fk.create_switch_IK_FK(joint_chain,
                                                                                             joint_chain_IK,
                                                                                             joint_chain_FK, IK_group,
                                                                                             FK_group,
                                                                                             IK_controler_ZRO_grp)

        # la fonction ribbon
        if ribbon_toggle == 1:

            my_name = cmds.textField("my_name", q=1, text=1) or "srf1"

            flc_created, surface_created = ribbon.create_ribbon(joint_chain, my_name)

        else:
            print("no ribbon")


###########################################################################

# création de la window

def ui():
    # supprimer la window si elle existe deja
    if cmds.window("Switch_IK_FK", exists=1):
        cmds.deleteUI("Switch_IK_FK")

    window = cmds.window("Switch_IK_FK", title="Switch_IK_FK", width=520)
    cmds.columnLayout(adjustableColumn=2)

    cmds.rowColumnLayout(numberOfColumns=2, columnAlign=(100, "left"), columnWidth=[(1, 240), (2, 240)])
    cmds.setParent('..')
    cmds.showWindow(window)

    #########################################################################

    # layout de la window
    space = 10

    # title
    cmds.text(label="Switch_IK_FK", height=50, align="center")

    cmds.separator(height=space * 2, style="in")

    # sélectionner les joints dans un premier temps
    cmds.text(label="Select the first to the last joint of a joint chain to execute the switch IK/FK script",
              align='center')

    cmds.separator(height=space * 2, style="none")

    # paramètres controlers
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(120, 150, 100))
    cmds.text(label="Scale of all controlers : ", align="center")
    ctl_scale_textfield = cmds.textField("ctl_scale", placeholderText="1")
    opposite_ik_controler = cmds.checkBox("opposite_ik_controler", label="opposite ik controler", value=False)

    cmds.setParent('..')
    cmds.separator(height=space * .5, style="none")

    # apppliquer le script sur cette joint chain
    cmds.button(label="Apply Switch IK/FK", bgc=(0.2, 0.6, 0.25),
                command=lambda *_: ik_fk.create_IK_FK_switch(cmds.ls(sl=1), ribbon_toggle=0))
    cmds.separator(height=space, style="none")

    # ribbon
    cmds.text(label="Switch_IK_FK with Ribbon", height=50, align="center")

    cmds.separator(height=space * 2, style="in")
    # paramétrage ribbon
    # with_ribbon_checkbox = cmds.checkBox("with_ribbon", label="With Ribbon", value=0)

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(150, 150))
    cmds.text(label="Name of the chain : ", align='left')
    my_name_textfield = cmds.textField("my_name", placeholderText="srf1")
    cmds.setParent('..')
    cmds.separator(height=space, style="none")

    cmds.text(label="Ribbon deformers : ", align='left')
    sine_toggle_checkbox = cmds.checkBox("sine_toggle", label="sine deformer", value=0)

    cmds.separator(height=space, style="none")

    # follicules joint pour bind
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(140, 140))
    cmds.text(label="Quantity of follicle joints : ", align='left')
    flc_number_textfield = cmds.textField("flc_number_textfield", placeholderText="flc joints")

    cmds.setParent('..')
    cmds.separator(height=space, style="none")
    cmds.button(label="Apply Switch IK/FK with Ribbon", bgc=(0.2, 0.6, 0.25),
                command=lambda *_: ik_fk.create_IK_FK_switch(cmds.ls(sl=1), ribbon_toggle=1))

    # infos
    cmds.text(label="v.03 24/09/2025 Emmanuel Chagnon", height=space * 5, align="center")


ui()





