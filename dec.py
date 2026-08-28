import sys,os,json,base64,hashlib,glob
def R(f):
 try:
  from PIL import Image;from pyzbar.pyzbar import decode
  x=decode(Image.open(f))
  if x:return x[0].data
 except Exception:pass
 try:
  import cv2
  _,vs,_,_=cv2.QRCodeDetector().detectAndDecodeMulti(cv2.imread(f))
  for v in vs or []:
   if v:return v
 except Exception:pass
D=sys.argv[1];O=sys.argv[2] if len(sys.argv)>2 else "."
H=None;C={}
for f in sorted(glob.glob(D+"/*")):
 s=R(f)
 if not s:continue
 j=json.loads(s)
 if j.get("h")==1:H=j
 else:C[j["i"]]=base64.b64decode(j["d"])
if not H:raise SystemExit("no header")
m=sorted(set(range(H["n"]))-set(C))
if m:raise SystemExit(f"missing {len(m)} chunks {m[:20]}")
b=b"".join(C[i] for i in range(H["n"]))
g=hashlib.sha256(b).hexdigest()
if g!=H["sha256"] or len(b)!=H["size"]:raise SystemExit(f"mismatch {g} {len(b)}")
os.makedirs(O,exist_ok=True);open(O+"/"+H["name"],"wb").write(b)
print(f"OK {O}/{H['name']} {len(b)}B {g}")
