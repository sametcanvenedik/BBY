import os
import numpy as np
from PIL import Image

def convert_npy_to_tiff(input_dir, output_dir):
    # Input ve output dizinlerini kontrol et
    if not os.path.exists(input_dir):
        raise ValueError(f"Input directory '{input_dir}' does not exist.")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Dizin içindeki tüm .npy dosyalarını al
    npy_files = [f for f in os.listdir(input_dir) if f.endswith('.npy')]
    
    for npy_file in npy_files:
        # .npy dosyasının tam yolunu oluştur
        npy_path = os.path.join(input_dir, npy_file)
        
        # NumPy dizisini yükle
        numpy_array = np.load(npy_path)
        
        # NumPy dizisini kontrol et
        print(f"Processing file: {npy_file}")
        print(f"Array shape: {numpy_array.shape}")
        print(f"Array dtype: {numpy_array.dtype}")

        # NumPy dizisinin 2 veya 3 boyutlu olduğunu ve dtype'inin uint8 olduğunu kontrol et
        if numpy_array.ndim == 3 and numpy_array.shape[2] == 1:
            numpy_array = numpy_array[:, :, 0]  # Üçüncü boyutu sıkıştır (kanal boyutunu kaldır)
        elif numpy_array.ndim != 2 or numpy_array.dtype != np.uint8:
            raise ValueError(f"Array must be 2D or 3D with one channel and of type uint8, but got shape {numpy_array.shape} and type {numpy_array.dtype}")
        
        # NumPy dizisini TIFF formatında kaydetme
        image = Image.fromarray(numpy_array)
        
        # Output dosya ismi
        tiff_filename = os.path.splitext(npy_file)[0] + '.tiff'
        tiff_path = os.path.join(output_dir, tiff_filename)
        
        # TIFF formatında kaydetme
        dpi = 412
        image.save(tiff_path, compression=None, dpi= (dpi,dpi))
        print(f"Saved {tiff_path}")
        
        # Kaydedilen TIFF dosyasını yükleme ve kontrol etme
        loaded_image = Image.open(tiff_path)
        loaded_array = np.array(loaded_image)
        
        # Orijinal ve yüklenmiş verilerin karşılaştırılması
        if not np.array_equal(numpy_array, loaded_array):
            raise ValueError(f"Data mismatch found in file: {tiff_filename}")
        print(f"Verified {tiff_path} successfully.")

# Kullanım
input_directory = 'AA'  # .npy dosyalarının bulunduğu dizin
output_directory = f'{input_directory}/tiff'  # TIFF dosyalarının kaydedileceği dizin

convert_npy_to_tiff(input_directory, output_directory)
