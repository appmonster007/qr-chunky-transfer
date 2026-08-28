import sys,os,json,base64,hashlib,glob
D=sys.argv[1];O=sys.argv[2] if len(sys.argv)>2 else "."
def R(p):
 try:
  from PIL import Image;from pyzbar.pyzbar import decode
  x=decode(Image.open(p))
  if x:return x[0].data.decode()
 except Exception:pass
 try:
  import cv2
  im=cv2.imread(p)
  if im is None:return None
  d=cv2.QRCodeDetector();v,_,_=d.detectAndDecode(im)
  if v:return v
  ok,vs,_,_=d.detectAndDecodeMulti(im)
  if ok and vs:
   for v in vs:
    if v:return v
 except Exception:pass
 return None
H=None;C={};F=sorted(sum([glob.glob(os.path.join(D,e)) for e in ("*.png","*.jpg","*.jpeg","*.PNG","*.JPG","*.JPEG")],[]))
if not F:raise SystemExit(f"no images in {D}")
for f in F:
 s=R(f)
 if not s:print(f"skip {f} (no QR)");continue
 try:j=json.loads(s)
 except Exception:print(f"skip {f} (bad json)");continue
 if j.get("h")==1:H=j
 elif "i" in j and "d" in j:C[j["i"]]=base64.b64decode(j["d"])
if not H:raise SystemExit("header (h=1) missing")
m=sorted(set(range(H["n"]))-set(C))
if m:raise SystemExit(f"missing chunks: {m[:10]}{'...' if len(m)>10 else ''} ({len(m)} total)")
b=b"".join(C[i] for i in range(H["n"]))
g=hashlib.sha256(b).hexdigest()
if g!=H["sha256"]:raise SystemExit(f"sha256 mismatch: got {g} expected {H['sha256']}")
if len(b)!=H["size"]:raise SystemExit(f"size mismatch: got {len(b)} expected {H['size']}")
os.makedirs(O,exist_ok=True);p=os.path.join(O,H["name"]);open(p,"wb").write(b)
print(f"OK {p} {len(b)}B sha256={g}")
