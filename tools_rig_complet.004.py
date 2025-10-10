from maya import cmds

######
#
#    RIG Tools
#    
#    ce script est le début d'un outil persos avec beaucoup de fonctions utiles en rig que j'utilise souvent
#        -onglet follicle v 001
#        -onglet ribbon v 001
#        -onglet controler v 001
#        -onglet joint v 001
#        -onglet group v 001
#
#    Emmanuel Chagnon
#    08/09/2025
#    v 001
#
######

###########################################################################


class math :
    def __init__(self, *_):
        
        
        return 
    
    def remap_value(x, old_start, old_end, new_start, new_end):
        return new_start + ((x - old_start) / (old_end - old_start)) * (new_end - new_start)            

class group :
    def __init__(self, *_):

        return 
   
    def add_group(list, suffix, guizmo):
        print("guizmo =",guizmo)
        grp_created = []
        
        for element in list :
            grp = cmds.group(n=f'{element}_{suffix}_grp', empty = 1)
            
            pos = cmds.xform(element, q=1, ws=1, t=1)
            rot = cmds.xform(element, q=1, ws=1, rotation=1)
            cmds.xform(grp, ws=1, t=pos, rotation=rot)
            
            if cmds.listRelatives(element, parent=1) :
                element_parent = cmds.listRelatives(element, parent=1)
                cmds.parent(grp, element_parent)
                        
            cmds.parent(element, grp)
            
            print("guizmo =",guizmo)
            
            if guizmo == "world" :
                cmds.xform(f'{grp}.scalePivot', ws=1, t=[0,0,0], ro=[0,0,0])
                cmds.xform(f'{grp}.rotatePivot', ws=1, t=[0,0,0], ro=[0,0,0])
                
            elif guizmo :

                pos = cmds.xform(guizmo, q=1, ws=1, t=1)
                rot = cmds.xform(guizmo, q=1, ws=1, ro=1)
                print("rot =",rot,"pos = ",pos)
                cmds.xform(f'{grp}.scalePivot', ws=1, t= pos, ro=rot)
                cmds.xform(f'{grp}.rotatePivot', ws=1, t= pos, ro= rot)
                 
            
            grp_created.append(grp)
            
        return grp_created
        
    def parameter_group(self,*_):
        
        list = cmds.ls(sl=1)
        
        if cmds.textField("grp_suffix", q=1, text=1) :
            suffix = cmds.textField("grp_suffix", q=1, text=1)
        else :
            suffix = ''
        
        guizmo = None  
        if cmds.checkBox("guizmo_origin", q=1, value=1) == 1:
            guizmo = "world"
        elif cmds.checkBox("guizmo_onto", q=1, value=1) == 1:
            if cmds.textField("grp_guizmo", q=1, text=1):
                guizmo = cmds.textField("grp_guizmo", q=1, text=1)

        group.add_group(list, suffix, guizmo)
    
class joint :
    def __init__(self, *_):
        joint.add_jnt(cmds.ls(sl=1), parent=1) 
        
        return 
        
        
        
    def add_jnt(list, parent):
        cmds.select(clear=1)
        jnt_created = []
        for element in list :
            
            if "_" in element :
                element_name = element.split('_', 1)[1]
            else :
                element_name = element   
                
            jnt = cmds.joint(n=f'jnt_{element_name}')
            
            if parent == 1 :
                cmds.parent(jnt, element)
                cmds.xform(jnt, t=[0,0,0], ro=[0,0,0])
                cmds.setAttr
                cmds.select(clear=1)
            jnt_created.append(jnt)
            
        return jnt_created   
         
class controler :
    def __init__(self, *_):
        parent = cmds.optionMenu("ctl_menu", q=1, value=1)
        print(parent)
        if parent=="no parenting and positionning" :
            parent = 0
        if parent=="parent and positionning" :
            parent = 1       
        if parent=="children and positionning" :
            parent = 2    
        controler.add_ctl(cmds.ls(sl=1), parent=parent, scale = 1, normal = [1,0,0]) 
        
        return 
        
    def scale_ctl(ctl_list, scale):
        for i in range(0, len(ctl_list)) :
            if ctl_list[i] :
                ctl = ctl_list[i]
                selected_cv = []
                n=0
                while n<=10 :
                    selected_cv.append(f'{ctl}.cv[{n}]')
                    n += 1
                cmds.scale(scale,scale,scale, selected_cv, a=1, ws=1)
            
        return ctl_list
        
    def rotate_ctl(ctl_list, axis, degrees):
        for i in range(0, len(ctl_list)) :
            if ctl_list[i] :
                ctl = ctl_list[i]
                selected_cv = []
                n=0
                while n<=10 :
                    selected_cv.append(f'{ctl}.cv[{n}]')
                    n += 1
                
                if axis == "X" :
                    cmds.rotate(degrees,0,0, selected_cv, a=1, os=1)
                if axis == "Y" :
                    cmds.rotate(0, degrees,0, selected_cv, a=1, os=1)
                if axis == "Z" :
                    cmds.rotate(0,0,degrees, selected_cv, a=1, os=1)
        return ctl_list
        
    def add_ctl(list, parent, scale):
        ctl_created = []
        ctl_grp_created = []
        
        for element in list :
            pos = cmds.xform(element, q=1, ws=1, t=1)
            rot = cmds.xform(element, q=1, ws=1, ro=1)
            print(pos, rot)
            if "_" in element :
                element_name = element.split('_', 1)[1]
            else :
                element_name = element
            ctl = cmds.circle(n=f'ctl_{element_name}', radius  = 1, normal = [0,1,0])[0]
            
            #grandir le controler à la taille demandée
            ctl  = controler.scale_ctl([ctl], scale)
            #rotate la shape du controler dans l'orientation demandée
            ctl = controler.rotate_ctl(ctl, "X", 0)
            
            #group
            ctl_ZRO_grp = cmds.group(ctl, n=f'{ctl}_ZRO_grp')
            cmds.select(clear=1)
            
            print(parent," is parent")            
            if parent == 0 : # pas parenter mais mettre à la meme pos world
                pos = cmds.xform(element, q=1, ws=1, t=1)
                cmds.xform(ctl_ZRO_grp, ws=1, t=pos, ro = [0,0,0])
            
            elif parent == 1 : #enfant de selection
                cmds.parent(ctl_ZRO_grp, element)
                cmds.xform(ctl_ZRO_grp, t=[0,0,0], ro=[0,0,0])
                
            elif parent == 2 : #parent de selection

                cmds.xform(ctl_ZRO_grp, ws=1, t=pos, ro = rot)
                 
                if cmds.listRelatives(element, parent=1) :
                    element_parent = cmds.listRelatives(element, parent=1)
                    cmds.parent(ctl_ZRO_grp, element_parent)
                    cmds.parent(element, ctl)    
                
            ctl_created.append(ctl)
            ctl_grp_created.append(ctl_ZRO_grp)
            
               
        return ctl_created, ctl_grp_created  
                
class follicle :
    
    def __init__(self):
     
        
        return      
        

        
    def create_follicle(surface, follicle_on_u, follicle_param_u_start, follicle_param_u_end, follicle_param_u_offset, follicle_on_v, follicle_param_v_start, follicle_param_v_end, follicle_param_v_offset):
        
        surface_name = surface.split('_')[1]

        flc_created = []
        
        flc_grp = cmds.group(name = f'flc_{surface_name}_grp', empty=1)
        
        flc_number = follicle_on_u*follicle_on_v
        
        #crée des follicules distribuées sur v
        for i in range(follicle_on_u):
            for n in range(follicle_on_v):
                
                if follicle_on_u > 1 :
                    #espacement équidistant sur U + offset
                    parameter_u = i / (follicle_on_u - 1) 
                    
                    #remaper
                    parameter_u = math.remap_value(parameter_u, 0, 1, follicle_param_u_start, follicle_param_u_end)

                    if follicle_param_u_offset :
                        parameter_u += float(follicle_param_u_offset)
                                                
                    if parameter_u > 1 :
                        parameter_u += -1
                        if f"{flc_created[-1]}.parameterU" == 1:
                            parameter_u = 0
                else :
                    if follicle_param_u_offset :
                        parameter_u = float(follicle_param_u_offset)
                    else :
                        parameter_u = 0.5 

                if  follicle_on_v > 1 :
                    #espacement équidistant sur V + offset
                    parameter_v = n / (follicle_on_v - 1)  
                    
                    #remaper
                    parameter_v = math.remap_value(parameter_v, 0, 1, follicle_param_v_start, follicle_param_v_end)

                    if follicle_param_v_offset :
                        parameter_v += float(follicle_param_v_offset)
                    if parameter_v > 1 :
                        parameter_v += -1
                        if f"{flc_created[-1]}.parameterV" == 1:
                            parameter_v = 0
                else : 
                    if follicle_param_v_offset :
                        parameter_v = float(follicle_param_v_offset)
                    else :
                        parameter_v = 0.5

                #ckeckbox inverse
                if cmds.checkBox("inverse_parameter", q=1, value = 1) == 1:
                    switch_parameter_u = parameter_u
                    parameter_u = parameter_v                
                    parameter_v = switch_parameter_u                
                                        
                follicle_index = len(flc_created)
                    
                # Créer le follicle node avec sa shape et son transform
                follicle_shape = cmds.createNode("follicle", name=f"flc_{surface_name}_{follicle_index}Shape")
                
                follicle_transform = cmds.listRelatives(follicle_shape, parent=1)[0]
                cmds.rename(follicle_transform, f"flc_{surface_name}_{follicle_index}")
                follicle_transform = f"flc_{surface_name}_{follicle_index}"
                
                cmds.connectAttr(f"{surface}.worldSpace[0]", f"{follicle_shape}.inputSurface", f=1)
                cmds.connectAttr(f"{surface}.worldMatrix[0]", f"{follicle_shape}.inputWorldMatrix", f=1)
                cmds.connectAttr(f"{follicle_shape}.outRotate", f"{follicle_transform}.rotate", f = 1)
                cmds.connectAttr(f"{follicle_shape}.outTranslate", f"{follicle_transform}.translate", f = 1)
                
                cmds.setAttr(f"{follicle_shape}.parameterU", parameter_u)
                cmds.setAttr(f"{follicle_shape}.parameterV", parameter_v)
                
                cmds.parent(follicle_transform, flc_grp)
                flc_created.append(follicle_transform)
                
        return flc_created
    
        
    def parameter_follicle(self, *_):
        
        object_transform = cmds.textField("surface_name", q=1, text=1)
        
        #si il n'y a pas de nom spécifié
        if not object_transform :
            
            object_transform = cmds.ls(sl=1)[0]
            object_shape = cmds.listRelatives(object_transform, children=1)[0]
                        
            if cmds.objectType(object_shape) == "nurbsSurface" :
                surface_shape = object_shape
                print("selected surface is ", surface_shape)
                surface = object_transform
                
            else :
                print("selected object is not a nurbsSurface, it's a", cmds.objectType(object_shape))
                return    
                
        #si il y a un nom spécifié
        else :
            object_shape = cmds.listRelatives(object_transform, children=1)
            print(object_shape)
            if cmds.objectType(object_shape) == "nurbsSurface" :
                surface_shape = object_shape
                print("selected surface is ", surface_shape)
                surface = object_transform

            else :
                print(object_transform + " is not a surface")
                return

        surface_name = surface.split('_')[1]
        
        #nombre de follicles sur u et v
        follicle_on_u = cmds.textField("follicle_on_u_field", q=1, text=1)
        if not follicle_on_u :
            follicle_on_u = 1
        else :
            follicle_on_u = int(follicle_on_u)
            
        follicle_on_v = cmds.textField("follicle_on_v_field", q=1, text=1)
        if not follicle_on_v :
            follicle_on_v = 1
        else :
            follicle_on_v = int(follicle_on_v)
            
        #offsets
        follicle_param_u_offset = cmds.textField("follicle_param_u_offset_field", q=1, text=1)
        follicle_param_v_offset = cmds.textField("follicle_param_v_offset_field", q=1, text=1)
        
        #start end
        if not cmds.textField("follicle_param_u_start_field", q=1, text=1) :
            follicle_param_u_start = 0
        else : 
            follicle_param_u_start = float(cmds.textField("follicle_param_u_start_field", q=1, text=1))
            
        if not cmds.textField("follicle_param_u_end_field", q=1, text=1) :
            follicle_param_u_end = 1
        else :
            follicle_param_u_end = float(cmds.textField("follicle_param_u_end_field", q=1, text=1))
        
        if not cmds.textField("follicle_param_v_start_field", q=1, text=1) :
            follicle_param_v_start = 0
        else : 
            follicle_param_v_start = float(cmds.textField("follicle_param_v_start_field", q=1, text=1))
            
        if not cmds.textField("follicle_param_v_end_field", q=1, text=1) :
            follicle_param_v_end = 1
        else :
            follicle_param_v_end = float(cmds.textField("follicle_param_v_end_field", q=1, text=1))
        

        flc_created = follicle.create_follicle(surface, follicle_on_u, follicle_param_u_start, follicle_param_u_end, follicle_param_u_offset, follicle_on_v, follicle_param_v_start, follicle_param_v_end, follicle_param_v_offset)
        created = flc_created
        
        #ajouter joints et controlers
        if cmds.checkBox("add_ctl", q=1, value = 1) == 1 :
            cmds.select(clear=1)
            created, created_grp = controler.add_ctl(flc_created, parent = 1, scale = 1)
            
        if cmds.checkBox("add_jnt", q=1, value = 1) == 1 :
            cmds.select(clear=1)

            created = joint.add_jnt(created, parent = 1)
            
        if cmds.checkBox("create_set", q=1, value = 1) == 1 :
            cmds.sets(name = f'{surface}_flc_set', empty = 1)
            for flc in flc_created :
                cmds.sets(flc, add = f'{surface}_flc_set')
            
def window():        
    #ouvrir la windows
    if cmds.window("Rig_tools", exists=1) :
        cmds.deleteUI("Rig_tools") 
    
    win = cmds.window("Rig_tools", title="Rig_tools", widthHeight = (500,600))
    tabs = cmds.tabLayout()
            
    ########################################    
    
    #paramètres du layout
    alinea = 20
    space_height = 25
    
    ########################################    
    
    #tab 1 Follicle
    ribbonTab = cmds.columnLayout(adjustableColumn=True)
    cmds.tabLayout (tabs, edit=True, tabLabel=[ribbonTab, "Follicle"])
    
    #title
    cmds.text(label="Follicle", height = space_height*2 , align="center")
    
    cmds.separator(height = 5, style = "in")
    cmds.separator(height = space_height*.25, style = "none")
              
    #surface object
    cmds.rowLayout(numberOfColumns=3,  columnWidth3 = (alinea, 150, 170))
    cmds.separator(height = space_height*2, style = "none")  
    cmds.text(label="On Selected surface or ", align='center')
    surface_name = cmds.textField("surface_name", placeholderText="write the name of the surface")
    
    cmds.setParent("..")
    
    #follicle_on_u
    cmds.rowLayout(numberOfColumns=2,  columnWidth2 = (150, 170))
    cmds.text(label="How many follicle on U ? ", align='center')
    follicle_on_u_field = cmds.textField("follicle_on_u_field", placeholderText="1")
    
    cmds.setParent("..")
    
    #parameters_on_u
    cmds.rowLayout(numberOfColumns=5,  columnWidth5 = (alinea, 130, 100, 100, 100))
    cmds.separator(height = space_height, style = "none")  
    
    cmds.text(label="Between parameter U = ", align='left')
    follicle_param_u_start_field = cmds.textField("follicle_param_u_start_field", placeholderText="0")
    cmds.text(label=" and parameter U = ", align='left')
    follicle_param_u_end_field = cmds.textField("follicle_param_u_end_field", placeholderText="1")
    
    cmds.setParent("..")
    
    cmds.rowLayout(numberOfColumns=3,  columnWidth3 = (alinea, 130, 20))
    cmds.separator(height = space_height, style = "none")  
    cmds.text(label="With an offset of + ", align='left')
    follicle_param_u_offset_field = cmds.textField("follicle_param_u_offset_field", placeholderText="0")
    
    cmds.setParent("..")
    
    cmds.separator(height = space_height, style = "none")
    
    #follicle_on_v
    cmds.rowLayout(numberOfColumns=2,  columnWidth2 = ( 150, 170))
    cmds.text(label="How many follicle on V ? ", align='center')
    follicle_on_v_field = cmds.textField("follicle_on_v_field", placeholderText="1")
    
    cmds.setParent("..")
    
    #parameters_on_v
    cmds.rowLayout(numberOfColumns=5,  columnWidth5 = (alinea, 130, 100, 100, 100))
    cmds.separator(height = space_height, style = "none")  
    
    cmds.text(label="Between parameter V = ", align='left')
    follicle_param_v_start_field = cmds.textField("follicle_param_v_start_field", placeholderText="0")
    cmds.text(label=" and parameter V = ", align='left')
    follicle_param_v_end_field = cmds.textField("follicle_param_v_end_field", placeholderText="1")
    
    cmds.setParent("..")
    
    cmds.rowLayout(numberOfColumns=3,  columnWidth3 = (alinea, 130, 20))
    cmds.separator(height = space_height, style = "none")  
    cmds.text(label="With an offset of + ", align='left')
    follicle_param_v_offset_field = cmds.textField("follicle_param_v_offset_field", placeholderText="0")
    
    cmds.setParent("..")  

    #other parameters
    cmds.separator(height = space_height, style = "none")  
    inverse_parameter_checkbox = cmds.checkBox("inverse_parameter", label="Switch your parameters between u and v", value=False)
    add_ctl_checkbox = cmds.checkBox("add_ctl", label="Add controlers inside follicle", value=False)
    add_joint_checkbox = cmds.checkBox("add_jnt", label="Add joints inside follicle", value=False)
    create_set_checkbox = cmds.checkBox("create_set", label="create a selection set with follicle inside", value=True)

    #button
    cmds.separator(height = space_height, style = "none")
    cmds.button(label="Create follicles on surface",  height=space_height*2, bgc = (0.2, 0.6, 0.25), command = follicle.parameter_follicle)        

    cmds.separator(height = space_height, style = "none")
    cmds.separator(height = 5, style = "in")
    cmds.separator(height = space_height, style = "none")

    
    
    cmds.setParent ("..")
    
    
    
    ########################################    
    
    #tab 2 Ribbon
    follicleTab = cmds.columnLayout()
    cmds.tabLayout (tabs, edit=True, tabLabel=[follicleTab, "Ribbon"])
    
    #layout du tab 2
    cmds.button(label="Button")
    
    cmds.setParent ("..")
    
    ########################################    
    
    #tab 3 Controler
    ctlTab = cmds.columnLayout(adjustableColumn=True)
    cmds.tabLayout (tabs, edit=True, tabLabel=[ctlTab, "Controler"])

    #title
    cmds.text(label="Controler", height = space_height*2 , align="center")
    
    cmds.separator(height = 5, style = "in")
    cmds.separator(height = space_height*.25, style = "none")
    cmds.separator(height = space_height, style = "none")  
  
    #parameters
    cmds.rowLayout(numberOfColumns=3,  columnWidth3 = (alinea, 320, alinea))
    cmds.separator(height = space_height, style = "none")

    ctl_menu = cmds.optionMenu("ctl_menu", label = "Choose a parenting option :")
    options = ["no parenting and positionning","parent and positionning","children and positionning"]
    for opt in options :
        cmds.menuItem(label=opt)
    cmds.separator(height = space_height, style = "none")
    cmds.setParent ("..")     
    ctl_add_joint_checkbox = cmds.checkBox("ctl_add_jnt", label="Add joints inside ctl", value=False)

    #add controler
    cmds.button(label="Create circle controlers on selection",  height=space_height*2, bgc = (0.2, 0.6, 0.25), command = controler)        

    cmds.separator(height = space_height, style = "none")
    cmds.separator(height = 5, style = "in")
    cmds.separator(height = space_height, style = "none")
    
    #scale controler
    cmds.rowLayout(numberOfColumns=3,  columnWidth3 = (alinea, 170, 120))
    cmds.separator(height = space_height, style = "none")
    cmds.text(label="Set controler selected scale to ", height = space_height*2 , align="left")
    ctl_scale_textfield = cmds.textField("ctl_scale", placeholderText="1")
    cmds.setParent ("..")

    cmds.button(label="Set selected controler scale",  height=space_height*2, bgc = (0.2, 0.6, 0.25), command = lambda *_ :controler.scale_ctl(cmds.ls(sl=1), float(cmds.textField("ctl_scale", q=1, text=1) or 1 ) )  )        

    cmds.separator(height = space_height, style = "none")
    cmds.separator(height = 5, style = "in")
    cmds.separator(height = space_height, style = "none")

    #rotate controler
    cmds.text(label="Rotate controler :", height = space_height*2 , align="left")
    
    cmds.rowLayout(numberOfColumns=6,  columnWidth6 = (60, 60,60, 30, 30, 40))
    cmds.button(label=" X axis ",  height=space_height*2, command = lambda *_ :controler.rotate_ctl(cmds.ls(sl=1),"X", float(cmds.textField("ctl_rotate_amount", q=1, text=1) or 90) ) )
    cmds.button(label=" Y axis ",  height=space_height*2, command = lambda *_ :controler.rotate_ctl(cmds.ls(sl=1),"Y", float(cmds.textField("ctl_rotate_amount", q=1, text=1) or 90) ) )
    cmds.button(label=" Z axis ",  height=space_height*2, command = lambda *_ :controler.rotate_ctl(cmds.ls(sl=1),"Z", float(cmds.textField("ctl_rotate_amount", q=1, text=1) or 90) ) )
    cmds.text(label=" by ", height = space_height*2 , align="left")
    ctl_rotate_amount_textfield = cmds.textField("ctl_rotate_amount", placeholderText="90")
    cmds.text(label=" degrees", height = space_height*2 , align="left")

    cmds.setParent ("..")
    cmds.setParent ("..")     
    
    ########################################    
    
    #tab 4 Joint
    jointTab = cmds.columnLayout(adjustableColumn=True)
    cmds.tabLayout (tabs, edit=True, tabLabel=[jointTab, "Joint"])

    #title
    cmds.text(label="Joint", height = space_height*2 , align="center")
    
    cmds.separator(height = 5, style = "in")
    cmds.separator(height = space_height*.25, style = "none")
    cmds.separator(height = space_height, style = "none")  

    #add joint
    cmds.button(label="Create joints under selection",  height=space_height*2, bgc = (0.2, 0.6, 0.25), command = joint)        
    
    cmds.setParent ("..")
    
    ########################################    
    
    #tab 5 Group
    groupTab = cmds.columnLayout(adjustableColumn=True)
    cmds.tabLayout (tabs, edit=True, tabLabel=[groupTab, "Group"])

    #title
    cmds.text(label="Group", height = space_height*2 , align="center")

    cmds.separator(height = 5, style = "in")
    cmds.separator(height = space_height*.25, style = "none")
    cmds.separator(height = space_height, style = "none")  
       
    #suffix
    cmds.rowLayout(numberOfColumns=4,  columnWidth4 = (alinea, 130, 100, 100))
    cmds.separator(height = space_height, style = "none")  
    cmds.text(label="Group suffix = ", align='left')
    grp_suffix = cmds.textField("grp_suffix", placeholderText=" ")
    cmds.text(label=" + '_grp' ", align='left')
    cmds.setParent ("..")

    #parameters
    cmds.separator(height = space_height, style = "none")  
    guizmo_origin_checkbox = cmds.checkBox("guizmo_origin", label="Put group guizmo at world origin", value=False)
    cmds.separator(height = space_height, style = "none")  

    cmds.rowLayout(numberOfColumns=3,  columnWidth3 = (250, 80, 80))
    guizmo_onto_checkbox = cmds.checkBox("guizmo_onto", label="Put group guizmo at an object world space", value=False)
    cmds.text(label="Object name = ", align='left')
    grp_guizmo = cmds.textField("grp_guizmo", placeholderText="Name of the object")
    cmds.setParent ("..")    
 
    
    #add group
    cmds.separator(height = space_height, style = "none")  
    cmds.button(label="Create groups for selection",  height=space_height*2, bgc = (0.2, 0.6, 0.25), command = group.parameter_group)   
    
    cmds.separator(height = space_height, style = "none")
    cmds.separator(height = 5, style = "in")
    cmds.separator(height = space_height, style = "none")  

     
    
    cmds.showWindow (win)

window()
