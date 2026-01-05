from maya import cmds

from PySide2 import QtWidgets, QtCore, QtGui
# from PySide6 import QtWidgets, QtCore, QtGui

from maya.api import create_controller, create_joint
from maya.api import matrix_constraint


class Main:

    _CREATOR = "Emmanuel"
    _NAME = "main"
    _CONTROLLER_SCALE = 1

    def __init__(self, name=_NAME, ctl_scale=_CONTROLLER_SCALE):
        print("Main created")
        self._ctl_scale = ctl_scale
        self._name = name

    def set_scale(self, ctl_scale):
        self._ctl_scale = ctl_scale

    def scale(self):
        return self._ctl_scale

    def set_name(self, name):
        self._name = name

    def name(self):
        return self.name


class Limb(Main):
    """
    Create a limb for arms, legs
    Inputs :
        joint_chain
    Functions :
        duplicate_joint_chain
        create_FK_chain
        create_IK_chain
        create switch
        # create ribbon
    Outputs :
        controllers Fk, Ik, Switch
        # ribbon main controllers, tweaks
        output locator
    """
    _NUMBER = 0

    def __init__(self, name=None, suffix=_NUMBER, parent=None):
        super().__init__(parent=parent)

        self._suffix = suffix

        self.joint_chain = []
        self._created_nodes =[]

        self._NUMBER += 1


    def set_suffix(self, suffix):
        self._suffix = suffix

    def suffix(self):
        return self.suffix

    def set_joint_chain(self, joint_chain: list):
        self.joint_chain = joint_chain

    def duplicate_joint_chain(self, joint_chain, suffix):
        duplicated_joint_chain = []
        
        for joint in joint_chain:
            index = joint_chain.index(joint)
            jnt = cmds.joint(name=f"{joint}_{suffix}")
            cmds.select(clear=1)
            cmds.matchTransform(jnt, joint)
            
            if len(duplicated_joint_chain) > 0:
                cmds.parent(jnt, duplicated_joint_chain[index-1])
            
            duplicated_joint_chain.append(jnt)

        return duplicated_joint_chain

    def create_FK_chain(self):
        """
        Duplicate the joint chain and make it FK chain        
        """
        fk_joint_chain = self.duplicate_joint_chain(self.joint_chain, suffix = "FK")
        

    def create_IK_chain(self):
        """
        Duplicate the joint chain and make it IK chain        
        """
        ik_joint_chain = self.duplicate_joint_chain(self.joint_chain, suffix = "IK")

def created_nodes(self):
        return self._created_nodes


class LimbWindow(QtWidgets.QMainWindow):

    _CREATED_LIMBS = []

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Title
        title_label = QtWidgets.QLabel("Switch_IK_FK")

        # Sub title
        subtitle_label = QtWidgets.QLabel("Select the first to the last joint of a joint chain to execute the switch IK/FK script : ")

        # Parameters
        # -- Controllers scale
        scale_label = QtWidgets.QLabel("Scale of all controllers")
        scale_line_edit = QtWidgets.QLineEdit()
        scale_line_edit.setPlaceholderText("1")

        scale_line_layout = QtWidgets.QHBoxLayout()
        scale_line_layout.addWidget(scale_label)
        scale_line_layout.addWidget(scale_line_edit)

        # -- Stretch
        stretch_checkbox = QtWidgets.QCheckBox("Add Stretch")

        # Apply
        apply_btn = QtWidgets.QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_IK_FK)

        # Reinitialize
        deconstruct_btn = QtWidgets.QPushButton("Deconstruct")
        deconstruct_btn.clicked.connect(self.deconstruct)

        # Info
        info_label = QtWidgets.QLabel("v.04 12/12/2025 Emmanuel Chagnon")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        layout.addLayout(scale_line_layout)
        layout.addWidget(stretch_checkbox)
        layout.addWidget(apply_btn)
        layout.addWidget(deconstruct_btn)
        layout.addWidget(info_label)

        # Main widget
        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(layout)

        # Main Settings
        self.setCentralWidget(main_widget)
        self.setMinimumHeight(400)
        self.setMinimumWidth(400)

    def apply_IK_FK(self):
        print("> Apply")
        joint_chain = cmds.ls(sl=1)

        # Tests
        if not joint_chain:
            print("Please select a joint chain before executing the script")
            return

        for j in joint_chain:
            if cmds.objectType(j) != "joint":
                print(f"The object {j} is not of type 'joint', it is type : {cmds.objectType(j)}")
                print("Please select a joint chain before executing the script")
                return

        # Create the Limb
        limb = Limb()
        limb.set_joint_chain(joint_chain=joint_chain)





        # Store
        self._CREATED_LIMBS += limb






    def deconstruct(self):
        print("> Deconstruct")
        for limb in self._CREATED_LIMBS:
            cmds.delete(limb.created_nodes())



def run():
    try:
        in_maya = not cmds.about(batch=True)
    except:
        in_maya = False

    if in_maya:
        window = LimbWindow()
        window.show()

    else:
        app = QtWidgets.QApplication()
        window = LimbWindow()
        window.show()
        exit(app.exec_())


if __name__ == '__main__':
    run()
