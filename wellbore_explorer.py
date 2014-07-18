
import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from numpy import arange
from numpy import linspace
from numpy import array
from numpy import where
from numpy import polyfit
from numpy import poly1d

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
import matplotlib.ticker as ticker
import numpy.random
import math
import csv


from scipy import interpolate
from scipy import cluster


# CALCULATE:
# Average inclination
# Straitness Index
# 


well_list = []  
well_names = [] # well name <--> UWI

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: PyQt with matplotlib')

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

	self.xdata = []
	self.ydata = []
	self.dev_data = []
	self.md_data = []

        #self.textbox.setText('1 2 3 4')
        self.on_draw()

    def on_press(self):
	return

    def well_selected(self, ind):
	print "Well Selected", well_list[ind.row()], well_names[well_list[ind.row()]] 

	self.xdata = master_dict[well_names[well_list[ind.row()]]]['Deviation N/S']
	self.ydata = master_dict[well_names[well_list[ind.row()]]]['TV Depth']
	self.dev_data = array(master_dict[well_names[well_list[ind.row()]]]['Deviation Angle'])
	self.md_data = master_dict[well_names[well_list[ind.row()]]]['Measured Depth']

	self.on_draw()

	return


    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())

    def sort_by_straitness(self):

	fd = open('out.csv','w')
	print "API, STRAITNESS RATIO, ANGLE"
	fd.write("API, STRAITNESS RATIO, ANGLE\n")
	 
	for well in master_dict.keys():
	    
	    self.xdata = master_dict[well]['Deviation N/S']
	    self.ydata = master_dict[well]['TV Depth']
	    self.dev_data = array(master_dict[well]['Deviation Angle'])
	    self.md_data = master_dict[well]['Measured Depth']

	    if self.xdata:
		try:

		    centroid, label = cluster.vq.kmeans2(self.dev_data, 3)
		    ct = centroid[label[-1]]
		    x0 = where(self.dev_data >= ct)[0][0]

		    #x0 = where(self.dev_data > 70)[0][0]
		    targ_x = self.xdata[x0:]
		    targ_y = self.ydata[x0:]


		    lin_int = poly1d(polyfit(targ_x, targ_y, 1))
		    xs = [self.xdata[x0], self.xdata[-1]]
		    out = lin_int(xs)
		    stlen = ((out[-1]-out[0])**2.0 + (xs[-1]-xs[0])**2.0)**0.5
		    angle = -1*math.atan((out[-1]-out[0])/(abs(xs[-1]-xs[0]))*360/(2*math.pi))

		    tcknot, u = interpolate.splprep([self.xdata, self.ydata],
						    u=self.md_data,
						    s=0,
						    k=3)
		    mds = linspace(min(u), max(u), 5000)
		    out = interpolate.splev(mds, tcknot)
		    mds = linspace(self.md_data[x0], self.md_data[-1], 5000)
		    out = interpolate.splev(mds, tcknot)

		    splen = 0.0
		    for i in arange(0, len(out[0])-1):
			splen += ((out[0][i+1] - out[0][i])**2.0 + (out[1][i+1] - out[1][i])**2.0) ** 0.5
		 
		    print "%s, %s, %s" %(well, (1-stlen/splen)*1000, angle)
		    fd.write("%s, %s, %s\n" %(well, (1-stlen/splen)*1000, angle))
		    
		except SystemError:
		    print "%s, ERROR, ERROR" % (well,)
		    fd.write("%s, ERROR, ERROR\n" % (well,))
		    pass

	fd.close()
	print "WELLBORE DATA WRITTEN TO out.csv"

	return

        
    def on_draw(self):
        """ Redraws the figure
        """

	print "on_draw"
	self.axes.clear()
        #self.title.set_text(self.wellname)
	self.axes.set_picker(1)
        self.axes.set_color_cycle(['b','g','r','c','m','y','k','w','#A6CEE3','#1F78B4','#B2DF8A','#CAB2D6','#FB9A99','#E31A1C','#FF7F00','#CAB2D6','#FFFF99'])
        #self.axes.set_yscale('log')
        #self.axes.set_xscale('log')
        self.axes.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        #self.axes.set_ylim(0.01, 10000)
        #axes.set_xlim(0, 3000)
        self.axes.set_xlabel("X (ft)")
        self.axes.set_ylabel("Y (ft)")

        self.axes.yaxis.grid(True, which="both", ls='-', color='#C0C0C0')
        self.axes.xaxis.grid(True, which="both", ls='-', color='#C0C0C0')
        self.axes.grid(True) 

	if self.xdata:


	    #############
	    #K-MEANS
	    centroid, label = cluster.vq.kmeans2(self.dev_data, 3)
	    ct = centroid[label[-1]]
	    #x0 = where(label == label[-1])[0][0]

	    #############
	    x0 = where(self.dev_data >= ct)[0][0]
	    targ_x = self.xdata[x0:]
	    targ_y = self.ydata[x0:]

	    lin_int = poly1d(polyfit(targ_x, targ_y, 1))
	    xs = [self.xdata[x0], self.xdata[-1]]
	    out = lin_int(xs)
	    self.axes.plot(xs, out, '-', color='red')

	    stlen = ((out[-1]-out[0])**2.0 + (xs[-1]-xs[0])**2.0)**0.5
	    print "STRAIT_LENGTH", stlen
	    angle = -1*math.atan((out[-1]-out[0])/(abs(xs[-1]-xs[0]))*360/(2*math.pi))

	    tcknot, u = interpolate.splprep([self.xdata, self.ydata],
					    u=self.md_data,
					    s=0,
					    k=3)
	    mds = linspace(min(u), max(u), 5000)
	    out = interpolate.splev(mds, tcknot)
	    self.axes.plot(out[0], out[1], '-')
	    
	    mds = linspace(self.md_data[x0], self.md_data[-1], 5000)
	    out = interpolate.splev(mds, tcknot)
	    
	    splen = 0.0
	    for i in arange(0, len(out[0])-1):
		splen += ((out[0][i+1] - out[0][i])**2.0 + (out[1][i+1] - out[1][i])**2.0) ** 0.5
	    print "SPLINE_LENGTH", splen
	    self.axes.plot(out[0], out[1], '-')
	    print out[0][0], out[0][-1], out[1][0], out[1][-1]

	    print "RATIO", (1-stlen/splen)*1000
	    print "ANGLE", angle
	    # the larger the worse


	    


	#self.axes.plot(self.xdata, self.ydata, '.', color='green')

        self.canvas.draw()
	return
    
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100

        self.fig = plt.figure(facecolor="white")
        #self.title = self.fig.suptitle(self.wellname)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
	self.axes = self.fig.add_subplot(111, axisbelow=True)
	plt.gca().invert_yaxis()
	#self.bfaxes = self.fig.add_subplot(122, axisbelow=True)
	 
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        #self.canvas.mpl_connect('pick_event', self.on_pick)
	#self.canvas.mpl_connect('button_press_event', self.on_press)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
        # 
        #self.textbox = QLineEdit()	

	self.lspinbox = QDoubleSpinBox()
	self.lspinbox.setMinimum(0.01)
	self.lspinbox.setMaximum(1)
	self.lspinbox.setSingleStep(0.1)
	self.lspinbox.setValue(0.1)
	

	self.DOFPspinbox = QSpinBox()
	self.DOFPspinbox.setMinimum(0)
	self.DOFPspinbox.setMaximum(100)
	self.DOFPspinbox.setSingleStep(1)
	self.DOFPspinbox.setValue(0)

        self.connect(self.DOFPspinbox, SIGNAL('valueChanged (int)'), self.on_press)

        #self.textbox.setMinimumWidth(200)
        # self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_draw)
	# self.connect(self.lspinbox, SIGNAL('valueChanged (double)'), self.on_draw)
        
        self.draw_button = QPushButton("Sort Alphabetically")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_press)

	self.reset_button = QPushButton("Sort by Straitness")
	self.connect(self.reset_button, SIGNAL('clicked()'), self.sort_by_straitness)

	self.bf_sens = QPushButton("Sort by X")
	self.connect(self.bf_sens, SIGNAL('clicked()'), self.on_press)
        
        self.calc_bf = QCheckBox("Export Data")
        self.calc_bf.setChecked(False)
        self.connect(self.calc_bf, SIGNAL('stateChanged(int)'), self.on_press)


	self.well_listview = QListView()
	self.listmodel = QStandardItemModel(self.well_listview)

	#self.well_list.sort()
	for well in well_list:
	    item = QStandardItem()
	    item.setText(well)
	    item.setEditable(False)
	    self.listmodel.appendRow(item)

	self.well_listview.setModel(self.listmodel)
	self.connect(self.well_listview, SIGNAL('doubleClicked(QModelIndex)'), self.well_selected)

        #slider_label = QLabel('Bar width (%):')
        #self.slider = QSlider(Qt.Horizontal)
        #self.slider.setRange(1, 100)
        #self.slider.setValue(20)
        #self.slider.setTracking(True)
        #self.slider.setTickPosition(QSlider.TicksBothSides)
        #self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)
        
        #
        # Layout with box sizers
        # 
	lhbox1 = QHBoxLayout()
	lhbox1.addWidget(QLabel("Bourdet Derrivative L:"))
	lhbox1.addWidget(self.lspinbox)

        lhbox2 = QHBoxLayout()
	lhbox2.addWidget(QLabel("Offset DOFP:"))
	lhbox2.addWidget(self.DOFPspinbox)
	
        vboxtools = QVBoxLayout()
	vboxtools.addLayout(lhbox1)
	vboxtools.addLayout(lhbox2)
        
        for w in [  self.draw_button, self.reset_button, self.bf_sens, self.calc_bf]:
            vboxtools.addWidget(w)
            vboxtools.setAlignment(w, Qt.AlignVCenter)

	lrtoolsbox = QHBoxLayout()
	lrtoolsbox.addLayout(vboxtools)
	lrtoolsbox.addWidget(self.well_listview)
		
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(lrtoolsbox)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    def create_status_bar(self):
        self.status_text = QLabel("Double click on a well name")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

def extend_dict(d1, d2):

    dnew = {}

    if len(d1) == 0:

	for k, v in d2.items():
	    dnew[k] = [v,]

    else:
	for k, v in d2.items():
	    dnew[k] = d1[k] + [v]

    return dnew
    

if __name__ == "__main__":

    fd = open("./IHS Raw Data/Directional_Surveys.csv", 'rb')

    reader = csv.DictReader(fd)

    uwi = 0
    newuwi = 0
    master_dict = {}
    tmp_dict = {}
    well_names = {}
    lastrow = []

    for row in reader:

	newuwi = int(row['UWI'])

	if uwi == newuwi or not uwi:
	    tmp_dict = extend_dict(tmp_dict, row)
	    
	elif len(tmp_dict):
	    well_names[lastrow['Well Name'] + ' ' + lastrow['Well Num']] = uwi
	    master_dict[uwi] = tmp_dict.copy()
	    tmp_dict = {}

	lastrow = row
	uwi = newuwi
	

    fd.close()


    for k in master_dict.keys():

	welldata = master_dict[k]
	# strings to floats
	for j in master_dict[k].keys():
	    try:
		if ['Deviation Azimuth',
		    'Deviation E/W',
		    'Deviation N/S',
		    'TV Depth',
		    'Measured Depth',
		    'Deviation Angle',
		    'UWI'].index(j):
		    welldata[j] = map(float, welldata[j])
	    except ValueError:
		pass


	for i in arange(0, len(welldata['Deviation E/W'])):
	    if welldata['E/W'][i] == 'W':
		welldata['Deviation E/W'][i] *= -1

	    if welldata['N/S'][i] == 'S':
		welldata['Deviation N/S'][i] *= -1
	    
	
    #api = master_dict.keys()[40]
    
    #xdata = master_dict[api]['Deviation N/S']
    #ydata = master_dict[api]['TV Depth']

    well_list = well_names.keys()
    well_list.sort()


    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
