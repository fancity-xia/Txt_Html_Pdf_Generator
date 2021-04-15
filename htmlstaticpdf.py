#!/usr/bin/python -w
#-*- coding:utf8 -*-

__author__= 'xiazhanfeng' 

import os
import re
import sys
from collections import defaultdict
import argparse
import logging
import configparser, traceback
from pyh import *
from PIL import Image
import traceback

__author__ = "xiazhanfeng"
__version__ = '$Revision: 1 $'
__date__ = '$Fri, 15 May 2020 $'

'''
使用pyh生成根据文本内容生成html
20200914优化 表格过长导致超出A4边界
'''

class Myhtml():
	'''根据可读的文本格式(图片表格等为路径显示)格式创建浏览器的html格式数据'''
	
	def __init__(self, title, limit = ""):
		#self.out = out
		self.html_title(title)
		self.limit = limit 
	
	
	def html_outprint(self, out):
		self.page.printOut(out)


	def html_png(self, pngpath, title, pos="center"):
		'''
		params:
		pngpath: png picture realpath
		title: png introduction(down below)
		'''
		pngdiv = self.page <<div(style = "text-align: %s" % pos)
		width_num, height_num = self.suit_a4(pngpath)
		#pngdiv << p(title, style = "text-align: %s" % pos)
		pngdiv << img(src = pngpath, width=width_num, height=height_num)
		pngdiv << p(title, style = "text-align: %s" % pos)


	@staticmethod
	def suit_a4(pngpath, axis = 'width'):
		'''
		读取图片, 适配A4大小,也可通过PIL去生成缩略图,此处为通过html设置
		params:
		pngpath: png picture realpath
		axis: zoom in or out according to width or height(default width)
		'''
		a4w, a4h = 1000, 1800
		image = Image.open(pngpath)
		w, h = image.size
		#print(image.size)
		if axis == "width":
			return a4w, round(h/(w/(a4w*0.85)),2)
		elif axis == "height":
			return round(w/(h/(a4h*0.85)),2), a4h
		


	def html_table(self, tablepath, title, limit = ""):
		'''
		params:
		tablepath: table realpath
		title: table introduction(upper)
		'''
		print(tablepath)
		table_hash = self.read_table(tablepath, limit)
		#属性
		self.page << br()
		tablediv = self.page <<div()
		#加表标题; table suit for sheet
		tablediv << p(title, style = "text-align: left")
		mytable = tablediv << table(border="1", cellpadding ="3", cellspacing = "0" ,style="table-layout:fixed;word-break:break-all")
		#表头颜色
		tr1 = mytable <<tr(bgcolor = "#48a6fb", align="all")
		#列名
		header_generator = ("th(\"%s\")" % str(ele) for ele in table_hash['1'])
		header_string = ""
		for ele in header_generator:
			if header_string:
				header_string = header_string + " + " + ele
			else:
				header_string = ele
		tr1<<eval(header_string)
		#填充表格
		for i in range(2,len(table_hash.keys()) + 1):
			tr2 = mytable <<tr()
			for j in range(len(table_hash[str(i)])):
				tr2<<td(str(table_hash[str(i)][j]))
		#加表标题
		#tablediv << p(title, style = "text-align: left")


	
	def html_slide(self, pnglist):
		print("Not Achieve slide png")
		pass
	

	def html_div(self, desc, level=2, pos="left"):
		'''标题文字, 几级标题, 标题位置'''
		try:
			if not desc:
				return ""
			if level:
				if int(level)<4:
					voidline = (4-level)*"br() +"
					voidline = re.sub(r'\+$', "", voidline)
					self.page << eval(voidline)
				flag = "h" + str(level)
				mydiv = self.page <<div(style="text-align:" + pos)<< eval(flag)(desc)
		except:
			print(level)
			traceback.print_exc()


	def html_title(self, title):
		'''header内部标签,网页打开html可看到,pdf则无法查看'''
		self.page = PyH(title)
		#self.page.addCSS("src/sheets-of-paper.css")
		

	def html_divpara(self, desc, pos="left", font_size=16, color='black', bold=False):
		'''
		正文描述, 正文位置, 是否加粗
		params:
		desc: paragraph text
		pos: left or right
		bold: True or False
		'''
		#desc = eval(desc)
		#print(r''+desc)
		if not desc:
			return ""
		descs = re.split('\\\\n', desc)
		#20210414 special conclusion
		desc_string = '+'.join(f"p(\"{i}\", style = \"text-align:{pos};font-size:{font_size}px;color:{color}\")" for i in descs)
		dpdiv = self.page <<div(style="text-align:" + pos)
		if bold:
			dpdiv << b() + eval(desc_string) 
		else:
			dpdiv << eval(desc_string)


	@staticmethod
	def read_table(tablename, limit = ""):
		'''默认第一行为表头'''
		table_hash = defaultdict(list)
		te = open(tablename, 'r')
		index = 0
		for teline in te:
			index += 1
			if limit:
				if index > limit:
					return table_hash
			teline = teline.strip()
			telines = re.split('\s\s+|\t', teline)
			table_hash[str(index)] = telines
		return table_hash

	
	@staticmethod
	def read_config(configfile):
		'''
		配置必须为configparser的格式
		configfile: ref ro configparser
		'''
		config = configparser.ConfigParser()
		config.read(configfile, encoding='utf8')
		return config


class Index():

	'''解析config里面的每种type[png, text, table, main等类型]'''
	def __init__(self, title, limit=""):
		self.myhtml = Myhtml(title, limit)
		#self.htmlize()
		

	def htmlize(self, infodict):
		if infodict['type'] == 'png':
			self.pnglize(infodict)
		elif infodict['type'] == 'table':
			self.tablelize(infodict)
		elif infodict['type'] == 'paragraph':
			self.paralize(infodict)
		elif infodict['type'] == 'slide':
			self.slidelize(infodict)


	def baseload(self, infodict):
		#标题
		#项目概况<<2 2表示标题level, 默认为2
		try:
			title ,level = re.split('<<', infodict['subtitle'])
		except:
			traceback.print_exc()
			mysplit = re.split('<<', infodict['subtitle'])
			if len(mysplit) == 1:
				title = mysplit[0]
			elif len(mysplit) > 2:
				print(infodict['subtitle'] + " split elements much than expected")
				sys.exit()
		if not level:
			level = 2
		basediv = self.myhtml.html_div(title, int(level))
		#兼容旧版未进行替换
		if infodict.get('prolog'):
			self.myhtml.html_div(infodict['prolog'], 3)
		#需要进行格式化topic
		if infodict.get('ftopic'):
			self.myhtml.html_divpara(infodict['ftopic'])
		#普通topic
		if infodict.get('topic'):
			self.myhtml.html_divpara(infodict['topic'])
		#self.myhtml.html_divpara(infodict['caption'])
		return basediv


	def mainlize(self, infodict):
		'''目前只有title'''
		self.myhtml.html_title(infodict['title'])
		
	
	def slidelize(self, infodict):
		self.baseload(infodict)
		self.myhtml.html_slide(infodict['pnglist'])
		self.myhtml.html_divpara(infodict['conclusion'])


	def pnglize(self, infodict):
		#标题
		self.baseload(infodict)
		self.myhtml.html_png(infodict['pngpath'], infodict['caption'])
		self.myhtml.html_divpara(infodict['conclusion'], 'left', '10', 'grey')
		#self.myhtml.html_png(infodict['pngpath'], infodict['caption'])


	def tablelize(self, infodict):
		self.baseload(infodict)
		if os.path.lexists(infodict['tablepath']) and os.path.getsize(infodict['tablepath']):
			self.myhtml.html_table(infodict['tablepath'], infodict.get('caption', ""))
		infodict['conclusion'] = infodict.get('conclusion', "")
		self.myhtml.html_divpara(infodict['conclusion'], 'left', '10', 'grey')
		#self.myhtml.html_table(infodict['tablepath'], infodict['caption'])
	

	def paralize(self, infodict):
		tablediv = self.baseload(infodict)
		self.myhtml.html_divpara(infodict.get('conclusion', ""), 'left')


if __name__  == '__main__':
	parser = argparse.ArgumentParser(description='Reading config and producing my html format module by pyh')
	parser.add_argument('--config','-c', required=True, help='config file for html')
	parser.add_argument('--out','-o', required=True, help='out html filename')
	parser.add_argument('--limit','-l', required=False, help='limit table row number', default="")
	args = parser.parse_args()
	config = args.config
	out = args.out
	limit = args.limit
