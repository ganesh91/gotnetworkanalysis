from lxml import etree
import re
from collections import defaultdict

def parseXML(filename):
	doc=etree.parse(filename)
	return(doc)

def listNamespaces(eTree,ns):
	wikiNs=dict([(wikiNSElement.text,wikiNSElement.attrib['key']) for wikiNSElement in eTree.getroot().getiterator(ns+"namespace")])
	return(wikiNs)

def listTemplates(eTree,ns,extractNamespace):
	templates=[]
	for tmpltElement in eTree.getroot().getiterator(ns+"page"):
		if tmpltElement.find(ns+"ns").text == extractNamespace:
			templates.append(tmpltElement.find(ns+"title").text.split(":")[1])
	return(templates)

def extractText(eTree,ns,extractNamespace,extractTemplate):
	text=[]
	for tmpltElement in eTree.getroot().getiterator(ns+"page"):
		if tmpltElement.find(ns+"ns").text == extractNamespace:
			text.append(tmpltElement.find(ns+"revision/"+ns+"text").text)
	text=[extractInfoBox(iBox,extractTemplate) for iBox in text]
	text=[txt for txt in text if txt is not None]
	return(text)

def extractInfoBox(text,tagger):
	pttn=re.sub(r'<.*?>','',text.replace("\n",""))#.replace("{{","#@").replace("}}","@#"))
	tagged=re.findall(r"{{"+tagger+".*?}}",pttn)
	for en,item in enumerate(tagged):
		tagged[en]=item#.replace("#@","").replace("@#","")
	if len(tagged) >=1:
		tagged=tagged[0]
	else:
		tagged=None
	return(tagged)

def parseInfoBox(corpus,output):
	# print(corpus)
	text=corpus.replace("Character| ","").replace("{","").replace("}","")
	brakets=re.findall(r'\[\[.*?\]\]',text)
	for braket in brakets:
		alias=braket.replace("[","").replace("]","").split("|")
		if len(alias) >1:
			alias=alias[1]
		else:
			alias=alias[0]
		text=text.replace(braket,","+alias)
	infoDict=defaultdict(str)
	for item in text.split("|"):
		split=[words.strip().strip(",") for words in item.split("=")]
		if len(split) > 1 :
			infoDict[split[0]]=re.sub(r'\(.*?\)',"",split[1])
	if infoDict['Title'] not in [""]:
		for item in infoDict.keys():
			if item in ['Actor','Religion','Titles','Season','Status','Family','Place','Allegiance','Culture','Appearences']:
				subItems=infoDict[item].split(",")
				for si in subItems:
					if si not in ["\"",""," "]:
						si=re.sub(r'\"',"",si)
						if item=="Family":
							relations=re.sub(r" - ",":",si).split(":")
							if len(relations) > 1:
								output.write("\",\"".join(["\""+infoDict['Title'],"Family",relations[0].strip()+"\""]))
								output.write("\n")
								# output.write("\",\"".join(["\""+infoDict['Title'],relations[1].strip(),relations[0].strip()+"\""]))
								# output.write("\n")
						else:
							output.write("\",\"".join(["\""+infoDict['Title'],item,si.strip()+"\""]))
							output.write("\n")
