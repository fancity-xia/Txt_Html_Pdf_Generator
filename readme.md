## 文本内容PDF， Html 生成器（BGI）

***Version 1.0***

***Author fancity.xia***



#### 需求：

根据Config TxT文档生成HTML以及PDF文件



#### 流程说明

###### htmlstaticpdf.py 

提供Txt转换html方法函数



###### pyh.py

提供python抽象化html函数



###### exchange_html.py

提供Txt->html(html_pipeline)和html->pdf(html2pdf)接口函数



```
import sys
sys.path.append("path")
from exchange_html import html_pipeline, html2pdf
html_pipeline(configs.outdir + "/report.config", configs.outdir + "/report.html")
html2pdf(configs.outdir + "/report.html", configs.outdir + "/report.pdf", wkhtmltopdf, cover)
```



#### 输入文件详细说明

###### Config Txt格式

`格式参考python Configparser格式`

`每一个标题即为一个section, 每个section有subtitle, topic, caption, type, conclusion`

`topic对应有ftopic，可以填写变量使用str的format进行填充变量`

`type对应有pngpath和tablepath`

`subtitle 有 "<<2"表示html的2级标题, 所有字段内不可使用单个%,对于单个存在的，需用%%替换单个%`



###### software

wkhtmltopdf  version >= 0.12.3



###### cover

html生成pdf封面