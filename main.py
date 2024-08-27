from window_interaction import interactions
from process import Process
from PyQt5.QtWidgets import QApplication
import sys

class Main():

    def __init__(self) -> None: # kullanacağımız sınıfları içeri alıyoruz.
        self._view = interactions(self)
        self._process = Process(self)
        self._view.show() # bu sınıfla oluşturulan arayüzü görüntüleme için kullanılıyor.

    def select_data_folder(self): # _view objesi ile bu fonksiyona arayüzdeki dosya seç butonu bağlı, bu fonksiyon arayüzden gelen dosya yolunu process objesinde dololatır.
        self._process.Path = ''
        path_name = self._view.select_folder()
        self._process.set_path(path_name) # process objesine dosya yolunu gönder
        if path_name != '':
            self._process.find_frames()
            if self._process.Frames:
                self._view.add_list(self._process.Frames)
            else:
                print("folder path is empty!")
        else:
            print("folder path is empty!")
    
    def background_calculation(self):
        self._process.start_background_thread()

    def calculation_first(self):
        self._view.clearImages()
        self._process.start_calc_thread()
    
    def calculation_secound(self):
        self._view.clearImages()
        self._process.start_calc_thread2()
    
    def update_progress(self, value, idx): #iş parçacıklarından gelen ilerleme verisi ile progress barı view objesi kullanarak güncelle komutu verir.
        self._view.update_prog(value)
        self._view.set_list_index(idx)
    
    def send_to_show_background(self, f1, f2): #iş parçacıklarından gelen veri ile view objesini kullanarak image labelini güncelle komutu  verir ve sonucu görselleştirir.
        self._view.show_image1(self._process.convert_to_pixmap(f1))
        self._view.show_image4(self._process.convert_to_pixmap(f2))
    
    def send_to_show(self, f1, f2, f3, f4): #iş parçacıklarından gelen veri ile view objesini kullanarak image labelini güncelle komutu  verir ve sonucu görselleştirir.
        self._view.show_image1(self._process.convert_to_pixmap(f1))
        self._view.show_image2(self._process.convert_to_pixmap(f2))
        self._view.show_image3(self._process.convert_to_pixmap(f3))
        max, idx = self._process.find_max_val(f4)
        _f4 = self._process.add_max_value_text_and_point(self._process.transform32to8bitimage(f4), max, idx)
        self._view.show_image4(_f4)
        self._view.set_max_info(max,idx)
    
    def send_to_show2(self, f1, f2, f3, f4): #iş parçacıklarından gelen veri ile view objesini kullanarak image labelini güncelle komutu  verir ve sonucu görselleştirir.
        self._view.show_image1(self._process.convert_to_pixmap(f1))
        self._view.show_image3(self._process.convert_to_pixmap(f3))
        max, idx = self._process.find_max_val(f2)
        _f2 = self._process.add_max_value_text_and_point(self._process.transform32to8bitimage(f2), max, idx)
        self._view.show_image2(_f2)
        self._view.set_max_info(max,idx)    
        self._view.show_image4(self._process.convert_to_pixmap(self._process.transform32to8bitimage(f4)))
    
    def end_of_backg(self, f): #iş parçacıklarından gelen veri ile view objesini kullanarak image labelini güncelle komutu  verir ve sonucu görselleştirir.
        self._view.background_done(self._process.convert_to_pixmap(f))

    def selectDataA(self):
        path, f_name = self._view.select_file()
        self._view.setfileAname(f_name)

    def selectDataB(self):
        path, f_name = self._view.select_file()
        self._view.setfileBname(f_name)

app = QApplication(sys.argv)
app.setStyle('Fusion')
main = Main()

sys.exit(app.exec_())