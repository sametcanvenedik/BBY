"""
Bu dosya controllerden gelen komutlar ile veri üzerinde işlem yaparken veriyi işleyen ve tutan kısımdır.
"""
#dosya işlemlei için kütüphaneler
import glob 
import os
import time

#görüntü işlemleri için kütüphaneler.
import numpy as np
import cv2
from skimage.morphology import disk, closing, opening
from PIL import Image
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont

# iş parçaları arasında veri aktarımı için kütüphane.
from PyQt5.QtCore import QThread, pyqtSignal

# from vimba import * # kamera eklendiğinde yorum satırı olmaktan çıkarılıcak
class start_background_thread(QThread): 
    result_ready = pyqtSignal(np.ndarray)
    progress = pyqtSignal(int, int)
    on_progres = pyqtSignal(np.ndarray, np.ndarray)

    frame_list = []

    def run(self):
        f_count = len(self.frame_list)
        f_shape = np.load(self.frame_list[0])
        sof = np.zeros([f_shape.shape[0], f_shape.shape[1]], dtype=np.float32)
        i = 1
        for f in self.frame_list:
            frame_d = np.load(f)
            frame = frame_d[:,:,0]
            background_norm = (sof / i).astype(np.uint8)  
            self.on_progres.emit(frame, background_norm )
            frame_32 = frame.astype(np.uint32)
            sof += frame_32
            self.progress.emit((i) * 100 // f_count, i)
            i += 1

        background_norm = (sof / f_count).astype(np.uint8)
        self.result_ready.emit(background_norm)


class WorkerThread(QThread):
    result_ready = pyqtSignal(np.ndarray)
    progress = pyqtSignal(int, int)
    on_progres = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray)

    frame_list = []

    def __init__(self, bckgrnd):
        super(WorkerThread, self).__init__()
        self.back_g = bckgrnd

    def run(self):
        f_count = len(self.frame_list)
        f_shape = np.load(self.frame_list[0])
        sof = np.zeros([f_shape.shape[0], f_shape.shape[1]], dtype=np.uint32)

        i = 1
        for f in self.frame_list:
            frame = np.load(f)
            _frame = frame[:, :, 0]
            
            # Frame'den background çıkarma ve negatif değerleri sıfıra yuvarlama
            sub_f = np.subtract(_frame, self.back_g, dtype=np.int32)
            sub_f = np.maximum(sub_f, 0).astype(np.uint8)
            
            # Median blur
            median_img = cv2.medianBlur(sub_f, 5)
            
            # Morphological closing
            closed_img = closing(median_img, disk(5))
            opened_img = opening(closed_img, disk(5))
            # Gaussian blur
            gauss_img = cv2.GaussianBlur(opened_img, (3, 3), cv2.BORDER_DEFAULT)
            
            # Sonuçları biriktirme
            sof += gauss_img
            
            # İlerleme sinyallerini yayma
            self.on_progres.emit(frame[:, :, 0], gauss_img, sub_f, sof)
            self.progress.emit((i) * 100 // f_count, i)
            i += 1

        self.result_ready.emit(sof)

class WorkerThread2(QThread):
    result_ready = pyqtSignal(np.ndarray)
    progress = pyqtSignal(int, int)
    on_progres = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray)

    frame_list = []

    def __init__(self, bckgrnd):
        super(WorkerThread2, self).__init__()
        self.back_g = bckgrnd

    def run(self):
        f_count = len(self.frame_list)
        f_shape = np.load(self.frame_list[0])
        sof = np.zeros([f_shape.shape[0], f_shape.shape[1]], dtype=np.uint32)
        empty = sof
        i = 1
        for f in self.frame_list:
            frame = np.load(f)
            _frame = frame[:, :, 0]
            
            # Frame'den background çıkarma ve negatif değerleri sıfıra yuvarlama
            sub_f = np.subtract(_frame, self.back_g, dtype=np.int32)
            sub_f = np.maximum(sub_f, 0).astype(np.uint8)
            sof += sub_f

            self.on_progres.emit(frame[:, :, 0], empty, sub_f, sof)
            self.progress.emit((i) * 100 // f_count, i)
            i += 1

        # Median blur
        median_img = cv2.medianBlur(sof.astype(np.float32), 5)
        # Morphological closing
        closed_img = closing(median_img, disk(5))
        opened_img = opening(closed_img, disk(5))
        # Gaussian blur
        gauss_img = cv2.GaussianBlur(opened_img, (3, 3), cv2.BORDER_DEFAULT)
        
        self.on_progres.emit(frame[:, :, 0], gauss_img, sub_f, sof)
        self.result_ready.emit(gauss_img)



class Test(QThread):
    """
    QThread sınıfından türetilmiş bir alt sınıf.\n
    Sistem tarafondan oluşturulup, QThread'lere ait start metodu ile çalımaya başlar ve içindeki run metodunu çalıştırır.
    """

    #dışarı veri göndermek için sinyaller.
    result_ready = pyqtSignal(np.ndarray)
    progress = pyqtSignal(int, int)
    on_progres = pyqtSignal(np.ndarray)                                        
    
    def show_and_resize(self, image, window_name, scale_factor=10):
        # İmage'yi belirtilen ölçekte büyüt
        resized_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)

        # Pencereyi oluştur ve görüntüyü göster
        cv2.imshow(window_name, resized_image)
        cv2.waitKey(0)
    
    def save_npy(self, image, image_name):
        np.save(f"{image_name}.npy" , image)

    def load_npy(self, image_name):
        return np.load(f"{image_name}.npy")

    def run(self):

        background = np.zeros((25,25), dtype=np.uint8)
        background[11:16,11:16] = 255
        self.save_npy(background, "background")
        r_background = self.load_npy("background")
        self.show_and_resize(r_background, "background")

        background_2 = np.zeros((25,25), dtype=np.uint8)
        background_2[6:21,6:21] = 255
        self.save_npy(background_2, "background_2")
        r_background_2 = self.load_npy("background_2")
        self.show_and_resize(r_background_2, "background_2")

        list_back = [background, background_2]
        f_count = len(list_back)
        print(f_count)

        frame = np.full((25,25), 255, dtype=np.uint8)
        self.save_npy(frame, "frame")
        r_frame = self.load_npy("frame")
        self.show_and_resize(r_frame, "frame")

        sof = np.zeros([background.shape[0],background.shape[1]],dtype=np.uint32) # görüntü toplamı için boş bir görüntü oluşturur.

        for f in list_back:
            sof += f[:,:] # görüntüleri toplar
        
        background_norm = ((1/f_count)*sof[:,:]).astype(np.uint8)
        self.show_and_resize(background_norm, "background_norm")

        sub_f = np.subtract(frame[:,:], background_norm, dtype=np.int32) # işlenen görüntüden backgroun görüntüsünü çıkarı 16 bit görüntü oluşturup sonucu içine yükler.
        sub_f = (np.maximum(sub_f, 0)).astype(np.uint8)
        self.show_and_resize(sub_f, "sub_f")

class Video_Maker(QThread):
    
    progress = pyqtSignal(int, int)
    frame_list= [] # işlenmek üzere görüntü listesini tutar.
    
    
    def run(self):
        
        # Video dosyasının adı ve çözünürlüğü
        video_name = 'output_video.avi'
        width, height = 1936, 1216

        # VideoWriter'ı oluşturun
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        is_color = False
        video_writer = cv2.VideoWriter(video_name, fourcc, 5.0, (width, height), isColor=is_color)
        f_count = len(self.frame_list) 
        i = 1
        # Her bir frame'i video dosyasına ekleyin
        for f in self.frame_list:  
            # Eğer frame'lerin boyutları uyumlu değilse, çerçeveyi yeniden boyutlandırın
            r_frame = np.load(f) 
            frame = r_frame
            if frame.shape[:2] != (height, width):
                frame = cv2.resize(frame, (width, height))
            # Video dosyasına frame'i ekleyin
            video_writer.write(frame)
            self.progress.emit((i) * 100 // f_count, i)                     # ilerlemeyi arayüze gönderir
            i +=1

        # Video dosyasını kapatın
        video_writer.release()

        print(f"Video oluşturuldu: {video_name}")

class frame_io(): 
    """
    Dosya giriş çıkış işlemleri sınıfı.
    """

    def frame_save(self, frame, frame_name):
        np.save( self.folder_dir + frame_name, frame)

    def frame_read():
        pass

    def create_save_folder(self) -> str:
        date = time.strftime("%d-%m-%Y-%H-%M-%S")
        folder_dir = f'./Data/{date}'
        os.mkdir(folder_dir)
        return folder_dir + '/'

    def save_npy_as_tiff(self, npy_array: np.ndarray, path: str):
        
        date = time.strftime("%d-%m-%Y-%H-%M-%S")
        output_path = f"{path}/tiff"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        tiff_path = f"{output_path}/{date}.tiff"
        # NumPy dizisini TIFF formatında kaydetme
        image = Image.fromarray(npy_array)
        
        # TIFF formatında kaydetme
        dpi = 412
        image.save(tiff_path, compression=None, dpi=(dpi, dpi))
        print(f"Saved {output_path}")
        
        # Kaydedilen TIFF dosyasını yükleme ve kontrol etme
        loaded_image = Image.open(tiff_path)
        loaded_array = np.array(loaded_image)
        
        # Orijinal ve yüklenmiş verilerin karşılaştırılması
        if not np.array_equal(npy_array, loaded_array):
            raise ValueError(f"Data mismatch found in file: {tiff_path}")
        print(f"Verified {tiff_path} successfully.")


class Process():
    def __init__(self, controller):
        self.fileSaver = frame_io()
        self._controller = controller
        self.Path = ' '
        self.Frames = []
        self.b_norm = []
        self.sum_of_frames = []

    def video_maker(self):
        self.video_maker_thread = Video_Maker()
        self.video_maker_thread.frame_list = self.Frames
        self.video_maker_thread.progress.connect(self._controller.update_progress)
        self.video_maker_thread.start()

    def test(self):
        self.test_thread = Test()
        self.test_thread.start()

    def find_frames(self) -> list[str]:
        if self.Path != '':
            name_patter = '/*.npy'
            file_dir_pattern = self.Path + name_patter
            frame_list = glob.glob(file_dir_pattern)
            
            # Dosya adlarını sayısal olarak sıralama
            sorted_frames = sorted(frame_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
            
            self.set_files(sorted_frames)
            return sorted_frames

    def start_background_thread(self):
        self.thread = start_background_thread()
        self.thread.frame_list = self.Frames
        self.thread.progress.connect(self._controller.update_progress)
        self.thread.on_progres.connect(self._controller.send_to_show_background)
        self.thread.result_ready.connect(self.result_of_backgroun)
        self.thread.start()

    def start_calc_thread(self):
        self.thread = WorkerThread(self.b_norm)
        self.thread.frame_list = self.Frames
        self.thread.progress.connect(self._controller.update_progress)
        self.thread.on_progres.connect(self._controller.send_to_show)
        self.thread.result_ready.connect(self.resulf_of_frames)
        self.thread.start()
    
    def start_calc_thread2(self):
        self.thread = WorkerThread2(self.b_norm)
        self.thread.frame_list = self.Frames
        self.thread.progress.connect(self._controller.update_progress)
        self.thread.on_progres.connect(self._controller.send_to_show2)
        self.thread.result_ready.connect(self.resulf_of_frames)
        self.thread.start()

   

    def find_max_val(self, f):
        points = np.unravel_index(np.argmax(f), f.shape)
        value = str(np.max(f))
        return value, tuple(points)

    def result_of_backgroun(self, f: np.ndarray):
        self.set_bnorm(f)
        self._controller.end_of_backg(f)

    def resulf_of_frames(self, f: np.ndarray):
        self.set_frames(f)
        self.fileSaver.save_npy_as_tiff(f,self.Path)

    def result_of_colored_frames(self, f):
        scaled_frame = self.transform32to8bitimage(f)
        index, value = self.find_max_val(f)
        self._controller.send_to_show_pointed(scaled_frame, index)
        self._controller.end_of_backg()

    def see_points(self, f, points):
        scaled_frame = self.transform32to8bitimage(f)
        self._controller.send_to_show_pointed(scaled_frame, points)
        self._controller.end_of_backg()

    def transform32to8bitimage(self, f) -> np.ndarray:
        # Maksimum değeri bulun ve float32'e dönüştürün
        max_uint32 = np.max(f).astype(np.float32)
        
        # Bölme işleminde maksimum değerin sıfır olmadığından emin olun
        if max_uint32 == 0:
            max_uint32 = 1.0  # Sıfır bölme hatasını önlemek için 1'e ayarlayın
        
        # Array'i 0-255 aralığına ölçeklendirin ve uint8'e dönüştürün
        scaled_array = (f / max_uint32) * 255.0
        return scaled_array.astype(np.uint8)

    def add_max_value_text_and_point(self, image: np.ndarray, max_value: int, max_point: tuple) -> QImage:
        height, width = image.shape
        q_img = QImage(image.data, width, height, QImage.Format_Grayscale8)
        
        q_img = q_img.convertToFormat(QImage.Format_RGB32)
        
        painter = QPainter(q_img)
        red_color = QColor(255, 0, 0)  # Kırmızı renk
        painter.setPen(red_color)
        painter.setFont(QFont('Arial', 50))
        
        text = f"Max: {max_value}"
        painter.drawText(width - 400, height - 50, text)  # Sağ alt köşeye yaz
        
        painter.setBrush(red_color)
        painter.drawEllipse(max_point[1], max_point[0], 15, 15)  # Nokta boyutu 5x5, (x, y) koordinatları
        painter.end()
        
        pixmap = QPixmap.fromImage(q_img)
        return pixmap
    
    def convert_to_pixmap(self, frame) -> QPixmap:
        height, width = frame.shape[0:2]
        q_img = QImage(frame.data.tobytes(), width, height, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_img)
        return pixmap

    def convert_to_colored_pixmap(self, frame, index) -> QPixmap:
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        rgb_image = cv2.circle(rgb_image, tuple(index), 5, (255, 0, 0), -1)
        height, width, channel = rgb_image.shape
        bytesPerLine = width * channel
        q_img = QImage(rgb_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        return pixmap


    def set_path(self, path):
        self.Path = path

    def set_files(self, frames):
        self.Frames = frames

    def set_bnorm(self, f):
        self.b_norm = f

    def set_frames(self, f):
        self.sum_of_frames = f
