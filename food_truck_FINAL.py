
from PyQt5.QtWidgets import *
import pymysql, sys, hashlib
from PyQt5.QtCore import *
import datetime


#SCREEN 1 - LOGIN
class DbLoginDialog(QDialog):
    def __init__(self, connection):
        super(DbLoginDialog, self).__init__()
        self.setModal(True)
        self.setWindowTitle("GT Food Truck")

        self.user = QLineEdit()
        self.password = QLineEdit()

        form_group_box = QGroupBox()
        layout = QFormLayout()
        layout.addRow(QLabel("Username"), self.user)
        layout.addRow(QLabel("Password"), self.password)
        form_group_box.setLayout(layout)

        # Consider these 3 lines boiler plate for a standard Ok | Cancel dialog
        login_button = QPushButton('Login')
        login_button.clicked.connect(self.user_login)
        register_button = QPushButton('Register')
        register_button.clicked.connect(self.want_register)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(form_group_box)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(login_button)
        hbox_layout.addWidget(register_button)
        vbox_layout.addLayout(hbox_layout)
        self.setLayout(vbox_layout)
        self.password.setFocus()

    def want_register(self):
        self.close()
        reg = DbRegisterDialog(connection)
        reg.exec()

    def user_login(self):
        self.i_username = self.user.text()
        i_password = self.password.text()

        if self.i_username == '' or i_password == '':
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setText("Please enter a username and password.")
            message.exec()

        cursor = connection.cursor()
        cursor.callproc('login', [self.i_username,
                                    i_password])
        cursor2 = connection.cursor()
        sql = 'SELECT username, userType FROM login_result'
        cursor2.execute(sql)
        row = cursor2.fetchone()

        if row == None:
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setText("Your username and password do not match our database records.")
            message.exec()
        else:
            rec_user = row[0]
            rec_type = row[1]

            if rec_user == self.i_username:
                message = QMessageBox()
                message.setText("You have successfully logged in!")
                message.setWindowTitle('Success!')
                message.exec()
                self.close()
                main_window = MainWindow(rec_user, rec_type, connection)
                main_window.exec()

#SCREEN 2 - REGISTER
class DbRegisterDialog(QDialog):
    def __init__(self, connection):
        super(DbRegisterDialog, self).__init__()
        self.setModal(True)
        self.setWindowTitle("Register")

        self.user = QLineEdit()
        self.password = QLineEdit()
        self.firstName = QLineEdit()
        self.balance = QLineEdit('0.00')
        self.email = QLineEdit()
        self.lastName = QLineEdit()
        self.conf_password = QLineEdit()
        
        self.user_type = QComboBox()
        self.user_type.addItem('')
        self.user_type.addItem('Admin')
        self.user_type.addItem('Manager')
        self.user_type.addItem('Staff')

        l_layout = QFormLayout()
        l_layout.addRow(QLabel("Username"), self.user)
        l_layout.addRow(QLabel('First Name'), self.firstName)
        l_layout.addRow(QLabel("Password"), self.password)
        l_layout.addRow(QLabel('Balance'), self.balance)

        r_layout = QFormLayout()
        r_layout.addRow(QLabel('Email'), self.email)
        r_layout.addRow(QLabel('Last Name'), self.lastName)
        r_layout.addRow(QLabel('Confirm Password'), self.conf_password)
        r_layout.addWidget(self.user_type)

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.go_back)
        acc_register_button = QPushButton('Register')
        acc_register_button.clicked.connect(self.reg_account)

        vlbox_layout = QVBoxLayout()
        vlbox_layout.addLayout(l_layout)
        vlbox_layout.addWidget(back_button)
        vrbox_layout = QVBoxLayout()
        vrbox_layout.addLayout(r_layout)
        vrbox_layout.addWidget(acc_register_button)

        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(vlbox_layout)
        hbox_layout.addLayout(vrbox_layout)

        super_layout = QVBoxLayout()
        super_layout.addWidget(QLabel('Register'))
        super_layout.addLayout(hbox_layout)

        self.setLayout(super_layout)
        self.password.setFocus()

    def go_back(self):
        self.close()
        main_page = DbLoginDialog(connection)
        main_page.exec()

    def reg_account(self):
        i_username = self.user.text()
        i_password = self.password.text()
        i_firstname = self.firstName.text()
        i_lastname = self.lastName.text()
        i_balance = round(float(self.balance.text()), 2)
        i_email = self.email.text()
        i_user_type = self.user_type.currentText()
        i_comfpass = self.conf_password.text()

        if (i_password ==  i_comfpass) and (len(i_password) >= 8):
            cursor1 = connection.cursor()
            cursor1.callproc('register', [i_username,
                                            i_email,
                                            i_firstname,
                                            i_lastname,
                                            i_password,
                                            i_balance,
                                            i_user_type,])

            message = QMessageBox()
            message.setText("Thank you for registering. Please Login.")
            message.setWindowTitle('Success')
            message.exec()
            self.close()
            main_page = DbLoginDialog(connection)
            main_page.exec()
        else:
            if (i_password !=  i_comfpass):
                message = QMessageBox()
                message.setText("Your passwords do not match.")
                message.setWindowTitle('Error')
                message.exec()
            if (len(i_password) < 8):
                message = QMessageBox()
                message.setText("Your passwords does not meet the length requirements.")
                message.setWindowTitle('Error')
                message.exec()

#SCREEN 3 - HOME PAGE
class MainWindow(QDialog):
    def __init__(self, username, user_type, connection):
        super(MainWindow, self).__init__()
        self.user_type = user_type
        self.username = username
        self.connection = connection
        self.setModal(True)
        self.setWindowTitle('Home')

    #Customer Button Layout
        cust_layout = QVBoxLayout()
        cust_layout_box = QGroupBox('Customer')
        cust_box_layout = QVBoxLayout()

        explore_button = QPushButton('Explore')
        explore_button.clicked.connect(self.explore)
        cust_box_layout.addWidget(explore_button)

        current_info_button = QPushButton('View Current Information')
        current_info_button.clicked.connect(self.viewCurrentInfo)
        cust_box_layout.addWidget(current_info_button)

        order_history_button = QPushButton('View Order History')
        order_history_button.clicked.connect(self.orderHistory)
        cust_box_layout.addWidget(order_history_button)

        cust_layout_box.setLayout(cust_box_layout)
        cust_layout.addWidget(cust_layout_box)

    #Admin Button Layout
        admin_layout = QVBoxLayout()
        admin_layout_box = QGroupBox('Administrator')
        admin_box_layout = QVBoxLayout()

        manage_bldg_stat_button = QPushButton('Manage Building and Station')
        manage_bldg_stat_button.clicked.connect(self.manageBuildings)
        admin_box_layout.addWidget(manage_bldg_stat_button)

        manage_food_button = QPushButton('Manage Food')
        manage_food_button.clicked.connect(self.manageFood)
        admin_box_layout.addWidget(manage_food_button)

        admin_layout_box.setLayout(admin_box_layout)
        admin_layout.addWidget(admin_layout_box)

    #Manager Button Layout
        manager_layout = QVBoxLayout()
        manager_layout_box = QGroupBox('Manager')
        manager_box_layout = QVBoxLayout()

        manage_food_truck_button = QPushButton('Manage Food Truck')
        manage_food_truck_button.clicked.connect(self.manageFoodTruck)
        manager_box_layout.addWidget(manage_food_truck_button)

        view_food_truck_button = QPushButton('View Food Truck Summary')
        view_food_truck_button.clicked.connect(self.viewFTSummary)
        manager_box_layout.addWidget(view_food_truck_button)

        manager_layout_box.setLayout(manager_box_layout)
        manager_layout.addWidget(manager_layout_box)

    #Staff Layout
        staff_layout = QVBoxLayout()
        staff_layout.addWidget(QLabel("You're a Staff Member!"))

    #Customer-Admin Layout
        cust_admin_layout = QVBoxLayout()
        cust_admin_layout.addWidget(cust_layout_box)
        cust_admin_layout.addWidget(admin_layout_box)

    #Customer-Manager Layout
        cust_manager_layout = QVBoxLayout()
        cust_manager_layout.addWidget(cust_layout_box)
        cust_manager_layout.addWidget(manager_layout_box)

    #Customer-Staff Layout
        cust_staff_layout = QVBoxLayout()
        cust_staff_layout.addWidget(cust_layout_box)
        cust_staff_layout.addWidget(QLabel("You're a Staff Member"))

        if user_type == 'Customer':
            self.setLayout(cust_layout)

        elif user_type == 'Admin':
            self.setLayout(admin_layout)

        elif user_type == 'Manager':
            self.setLayout(manager_layout)

        elif user_type == 'Staff':
            self.setLayout(staff_layout)

        elif user_type == 'Admin-Customer':
            self.setLayout(cust_admin_layout)

        elif user_type == 'Manager-Customer':
            self.setLayout(cust_manager_layout)

        elif user_type == 'Staff-Customer':
            self.setLayout(cust_staff_layout)

    def explore(self):
        self.close()
        expl = Explore(self.username, self.user_type, self.connection)
        expl.exec()

    def viewCurrentInfo(self):
        self.close()
        vci = ViewCurrentInfo(self.username, self.user_type, self.connection)
        vci.exec()

    def orderHistory(self):
        self.close()
        oh = OrderHistory(self.username, self.user_type, self.connection)
        oh.exec()

    def manageBuildings(self):
        self.close()
        mbs = ManageBuildings(self.username, self.connection, None, None, None, None, None)
        mbs.exec()

    def manageFood(self):
        self.close()
        cf = ManageFood(self.username, self.connection, None, None, None)
        cf.exec()

    def manageFoodTruck(self):
        self.close()
        mft = ManageFoodTruck(self.username, self.connection, None, None, None, None, False)
        mft.exec()

    def viewFTSummary(self):
        self.close()
        vfts = FoodTruckSummary(self.username, self.connection, None, None, None, None, None, None)
        vfts.exec()

"""ADMIN PAGES"""
#SCREEN 4 - MANAGE BUILDINGS
class ManageBuildings(QDialog):
    def __init__(self, username, connection, building, station, tag, mincap, maxcap):
        super(ManageBuildings, self).__init__()
        self.setModal(True)
        self.setWindowTitle("Manage Building and Station")

        self.connection = connection
        self.username = username
        self.buildingName = building
        self.stationName = station
        self.buildingTag = tag
        self.minCapacity = mincap
        self.maxCapacity = maxcap

        #Building Filter
        cursor1 = connection.cursor()
        query = 'SELECT buildingName FROM building'
        cursor1.execute(query)

        self.building_filter = QComboBox()
        self.building_filter.addItem(None)
        for record in cursor1:
            building = record[0]
            self.building_filter.addItem(building)

        form_group_box3 = QGroupBox()
        build_layout = QFormLayout()
        build_layout.addRow(QLabel("Building:"), self.building_filter)
        form_group_box3.setLayout(build_layout)

        #Station Filter
        cursor2 = connection.cursor()
        query = 'SELECT stationName FROM station'
        cursor2.execute(query)

        self.station_filter = QComboBox()
        self.station_filter.addItem(None)
        for record in cursor2:
            station = record[0]
            self.station_filter.addItem(station)

        form_group_box4 = QGroupBox()
        station_layout = QFormLayout()
        station_layout.addRow(QLabel("Station:"), self.station_filter)
        form_group_box4.setLayout(station_layout)

        #Building Tag Filter
        self.tag_filter = QLineEdit()
        form_group_box1 = QGroupBox()
        tag_layout = QFormLayout()
        tag_layout.addRow(QLabel("Building Tag (contain)"), self.tag_filter)
        form_group_box1.setLayout(tag_layout)

        #Capacity Filter
        self.minCap = QLineEdit()
        self.maxCap = QLineEdit()
        form_group_box2 = QGroupBox()
        cap_layout = QFormLayout()
        cap_layout.addRow(QLabel("Min Capacity:"), self.minCap)
        cap_layout.addRow(QLabel("Max Capacity:"), self.maxCap)
        form_group_box2.setLayout(cap_layout)

        #Buttons
        self.filter_button = QPushButton('Filter')
        self.filter_button.clicked.connect(self.filter)
        self.home_button = QPushButton('Home')
        self.home_button.clicked.connect(self.home)
        self.updateStation_button = QPushButton('Update Station')
        self.updateStation_button.clicked.connect(self.updateStation)
        self.updateBuilding_button = QPushButton('Update Building')
        self.updateBuilding_button.clicked.connect(self.updateBuilding)
        self.createStation_button = QPushButton('Create Station')
        self.createStation_button.clicked.connect(self.createStation)
        self.createBuilding_button = QPushButton('Create Building')
        self.createBuilding_button.clicked.connect(self.createBuilding)
        self.deleteStation_button = QPushButton('Delete Station')
        self.deleteStation_button.clicked.connect(self.deleteStation)
        self.deleteBuilding_button = QPushButton('Delete Building')
        self.deleteBuilding_button.clicked.connect(self.deleteBuilding)

        self.createStation_button.setEnabled(False)
        self.updateStation_button.setEnabled(False)
        self.updateBuilding_button.setEnabled(False)
        self.deleteStation_button.setEnabled(False)
        self.deleteBuilding_button.setEnabled(False)


        #Buildings Table
        cursor3 = connection.cursor()
        cursor3.callproc('ad_filter_building_station', [self.buildingName,
                                                        self.buildingTag,
                                                        self.stationName,
                                                        self.minCapacity,
                                                        self.maxCapacity])
        cursor4 = connection.cursor()
        query4 = 'SELECT * FROM ad_filter_building_station_result'
        cursor4.execute(query4)
        cursor4_results = cursor4.fetchall()

        num = len(cursor4_results)
        self.building_table = QTableWidget(num, 5, self)
        self.building_table.setHorizontalHeaderLabels(['Building Name', 'Tags', 'Station Name', 'Capacity', 'Food Truck(s)'])
        for i, building in enumerate(cursor4_results):
            self.building_table.setItem(i, 0, QTableWidgetItem(building[0]))
            self.building_table.setItem(i, 1, QTableWidgetItem(building[1]))
            self.building_table.setItem(i, 2, QTableWidgetItem(building[2]))
            cap = building[3]
            if cap == None:
                cap = None
            else:
                cap = str(cap)
            self.building_table.setItem(i, 3, QTableWidgetItem(cap))
            self.building_table.setItem(i, 4, QTableWidgetItem(building[4]))

        #Enable Buttons
        self.building_table.itemClicked.connect(self.enable)

        #Layout
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox1.addWidget(form_group_box3)
        vbox1.addWidget(form_group_box4)
        hbox.addLayout(vbox1)
        vbox2 = QVBoxLayout()
        vbox2.addWidget(form_group_box1)
        vbox2.addWidget(form_group_box2)
        hbox.addLayout(vbox2)
        vbox.addLayout(hbox)
        vbox.addWidget(self.filter_button)
        vbox.addWidget(self.building_table)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.createStation_button)
        hbox3.addWidget(self.updateStation_button)
        hbox3.addWidget(self.deleteStation_button)
        vbox.addLayout(hbox3)
        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.createBuilding_button)
        hbox4.addWidget(self.updateBuilding_button)
        hbox4.addWidget(self.deleteBuilding_button)
        vbox.addLayout(hbox4)
        vbox.addWidget(self.home_button)
        self.connection = connection

        self.setLayout(vbox)

    def enable(self):
        row = self.building_table.currentRow()
        highlight = self.building_table.selectRow(row)
        if self.building_table.currentIndex() == 1:
            self.createStation_button.setEnabled(False)
            self.updateStation_button.setEnabled(False)
            self.updateBuilding_button.setEnabled(False)
            self.deleteStation_button.setEnabled(False)
            self.deleteBuilding_button.setEnabled(False)
        else:
            self.createStation_button.setEnabled(True)
            self.updateStation_button.setEnabled(True)
            self.updateBuilding_button.setEnabled(True)
            self.deleteStation_button.setEnabled(True)
            self.deleteBuilding_button.setEnabled(True)

    def updateStation(self):
        row = self.building_table.currentRow()
        building = self.building_table.item(row,  0).text()
        station = self.building_table.item(row,  2).text()
        if station != '':
            self.close()
            us = UpdateStation(self.username, station, building, self.connection)
            us.exec()
        else:
            message = QMessageBox()
            text = "This building has no station."
            message.setText(text)
            message.exec()

    def createStation(self):
        row = self.building_table.currentRow()
        building = self.building_table.item(row,  0).text()
        station = self.building_table.item(row,  2).text()
        if station == '' or station == None:
            self.close()
            cs = CreateStation(self.username,  self.connection,  building)
            cs.exec()
        else:
            message = QMessageBox()
            text = "This building already has station."
            message.setText(text)
            message.exec()
        
    def deleteStation(self):
        try:
            cursor = self.connection.cursor()
            row = self.building_table.currentRow()
            station = self.building_table.item(row,  2).text()
            cursor.callproc('ad_delete_station', [station])

            message = QMessageBox()
            text = "You have deleted the " + station + " station."
            message.setText(text)
            message.exec()

            self.close()
            mb = ManageBuildings(self.username, self.connection, None, None, None, None, None)
            mb.exec()
        except:
            message = QMessageBox()
            text = "This building has no station."
            message.setText(text)
            message.exec()


    def updateBuilding(self):
        self.close()
        row = self.building_table.currentRow()
        building = self.building_table.item(row,  0).text()
        ub = UpdateBuilding(self.username, self.connection, building)
        ub.exec()

    def createBuilding(self):
        self.close()
        cb = CreateBuilding(self.username,  self.connection)
        cb.exec()

    def deleteBuilding(self):
        cursor = self.connection.cursor()
        row = self.building_table.currentRow()
        building = self.building_table.item(row,  0).text()
        cursor.callproc('ad_delete_building', [building])

        message = QMessageBox()
        text = "You have deleted the " + building + " building."
        message.setText(text)
        message.exec()

        self.close()
        mb = ManageBuildings(self.username, self.connection, None, None, None, None, None)
        mb.exec()

    def filter(self):
        self.close()
        building = self.building_filter.currentText()
        station = self.station_filter.currentText()
        tag = self.tag_filter.text()
        mincap = self.minCap.text()
        if mincap == '':
            mincap = None
        else:
            mincap = int(mincap)
        maxcap = self.maxCap.text()
        if maxcap == '':
            maxcap = None
        else:
            maxcap = int(maxcap)
        ff = ManageBuildings(self.username, self.connection, building, station, tag, mincap, maxcap)
        ff.exec()

    def home(self):
        self.close()

        cursor = self.connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]

        main_window = MainWindow(self.username, usertype, self.connection)
        main_window.exec()

#SCREEN 5 - CREATE BUILDINGS
class CreateBuilding(QDialog):
    def __init__(self, username, connection):
        super(CreateBuilding, self).__init__()
        self.setModal(True)
        self.setWindowTitle("Create Building")

        self.username = username
        self.connection = connection

        self.buildingName = QLineEdit()
        self.description = QTextEdit()

        form_group_box = QGroupBox()
        layout = QFormLayout()
        layout.addRow(QLabel("Building Name:"), self.buildingName)
        layout.addRow(QLabel("Description:"), self.description)
        form_group_box.setLayout(layout)

        #Buttons
        self.remove_tag = QPushButton('-')
        self.remove_tag.clicked.connect(self.removeTag)
        self.remove_tag.setEnabled(False)
        self.add_tag = QPushButton('+')
        self.add_tag.clicked.connect(self.addTag)
        create_button = QPushButton('Create')
        create_button.clicked.connect(self.create)
        home_button = QPushButton('Home')
        home_button.clicked.connect(self.home)

        #Tags:
        group = QGroupBox()
        self.tag_box = QVBoxLayout()
        self.tag_form = QFormLayout()
        self.tags = QListWidget()
        self.tags.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tags.itemClicked.connect(self.remove_enable)
        self.tag_form.addRow(QLabel("Tag(s):"), self.tags)
        self.tag_box.addLayout(self.tag_form)

        hbox1 = QHBoxLayout()
        self.new_tag_form = QFormLayout()
        self.new_tag = QLineEdit()
        self.new_tag_form.addRow(QLabel("Add Tag:"), self.new_tag)
        hbox1.addLayout(self.new_tag_form)
        hbox1.addWidget(self.add_tag)
        hbox1.addWidget(self.remove_tag)

        self.tag_box.addLayout(hbox1)
        group.setLayout(self.tag_box)

        #Layout
        vbox = QVBoxLayout()
        vbox.addWidget(form_group_box)
        vbox.addWidget(group)
        hbox = QHBoxLayout()
        hbox.addWidget(home_button)
        hbox.addWidget(create_button)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def remove_enable(self):
        self.remove_tag.setEnabled(True)

    def removeTag(self):
        index_number = self.tags.currentRow()
        bye_bye_tag = self.tags.takeItem(index_number)

    def addTag(self):
        if self.new_tag.text() != None:
            tag_item = self.new_tag.text()
            new_tag = QListWidgetItem(tag_item)
            self.tags.addItem(new_tag)
            self.new_tag.setText(None)
            new_tag .setSelected(True)

    def create(self):
        newBuilding= self.buildingName.text()
        description = self.description.toPlainText()
        tags = self.tags.selectedItems()
        if (len(tags) > 0) and (newBuilding != None) and (description != None):
            cursor = self.connection.cursor()
            cursor.callproc('ad_create_building', [newBuilding,
                                                    description,])
            
            x = []
            for i in range(len(tags)):
                individ_tag = str(self.tags.selectedItems()[i].text())
                cursor2 = self.connection.cursor()
                cursor.callproc('ad_add_building_tag', [newBuilding, individ_tag])
            self.close()
            message = QMessageBox()
            text = "You have created the " + newBuilding + " building."
            message.setText(text)
            message.exec()
            mb = ManageBuildings(self.username, self.connection, None, None, None, None, None)
            mb.exec()
        else:
            message = QMessageBox()
            text = "Please fill all fields"
            message.setText(text)
            message.exec()

    def home(self):
        self.close()

        cursor = self.connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]

        main_window = MainWindow(self.username, usertype, self.connection)
        main_window.exec()

#SCREEN 6 - UPDATE BUILDINGS
class UpdateBuilding(QDialog):
    def __init__(self, username, connection,building):
        super(UpdateBuilding, self).__init__()
        self.setModal(True)
        self.setWindowTitle("UpdateBuilding")

        self.username = username
        self.connection = connection
        self.building = building

        self.buildingName = QLineEdit(building)
        form_group_box = QGroupBox()
        layout = QFormLayout()
        layout.addRow(QLabel("Building Name:"), self.buildingName)
        

        #Get Building Description
        cursor1 = self.connection.cursor()
        cursor1.execute('SELECT description FROM building where buildingName=(%s)',building)
        desc = cursor1.fetchone()
        desc = desc[0]
        self.description = QTextEdit(desc)
        layout.addRow(QLabel("Description:"), self.description)
        form_group_box.setLayout(layout)

        #Buttons
        self.remove_tag = QPushButton('-')
        self.remove_tag.clicked.connect(self.removeTag)
        self.remove_tag.setEnabled(False)
        self.add_tag = QPushButton('+')
        self.add_tag.clicked.connect(self.addTag)
        update_button = QPushButton('Update')
        update_button.clicked.connect(self.update)
        home_button = QPushButton('Home')
        home_button.clicked.connect(self.home)

        #Tags
        group = QGroupBox()
        self.tag_box = QVBoxLayout()
        self.tag_form = QFormLayout()
        self.tags = QListWidget()
        self.tags.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tags.itemClicked.connect(self.remove_enable)
        cursor2 = self.connection.cursor()
        cursor2.execute('SELECT tag from BuildingTag  where buildingName = (%s)', self.building)
        my_result2 = cursor2.fetchall()
        for x in my_result2:
            each = QListWidgetItem(x[0])
            self.tags.addItem(each)
            each.setSelected(True)
        self.tag_form.addRow(QLabel("Tag(s):"), self.tags)
        self.tag_box.addLayout(self.tag_form)

        hbox1 = QHBoxLayout()
        self.new_tag_form = QFormLayout()
        self.new_tag = QLineEdit()
        self.new_tag_form.addRow(QLabel("Add Tag:"), self.new_tag)
        hbox1.addLayout(self.new_tag_form)
        hbox1.addWidget(self.add_tag)
        hbox1.addWidget(self.remove_tag)

        self.tag_box.addLayout(hbox1)
        group.setLayout(self.tag_box)

        #Layout
        vbox = QVBoxLayout()
        vbox.addWidget(form_group_box)
        vbox.addWidget(group)
        hbox = QHBoxLayout()
        hbox.addWidget(home_button)
        hbox.addWidget(update_button)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def remove_enable(self):
        self.remove_tag.setEnabled(True)

    def removeTag(self):
        index_number = self.tags.currentRow()
        bye_bye_tag = self.tags.takeItem(index_number)
        no_tag = bye_bye_tag.text()
        my_cursor = connection.cursor()
        my_cursor.callproc('ad_remove_building_tag', [f'{self.building}', f'{no_tag}'])

        msg = QMessageBox()
        msg.setText(f'You have removed the tag: {no_tag}')
        msg.setWindowTitle('Tag Removed')
        msg.exec()


    def addTag(self):
        if self.new_tag.text() != None:
            tag_item = self.new_tag.text()
            new_tag  = QListWidgetItem(tag_item)
            self.tags.addItem(new_tag)
            new_tag.setSelected(True)
            self.new_tag.setText(None)
            cursor = self.connection.cursor()
            cursor.callproc('ad_add_building_tag', [self.building,
                                                    tag_item])
            message = QMessageBox()
            text = "You have added a tag to the " + self.building + " building."
            message.setText(text)
            message.setWindowTitle('Tag Added')
            message.exec()

    def update(self):
        newBuilding= self.buildingName.text()
        description = self.description.toPlainText()
        cursor = self.connection.cursor()
        cursor.callproc('ad_update_building', [self.building,
                                                newBuilding,
                                                description,])
        message = QMessageBox()
        text = "You have updated the " + self.building + " building."
        message.setText(text)
        message.exec()
        mb = ManageBuildings(self.username, self.connection, None, None, None, None, None)
        mb.exec()
        self.close()

    def home(self):
        self.close()

        cursor = self.connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]

        main_window = MainWindow(self.username, usertype, self.connection)
        main_window.exec()

#SCREEN 7 - CREATE STATION
class CreateStation(QDialog):
    def __init__(self, username, connection, building):
        super(CreateStation, self).__init__()
        self.setModal(True)
        self.setWindowTitle("Create Station")

        #Variables
        self.username = username
        self.stationName = QLineEdit()
        self.capacity = QLineEdit()
        self.buildingName = building
        self.connection = connection

        #Update Station
        form_group_box = QGroupBox()
        layout = QFormLayout()
        layout.addRow(QLabel("Station Name:"), self.stationName)
        layout.addRow(QLabel("Capacity:"), self.capacity)
        form_group_box.setLayout(layout)

        self.build = QComboBox()
        self.build.addItem(self.buildingName)

        cursor1 = self.connection.cursor()
        cursor1.callproc('ad_get_available_building')
        cursor2 = self.connection.cursor()
        query2 = 'SELECT buildingname FROM ad_get_available_building_result'
        cursor2.execute(query2)
        for item in cursor2:
            building = item[0]
            self.build.addItem(building)

        #Buttons
        update_button = QPushButton('Create')
        update_button.clicked.connect(self.create)
        home_button = QPushButton('Home')
        home_button.clicked.connect(self.home)

        #Layout
        vbox = QVBoxLayout()
        vbox.addWidget(form_group_box)
        vbox.addWidget(self.build)
        hbox = QHBoxLayout()
        hbox.addWidget(home_button)
        hbox.addWidget(update_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def create(self):
        station = self.stationName.text()
        capacity = self.capacity.text()
        capacity = int(capacity)
        building = self.build.currentText()

        cursor = self.connection.cursor()
        cursor.callproc('ad_create_station', [station,
                                                building,
                                                capacity])
        message = QMessageBox()
        text = "You have created the " + station + " station."
        message.setText(text)
        message.exec()


    def home(self):
        self.close()

        cursor = self.connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]

        main_window = MainWindow(self.username, usertype, self.connection)
        main_window.exec()

#SCREEN 8 - UPDATE STATION
class UpdateStation(QDialog):
    def __init__(self, user, station, building, connection):
        super(UpdateStation, self).__init__()
        self.setModal(True)
        self.setWindowTitle("Update Station")

        #Get Capacity
        self.connection = connection
        cursor = self.connection.cursor()
        query = 'SELECT capacity FROM station'
        cursor.execute(query)
        row = cursor.fetchone()
        cap = str(row[0])

        #Variables
        self.username = user
        self.stationName = station
        self.capacity = QLineEdit(cap)
        self.buildingName = building

        #Station to be updated
        stationLabel = QLabel(("Station Name: ") + (self.stationName))

        #Update Station
        form_group_box = QGroupBox()
        layout = QFormLayout()
        layout.addRow(QLabel("Capacity:"), self.capacity)
        form_group_box.setLayout(layout)

        self.build = QComboBox()
        self.build.addItem(self.buildingName)

        cursor1 = self.connection.cursor()
        cursor1.callproc('ad_get_available_building')
        cursor2 = self.connection.cursor()
        query2 = 'SELECT buildingname FROM ad_get_available_building_result'
        cursor2.execute(query2)
        for item in cursor2:
            building = item[0]
            self.build.addItem(building)

        #Buttons
        update_button = QPushButton('Update')
        update_button.clicked.connect(self.update)
        home_button = QPushButton('Home')
        home_button.clicked.connect(self.home)

        #Layout
        vbox = QVBoxLayout()
        vbox.addWidget(stationLabel)
        vbox.addWidget(form_group_box)
        vbox.addWidget(self.build)
        hbox = QHBoxLayout()
        hbox.addWidget(home_button)
        hbox.addWidget(update_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def update(self):
        capacity = self.capacity.text()
        building = self.build.currentText()


        cursor = self.connection.cursor()
        cursor.callproc('ad_update_station', [self.stationName,
                                                capacity,
                                                building])
        message = QMessageBox()
        text = "You have updated the " + self.stationName + " station."
        message.setText(text)
        message.exec()


    def home(self):
        self.close()

        cursor = self.connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]

        main_window = MainWindow(self.username, usertype, self.connection)
        main_window.exec()

#SCREEN 9 - MANAGE FOOD
class ManageFood(QDialog):
    def __init__(self, username, connection, filterfood, ftype, asc_desc):
        super(ManageFood, self).__init__()
        self.setModal(True)
        self.setWindowTitle("Manage Food")


        self.username = username
        self.connection = connection
        self.filterfood = filterfood
        self.asc_desc = asc_desc
        self.ftype = ftype

        #Filter - FOOD
        label = QLabel("Filter By:")

        self.foodName_filter = QComboBox()
        self.foodName_filter.addItem(None)
        cursor = self.connection.cursor()
        query = 'SELECT foodName FROM food'
        cursor.execute(query)
        for item in cursor:
            food = item[0]
            self.foodName_filter.addItem(food)

        self.asc_desc_filter = QComboBox()
        self.asc_desc_filter.addItem('ASC')
        self.asc_desc_filter.addItem('DESC')

        self.type_filter = QComboBox()
        self.type_filter.addItem('Food Name')
        self.type_filter.addItem('Menu Count')
        self.type_filter.addItem('Purchase Count')

        #Create Table
        cursor2 = self.connection.cursor()
        cursor2.callproc('ad_filter_food', [self.filterfood,
                                                self.ftype,
                                                self.asc_desc])                                               
        cursor3 = self.connection.cursor()
        query3 = 'SELECT * FROM ad_filter_food_result'
        cursor3.execute(query3)
        cur = cursor3.fetchall()

        food_num =len(cur)

        self.food_table = QTableWidget(food_num, 3, self)
        self.food_table.setHorizontalHeaderLabels(['Food Name', 'Menu Count', 'Purchased Count'])
        for i, food in enumerate(cur):
            self.food_table.setItem(i, 0, QTableWidgetItem(food[0]))
            menu = food[1]
            menu = str(menu)
            purchase = food[2]
            purchase = str(purchase)
            self.food_table.setItem(i, 1, QTableWidgetItem(menu))
            self.food_table.setItem(i, 2, QTableWidgetItem(purchase))

        #Buttons
        filter_button = QPushButton('Filter')
        filter_button.clicked.connect(self.exec_filter)
        home_button = QPushButton('Home')
        home_button.clicked.connect(self.home)
        create_button = QPushButton('Create')
        create_button.clicked.connect(self.create)
        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete)
        self.delete_button.setEnabled(False)

        self.food_table.itemClicked.connect(self.enable)

        #Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.foodName_filter)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label)
        hbox1.addWidget(self.type_filter)
        hbox1.addWidget(self.asc_desc_filter)
        vbox.addLayout(hbox1)
        vbox.addWidget(filter_button)
        vbox.addWidget(self.food_table)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(home_button)
        hbox2.addWidget(create_button)
        hbox2.addWidget(self.delete_button)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)
        self.adjustSize()

    def enable(self):
        row = self.food_table.currentRow()
        highlight = self.food_table.selectRow(row)
        if self.food_table.currentIndex() == 1:
            self.delete_button.setEnabled(False)
        else:
            self.delete_button.setEnabled(True)

    def exec_filter(self):
        self.food_filter = self.foodName_filter.currentText()
        self.ascDesc_filter = self.asc_desc_filter.currentText()
        self.ftype_filter = self.type_filter.currentText()
        if self.ftype_filter == "Food Name":
            self.ftype_filter = "name"
        elif self.ftype_filter == "Menu Count":
            self.ftype_filter = "menuCount"
        elif self.ftype_filter == "Purchase Count":
            self.ftype_filter = "purchaseCount"
        mf = ManageFood(self.username, self.connection, self.food_filter, self.ftype_filter, self.ascDesc_filter)
        self.close()
        mf.exec()

    def create(self):
        self.close()
        cf = CreateFood(self.username, self.connection)
        cf.exec()

    def delete(self):
        row = self.food_table.currentRow()
        food = self.food_table.item(row,  0).text()
        cursor = self.onnection.cursor()
        cursor.callproc('ad_delete_food', [food])

        message = QMessageBox()
        text = food + " will be deleted from the pantry."
        message.setText(text)
        message.exec()

        self.close()
        mf = ManageFood(self, self.username, self.connection, None, None, None)
        mf.exec()

    def home(self):
        self.close()

        cursor = self.connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]

        main_window = MainWindow(self.username, usertype, self.connection)
        main_window.exec()

#SCREEN 10 - CREATE FOOD
class CreateFood(QDialog):
    def __init__(self, username, connection):
        super(CreateFood, self).__init__()
        self.setModal(True)
        self.setWindowTitle("Create Food")

        self.foodName = QLineEdit()
        self.connection = connection
        self.username = username

        #Food Input
        form_group_box = QGroupBox()
        layout = QFormLayout()
        layout.addRow(QLabel("Name:"), self.foodName)
        form_group_box.setLayout(layout)

        #Buttons
        create_button = QPushButton('Create')
        create_button.clicked.connect(self.create)
        home_button = QPushButton('Home')
        home_button.clicked.connect(self.home)

        #Layout
        vbox = QVBoxLayout()
        vbox.addWidget(form_group_box)
        hbox = QHBoxLayout()
        hbox.addWidget(home_button)
        hbox.addWidget(create_button)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def create(self):
        fName = self.foodName.text()
        cursor = self.connection.cursor()
        cursor.execute('SELECT foodName FROM food where foodName=(%s)',fName)

        row = cursor.fetchone()

        if row == None:
            message = QMessageBox()
            text = fName + " will be added to the pantry."
            message.setText("This food will be added.")
            message.exec()
        else:
            message = QMessageBox()
            text = fName + " is already in the pantry."
            message.setText(text)
            message.exec()


    def home(self):
        self.close()

        cursor = self.connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]

        main_window = MainWindow(self.username, usertype, self.connection)
        main_window.exec()

"""MANAGER PAGES"""
#SCREEN 11 - MANAGE FOOD TRUCK
class ManageFoodTruck(QDialog):
    def __init__(self, username, connection, food_truck, station, staffMin, staffMax, remain):
        super(ManageFoodTruck, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Manage Food Truck')

        self.username = username
        self.connection = connection
        self.food_truck = food_truck
        self.station = station
        self.staffMin = staffMin
        self.staffMax = staffMax
        self.remain = remain

        #Food Truck Name
        self.food_truck_contain_tag = QLineEdit()
        ftName_layout = QFormLayout()
        ftName_layout.addRow(QLabel('Food Truck Name (contains):'),self.food_truck_contain_tag)

        #Station Names Drop Down
        my_cursor = self.connection.cursor()
        my_cursor.execute('SELECT * from station')

        self.stat_names = QComboBox()
        self.stat_names.addItem(None)
        for x in my_cursor:
            station = x[0]
            self.stat_names.addItem(station)

        # Staff Min/Max
        self.staff_count_tag_min = QLineEdit(None)
        self.staff_count_tag_min.setFixedWidth(30)
        self.staff_count_tag_max = QLineEdit(None)
        self.staff_count_tag_max.setFixedWidth(30)

        #Cap Check Box
        self.capacity_box = QCheckBox("Has Remaining Capacity", self)

        #Filter Button
        filter_button = QPushButton('Filter')
        filter_button.clicked.connect(self.filter) #connect to the filter function 

        #Table
        my_cursor = self.connection.cursor()
        my_cursor.callproc('mn_filter_foodTruck', [self.username
                                                    , self.food_truck
                                                    , self.station
                                                    , self.staffMin
                                                    , self.staffMax
                                                    , self.remain])
        my_cursor.execute('SELECT *  FROM mn_filter_foodTruck_result')
        self.food_truck_info = my_cursor.fetchall()

        num_ft = len(self.food_truck_info)

        self.food_truck_table = QTableWidget(num_ft, 5, self) #how to get row result to be dependent of sql query 
        self.food_truck_table.setHorizontalHeaderLabels(['Food Truck Name', 'Station Name', 'Remaining Capacity', 'Staff(s)', "#Menu Item"])

        for i, truck in enumerate(self.food_truck_info):
            remainCap = str(truck[2])
            staffNum = str(truck[3])
            menuItems = str(truck[4])
            self.food_truck_table.setItem(i, 0, QTableWidgetItem(truck[0]))
            self.food_truck_table.setItem(i, 1, QTableWidgetItem(truck[1]))
            self.food_truck_table.setItem(i, 2, QTableWidgetItem(remainCap))
            self.food_truck_table.setItem(i, 3, QTableWidgetItem(staffNum))
            self.food_truck_table.setItem(i, 4, QTableWidgetItem(menuItems))

        #Buttons
        last_row = QHBoxLayout()
        back_button = QPushButton('Home')
        back_button.clicked.connect(self.go_back)
        create_button = QPushButton('Create Food Truck')
        create_button.clicked.connect(self.create)
        self.update_button = QPushButton('Update Food Truck')
        self.update_button.clicked.connect(self.update)
        self.update_button.setEnabled(False)
        self.delete_button = QPushButton('Delete Food Truck')
        self.delete_button.clicked.connect(self.delete)
        self.delete_button.setEnabled(False)

        self.food_truck_table.itemClicked.connect(self.enable)

        
        #Layout
        self.super_layout = QVBoxLayout()
        row_one = QHBoxLayout()
        row_one.addLayout(ftName_layout)
        row_one.addWidget(QLabel('Station Name:'))
        row_one.addWidget(self.stat_names)
        row_two = QHBoxLayout()
        row_two.addWidget(QLabel('Staff Count'))
        row_two.addWidget(self.staff_count_tag_min)
        row_two.addWidget(self.staff_count_tag_max)
        row_two.addWidget(self.capacity_box)


        last_row.addWidget(back_button)
        last_row.addWidget(create_button)
        last_row.addWidget(self.update_button)
        last_row.addWidget(self.delete_button)

        self.super_layout.addLayout(row_one) #adds building and station name drop downs
        self.super_layout.addLayout(row_two) #adds black line pic
        self.super_layout.addWidget(filter_button)
        self.super_layout.addWidget(self.food_truck_table)
        self.super_layout.addLayout(last_row)
        self.setLayout(self.super_layout) #this has to be done before anything 

    def enable(self):
        row = self.food_truck_table.currentRow()
        highlight = self.food_truck_table.selectRow(row)
        if self.food_truck_table.currentIndex() == 1:
            self.delete_button.setEnabled(False)
            self.update_button.setEnabled(False)
        else:
            self.delete_button.setEnabled(True)
            self.update_button.setEnabled(True)

    def filter(self):
        user = self.username
        ftname = self.food_truck_contain_tag.text()
        location = self.stat_names.currentText()
        staffMin = self.staff_count_tag_min.text()
        if staffMin == '':
            staffMin = None
        else:
            staffMin = int(staffMin)
        staffMax = self.staff_count_tag_max.text()
        if staffMax == '':
            staffMax = None
        else:
            staffMax = int(staffMax)
        if self.capacity_box.isChecked() == True:
            cap = True
        else:
            cap = False

        self.close()
        reload = ManageFoodTruck(user, self.connection, ftname, location, staffMin, staffMax, cap)
        reload.exec()

    def go_back(self):
        self.close()
        cursor = connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]
        main_window = MainWindow(self.username, usertype, connection)
        main_window.exec()
    
    def create(self):
        self.close()
        cft = CreateFoodTruck(self.username, self.connection)
        cft.exec()
    
    def update(self): 
        self.close()
        row = self.food_truck_table.currentRow()
        ft = self.food_truck_table.item(row,  0).text()
        self.close()
        uft = UpdateFoodTruck(self.username, self.connection, ft)
        uft.exec()
    
    def delete(self):
        row = self.food_truck_table.currentRow()
        ft = self.food_truck_table.item(row,  0).text()
        try:
            cursor = connection.cursor()
            cursor.callproc('mn_delete_foodTruck', [ft])

            message = QMessageBox()
            text = ft + " will be deleted."
            message.setText(text)
            message.exec()
        except:
            message = QMessageBox()
            text = "You cannot delete this food truck"
            message.setText(text)
            message.exec()

        self.close()
        mft = ManageFoodTruck(self.username, self.connection, None, None, None, None, False)
        mft.exec()

# SCREEN 12 - CREATE FOOD TRUCK
class CreateFoodTruck(QDialog):
    def __init__(self, username, connection):
        super(CreateFoodTruck, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Create Food Truck')

        self.username = username
        self.connection = connection

        #Food Truck Name
        self.ft_name = QLineEdit()
        self.ft_name.setFixedWidth(250)
        food_truck_name = QFormLayout()
        food_truck_name.addRow(QLabel('Food Truck Name:'), self.ft_name)

        #Stations
        self.stat_names = QComboBox()
        my_cursor = connection.cursor()
        my_cursor.execute("SELECT * from station where capacity >= 1")
        my_result = my_cursor.fetchall()
        for x in my_result:
            self.stat_names.addItem(x[0])

        self.station_form_box = QFormLayout()
        self.station_form_box.addRow(QLabel("Station:"), self.stat_names)

    #Available + Working Staff:
        group2 = QGroupBox()
        self.staffBox = QVBoxLayout()
        self.add_staff_button = QPushButton('+')
        self.add_staff_button.setFixedWidth(50)
        self.add_staff_button.clicked.connect(self.add_staff)
        self.staff_form = QFormLayout()
        self.staff_list = QListWidget()
        self.staff_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.staff_form.addRow(QLabel("Assigned Staff:"),self.staff_list)

        hbox2 = QHBoxLayout()
        self.new_staff_form = QFormLayout()

        self.staff_dropbox = QComboBox()
        self.staff_dropbox.addItem(None)
        my_cursor2 = connection.cursor()
        my_cursor2.execute('SELECT * from staff where foodTruckName is NULL')
        my_result2 = my_cursor2.fetchall()
        for x in my_result2:
            self.staff_dropbox.addItem(x[0])
        self.new_staff_form.addRow(QLabel("Assign Staff Member:"), self.staff_dropbox)

        hbox2.addLayout(self.new_staff_form)
        hbox2.addWidget(self.add_staff_button)
        self.staffBox.addLayout(self.staff_form)
        self.staffBox.addLayout(hbox2)

        group2.setLayout(self.staffBox)

        self.staff_member_list = []

    #Foods:
        self.add_item_button = QPushButton('+')
        self.add_item_button.clicked.connect(self.add_food)

        group = QGroupBox()
        self.vbox1 = QVBoxLayout()
        self.food_box = QVBoxLayout()
        self.menu_item = QListWidget()
        self.menu_item.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.food_form = QFormLayout()
        self.food_form.addRow(QLabel("Menu Items:"), self.menu_item)

        #New Menu Items
        hbox1 = QHBoxLayout()
        self.new_food_form = QHBoxLayout()
        add_item = QLabel("Add to Menu:")

        self.food_names = QComboBox()
        my_cursor = connection.cursor()
        my_cursor.execute('use cs4400spring2020')
        my_cursor.execute('select * from food')
        my_result = my_cursor.fetchall()
        for x in my_result:
            self.food_names.addItem(x[0])

        self.food_price = QLineEdit()
        ty_dolla_sign = QLabel('$')
        self.new_food_form.addWidget(self.food_names)
        self.new_food_form.addWidget(ty_dolla_sign)
        self.new_food_form.addWidget(self.food_price)
        hbox1.addWidget(add_item)
        hbox1.addLayout(self.new_food_form)
        hbox1.addWidget(self.add_item_button)

        #Put it together
        self.vbox1.addLayout(self.food_form)
        self.vbox1.addLayout(hbox1)

        group.setLayout(self.vbox1)

        self.menu_item_list = []

    #Buttons
        back_button = QPushButton('Back')
        back_button.clicked.connect(self.go_back)
        create_button = QPushButton('Create')
        create_button.clicked.connect(self.create)

    #Layout
        self.super_layout = QVBoxLayout()
        row_one = QHBoxLayout()
        row_one.addLayout(food_truck_name)
        row_two = QHBoxLayout()
        row_two.addLayout(self.station_form_box)
        last_row = QHBoxLayout()
        last_row.addWidget(back_button)
        last_row.addWidget(create_button)

        self.super_layout.addLayout(row_one)
        self.super_layout.addLayout(row_two)
        self.super_layout.addWidget(group2)
        self.super_layout.addWidget(group)
        self.super_layout.addLayout(last_row)
        self.setLayout(self.super_layout)

    def add_food(self):
        item = self.food_names.currentText()
        price = self.food_price.text()
        if self.food_names.currentText() != None and self.food_price != None:
            menu_item_combo ="(" + item + ", $" + price +")"
            new_item  = QListWidgetItem(menu_item_combo)
            self.menu_item.addItem(new_item)
            new_item .setSelected(True)
            self.food_price.setText(None)

            self.menu_item_list += [(item,price)]

    def add_staff(self):
        staffMember = self.staff_dropbox.currentText()
        if self.staff_dropbox.currentText() != None and self.staff_dropbox.currentText() != "":
            new_item  = QListWidgetItem(staffMember)
            self.staff_list.addItem(new_item)
            new_item .setSelected(True)

            self.staff_member_list += [staffMember]

    def go_back(self):
        self.close()
        cursor = self.connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]
        main_window = MainWindow(self.username, usertype, connection)
        main_window.exec()

    def create(self):
        new_ft = self.ft_name.text()
        ftstation = self.stat_names.currentText()
        if new_ft != None and ftstation != None and len(self.menu_item_list)>=1 and len(self.staff_member_list)>=1:
            cursor1 = self.connection.cursor()
            cursor1.callproc('mn_create_foodTruck_add_station', [new_ft,
                                                                    ftstation,
                                                                    self.username])
            for each in self.menu_item_list:
                food = each[0]
                price = each[1]
                price = round(float(price), 2)
                cursor2 = self.connection.cursor()
                cursor2.callproc('mn_create_foodTruck_add_menu_item', [f'{new_ft}', f'{price}', f'{food}'])
            for each in self.staff_member_list:
                staff = each
                cursor1 = self.connection.cursor()
                cursor1.callproc('mn_create_foodTruck_add_staff', [new_ft, staff])

            self.close()

            cursor = self.connection.cursor()
            query = 'SELECT userType from login_result'
            cursor.execute(query)
            row = cursor.fetchone()
            usertype = row[0]

            main_window = MainWindow(self.username, usertype, self.connection)
            main_window.exec()
        else:
            message = QMessageBox()
            text = "The Food Truck cannot be created."
            message.setText(text)
            message.exec()

#SCREEN 13 - UPDATE FOOD TRUCK
class UpdateFoodTruck(QDialog):
    def __init__(self, username, connection, ftname):
        super(UpdateFoodTruck, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Update Food Truck')

        self.username = username
        self.connection = connection
        self.ftname = ftname

        #Food Truck Name
        food_truck_name = QFormLayout()
        food_truck_name.addRow(QLabel('Food Truck Name:'), QLabel(self.ftname))

        #Stations
        cursor = self.connection.cursor()
        cursor.execute("SELECT stationName FROM FoodTruck where foodTruckName =(%s)", self.ftname)
        cur = cursor.fetchone()
        station = cur[0]

        self.stat_names = QComboBox()
        self.stat_names.addItem(station)
        my_cursor = connection.cursor()
        my_cursor.execute("SELECT * from station where stationName <> (%s)", station)
        my_result = my_cursor.fetchall()
        for x in my_result:
            self.stat_names.addItem(x[0])

        self.station_form_box = QFormLayout()
        self.station_form_box.addRow(QLabel("Station:"), self.stat_names)

        #Available + Working Staff:
        group2 = QGroupBox()
        self.staffBox = QVBoxLayout()
        self.add_staff_button = QPushButton('+')
        self.add_staff_button.setFixedWidth(50)
        self.add_staff_button.clicked.connect(self.add_staff)
        self.staff_form = QFormLayout()
        self.staff_list = QListWidget()
        self.staff_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.staff_form.addRow(QLabel("Assigned Staff:"), self.staff_list)

        self.staff_list.itemClicked.connect(self.enable_remove)

        cursor1 = self.connection.cursor()
        cursor1.callproc('mn_view_foodTruck_staff', [self.ftname])
        cursor12 = self.connection.cursor()
        query12 = 'SELECT * FROM mn_view_foodTruck_staff_result'
        cursor12.execute(query12)
        results12 = cursor12.fetchall()
        for each in results12:
            self.staff_list.addItem(each[0])

        hbox2 = QHBoxLayout()
        self.new_staff_form = QFormLayout()

        self.staff_dropbox = QComboBox()
        self.staff_dropbox.addItem(None)
        my_cursor2 = connection.cursor()
        my_cursor2.execute('SELECT * from staff where foodTruckName is NULL')
        my_result2 = my_cursor2.fetchall()
        for x in my_result2:
            self.staff_dropbox.addItem(x[0])
        self.new_staff_form.addRow(QLabel("Assign Staff Member:"), self.staff_dropbox)

        hbox2.addLayout(self.new_staff_form)
        hbox2.addWidget(self.add_staff_button)
        self.staffBox.addLayout(self.staff_form)
        self.staffBox.addLayout(hbox2)

        group2.setLayout(self.staffBox)

        self.staff_member_list = []

        #Foods:
        self.add_item = QPushButton('+')
        self.add_item.clicked.connect(self.add_food)
        group = QGroupBox()
        self.vbox1 = QVBoxLayout()
        self.food_box = QVBoxLayout()
        self.menu_item = QListWidget()
        self.menu_item.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.food_form = QFormLayout()
        self.food_form.addRow(QLabel("Menu Items:"), self.menu_item)

        cursor3 = self.connection.cursor()
        cursor3.execute('SELECT foodName, price from MenuItem  where foodTruckName = (%s)', self.ftname)
        my_result3 = cursor3.fetchall()
        for x in my_result3:
            name = x[0]
            price = x[1]
            combo = "(" +name+ ", $" +str(price) +")"
            each = QListWidgetItem(combo)
            self.menu_item.addItem(combo)

        #New Menu Items
        hbox1 = QHBoxLayout()
        self.new_food_form = QHBoxLayout()
        add_item = QLabel("Add to Menu:")

        self.food_names = QComboBox()
        my_cursor = connection.cursor()
        my_cursor.execute('use cs4400spring2020')
        my_cursor.execute('select * from food')
        my_result = my_cursor.fetchall()
        for x in my_result:
            self.food_names.addItem(x[0])

        self.food_price = QLineEdit()
        moneybagg_yo = QLabel('$')
        self.new_food_form.addWidget(self.food_names)
        self.new_food_form.addWidget(moneybagg_yo)
        self.new_food_form.addWidget(self.food_price)
        hbox1.addWidget(add_item)
        hbox1.addLayout(self.new_food_form)
        hbox1.addWidget(self.add_item)

        remove_layout = QHBoxLayout()
        self.remove_button = QPushButton('Remove Staff Member')
        self.remove_button.setEnabled(False)
        self.remove_button.clicked.connect(self.remove_staff)
        remove_layout.addWidget(self.remove_button)

        #Put it together
        self.vbox1.addLayout(self.food_form)
        self.vbox1.addLayout(hbox1)

        group.setLayout(self.vbox1)

        self.menu_item_list = []

        #Buttons
        add_button = QPushButton('+')
        back_button = QPushButton('Back')
        back_button.clicked.connect(self.go_back)
        update_button = QPushButton('Update')
        update_button.clicked.connect(self.update)

        #Layout
        self.super_layout = QVBoxLayout()
        row_one = QHBoxLayout()
        row_one.addLayout(food_truck_name)
        row_two = QHBoxLayout()
        row_two.addLayout(self.station_form_box)
        row_three = QHBoxLayout()
        row_three.addWidget(QLabel('Assigned Staff'))
        row_three.addWidget(self.staff_list)
        last_row = QHBoxLayout()
        last_row.addWidget(back_button)
        last_row.addWidget(update_button)

        self.super_layout.addLayout(row_one)
        self.super_layout.addLayout(row_two)
        self.super_layout.addWidget(group2)
        self.super_layout.addLayout(remove_layout)
        self.super_layout.addWidget(group)
        self.super_layout.addLayout(last_row)
        # self.super_layout.addLayout(myBoxLayout)
        self.setLayout(self.super_layout)

    def enable_remove(self):
        self.remove_button.setEnabled(True)
        pass

    def add_food(self):
        item = self.food_names.currentText()
        price = self.food_price.text()
        if self.food_names.currentText() != None and self.food_price != None:
            menu_item_combo ="(" + item + ", $" + price +")"
            new_item  = QListWidgetItem(menu_item_combo)
            self.menu_item.addItem(new_item)
            new_item .setSelected(True)
            self.food_price.setText(None)

            self.menu_item_list += [(item,price)]

        food = item
        price = round(float(price), 2)
        cursor2 = self.connection.cursor()
        cursor2.callproc('mn_create_foodTruck_add_menu_item', [self.ftname,
                                                                    price,
                                                                    food])
        message = QMessageBox()
        text = "You have added " + item + " to the menu."
        message.setText(text)
        message.exec()

    def add_staff(self):
        staffMember = self.staff_dropbox.currentText()
        if self.staff_dropbox.currentText() != None and self.staff_dropbox.currentText() != "":
            new_item = QListWidgetItem(staffMember)
            self.staff_list.addItem(new_item)
            new_item .setSelected(True)

            self.staff_member_list += [staffMember]

    def remove_staff(self):
        index_number = self.staff_list.currentRow()
        bye_bye_staff = self.staff_list.takeItem(index_number)
        gone_staff = bye_bye_staff.text()
        gone_staff_name = gone_staff.split()
        gone_fname = gone_staff_name[0]
        gone_lname = gone_staff_name[1]
        gone_cursor = connection.cursor()
        gone_cursor.execute(f'select username from user where firstName = "{gone_fname}" and lastName = "{gone_lname}"')
        gone_username = gone_cursor.fetchall()
        really_gone_like_actually = gone_username[0][0]
        gone_cursor.execute(f'update staff set foodTruckName = NULL where username = "{really_gone_like_actually}"')

        msg_box = QMessageBox()
        msg_box.setText('Note: If a food truck has no staff, it will be deleted.')
        msg_box.setWindowTitle('Note!')
        msg_box.exec()

    def go_back(self):
        self.close()
        cursor = connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]
        main_window = MainWindow(self.username, usertype, connection)
        main_window.exec()

    def update(self):
        new_station = self.stat_names.currentText()
        cursor = self.connection.cursor()
        cursor.callproc('mn_update_foodTruck_station', [self.ftname,
                                                            new_station])

        self.close()
        cursor = connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]
        main_page = MainWindow(self.username, usertype, connection)
        main_page.exec()


#SCREEN 14 - FOOD TRUCK SUMMARY
class FoodTruckSummary(QDialog):
    def __init__(self, username, connection, foodtruck, stationname, mindate, maxdate, sortby, sortdirection):
        super(FoodTruckSummary, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Food Truck Summary')

        self.username = username
        self.connection = connection 
        self.foodtruck = foodtruck
        self.station = stationname
        self.mindate = mindate
        self.maxdate = maxdate
        self.sortby = sortby
        self.sortdirection = sortdirection
        # doing the layout row by row

        self.super_layout = QVBoxLayout()

         # first row:
        row_one = QHBoxLayout()


        # food truck name: THIS SHOULD BE DONE FOR CONTAINING
        row_one.addWidget(QLabel('Food Truck Name (contain)'))
        self.food_truck_contain_tag = QLineEdit()
        row_one.addWidget(self.food_truck_contain_tag)



        # station names drop down
        row_one.addWidget(QLabel('Station Name'))
        self.stat_names = QComboBox()
        self.stat_names.addItem('')
        #the below block fills in the dropdown with one by one of the station names, dont use procedure here since overcomplicates
        my_cursor = connection.cursor()
        my_cursor.execute('use cs4400spring2020')
        my_cursor.execute('select * from station')
        my_result = my_cursor.fetchall()
        for x in my_result:
            self.stat_names.addItem(x[0])


        row_one.addWidget(self.stat_names)

        #making second row
        row_two = QHBoxLayout()

        row_two.addWidget(QLabel('Date'))
        self.date_start_tag = QLineEdit()
        self.date_end_tag = QLineEdit()

        row_two.addWidget(self.date_start_tag)
        row_two.addWidget(self.date_end_tag)

        #making row 2.5
        #Filter 
        label = QLabel("Filter By:")

        self.asc_desc_filter = QComboBox()
        self.asc_desc_filter.addItem('ASC')
        self.asc_desc_filter.addItem('DESC')

        self.type_filter = QComboBox()
        self.type_filter.addItem('foodTruckName')
        self.type_filter.addItem('totalOrder')
        self.type_filter.addItem('totalRevenue')
        self.type_filter.addItem('totalCustomer')

        #making third row
        row_three = QHBoxLayout()
        # filter button
        filter_button = QPushButton('Filter')
        filter_button.clicked.connect(self.filter) # connect to the filter function

        row_three.addWidget(label)
        row_three.addWidget(self.type_filter)
        row_three.addWidget(self.asc_desc_filter)
        row_three.addWidget(filter_button)

        # table
        cursor3 = connection.cursor()
        cursor3.callproc('mn_filter_summary', [self.username,
                                                            self.foodtruck,
                                                            self.station,
                                                            self.mindate,
                                                            self.maxdate,
                                                            self.sortby,
                                                            self.sortdirection])
        cursor4 = connection.cursor()
        query4 = 'SELECT * FROM mn_filter_summary_result'
        cursor4.execute(query4)
        cursor4_results = cursor4.fetchall()

        
        num = len(cursor4_results)
        self.option_table = QTableWidget(num, 4, self) 
        self.option_table.setHorizontalHeaderLabels(['Food Truck Name', '# Total Order', 'Total Revenue', '# Customer'])
        for i, info in enumerate(cursor4_results):
            self.option_table.setItem(i, 0, QTableWidgetItem(info[0]))
            order = info[1]
            if order == None:
                order = None
            else:
                order = str(order)
            rev = info[2]
            if rev == None:
                rev = None
            else:
                rev = str(rev)
            cust = info[3]
            if cust == None:
                cust = 0
            else:
                cust = str(cust)
            self.option_table.setItem(i, 1, QTableWidgetItem(order))
            self.option_table.setItem(i, 2, QTableWidgetItem(rev))
            self.option_table.setItem(i, 4, QTableWidgetItem(cust))


        #making fourth row
        last_row = QHBoxLayout()

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.go_back)
        self.view_detail_button = QPushButton('View Detail')
        self.view_detail_button.clicked.connect(self.view_detail_summary)
        self.view_detail_button.setEnabled(False)
        last_row.addWidget(back_button)
        last_row.addWidget(self.view_detail_button)

        self.option_table.itemClicked.connect(self.enable)


        self.super_layout.addLayout(row_one)
        self.super_layout.addWidget(QLabel('Date Format: MM-DD-YYYY'))
        self.super_layout.addLayout(row_two)
        self.super_layout.addLayout(row_three)
        self.super_layout.addWidget(self.option_table)
        self.super_layout.addLayout(last_row)
        self.setLayout(self.super_layout)

    def filter(self):
        foodtruck = self.food_truck_contain_tag.text()
        station = self.stat_names.currentText()
        mindate = self.date_start_tag.text()
        if mindate == '':
            min_date = None
        else:
            min_date = datetime.datetime.strptime(mindate, '%m-%d-%Y').date()
        maxdate = self.date_end_tag.text()
        if maxdate == '':
            max_date = None
        else:
            max_date = datetime.datetime.strptime(maxdate, '%m-%d-%Y').date()
        sortby = self.type_filter.currentText()
        sortdirection = self.asc_desc_filter.currentText()

        self.close()
        vfts = FoodTruckSummary(self.username, self.connection, foodtruck, station, min_date, max_date, sortby, sortdirection)
        vfts.exec()

    def enable(self):
        row = self.option_table.currentRow()
        highlight = self.option_table.selectRow(row)
        if self.option_table.currentIndex() == 1:
            self.view_detail_button.setEnabled(False)
        else:
            self.view_detail_button.setEnabled(True)

    def go_back(self):
        self.close()
        cursor = connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]
        main_window = MainWindow(self.username, usertype, connection)
        main_window.exec()
    
    def view_detail_summary(self):
        self.close()
        row = self.option_table.currentRow()
        ft = self.option_table.item(row,  0).text()
        sd = SummaryDetail(self.username, ft, self.connection)
        sd.exec()

#SCREEN 15 - SUMMARY DETAIL
class SummaryDetail(QDialog, QAbstractTableModel):
    def __init__(self, username, foodtruck, connection):
        super(SummaryDetail, self).__init__()
        self.setModal(True)
        self.setWindowTitle("Summary Detail")

        self.username = username
        self.connection = connection
        self.foodtruck = foodtruck

        vbox = QVBoxLayout()
        info = QLabel(("Food Truck: ") + str(self.foodtruck))
        vbox.addWidget(info)

        #Build Table
        cursor = self.connection.cursor()
        procedure = cursor.callproc('mn_summary_detail', [self.username,
                                                        self.foodtruck])
        cursor1 = self.connection.cursor()
        query = 'SELECT * from mn_summary_detail_result'
        cursor1.execute(query)
        cursor1_results = cursor1.fetchall()

        num = len(cursor1_results)
        self.summary_table = QTableWidget(num, 5, self)
        self.summary_table.setHorizontalHeaderLabels(['Date', 'Customer Name','Purchase Total ($)', 'Items in Order', 'Foods'])
        for i, building in enumerate(cursor1_results):
            date = str(building[0])
            self.summary_table.setItem(i, 0, QTableWidgetItem(date))
            self.summary_table.setItem(i, 1, QTableWidgetItem(building[1]))
            total = building[2]
            if total == None:
                total = None
            else:
                total = str(total)
            num = building[3]
            if num == None:
                num = None
            else:
                num = str(num)
            self.summary_table.setItem(i, 2, QTableWidgetItem(total))
            self.summary_table.setItem(i, 3, QTableWidgetItem(num))
            self.summary_table.setItem(i, 4, QTableWidgetItem(building[4]))

        home_button = QPushButton('Home')
        home_button.clicked.connect(self.home)

        vbox.addWidget(self.summary_table)
        vbox.addWidget(home_button)

        self.setLayout(vbox)

    def home(self):
        self.close()

        cursor = self.connection.cursor()
        query = 'SELECT userType from login_result'
        cursor.execute(query)
        row = cursor.fetchone()
        usertype = row[0]

        main_window = MainWindow(self.username, usertype, self.connection)
        main_window.exec()

# SCREEN 16 - EXPLORE
class Explore(QDialog):
    def __init__(self, username, user_type, connection):
        super(Explore, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Customer Explore')
        self.username = username
        self.user_type = user_type
        self.bldg_name = ''
        self.station_name = ''
        self.bldg_tag = ''
        self.food_truck = ''
        self.food = ''

        # doing the layout row by row

        self.super_layout = QVBoxLayout()

        # first row:
        row_one = QHBoxLayout()

        row_one.addWidget(QLabel('Building Name'))

        # building names drop down
        self.bldg_names = QComboBox()
        self.bldg_names.addItem('')

        my_cursor = connection.cursor()

        my_cursor.execute('use cs4400spring2020')
        my_cursor.execute('select * from building')
        my_result = my_cursor.fetchall()
        for x in my_result:
            self.bldg_names.addItem(x[0])

        self.bldg_names.activated.connect(self.chg_bldg_name)

        row_one.addWidget(self.bldg_names)

        row_one.addWidget(QLabel('Station Name'))

        # station names drop down
        self.stat_names = QComboBox()
        self.stat_names.addItem('')

        my_cursor.execute('use cs4400spring2020')
        my_cursor.execute('select * from station')
        my_result = my_cursor.fetchall()
        for x in my_result:
            self.stat_names.addItem(x[0])

        self.stat_names.activated.connect(self.chg_stat_name)

        row_one.addWidget(self.stat_names)

        # second row
        row_two = QHBoxLayout()

        row_two.addWidget(QLabel('Building Tag (contain)'))

        # building tag text entry
        self.bldg_tag_entry = QLineEdit()
        self.bldg_tag_entry.textChanged.connect(self.chg_bldg_tag)
        row_two.addWidget(self.bldg_tag_entry)

        row_two.addWidget(QLabel('Food Truck Name (contain)'))

        # food truck text entry
        self.food_truck_tag = QLineEdit()
        self.food_truck_tag.textChanged.connect(self.chg_ft_tag)
        row_two.addWidget(self.food_truck_tag)

        # third row
        row_three = QHBoxLayout()

        row_three.addWidget(QLabel('Food (contain)'))

        # food text entry
        self.food_tag = QLineEdit()
        self.food_tag.textChanged.connect(self.chg_food)
        row_three.addWidget(self.food_tag)

        # filter button
        filter_button = QPushButton('Filter')
        filter_button.clicked.connect(self.filter)

        # table
        self.option_table = QTableWidget(2, 4, self)
        self.option_table.setHorizontalHeaderLabels(['Station', 'Building', 'Food Truck(s)', 'Food(s)'])
        self.option_table.itemClicked.connect(self.set_location_enable)

        # last row
        last_row = QHBoxLayout()
        back_button = QPushButton('Back')
        back_button.clicked.connect(self.go_back)
        self.select_button = QPushButton('Select As Current Location')
        self.select_button.setEnabled(False)
        self.select_button.clicked.connect(self.chg_current_loc)
        last_row.addWidget(back_button)
        last_row.addWidget(self.select_button)

        self.super_layout.addLayout(row_one)
        self.super_layout.addLayout(row_two)
        self.super_layout.addLayout(row_three)
        self.super_layout.addWidget(filter_button)
        self.super_layout.addWidget(self.option_table)
        self.super_layout.addLayout(last_row)

        self.setLayout(self.super_layout)

    def filter(self):
        my_cursor = connection.cursor()
        my_cursor.execute('use cs4400spring2020')
        my_cursor.callproc('cus_filter_explore', [f'{self.bldg_name}', f'{self.station_name}', f'{self.bldg_tag}', f'{self.food_truck}', f'{self.food}'])
        my_cursor.execute('select * from cus_filter_explore_result')
        curr = my_cursor.fetchall()
        result_len = len(curr)

        self.option_table.clear()
        self.option_table.setRowCount(result_len)
        for i, result in enumerate(curr):
            my_station = result[0]
            my_building = result[1]
            my_fts = result[2]
            my_foods = result[3]
            self.option_table.setItem(i, 0, QTableWidgetItem(my_station))
            self.option_table.setItem(i, 1, QTableWidgetItem(my_building))
            self.option_table.setItem(i, 2, QTableWidgetItem(my_fts))
            self.option_table.setItem(i, 3, QTableWidgetItem(my_foods))

        self.setLayout(self.super_layout)

    def set_location_enable(self):
        if self.option_table.currentIndex() == 1:
            self.select_button.setEnabled(False)
        else:
            self.select_button.setEnabled(True)

    def chg_bldg_name(self, index):
        self.bldg_name = self.bldg_names.itemText(index)

    def chg_stat_name(self, index):
        self.station_name = self.stat_names.itemText(index)

    def chg_bldg_tag(self):
        self.bldg_tag = self.bldg_tag_entry.text()

    def chg_ft_tag(self):
        self.food_truck = self.food_truck_tag.text()

    def chg_food(self):
        self.food = self.food_tag.text()

    def go_back(self):
        self.close()
        main_page = MainWindow(self.username, self.user_type, connection)
        main_page.exec()

    def chg_current_loc(self):
        my_cursor = connection.cursor()
        new_station = self.option_table.currentRow()
        stat_name = self.option_table.item(new_station, 0).text()
        my_cursor.callproc('cus_select_location', [f'{self.username}', f'{stat_name}'])
        success_message = QMessageBox()
        success_message.setWindowTitle('Success!')
        success_message.setText(f'Changed Location to {stat_name}')
        success_message.exec()


# SCREEN 17 - VIEW CURRENT INFO
class ViewCurrentInfo(QDialog):
    def __init__(self, username, user_type, connection):
        super(ViewCurrentInfo, self).__init__()
        self.setModal(True)
        self.setWindowTitle('View Current Information')
        self.username = username
        self.user_type = user_type
        self.stat = ''
        self.bldg = ''
        self.bldgtags = ''
        self.bldgdesc = ''
        self.balance = ''
        self.food_truck = ''

        # get current info
        my_cursor = connection.cursor()
        my_cursor.execute('use cs4400spring2020')
        my_cursor.callproc('cus_current_information_basic', [f'{self.username}'])
        my_cursor.execute('select * from cus_current_information_basic_result')
        curr = my_cursor.fetchall()

        self.stat = curr[0][0]
        self.bldg = curr[0][1]
        self.bldgtags = curr[0][2]
        self.bldgdesc = curr[0][3]
        self.balance = curr[0][4]
        balance_str = str(self.balance)

        # get food truck info

        my_cursor.callproc('cus_current_information_foodTruck', [f'{self.username}'])
        my_cursor.execute('select * from cus_current_information_foodTruck_result')
        self.food_truck_info = my_cursor.fetchall()

        num_ft = len(self.food_truck_info)

        self.food_truck_table = QTableWidget(num_ft, 3, self)
        self.food_truck_table.setHorizontalHeaderLabels(['Food Truck', 'Manager', 'Food(s)'])

        for i, truck in enumerate(self.food_truck_info):
            self.food_truck_table.setItem(i, 0, QTableWidgetItem(truck[0]))
            self.food_truck_table.setItem(i, 1, QTableWidgetItem(truck[1]))
            self.food_truck_table.setItem(i, 2, QTableWidgetItem(truck[2]))


        # layout
        layout = QVBoxLayout()

        # customer info
        cust_box = QGroupBox('Current Information')
        cust_info = QFormLayout()
        cust_info.addRow(QLabel('Station'), QLabel(self.stat))
        cust_info.addRow(QLabel('Building'), QLabel(self.bldg))
        cust_info.addRow(QLabel('Building Tag(s)'), QLabel(self.bldgtags))
        cust_info.addRow(QLabel('Building Description'), QLabel(self.bldgdesc))
        cust_info.addRow(QLabel('Balance'), QLabel(balance_str))
        cust_box.setLayout(cust_info)

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.go_back)
        self.order_button = QPushButton('Order')
        self.order_button.clicked.connect(self.order)
        self.order_button.setEnabled(False)
        self.food_truck_table.itemClicked.connect(self.enable_order)

        last_row = QHBoxLayout()
        last_row.addWidget(back_button)
        last_row.addWidget(self.order_button)

        layout.addWidget(cust_box)
        layout.addWidget(self.food_truck_table)
        layout.addLayout(last_row)

        self.setLayout(layout)

    def go_back(self):
        self.close()
        main_page = MainWindow(self.username, self.user_type, connection)
        main_page.exec()

    def order(self):
        my_date = datetime.datetime.now().date()
        my_cursor = connection.cursor()
        my_cursor.callproc('cus_order', [f'{my_date}', f'{self.username}'])
        my_cursor.execute(f'select max(orderid) from orders where customerUsername = "{self.username}"')
        my_result = my_cursor.fetchall()
        order_id = my_result[0][0]
        food_truck = self.food_truck_table.currentRow()
        ft_name = self.food_truck_table.item(food_truck, 0).text()
        self.food_truck = ft_name
        self.close()
        order_page = Order(self.username, self.user_type, self.food_truck, order_id, connection)
        order_page.exec()

    def enable_order(self):
        if self.food_truck_table.currentIndex() == 1:
            self.order_button.setEnabled(False)
        else:
            self.order_button.setEnabled(True)


# SCREEN 18 - ORDER
class Order(QDialog):
    def __init__(self, username, user_type, food_truck, order_id, connection):
        super(Order, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Customer Order')
        self.date = datetime.datetime.now().date()

        self.username = username
        self.user_type = user_type
        self.food_truck = food_truck
        self.order_id = order_id

        layout = QVBoxLayout()

        order_box = QGroupBox('Order')
        box_lay = QVBoxLayout()
        ord_box_lay = QHBoxLayout()
        ord_box_lay.addWidget(QLabel('Food Truck:'))
        ord_box_lay.addWidget(QLabel(self.food_truck))
        box_lay.addLayout(ord_box_lay)
        id_box_layout = QHBoxLayout()
        id_box_layout.addWidget(QLabel('Order ID:'))
        id_box_layout.addWidget(QLabel(f'{self.order_id}'))
        box_lay.addLayout(id_box_layout)
        order_box.setLayout(box_lay)
        layout.addWidget(order_box)

        # table of food
        my_cursor = connection.cursor()
        my_cursor.execute('use cs4400spring2020')
        my_cursor.execute(f'select foodName, price from menuitem where foodTruckName = "{self.food_truck}"')
        curr = my_cursor.fetchall()

        food_num = len(curr)

        self.food_table = QTableWidget(food_num, 3, self)
        self.food_table.setHorizontalHeaderLabels(['Food', 'Price', 'Purchase Quantity'])
        for i, food in enumerate(curr):
            self.food_table.setItem(i, 0, QTableWidgetItem(food[0]))
            price = food[1]
            price_str = str(price)
            self.food_table.setItem(i, 1, QTableWidgetItem(price_str))
        self.food_table.cellChanged.connect(self.new_quant)
        layout.addWidget(self.food_table)

        # date entry
        date_layout = QHBoxLayout()
        date_label = QLabel('Date')
        date_layout.addWidget(date_label)
        self.date_entry = QLineEdit(f'{self.date}')
        self.date_entry.textChanged.connect(self.change_date)
        date_layout.addWidget(self.date_entry)
        layout.addLayout(date_layout)

        # last row of buttons
        last_row = QHBoxLayout()
        # to go back to current info
        back_button = QPushButton('Back')
        back_button.clicked.connect(self.go_back)
        last_row.addWidget(back_button)
        # to submit order
        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.submit)
        last_row.addWidget(submit_button)

        layout.addLayout(last_row)

        self.setLayout(layout)

    def go_back(self):
        self.close()
        curr_info = ViewCurrentInfo(self.username, self.user_type, connection)
        curr_info.exec()

    def new_quant(self):
        food = self.food_table.currentRow()
        food_name = self.food_table.item(food, 0).text()
        food_quantity = self.food_table.item(food, 2).text()
        my_cursor2 = connection.cursor()
        my_cursor2.execute('use cs4400spring2020')
        my_cursor2.callproc('cus_add_item_to_order', [f'{self.food_truck}', f'{food_name}', f'{food_quantity}', f'{self.order_id}'])
        success_box = QMessageBox()
        success_box.setText('If you had enough balance, added to order!')
        success_box.setWindowTitle('Success')
        success_box.exec()

    def submit(self):
        submission = QMessageBox()
        submission.setText('Order Submitted!')
        submission.setWindowTitle('Success')
        submission.exec()
        # go back to home page
        self.close()
        main_page = MainWindow(self.username, self.user_type, connection)
        main_page.exec()

    def change_date(self):
        self.date = self.date_entry.text()



# SCREEN 19 - ORDER HISTORY
class OrderHistory(QDialog):
    def __init__(self, username, user_type, connection):
        super(OrderHistory, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Customer Order History')
        self.username = username
        self.user_type = user_type

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Order History'))

        #table
        my_cursor = connection.cursor()
        my_cursor.execute('use cs4400spring2020')
        my_cursor.callproc('cus_order_history', [f'{self.username}'])
        my_cursor.execute('select * from cus_order_history_result')
        curr = my_cursor.fetchall()

        ord_hist_len = len(curr)

        ord_hist_table = QTableWidget(ord_hist_len, 5, self)
        ord_hist_table.setHorizontalHeaderLabels(['Date', 'OrderID', 'Order Total', 'Food(s)', 'Food Quantity'])

        for i, history in enumerate(curr):
            the_date = str(history[0])
            ord_hist_table.setItem(i, 0, QTableWidgetItem(the_date))
            ord_hist_table.setItem(i, 1, QTableWidgetItem(history[1]))
            the_total = str(history[2])
            ord_hist_table.setItem(i, 2, QTableWidgetItem(the_total))
            ord_hist_table.setItem(i, 3, QTableWidgetItem(history[3]))
            the_quant = str(history[4])
            ord_hist_table.setItem(i, 4, QTableWidgetItem(the_quant))

        layout.addWidget(ord_hist_table)

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)
        self.setLayout(layout)

    def go_back(self):
        self.close()
        main_page = MainWindow(self.username, self.user_type, connection)
        main_page.exec()




if __name__=='__main__':
    app = QApplication(sys.argv) #start the application
    global connection
    try:
        connection = pymysql.connect(host = 'localhost', 
                                    passwd='',
                                    user='root',
                                    db='cs4400spring2020')
    except Exception as e:
        print("Couldn't log onto the MySQL server")
        print(e)
        qApp.quit()
        sys.exit()
    screen = DbLoginDialog(connection)
    screen.show()
    sys.exit(app.exec_())

