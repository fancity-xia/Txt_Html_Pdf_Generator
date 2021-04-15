#!/root/Software/miniconda3/bin/python3 -w
#-*- coding:utf8 -*-

__author__= 'xiazhanfeng' 

import os
import re
import sys
from collections import defaultdict
import argparse
import configparser
#sys.path.append("/root/16s/Modules")
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from htmlstaticpdf import Myhtml, Index
import pdfkit
import subprocess

__author__ = "xiazhanfeng"
__version__ = '1.0'
__date__ = '20 May 2020 '



def html_pipeline(configfile, out, limit=""):
	'''
	按照index分别将可读configfile转换成html格式
	params:
	configfile [File]:
	out [str]: suffix .html
	limit [int]: table 可显示的行数(针对table行数太多)
	'''
	configs = Myhtml.read_config(configfile)
	config_keylist = list(configs.keys())
	myindex = Index(configs['main']['title'], limit)
	for i in range(1,len(config_keylist)-1):
		myindex.htmlize(dict(configs[str(i)]))
	myindex.myhtml.html_outprint(out)


def html2pdf(html, pdf, software, cover):
	'''
	html转换为pdf
	html [File]: html file realpath
	pdf [str]: transform html to pdf; pdf name
	software [software]: wkhtmltopdf path
	cover [File]: report covers(cover.html realpath)
	'''
	#wkhtmltopdf 0.12.6 add option --enable-local-file-access
	options = {'page-size': 'A4', 'margin-top': '0.75in', 'margin-right': '0.75in', 'margin-bottom': '0.75in', 'margin-left': '0.75in', 'encoding': 'UTF-8', 'outline': None, '--enable-local-file-access':'--enable-local-file-access'}
	#options = {'page-size': 'A4', 'margin-top': '0.75in', 'margin-right': '0.75in', 'margin-bottom': '0.75in', 'margin-left': '0.75in', 'encoding': 'UTF-8', 'outline': None, '--quiet':True}
	bindir = os.path.dirname(__file__)
	#添加wkhtmltopdf依赖的静态文件环境
	#os.environ['LD_LIBRARY_PATH'] = "/root/Software/miniconda3/lib"
	fontdir = os.environ['HOME'] + "/.fonts"
	print(fontdir)
	if not os.path.lexists(fontdir + "/wqy-microhei.ttc"):
		if not os.path.isdir(fontdir):
			os.makedirs(fontdir)
		string = "cp {}/wqy-microhei.ttc {}/wqy-microhei.ttc".format(bindir, fontdir)
		string = string.encode('utf8')
		log = subprocess.Popen(string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdo, stde = log.communicate()
		if stde.decode('utf8'):
			print(stde)
	config  = pdfkit.configuration(wkhtmltopdf=software)
	try:
		pdfkit.from_file(html, pdf, cover=cover, options=options, configuration=config, toc={'toc-header-text':'Category'}, cover_first=True)
	except Exception as e:
		print(e)

