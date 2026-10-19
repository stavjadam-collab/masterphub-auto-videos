import cv2,sys,numpy as np
for f in sys.argv[1:]:
    im=cv2.imread(f); h,w=im.shape[:2]
    # scrollbar strip -> repeat column left of it
    im[:,943:]=im[:,940:941]
    # pdf extension bubble: find red-ish blob on the right edge
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    red=((hsv[...,0]<10)|(hsv[...,0]>170))&(hsv[...,1]>120)&(hsv[...,2]>120)
    red[:, :880]=False; red[:, 925:]=False
    ys,xs=np.where(red)
    if len(ys)>30:
        cy,cx=int(ys.mean()),int(xs.mean())
        m=np.zeros((h,w),np.uint8); cv2.circle(m,(cx,cy),25,255,-1)
        im=cv2.inpaint(im,m,5,cv2.INPAINT_TELEA)
        print(f,'pdf at',cx,cy)
    cv2.imwrite(f,im)
