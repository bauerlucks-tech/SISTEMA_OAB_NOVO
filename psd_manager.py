
from psd_tools import PSDImage
from PIL import Image, ImageDraw

def ler_campos_psd(arq):
    psd=PSDImage.open(arq)
    out=[]
    for l in psd.descendants():
        if l.is_visible():
            x1,y1,x2,y2=l.bbox
            out.append({"nome":l.name,"tipo":l.kind,"pos":[x1,y1,x2,y2]})
    return out

def gerar_png(psd_path, dados, foto, area, saida):
    psd=PSDImage.open(psd_path)
    img=psd.composite().convert("RGB")
    d=ImageDraw.Draw(img)

    for k,v in dados.items():
        d.text((20,20), v, fill=(0,0,0))

    if foto:
        f=Image.open(foto)
        f=f.resize((area[2]-area[0],area[3]-area[1]))
        img.paste(f,(area[0],area[1]))

    img.save(saida)
