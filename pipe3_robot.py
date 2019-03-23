import os, sys, requests, io, json
from zipfile import ZipFile
from PIL import Image

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
			# objDict.update({

			# })

		return csvList, objDict

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
	csvList, memberList = downloadZip(retUrl)
	print(csvList)
	count = 0
	for member in memberList:
		member.save(os.path.join(outDir, str(count) + '.png'))
		count += 1
