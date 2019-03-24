import os, sys, requests, io, json
from zipfile import ZipFile
from PIL import Image
import numpy as np, cv2

def upload(url, fpath):
	with open(fpath, 'rb') as f:
		files = {'file' : f}

		try:
			r = requests.post(url, files=files)
			# print(r.text)
			return r.text

		except Exception as e:
			print('Did not send file: {}\nException: {}'.format(fpath, e))

def downloadImg(url):
	r = requests.get(url)
	return Image.open(io.BytesIO(r.content))

def downloadJson(url):
	fname = 'tmp.json'
	r = requests.get(url)
	with open(fname, 'wb') as of:
		of.write(r.content)

	jsonDict = {}
	with open(fname) as inf:
		jsonDict = json.load(inf)
	
	return jsonDict

def downloadZip(url):
	fname = 'tmp.zip'
	r = requests.get(url)
	with open(fname, 'wb') as of:
		of.write(r.content)

	with ZipFile(fname, 'r') as zf:
		# Gets csv file
		flist = zf.namelist()
		print(flist)
		for f in flist:
			if f.endswith('csv'):
				csvFile = zf.open(f, 'r')
				csvList = []
				for line in csvFile:
					line = line.decode('utf-8')

					# lineList = [str, float, str, int, int, int, int]
					lineList = line.strip('\n').split(',')
					lineList[1] = float(lineList[1])
					lineList[3:] = [int(f) for f in lineList[3:]]
					csvList.append(lineList)
				csvFile.close()
				break

		# # Rips images out of zip file
		objDict = {}
		for i, lineList in enumerate(csvList):
			fname, score, label, cmin, rmin, cmax, rmax = lineList
			maskimg = np.array(Image.open(zf.open(fname)))
			maskimg[maskimg > 0] = 255
			objDict.update({
				i : {
					'score' : score,
					'label' : label,
					'bb' 	: [cmin, rmin, cmax, rmax],
					'mask'  : maskimg,
					'fname' : fname
				}
			})

		# Adds visualed image
		fname = [f for f in flist if f.startswith('vis')][0]
		vis = np.array(Image.open(zf.open(fname)))
		vis = cv2.cvtColor(vis, cv2.COLOR_RGB2BGR)
		objDict.update({'vis' : {'mask' : vis, 'fname' : fname}})

		return objDict

if __name__ == '__main__':
	url = sys.argv[1]
	fpath = sys.argv[2]
	
	retUrl = upload(url, fpath)
	print(retUrl)

	# img = downloadImg(retUrl)
	# with open('dl.png', 'wb') as fo:
	# 	img.save(fo)

	# jsonDict = downloadJson(retUrl)
	# with open('dl.json', 'w') as of:
	# 	json.dump(of, jsonDict, indent=2)

	outDir = 'download'
	if not os.path.exists(outDir):
		os.makedirs(outDir)
	objDict = downloadZip(retUrl)
	# print(objDict)
	for objNum, obj in objDict.items():
		# print(objNum, obj)
		mask = obj['mask']
		fname = obj['fname']
		fpath = os.path.join(outDir, fname)
		cv2.imwrite(fpath, mask)
	cv2.imwrite(os.path.join(outDir, 'vis.png'), objDict['vis']['mask'])
