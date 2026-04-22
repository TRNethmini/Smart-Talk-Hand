import glob
import cv2
import numpy as np
import base64
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('.')
from services import multi_inference
from landmark_extractor import LandmarkExtractor

ext = LandmarkExtractor()
multi_inference.load_all_models()
ctx = multi_inference.models_registry['ssl_alphabet']

def get_seq(flip=False, rotate=None):
    frames = sorted(glob.glob('c:/Redmi/api/debug_frames/seq_ssl_alphabet_1774867813/*.jpg'))
    vecs = []
    for f in frames:
        img = cv2.imread(f)
        if flip:
            img = cv2.flip(img, 1) # horizontally
        if rotate is not None:
            img = cv2.rotate(img, rotate)
            
        _, buf = cv2.imencode('.jpg', img)
        encoded = base64.b64encode(buf).decode('utf-8')
        
        lms = ext.extract(encoded)
        vec = multi_inference.landmarks_to_frame_vec(lms or [], 1)
        vecs.append(vec)
        
    seq = multi_inference.frames_to_sequence(vecs, 30)
    lbl, topk = multi_inference.predict_topk_from_sequences('ssl_alphabet', seq, 5)
    return lbl, topk

with open('results.txt', 'w', encoding='utf-8') as fh:
    fh.write("Original: " + str(get_seq(flip=False)) + "\n")
    fh.write("Flipped: " + str(get_seq(flip=True)) + "\n")
    fh.write("Rotated 90 CW: " + str(get_seq(rotate=cv2.ROTATE_90_CLOCKWISE)) + "\n")
    fh.write("Rotated 90 CCW: " + str(get_seq(rotate=cv2.ROTATE_90_COUNTERCLOCKWISE)) + "\n")
    fh.write("Rotated 90 CCW + Flipped: " + str(get_seq(flip=True, rotate=cv2.ROTATE_90_COUNTERCLOCKWISE)) + "\n")
