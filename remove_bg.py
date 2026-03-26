"""
Schwarzen Hintergrund entfernen und als w_kopf_1.png speichern.
Aufruf: python remove_bg.py <pfad_zum_bild>
Beispiel: python remove_bg.py "C:/Users/dein_name/Desktop/kopf_roh.png"
"""
import sys
from PIL import Image
import numpy as np

def remove_black_bg(input_path, output_path, threshold=40):
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)

    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    # Pixel die sehr dunkel sind -> transparent
    black_mask = (r < threshold) & (g < threshold) & (b < threshold)
    data[black_mask, 3] = 0

    result = Image.fromarray(data)
    result.save(output_path)
    print(f"Gespeichert: {output_path}")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "kopf_roh.png"
    dst = "HackatonHTL/app/static/char/w_kopf_1.png"
    remove_black_bg(src, dst)
