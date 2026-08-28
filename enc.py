import sys,os,shutil,json,base64,hashlib,qrcode
S=sys.argv[1];O=sys.argv[2] if len(sys.argv)>2 else os.path.basename(S)+"-qr"
CS=2100
r=open(S,"rb").read();h=hashlib.sha256(r).hexdigest();n=-(-len(r)//CS)
if os.path.isdir(O):shutil.rmtree(O)
os.makedirs(O)
def W(p,i):
 q=qrcode.QRCode(version=40,error_correction=1,box_size=4,border=2);q.add_data(p);q.make(fit=False)
 q.make_image().save(f"{O}/{i:05}.png")
W(json.dumps({"h":1,"name":os.path.basename(S),"size":len(r),"sha256":h,"n":n},separators=(",",":")),0)
for i in range(n):W(json.dumps({"i":i,"d":base64.b64encode(r[i*CS:i*CS+CS]).decode()},separators=(",",":")),i+1)
print(f"{len(r)}B {h} -> {O}/ {n+1} PNGs")
