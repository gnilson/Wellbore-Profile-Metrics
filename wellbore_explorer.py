
import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from numpy import arange

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

xdata = []
ydata = []

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: PyQt with matplotlib')


        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        #self.textbox.setText('1 2 3 4')
        self.on_draw()


    def on_press(self):
	print "boo"
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
    
        
    def on_draw(self):
        """ Redraws the figure
        """

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

	#((self.well_prod[i+1]/self.dydx[i+1])-(self.well_prod[i+1]/self.dydx[i-1]))/(self.time[i+1]-self.time[i-1])

	#line, = self.axes.plot(self.time, self.well_prod, 'o', markersize=5, markeredgewidth=0.3)
	self.axes.plot(xdata, ydata, '-', color='green')

	
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
        
        self.draw_button = QPushButton("Hyp Regression")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_press)

	self.reset_button = QPushButton("Reset Start")
	self.connect(self.reset_button, SIGNAL('clicked()'), self.on_press)

	self.bf_sens = QPushButton("B-Factor Sens")
	self.connect(self.bf_sens, SIGNAL('clicked()'), self.on_press)
        
        self.calc_bf = QCheckBox("Calculate B-Factor")
        self.calc_bf.setChecked(False)
        self.connect(self.calc_bf, SIGNAL('stateChanged(int)'), self.on_press)


	self.well_listview = QListView()
	self.listmodel = QStandardItemModel(self.well_listview)

	self.well_list = ["one", "two", "three"]
	#self.well_list.sort()
	for well in self.well_list:
	    item = QStandardItem()
	    item.setText(well)
	    item.setEditable(False)
	    self.listmodel.appendRow(item)

	self.well_listview.setModel(self.listmodel)
	self.connect(self.well_listview, SIGNAL('doubleClicked(QModelIndex)'), self.on_press)

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


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

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
    master_dict = {}
    tmp_dict = {}

    for row in reader:
	newuwi = int(row['UWI'])

	if uwi == newuwi:
	    tmp_dict = extend_dict(tmp_dict, row)
	    
	else:
	    master_dict[uwi] = tmp_dict.copy()
	    tmp_dict = {}

	uwi = newuwi
	

    fd.close()


    for k in master_dict.keys():

	    for j in master_dict[k].keys():
		try:
		    if ['Deviation Azimuth',
			'Deviation E/W',
			'Deviation N/S',
			'TV Depth',
			'Measured Depth',
			'Deviation Angle',
			'UWI'].index(j):
			master_dict[k][j] = map(float, master_dict[k][j])
		except ValueError:
		    pass

    api = master_dict.keys()[40]
    
    xdata = master_dict[api]['Deviation N/S']
    ydata = master_dict[api]['TV Depth']

    main()
