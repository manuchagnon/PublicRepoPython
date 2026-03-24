from Qt import QtCore, QtWidgets, QtGui

import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from devUi.customWidgets.api import TreeWidget, HeaderWidget
from devUi.utils.api import *
from devMaya.utils.api import *

class SkinWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.obj = None
        self.skin_cluster = None
        self.joints = []
        self.side_one_joints = []
        self.side_two_joints = []

        # Label Object
        label_obj = QtWidgets.QLabel("Object to Apply Script to :")
        # label_obj.setAlignement(QtCore.Qt.AlignCenter)

        # Line Object
        self.line_object = QtWidgets.QLineEdit()
        self.line_object.setPlaceholderText("Name or Selected one")
        self.line_object.setMaximumWidth(180)

        # Button Select obj
        self.btn_obj = QtWidgets.QPushButton("Set ui with Selected Object")
        self.btn_obj.clicked.connect(self._define_obj)

        # Obj Layout
        obj_layout = QtWidgets.QHBoxLayout()
        obj_layout.addWidget(self.line_object)
        obj_layout.addWidget(self.btn_obj)

        # Label skincluster
        label_skincluster = QtWidgets.QLabel("Skincluster :")
        # label_skincluster.setAlignement(QtCore.Qt.AlignCenter)

        # Line Skincluster
        self.line_skincluster = QtWidgets.QLineEdit()
        self.line_skincluster.setPlaceholderText("No Skin Cluster")
        self.line_skincluster.setMaximumWidth(180)

        # Button Select Skincluster
        self.btn_skincluster = QtWidgets.QPushButton("Selected Skin Cluster")
        self.btn_skincluster.clicked.connect(self._sel_skincluster)

        # Skincluster Layout
        skincluster_layout = QtWidgets.QHBoxLayout()
        skincluster_layout.addWidget(self.line_skincluster)
        skincluster_layout.addWidget(self.btn_skincluster)

        # Button Select Joints
        self.btn_sel_jnt = QtWidgets.QPushButton("Select Skinned Joints")
        self.btn_sel_jnt.clicked.connect(self._sel_jnt)

        # Joint Tree L
        self._jnt_tree_L = TreeWidget()
        self._jnt_tree_L.set_placeholder_text("No Joint on side one")
        self._jnt_tree_L.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self._jnt_tree_L.setColumnCount(1)
        self._jnt_tree_L.setHeaderLabel("Joints on side one")
        self._jnt_tree_L.setRootIsDecorated(False)
        # self._jnt_tree_L.setHeight(200)
        self._jnt_tree_L.itemSelectionChanged.connect(lambda: self._sel_tree_jnt(self._jnt_tree_L.selectedItems()))

        # Joint Tree R
        self._jnt_tree_R = TreeWidget()
        self._jnt_tree_R.set_placeholder_text("No Joint on side two")
        self._jnt_tree_R.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self._jnt_tree_R.setColumnCount(1)
        self._jnt_tree_R.setHeaderLabel("Joints on side two")
        self._jnt_tree_R.setRootIsDecorated(False)
        # self._jnt_tree_R.setHeight(200)
        self._jnt_tree_R.itemSelectionChanged.connect(lambda: self._sel_tree_jnt(self._jnt_tree_R.selectedItems()))

        # Joint No Side
        self._jnt_tree = TreeWidget()
        self._jnt_tree.set_placeholder_text("No Joint on no side")
        self._jnt_tree.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self._jnt_tree.setColumnCount(1)
        self._jnt_tree.setHeaderLabel("Joints on no side")
        self._jnt_tree.setRootIsDecorated(False)
        # self._jnt_tree.setMinimumdHeight(150)
        self._jnt_tree.itemSelectionChanged.connect(lambda: self._sel_tree_jnt(self._jnt_tree.selectedItems()))

        # Suffixes L
        self.line_suffix_one = QtWidgets.QLineEdit()
        self.line_suffix_one.setText("_L")
        self.line_suffix_one.setPlaceholderText("_L")

        # Suffixes R
        self.line_suffix_two = QtWidgets.QLineEdit()
        self.line_suffix_two.setText("_R")
        self.line_suffix_two.setPlaceholderText("_R")

        # Button Select Mirror Joints side One
        self.btn_sel_mirror_jnt_L = QtWidgets.QPushButton("Select Mirrored Joints >>")
        self.btn_sel_mirror_jnt_L.clicked.connect(
            lambda: self._sel_mirror_jnt(joints=self.side_one_joints, suffix = self.line_suffix_one.text()) )

        # Button Select Mirror Joints side Two
        self.btn_sel_mirror_jnt_R = QtWidgets.QPushButton("<< Select Mirrored Joints")
        self.btn_sel_mirror_jnt_R.clicked.connect(
            lambda: self._sel_mirror_jnt(joints=self.side_two_joints, suffix=self.line_suffix_two.text()))

        # Joints Layout
        joints_layout = QtWidgets.QGridLayout()
        joints_layout.addWidget(self._jnt_tree_L, 0, 0, 3, 2)
        joints_layout.addWidget(QtWidgets.QLabel("Suffix:"), 3, 0, 1, 1)
        joints_layout.addWidget(self.line_suffix_one, 3, 1, 1, 1)
        joints_layout.addWidget(self.btn_sel_mirror_jnt_L, 4, 0, 1, 2)

        joints_layout.addWidget(self._jnt_tree_R, 0, 3, 3, 2)
        joints_layout.addWidget(QtWidgets.QLabel("Suffix:" ), 3, 3, 1, 1)
        joints_layout.addWidget(self.line_suffix_two, 3, 4, 1, 1)
        joints_layout.addWidget(self.btn_sel_mirror_jnt_R, 4, 3, 1, 2)

        joints_layout.addWidget(self._jnt_tree, 5, 0, 3, -1)

        # Button Add Joints to SkinCluster
        self.btn_add_jnt_to_skin = QtWidgets.QPushButton("Add Selected Joints to SkinCluster")
        self.btn_add_jnt_to_skin.clicked.connect(self._add_selected_jnt_to_skin)

        # Button Remove Joints of SkinCluster
        self.btn_remove_jnt_of_skin = QtWidgets.QPushButton("Remove Selected Joints of SkinCluster")
        self.btn_remove_jnt_of_skin.clicked.connect(self._remove_selected_jnt_of_skin)

        # Main Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(HeaderWidget(title = "Skin Cluster", color = get_color("orange")))
        layout.addWidget(label_obj, QtCore.Qt.AlignCenter)
        layout.addLayout(obj_layout)
        layout.addSpacing(10)
        layout.addWidget(label_skincluster, QtCore.Qt.AlignCenter)
        layout.addLayout(skincluster_layout)
        layout.addSpacing(10)
        layout.addWidget(self.btn_sel_jnt)
        layout.addLayout(joints_layout)
        layout.addSpacing(10)
        layout.addWidget(self.btn_add_jnt_to_skin)
        layout.addWidget(self.btn_remove_jnt_of_skin)

        self.setLayout(layout)

        # Settings
        self.resize(300, 550)
        self._refresh()

    def _define_obj(self):
        obj = select_object(obj=None)

        if obj:
            self.line_object.setText(obj)
        else:
            print("You must select an object")

        self._refresh()

    def _sel_skincluster(self):
        if not self.obj:
            print("First Define an Object")
            return

        skin_cluster = select_object(self.line_skincluster.text())

        if not skin_cluster:
            print(f"The Object {self.obj} doesn't have a SkinCluster attached to it")

    def _sel_jnt(self):
        print("select skinned jnt do nothing")

    def _sel_mirror_jnt(self, joints, suffix):
        other_suffix = self.line_suffix_two.text() if suffix != self.line_suffix_two.text() else self.line_suffix_one.text()

        mirror_joints, no_mirror_joints = mirrored_joints(joints, source_suffix=suffix, target_suffix=other_suffix)

        if no_mirror_joints:
            print(f"The joints {no_mirror_joints} don't have a mirrored version in the scene")

        if mirror_joints:
            select_objects(mirror_joints)

    def _sel_tree_jnt(self, items):
        joints_to_select = []
        for item in items:
            joints_to_select.append(item.text(0))

        select_objects(joints_to_select)

    def _refresh(self):
        self.line_skincluster.setText(None)
        self._jnt_tree_L.clear()
        self._jnt_tree_R.clear()
        self._jnt_tree.clear()

        self.joints = []
        self.side_one_joints = []
        self.side_two_joints = []



        self.obj = self.line_object.text()
        if not self.obj:
            return

        self.skin_cluster = get_skin_cluster(self.obj)
        if not self.skin_cluster:
            return
        self.line_skincluster.setText(self.skin_cluster)

        suffix_one = self.line_suffix_one.text()
        suffix_two = self.line_suffix_two.text()

        self.joints = skinned_joints(self.obj)

        no_mirror_list = []

        for joint in self.joints:
            if suffix_one in joint:
                self.side_one_joints.append(joint)
                item = QtWidgets.QTreeWidgetItem(self._jnt_tree_L)
                item.setText(0, joint)

            elif suffix_two in joint:
                self.side_two_joints.append(joint)

            else:
                no_mirror_list.append(joint)

        for joint in self.side_two_joints:
            item = QtWidgets.QTreeWidgetItem(self._jnt_tree_R)
            item.setText(0, joint)

        for joint in no_mirror_list:
            item = QtWidgets.QTreeWidgetItem(self._jnt_tree)
            item.setText(0, joint)

        self._jnt_tree_L.clearSelection()
        self._jnt_tree_R.clearSelection()
        self._jnt_tree.clearSelection()

    def _add_selected_jnt_to_skin(self):
        print(">> Add Joints to the Object's Skin Cluster")
        if not self.obj:
            print("First Define an Object")
            return

        if not self.skin_cluster:
            print("The Object doesn't have a Skin Cluster, creating a new one")

        selected_joints = cmds.ls(sl=1, type="joint")

        if not selected_joints:
            print("First Selected Joints")
            return

        res = skin_joints(selected_joints, obj=self.obj)

        if res:
            print("Done !")
        else:
            print("Not done")

        self._refresh()

    def _remove_selected_jnt_of_skin(self):
        print(">> Remove Joints of the Object's Skin Cluster")
        if not self.obj:
            print("First Define an Object")
            return

        if not self.skin_cluster:
            print("The Object doesn't have a Skin Cluster")

        selected_joints = cmds.ls(sl=1, type="joint")

        if not selected_joints:
            print("First Selected Joints")
            return

        res = skin_joints(selected_joints, obj=self.obj, remove_influence=True)

        if res:
            print("Done !")
        else:
            print("Not done")

        self._refresh()
