from .context import shenzhen_solitaire
from shenzhen_solitaire.cv import adjustment
from shenzhen_solitaire.cv import card_finder
import cv2

A = cv2.imread("Solitaire.png")

adj = adjustment.adjust_field(A)
X = card_finder.get_field_squares(A, adj)
for h in range(20):
    p = {None: 0}
    for x in X[h]:
        for x2 in ((x1[0], x1[1], x1[2]) for x1 in x):
            if x2 in p:
                p[x2] += 1
            else:
                p[x2] = 1
    B = sorted(p.items(), key=lambda x: x[1])
    print(*B, sep='\n')

    T = X[h].copy()
    cv2.imshow("Window", T)
    while cv2.waitKey(0) != 27:
        pass
    cv2.destroyWindow("Window")
assert 0

for ix, vx in enumerate(T):
    for iy, vy in enumerate(vx):
        if (vy[0] > 100) and (vy[1] > 100) and (vy[2] > 100):
            T[ix, iy] = [255, 255, 255]
        else:
            T[ix, iy] = [0, 0, 0]

cv2.imshow("Window", T)
cv2.waitKey(0)
cv2.destroyWindow("Window")


# for j in X:
#    cv2.imshow("Window", j)
#    cv2.waitKey(0)
