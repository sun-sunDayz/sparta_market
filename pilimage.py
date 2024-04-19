from PIL import Image

img = Image.open("media/clo2.png")
img = img.convert("RGBA")
print(img.mode)
x,y = img.size
for i in range(x):
    for j in range(y):
        r,g,b,a = img.getpixel((i,j))
        if sum([r,b,g]) > 720:
            img.putpixel((i,j), (140,190,255,255))

img.save("media/clo_active.png")
# print(img.show())
# img.save("cloud.png")
