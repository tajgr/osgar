#!/usr/bin/python
"""
  Artefacts detection
"""
from datetime import timedelta
import sys
import time

try:
    import cv2
except ImportError:
    print('\nERROR: Please install OpenCV\n    pip install opencv-python\n')

try:
    import numpy as np
except ImportError:
    print('\nERROR: Please install numpy\n    pip install numpy\n')

from osgar.logger import LogReader, lookup_stream_id
from osgar.lib.serialize import deserialize
#from matplotlib import pyplot as plt

KERNEL = np.ones((5, 5), np.uint8)
#yi, ye, xi, xe = 350, 550, 200, 1080


def showImg( img ):
    cv2.namedWindow('image',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 600,600)
    cv2.imshow( 'image', img )
    cv2.waitKey(0)
    #time.sleep(0.1)
    #cv2.destroyAllWindows()
    
    
def red_firefighter(img, ind = 0):
    m, n, __ = img.shape
    b,g,r = cv2.split(img)
    b = b.astype(float)
    g = g.astype(float)
    r = r.astype(float)
    mat = b + g + r
    mat[mat == 0] = 1.0  # avoid division by 0
    r[r < 120] = 0        # ignore 'dark red'
    reddish = r/mat*255  # 'normalize' red, i.e. red compared to other color planes
    reddish = reddish.astype(np.uint8)
    #plt.hist( reddish.ravel(), 256,[0,256])
    #plt.show()
    #plt.savefig("im/hist_%s" % str(ind), dpi=100)
    
    #cv2.imwrite( "im/gray_%04d.png" % ind, reddish )
    __, binaryImg = cv2.threshold(reddish, 120, 255, cv2.THRESH_BINARY)
    
    binaryImg = cv2.morphologyEx(binaryImg, cv2.MORPH_CLOSE, KERNEL)
    binaryImg = cv2.morphologyEx(binaryImg, cv2.MORPH_OPEN, KERNEL)
    
    __, contours, __ = cv2.findContours( binaryImg, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
    contours2 = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100 and area < m*n/16:
            contours2.append(cnt)
    
    b_rect = []
    for cnt in contours2:
        x,y,w,h = cv2.boundingRect(cnt)
        b_rect.append([x, y, w, h])
    
    ret = []
    if len(b_rect) == 1:
        x, y, w, h = b_rect[0]
        if ( w/h > 1/6 ) and ( w/h < 1/2 ): # only red firefighter in the standing position
            ret = b_rect
            
    elif len(b_rect) == 2: #checking size and position
        x1, y1, w1, h1 = b_rect[0]
        x2, y2, w2, h2 = b_rect[1]
        if abs(w1*h1 - w2*h2) < max( w1*h1, w2*h2) *0.5:
            if abs(w1-w2) < max( w1, w2) *0.2:
                if abs(x1 - x2) < max( w1, w2) *0.2:
                    if abs(y1 - y2) < max( h1, h2) *3:
                        ret.append([ min(x1, x2), min(y1, y2), abs(x1-x2) + min(w1, w2), abs(y1 -y2) + min(h1, h2) ])
    
    elif len(b_rect) >2:
        pass #maybe next time
        
    return ret
    


def camera_processing(logfile):
    only_stream = lookup_stream_id(logfile, 'rosmsg_image.image') #or "camera.raw"
    with LogReader(logfile) as log:
        for timestamp, stream_id, data in log.read_gen(only_stream):
            #print(timestamp)
            buf = deserialize(data)
            img = cv2.imdecode(np.fromstring(buf, dtype=np.uint8), 1)
            #print(img.shape)
            artefacts = red_firefighter(img, ind = timestamp)
            if len(artefacts) > 0:
                for x,y,w,h in artefacts:
                    cv2.rectangle(img, (x,y),(x+w, y+h), (0, 0, 255),3)
            
                print(timestamp, artefacts)
                showImg( img )
                #cv2.imwrite("im/im_%s.png" % str(timestamp), img)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit()
    
    camera_processing(sys.argv[1])
