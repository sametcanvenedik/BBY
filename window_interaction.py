from bby_window import Ui_MainWindow #ana ekran ile program arasında veri akışı ve arayüz güncellemelerinin iletilmesi için kullanılıyor
from PyQt5.QtWidgets import QMainWindow, QFileDialog
import os

class interactions(QMainWindow): 
    def __init__(self, controller):     
        super(interactions, self).__init__() #sınıf ana dosyadan çağrılınca ana programın fonksiyonlarını tanır.
        self._controller = controller
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.btn_open_file.setEnabled(True)
        self.ui.btn_background.setEnabled(False)
        self.ui.btn_calculate.setEnabled(False)
        self.ui.btn_calculate_2.setEnabled(False)
        self.ui.btn_video.setEnabled(False)

        self.ui.image.setScaledContents(True)
        self.ui.image_3.setScaledContents(True)
        self.ui.image_4.setScaledContents(True)
        self.ui.image_5.setScaledContents(True)

        self.ui.btn_open_file.clicked.connect(self._controller.select_data_folder)
        self.ui.btn_background.clicked.connect(self._controller.background_calculation)
        self.ui.btn_calculate.clicked.connect(self._controller.calculation_first)
        self.ui.btn_calculate_2.clicked.connect(self._controller.calculation_secound)
        self.ui.data_select.clicked.connect(self._controller.selectDataA)
        self.ui.reference_data_select.clicked.connect(self._controller.selectDataB)
        self.ui.gamma_analysis_window.clicked.connect(lambda: self.show_page(0))
        self.ui.kalibration_window.clicked.connect(lambda: self.show_page(1))
        self.ui.film_calibration_window.clicked.connect(lambda: self.show_page(2))
        # self.ui.btn_video.clicked.connect(self._controller.start_video_maker)
        
    
    def select_folder(self): # dosya seçme işlemini başlatır ve dosya yolunu geri gönderir.
       
        self.ui.progressBar.setValue(0)
        self.clearImages()   
        path_name = QFileDialog.getExistingDirectory(self,"Data Folder")
        self.ui.btn_background.setEnabled(True)
        return path_name

    def select_file(self):

        file_filter = (
        "NumPy Files (*.npy *.npz);;"
        "TIFF Files (*.tiff *.tif);;"
        "DICOM Files (*.dcm);;"
        "MCC Files (*.mcc);;"
        "All Files (*)"
        )
        path_name, _ = QFileDialog.getOpenFileName(self, "Select Data File", "", file_filter)
        file_name = path_name.split('/')[-1]
        return path_name, file_name
    def setfileAname(self, n):
        self.ui.DataAname.setText(n)
    
    def setfileBname(self, n):
        self.ui.DataBname.setText(n)

    def clearImages(self):
        self.ui.image.clear()
        self.ui.image_3.clear()
        self.ui.image_4.clear()
        self.ui.image_5.clear()
    
    def add_list(self, list): # verilen lsiteyi arayüzde litview de görüntüler.
        list_items = [os.path.basename(file) for file in list]
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(list_items)
        self.ui.listWidget.setCurrentRow(0)
    
    def update_prog(self, val): # verilen veri ile progress barı günceller.
        self.ui.progressBar.setValue(val)
    
    def set_list_index(self, idx): #istenen indekse gitmeyi ve listedeki itemler arasında gezinmeyi sağlar.
        self.ui.listWidget.setCurrentRow(idx)

    def set_max_info(self, max, max_point):
        self.ui.textEdit.setText(str(max))
        self.ui.textEdit_2.setText(str(max_point[1]))
        self.ui.textEdit_3.setText(str(max_point[0]))

    def show_image1(self, f):
        self.ui.image.setPixmap(f)

    def show_image2(self, f):
        self.ui.image_3.setPixmap(f)
    
    def show_image3(self, f):
        self.ui.image_4.setPixmap(f)
    
    def show_image4(self, f):
        self.ui.image_5.setPixmap(f)
    
    def background_done(self,f):
        self.show_image4(f)
        self.ui.btn_open_file.setEnabled(True)
        self.ui.btn_background.setEnabled(True)
        self.ui.btn_calculate.setEnabled(True)
        self.ui.btn_calculate_2.setEnabled(True)
    
    def show_page(self, page):
        self.page_names = {
        0: "Gama",
        1: "Veri İşlemleri",
        2: "Film Kalibrasyon",
        3: "Help"}
        self.ui.content.setCurrentIndex(page)
        self.ui.header_label.setText(self.page_names.get(page, "Unknow"))