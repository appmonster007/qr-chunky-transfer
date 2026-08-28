import sys,os,shutil,json,base64,hashlib,qrcode
from qrcode.constants import ERROR_CORRECT_L as L
S=sys.argv[1];O=sys.argv[2] if len(sys.argv)>2 else os.path.basename(S)+"-qr"
CS=2100
r=open(S,"rb").read();h=hashlib.sha256(r).hexdigest();n=(len(r)+CS-1)//CS
if os.path.isdir(O):shutil.rmtree(O)
os.makedirs(O)
def W(p,i):
 q=qrcode.QRCode(version=40,error_correction=L,box_size=4,border=2);q.add_data(p);q.make(fit=False)
 q.make_image(fill_color="black",back_color="white").save(os.path.join(O,f"chunk_{i:05d}.png"))
W(json.dumps({"h":1,"name":os.path.basename(S),"size":len(r),"sha256":h,"n":n,"cs":CS},separators=(",",":")),0)
for i in range(n):W(json.dumps({"i":i,"n":n,"d":base64.b64encode(r[i*CS:(i+1)*CS]).decode()},separators=(",",":")),i+1)
print(f"{S} {len(r)}B sha256={h} -> {O}/ ({n+1} PNGs, chunk={CS})")
