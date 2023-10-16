# -*- coding: utf-8 -*-

import http.server
import os
import re
import socketserver
import sys
import threading
import tkinter as tk
import types
import webbrowser
from multiprocessing import Pool
from time import *
from tkinter import *
from tkinter import colorchooser, filedialog, messagebox, simpledialog

import bs4
import html5lib
import imgkit
import keyboard
import pdfkit
import requests
from PIL import Image 
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_by_name
from translate import Translator
#from xes.tool import *


global css_code_input, css, open_path
encoding_s = "utf-8"
recorded_text = ""
recorded_text_attr = ""
httpd = None
c = True
url = 'https://validator.w3.org/nu/?out=json'
headers = {
    'Content-Type': 'text/html; charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}
open_path = ""
# HTML基本操作

# HTML保存


def save_html_code(*args):
    global open_path
    code = code_input.get("1.0", END)

    if open_path == "":
        obj = filedialog.asksaveasfilename(defaultextension=".html", title="保存", filetype=[
                                           ("网页文件", "*.html"), ("文本文件", "*.txt")])
        open_path = obj
        # print(open_path)
    with open(open_path, "w", encoding=encoding_s)as f:
        f.write(code)
    root.title("HTML编辑器-" + open_path + "-" + encoding_s)
# HTML预览


def run_html(*args):
    global open_path
    code = code_input.get("1.0", END)
    if ".txt" in open_path:
        messagebox.showwarning("提示", "txt文件不支持预览！")
    if open_path == "":
        save_html_code()
    page_url = "file://" + open_path
    webbrowser.open(page_url)
# HTML另存为


def save_copy(*args):
    path = filedialog.asksaveasfilename(
        title="保存", filetype=[("网页文件", "*.html"), ("文本文件", "*.txt")])
    with open(path+".html", "w")as f:
        f.write(code_input.get("1.0", END))
# 保存预览png


def save_img(*args):
    code = code_input.get("1.0", END)
    config = imgkit.config(
        wkhtmltoimage=r"./wkhtmltoimage.exe")
    path = filedialog.asksaveasfilename(
        title="保存", filetype=[("图片文件", "*.png")])
    if (".png" not in path):
        path = path + ".png"
    imgkit.from_string(code, path, options={
                       'format': 'png', 'width': '800', 'height': '600'}, config=config)
# 保存代码png


def code_to_image(*args):

    code = code_input.get("1.0", END)
    path = filedialog.asksaveasfilename(
        title="保存", filetype=[("图片文件", "*.png")])
    if (".png" not in path):
        path = path + ".png"
    lexer = get_lexer_by_name('html', stripall=True)
    formatter = ImageFormatter(font_size=14, line_numbers=True, image_pad=10)
    image_data = highlight(code, lexer, formatter)
    with open(path, "wb") as f:
        f.write(image_data)
    print(f"Image file exported to: {path}")
# HTML在线调试
# 创建本地服务器


def add_server(def_code):
    global httpd

    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(def_code.encode('utf-8'))

    # 创建非阻塞的HTTP服务器
    class NonBlockingHTTPServer(http.server.ThreadingHTTPServer):
        def server_bind(self):
            self.socket.settimeout(1)
            super().server_bind()
            self.socket.settimeout(None)

    # 创建服务器并在后台线程中运行

    def RunWebServer():
        server_address = ('localhost', 8000)
        httpd = NonBlockingHTTPServer(server_address, MyHandler)
        httpd.serve_forever()
    # 关闭服务器

    def on_closing():
        server_address = ('localhost', 8000)
        httpd = NonBlockingHTTPServer(server_address, MyHandler)
        httpd.server_close()
        httpd.socket.close()
        root.destroy()
    # 重启服务器
    if httpd is not None:
        httpd = NonBlockingHTTPServer(('localhost', 8000), MyHandler)
        httpd.server_close()
        httpd.socket.close()
    server_thread = threading.Thread(target=RunWebServer)
    server_thread.start()
    # 弹出窗口
    root.attributes("-topmost", 0)
    webbrowser.open("http://127.0.0.1:8000")
    # 绑定窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", on_closing)
# 生成网页代码


def online_debug(*args):
    html_code = code_input.get("1.0", END)
    def_code = f'''
<!DOCTYPE html>
<html>
<head>
    <title>HTML Editor</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/codemirror.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/theme/dracula.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/mode/htmlmixed/htmlmixed.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/addon/fold/foldgutter.css" />
    <meta charset=\'utf-8\'>
    <style>
        /* 定义编辑区域的样式 */
        .editor {{
            height: 300px;
        }}
    </style>
</head>
<body>
    <h1 align="center">在线编辑</h1>
    <!-- HTML编辑区域 -->
    <br>
    <hr>
    <p>HTML编辑区</p>
    <textarea class="editor" id="html-editor">{html_code}</textarea>
    <br><br>
    <hr>
    <p>HTML预览区</p>
    <br>
    <!-- HTML预览区域 -->
    <pre class="preview language-markup" id="preview"></pre>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/codemirror.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/mode/htmlmixed/htmlmixed.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/mode/xml/xml.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/addon/edit/closebrackets.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/addon/edit/matchtags.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/addon/fold/foldcode.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/addon/fold/xml-fold.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/addon/fold/foldgutter.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/addon/hint/show-hint.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/addon/hint/html-hint.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/addon/hint/anyword-hint.js"></script>
    
    <script>
        // 创建CodeMirror编辑器实例
        const editor = CodeMirror.fromTextArea(document.getElementById('html-editor'), {{
            mode: 'htmlmixed',
            theme: 'dracula',
            autoCloseTags: true,
            matchTags: {{ bothTags: true }},
            lineNumbers: true,
            lineWrapping: true,
            tabSize: 4,
            foldGutter: true,
            gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
            autoRefresh: true // 开启自动刷新
        }});
        
        const htmlCode = editor.getValue();
        const preview = document.getElementById('preview');
        preview.innerHTML = htmlCode;
        editor.on('change', function() {{
            // 获取编辑器的HTML代码
            const htmlCode = editor.getValue();

            // 将HTML代码设置到预览区域中
            const preview = document.getElementById('preview');
            preview.innerHTML = htmlCode;

        }});
        
        //CodeMirror.commands.autocomplete(editor);
        //CodeMirror.commands.autocomplete(editor, null, {{ closeOnUnfocus: false, completeSingle: false }});
    </script>
</body>
</html>
    '''
    '''class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(def_code.encode('utf-8'))

    # 创建非阻塞的HTTP服务器
    class NonBlockingHTTPServer(http.server.ThreadingHTTPServer):
        def server_bind(self):
            self.socket.settimeout(1)
            super().server_bind()
            self.socket.settimeout(None)

    # 创建服务器并在后台线程中运行
    def RunWebServer():
        server_address = ('localhost', 8000)
        httpd = NonBlockingHTTPServer(server_address, MyHandler)
        httpd.serve_forever()
    def on_closing():
        server_address = ('localhost', 8000)
        httpd = NonBlockingHTTPServer(server_address, MyHandler)
        httpd.server_close()
        httpd.socket.close()
        root.destroy()
    server_thread = threading.Thread(target=RunWebServer)
    server_thread.start()
    root.attributes("-topmost", 0)
    webbrowser.open("http://127.0.0.1:8000")
    root.protocol("WM_DELETE_WINDOW", on_closing)'''
    add_server(def_code)


# 打开HTML


def open_html(*args):
    global open_path, start, start1, encoding_s
    start = 1.0
    start1 = 1.0
    open_path = filedialog.askopenfilename(
        title="打开", filetype=[("网页文件", "*.html"), ("文本文件", "*.txt")])
    encoding_s = "utf-8"
    if open_path != '':
        try:
            with open(open_path, "r", encoding=encoding_s)as f:
                default_code = f.read()
        except UnicodeDecodeError:
            encodings = ['utf-8', 'gbk', 'latin-1']
            for encoding in encodings:
                try:
                    with open(open_path, "r", encoding=encoding)as f:
                        default_code = f.read()
                    encoding_s = encoding
                    break
                except UnicodeDecodeError:
                    continue

    root.title("HTML编辑器-" + open_path + "-" + encoding_s)
    code_input.delete("1.0", "end")
    code_input.insert(1.0, default_code)


def custom_prettify(soup):
    for element in soup:
        if element.name:
            element.attrs = {}
            element.string = None
            element.append("\n")

            if len(element.contents) == 1 and not element.contents[0].name:
                element.insert(0, "\n")

            for child in element:
                if child.name:
                    custom_prettify(child)
                else:
                    if child.strip():
                        child.insert_before("\n")
                        child.insert_after("\n")

    return soup
# 格式化


def format(*args):
    code = code_input.get("1.0", END)
    soup = bs4.BeautifulSoup(code, 'html.parser')
    half_formatted_html = soup.prettify()
    formatted_html=""
    tab_list=re.findall(r'\n *.*',half_formatted_html)
    for line in tab_list:
        cnt=0
        print(line,end='')
        for char in line:
            if char==' ':
                cnt+=1
            elif char!='\n':
                break
        new_line=line.lstrip()
        new_line = "    "*cnt+new_line
        formatted_html+=new_line+"\n"
    code_input.delete("1.0", END)
    code_input.insert('insert', half_formatted_html.split("\n")[0]+"\n"+formatted_html)
# 压缩


def compress_html():
    html = code_input.get('1.0', tk.END)
    # 删除HTML中的注释
    html = re.sub(r"<!--(.|\s)*?-->", "", html)

    # 删除多余的空格、制表符、换行符
    html = re.sub(r"\s+", " ", html)

    # 删除标签之间的空格
    html = re.sub(r">\s+<", "><", html)

    # 删除行首和行尾的空格
    html = html.strip()

    code_input.delete('1.0', tk.END)
    code_input.insert('1.0', html)
# 自动修复


def fix(*args):
    code = code_input.get("1.0", END)
    soup = bs4.BeautifulSoup(code, 'html5lib')
    half_fixed_html = soup.prettify()
    fixed_html=""
    tab_list=re.findall(r'\n *.*',half_fixed_html)
    for line in tab_list:
        cnt=0
        print(line,end='')
        for char in line:
            if char==' ':
                cnt+=1
            elif char!='\n':
                break
        new_line=line.lstrip()
        new_line = "    "*cnt+new_line
        fixed_html+=new_line+"\n"
    
    code_input.delete("1.0", END)
    code_input.insert('insert', half_fixed_html.split("\n")[0]+"\n"+fixed_html)


def cancel(*args):
    code_input.edit_undo()


def recovery(*args):
    code_input.edit_redo()


def ask_save_html():
    save_bool = messagebox.askyesno('保存', '是否保存?')
    if save_bool:
        save_html_code()
        root.destroy()
    else:
        root.destroy()


def redo():
    code_input.delete("1.0", END)


def find_text(*args):
    code_input.tag_remove("find", "1.0", "end")
    root.attributes("-topmost", 0)
    text = simpledialog.askstring('查找', '请输入要查找的内容:')
    last_index = "1.0"
    while True:
        search_index = code_input.search(
            text, f"{last_index}+1c", stopindex=tk.END)
        # print(search_index)
        if search_index == last_index:
            break
        end_index = f"{search_index}+{len(text)}c"
        # print(search_index, end_index)
        try:
            code_input.tag_add("find", search_index, end_index)
            last_index = search_index
        except:
            break


def get_line_num():
    code = code_input.get("1.0", END)
    enter_num = 0
    text_num = 0
    for i in code:
        text_num += 1
        if i == "\n":
            enter_num += 1
    return [enter_num, text_num]
# def pool_auto_save():
#     P = Pool()
#     P.apply_async(auto_save)
# def auto_save():
#     global x,open_path
#     x = True
#     print(1)
#     while x:
#         code = code_input.get("1.0",END)
#         if open_path != "":
#             with open(open_path,"w")as f:
#                 f.write(code)
#             root.title("HTML编辑器-" + open_path + "已保存")
#             sleep(5)
#             root.title("HTML编辑器-" + open_path)
#             print("保存成功")
#         else:
#             open_path = filedialog.asksaveasfilename(title = "保存",filetype = [("网页文件","*.html"),("文本文件","*.txt")]) + ".html"
#             with open(open_path,"w")as f:
#                 f.write(code)
#             root.title("HTML编辑器-" + open_path + "已保存")
#             sleep(5)
#             root.title("HTML编辑器-" + open_path)
#             print("保存成功")
#         sleep(60)
# def cancel_auto_save():
#     global x,P
#     x = False
#     P.close()
# CSS基本操作


def add_css_file():
    global css_code_input, css
    global css_path
    css_path = ""
    css = tk.Tk()
    css.attributes("-topmost", 1)
    css.title("CSS编辑器")
    css.geometry("600x400+330+335")
    # button_save = Button(css,text="保存",command=save_css_code).place(y=0,x=0)
    # button_open = Button(css,text="打开",command=open_css_code).place(y=0,x=40)
    cmds = tk.Menu(css)
    file = tk.Menu(cmds, tearoff=0)
    cmds.add_cascade(label="文件", menu=file)
    file.add_command(label="保存", command=save_css_code)
    file.add_command(label="打开", command=open_css_code)

    quick_tag = tk.Menu(cmds, tearoff=0)
    cmds.add_cascade(label="常用选择器", menu=quick_tag)
    quick_tag.add_command(label="id选择器", command=id_selector)
    quick_tag.add_command(label="类选择器", command=class_selector)
    quick_tag.add_command(label="标签选择器", command=tag_selector)

    quick_properties = tk.Menu(cmds, tearoff=0)
    cmds.add_cascade(label="常用属性", menu=quick_properties)
    quick_properties.add_command(label="字体颜色", command=color)
    quick_properties.add_command(label="字体大小", command=font_size)
    quick_properties.add_command(label="字体粗细", command=font_weight)
    quick_properties.add_command(label="字体样式", command=font_style)
    quick_properties.add_command(label="背景颜色", command=background_color)
    quick_properties.add_command(label="背景图片", command=background_image)
    css.config(menu=cmds)
    css_code_input = tk.Text(css)
    css_code_input.pack(side='top', fill='both', expand=True)
    css.mainloop()


def open_css_code():
    global css_path, css
    css_path = filedialog.askopenfilename(
        title="打开", filetype=[("层叠样式表文件", "*.css"), ("文本文件", "*.txt")])
    with open(css_path, "r")as f:
        css_code = f.read()
    css_code_input.delete("1.0", "end")
    css_code_input.insert(1.0, css_code)


def save_css_code():
    global css_path, css
    css_code = css_code_input.get("1.0", END)
    if css_path == "":
        css_path = filedialog.asksaveasfilename(
            title="保存", filetype=[("层叠样式表文件", "*.css"), ("文本文件", "*.txt")])
    with open(css_path+".css", "w")as f:
        f.write(css_code)
    css.quit()
# JS基本操作


def add_js_file():
    global js_path, js_code_input, js
    js_path = ""
    js = tk.Tk()
    js.attributes("-topmost", 1)
    js.title("JS编辑器")
    js.geometry("600x400+330+335")
    cmds = tk.Menu(js)
    file = tk.Menu(cmds, tearoff=0)
    cmds.add_cascade(label="文件", menu=file)
    file.add_command(label="保存", command=save_js_code)
    file.add_command(label="打开", command=open_js_code)

    quick_s = tk.Menu(cmds, tearoff=0)
    cmds.add_cascade(label="常用变量", menu=quick_s)
    quick_s.add_command(label="通过id获取元素", command=getElement)
    quick_s.add_command(label="获取cookie", command=getCookie)

    quick_code = tk.Menu(cmds, tearoff=0)
    cmds.add_cascade(label="常用语句", menu=quick_code)
    quick_code.add_command(label="打开网页", command=open_page)
    quick_code.add_command(label="提示框", command=alert)
    quick_code.add_command(label="是否框", command=confirm)
    quick_code.add_command(label="输入框", command=prompt)
    js.config(menu=cmds)
    # button_save = Button(js,text="保存",command=save_js_code).place(y=0,x=0)
    # button_open = Button(js,text="打开",command=open_js_code).place(y=0,x=40)
    js_code_input = tk.Text(js)
    js_code_input.pack(side='top', fill='both', expand=True)
    js.mainloop()


def save_js_code():
    global js, js_path
    js_code = js_code_input.get("1.0", END)
    if js_path == "":
        js_path = filedialog.asksaveasfilename(
            title="保存", filetype=[("javascript脚本文件", "*.js"), ("文本文件", "*.txt")])
    with open(js_path, "w")as f:
        f.write(js_code)


def open_js_code():
    global js_path, js
    js_path = filedialog.askopenfilename(
        title="打开", filetype=[("javascript脚本文件", "*.js"), ("文本文件", "*.txt")])
    with open(js_path, "r")as f:
        js_code = f.read()
    js_code_input.delete("1.0", "end")
    js_code_input.insert(1.0, js_code)

# 编辑器风格


def bg_color():
    bg_rgb = colorchooser.askcolor()
    if bg_rgb[1] != None:
        code_input.config(bg=bg_rgb[1])
        # code_input.config(insertbackground="black")
        listbox.config(bg=bg_rgb[1], borderwidth=0, highlightthickness=0,
                       highlightbackground=bg_rgb[1])


def t_color():
    t_rgb = colorchooser.askcolor()
    if t_rgb[1] != None:
        code_input.config(fg=t_rgb[1])
        code_input.config(insertbackground=t_rgb[1])


def reset_color():
    code_input.config(fg='black', bg='white')
    code_input.config(insertbackground="black")
    root.config(bg='white')
    listbox.config(bg="white", borderwidth=0,
                   highlightthickness=0, highlightbackground="white")


def green_code_color():
    code_input.config(fg='green', bg='#001115')
    code_input.config(insertbackground="green")
    root.config(bg='#001115')
    listbox.config(bg="#0A0A0A", borderwidth=0,
                   highlightthickness=0, highlightbackground="#001126")


def getIndex(text, index):
    return tuple(map(int, str.split(text.index(index), ".")))


def update_x():
    global c
    c = False
    quit()
    root.quit()


# 常用语句
# html
def doctype():
    code_input.insert('insert', r'<!DOCTYPE html>')


def h1():
    code_input.insert('insert', r'<h1></h1>')


def h2():
    code_input.insert('insert', r'<h2></h2>')


def h3():
    code_input.insert('insert', r'<h3></h3>')


def h4():
    code_input.insert('insert', r'<h4></h4>')


def h5():
    code_input.insert('insert', r'<h5></h5>')


def p():
    code_input.insert('insert', r'<p></p>')


def html():
    code_input.insert('insert', '<html>\n\n</html>')


def head():
    code_input.insert('insert', '<head>\n\n</head>')


def body():
    code_input.insert('insert', '<body>\n\n</body>')


def title_tag():
    code_input.insert('insert', '<title></title>')


def set_lang():
    code_input.insert('insert', r'<meta charset="utf-8"/>')


def set_srceen_size():
    code_input.insert(
        'insert', r'<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0" />')


def link():
    code_input.insert('insert', r'<link src="" type="">')


def form():
    code_input.insert('insert', '<form>\n\n</form>')


def input_tag():
    code_input.insert('insert', r'<input></input>')


def script():
    code_input.insert('insert', '<script>\n\n</script>')


def empty_tag():
    code_input.insert('insert', '<></>')
# html properties


def class_():
    code_input.insert('insert', r' class=""')


def id_():
    code_input.insert('insert', r'id=""')


def name():
    code_input.insert('insert', r'name=""')


def action():
    code_input.insert('insert', r'action="/"')


def style():
    code_input.insert('insert', r'style=""')


def hidden():
    code_input.insert('insert', r'hidden=')


def title():
    code_input.insert('insert', r'title=""')


def accesskey():
    code_input.insert('insert', r'accesskey=""')
# css selector


def id_selector():
    css_code_input.insert('insert', '#id选择器名称{\n\n}')


def class_selector():
    css_code_input.insert('insert', '.类选择器名称{\n\n}')


def tag_selector():
    css_code_input.insert('insert', '标签名{\n\n}')
# css properties


def color():
    css_code_input.insert('insert', 'color:;')


def font_family():
    css_code_input.insert('insert', 'font-family:;')


def font_style():
    css_code_input.insert('insert', 'font-style:;')


def font_size():
    css_code_input.insert('insert', 'font-size:;')


def font_weight():
    css_code_input.insert('insert', 'font-weight:;')


def text_align():
    css_code_input.insert('insert', 'text-align:;')


def background_image():
    css_code_input.insert('insert', r'background-image:url("");')


def background_color():
    css_code_input.insert('insert', r'background-color:;')
# js


def getElement():
    js_code_input.insert('insert', r'document.getElementById("id名称");')


def getCookie():
    js_code_input.insert('insert', r'document.cookie;')


def open_page():
    js_code_input.insert('insert', r'window.open("网址");')


def alert():
    js_code_input.insert('insert', r'alert("文本");')


def confirm():
    js_code_input.insert('insert', r'confirm("文本");')


def prompt():
    js_code_input.insert('insert', r'prompt("问题", "默认文本");')

# HTML自动填充


def auto_completer(text, m):
    global recorded_text, recorded_text_attr
    html_tag = ['<a></a>', '<abbr></abbr>', '<address></address>', '<area/>', '<article></article>', '<aside></aside>', '<audio></audio>', '<b></b>', '<base/>', '<bdi></bdi>', '<bdo></bdo>', '<blockquote></blockquote>', '<body></body>', '<br/>', '<button></button>', '<canvas></canvas>', '<caption></caption>', '<cite></cite>', '<code></code>', '<col/>', '<colgroup></colgroup>', '<data></data>', '<datalist></datalist>', '<dd></dd>', '<del></del>', '<details></details>', '<dfn></dfn>', '<dialog></dialog>', '<div></div>', '<dl></dl>', '<dt></dt>', '<em></em>', '<embed/>', '<fieldset></fieldset>', '<figcaption></figcaption>', '<figure></figure>', '<footer></footer>', '<form></form>', '<h1></h1>', '<h2></h2>', '<h3></h3>', '<h4></h4>', '<h5></h5>', '<h6></h6>', '<head></head>', '<header></header>', '<hr/>', '<html></html>', '<i></i>', '<iframe></iframe>', '<img/>', '<input/>', '<ins></ins>', '<kbd></kbd>', '<label></label>', '<legend></legend>',
                '<li></li>', '<link/>', '<main></main>', '<map></map>', '<mark></mark>', '<meta/>', '<meter></meter>', '<nav></nav>', '<noscript></noscript>', '<object></object>', '<ol></ol>', '<optgroup></optgroup>', '<option></option>', '<output></output>', '<p></p>', '<param/>', '<picture></picture>', '<pre></pre>', '<progress></progress>', '<q></q>', '<rb></rb>', '<rp></rp>', '<rt></rt>', '<rtc></rtc>', '<ruby></ruby>', '<s></s>', '<samp></samp>', '<script></script>', '<section></section>', '<select></select>', '<small></small>', '<source/>', '<span></span>', '<strong></strong>', '<style></style>', '<sub></sub>', '<summary></summary>', '<sup></sup>', '<svg></svg>', '<table></table>', '<tbody></tbody>', '<td></td>', '<template></template>', '<textarea></textarea>', '<tfoot></tfoot>', '<th></th>', '<thead></thead>', '<time></time>', '<title></title>', '<tr></tr>', '<track/>', '<u></u>', '<ul></ul>', '<var></var>', '<video></video>', '<wbr/>']
    html_attributes = [" accept=''", " accept-charset=''", " accesskey=''", " action=''", " align=''", " alt=''", " async=''", " autocomplete=''", " autofocus=''", " autoplay=''", " background=''", " bgcolor=''", " border=''", " charset=''", " checked=''", " cite=''", " class=''", " color=''", " cols=''", " colspan=''", " content=''", " contenteditable=''", " controls=''", " coords=''", " data=''", " datetime=''", " default=''", " defer=''", " dir=''", " dirname=''", " disabled=''", " download=''", " draggable=''", " dropzone=''", " enctype=''", " for=''", " form=''", " headers=''", " height=''", " hidden=''", " high=''", " href=''", " hreflang=''", " http-equiv=''", " id=''", " ismap=''", " itemprop=''", " keytype=''", " kind=''", " label=''", " lang=''", " list=''", " loop=''", " low=''", " manifest=''", " max=''", " maxlength=''", " media=''", " method=''", " min=''", " multiple=''", " muted=''", " name=''", " novalidate=''", " onabort=''", " onafterprint=''", " onbeforeprint=''",
                       " onbeforeunload=''", " onblur=''", " oncanplay=''", " oncanplaythrough=''", " onchange=''", " onclick=''", " oncontextmenu=''", " oncopy=''", " oncuechange=''", " oncut=''", " ondblclick=''", " ondrag=''", " ondragend=''", " ondragenter=''", " ondragleave=''", " ondragover=''", " ondragstart=''", " ondrop=''", " ondurationchange=''", " onemptied=''", " onended=''", " onerror=''", " onfocus=''", " onhashchange=''", " oninput=''", " oninvalid=''", " onkeydown=''", " onkeypress=''", " onkeyup=''", " onload=''", " onloadeddata=''", " onloadedmetadata=''", " onloadstart=''", " onmousedown=''", " onmousemove=''", " onmouseout=''", " onmouseover=''", " onmouseup=''", " onmousewheel=''", " onoffline=''", " ononline=''", " onpagehide=''", " onpageshow=''", " onpaste=''", " onpause=''", " onplay=''", " onplaying=''", " onpopstate=''", " onprogress=''", " onratechange=''", " onreset=''", " onresize=''", " onscroll=''", " onsearch=''", " onseeked=''", " onseeking=''", " onselect=''"]
    options = html_tag+html_attributes
    matches = [option for option in options if option.startswith(text)]
    matches.sort(key=len)
    if matches != []:
        listbox.delete(0, tk.END)
        for match in matches:
            listbox.insert(tk.END, match)
        # listbox.place(x=root.winfo_x() + code_input.winfo_x(), y=root.winfo_y() + code_input.winfo_y() + code_input.winfo_height())
        cursor_coords = code_input.bbox(code_input.index(tk.INSERT))
        listbox_width = min(400, code_input.winfo_width() - cursor_coords[0])
        listbox.place(x=cursor_coords[0], y=cursor_coords[1] +
                      cursor_coords[3], width=listbox_width, height=100)
    else:
        listbox.delete(0, tk.END)
        listbox.place_forget()
        # recorded_text = ""
        # code_input.unbind("<KeyRelease>")
    if m == 0:
        listbox.bind("<Double-Button-1>", select_option)
    else:
        listbox.bind("<Double-Button-1>", select_option_attr)

    return matches


def on_key_pressed(event):
    global recorded_text, recorded_text_attr
    if event.char == '<':
        code_input.unbind("<KeyRelease>")
        recorded_text = ""
        code_input.bind("<KeyRelease>", on_text_recorded)
    elif event.char == ' ':
        recorded_text_attr = ""
        code_input.bind("<KeyRelease>", on_text_recorded_attr)


def on_text_recorded(event):
    global recorded_text
    if event.char == '>':
        code_input.unbind("<KeyRelease>")
        recorded_text = ""
    else:
        if event.keysym == 'BackSpace':
            recorded_text = recorded_text[:-1]
            auto_completer(recorded_text, 0)
        else:
            recorded_text += event.char
            auto_completer(recorded_text, 0)


def on_text_recorded_attr(event):
    global recorded_text_attr
    if event.keysym == 'BackSpace':
        recorded_text_attr = recorded_text_attr[:-1]
        auto_completer(recorded_text_attr, 1)
    else:
        recorded_text_attr += event.char
        auto_completer(recorded_text_attr, 1)

def find_tag_start():
    index=code_input.index(tk.INSERT)
    line=index.split('.')[0]
    col=index.split('.')[1]
    cline_text=code_input.get(f'{line}.0',f'{line}.end')
    find_index=-1
    for i in range(int(col)-1,-1,-1):
        if cline_text[i]=='<':
            find_index=i
            break
    if find_index!=-1:return str(find_index)
    return "linestart"

def select_option(event):
    global recorded_text
    selection = listbox.get(tk.ACTIVE)
    if selection:
        index = code_input.index(tk.INSERT)
        tag_start_col=find_tag_start()
        code_input.insert(index, selection[len(code_input.get(f"{int(float(index))}.{int(float(tag_start_col))}", index)):])
        listbox.place_forget()
        code_input.unbind("<KeyRelease>")
        recorded_text = ""


def select_option_attr(event):
    global recorded_text_attr
    selection = listbox.get(tk.ACTIVE)
    if selection:
        index = float(code_input.index(tk.INSERT))
        before_index_text = str(code_input.get(f"{index} linestart", index))
        last_space_index = float(
            str(int(index//1))+"."+str(before_index_text.rfind(" ")))
        # print(index, last_space_index)
        selected_index = int(round(index-last_space_index, 2)*10)
        selected_text = selection[selected_index:]
        code_input.insert(index, selected_text)

        listbox.place_forget()
        code_input.unbind("<KeyRelease>")
        recorded_text_attr = ""


# 检查


def check():
    code_input.tag_remove("error", "1.0", "end")
    code_input.tag_remove("info", "1.0", "end")
    error = ""
    html_code = code_input.get('1.0', tk.END)
    try:
        res = requests.post(url, headers=headers,
                            data=html_code.encode('utf-8'))
        json_res = res.json()
    except:
        retry = messagebox.askretrycancel('警告', '网络未连接，请检查网络后重试！')
        if retry:
            check()
            return 0
        else:
            return 0
    # print(json_res)
    translator = Translator(to_lang='zh')
    if json_res['messages']:
        error += "HTML code is invalid.\n"
        for message in json_res['messages']:
            error += "第{}行 {}:{}({})\n".format(message['lastLine'], message['type'],
                                               message['message'], translator.translate(message['message']))
            code_input.tag_add(message['type'], str(
                message['lastLine'])+".0", str(message['lastLine'])+".end")
        messagebox.showerror("HTML code is invalid.", error)
    else:
        error += "代码通过验证！"
        messagebox.showinfo("代码通过验证！", error)
        code_input.tag_remove("error", "1.0", "end")
# 模板


def m1():
    global start, start1
    start = 1.0
    start1 = 1.0
    with open("./模板1.html", "r", encoding="utf-8")as f:
        m_code = f.read()
    code_input.delete("1.0", END)
    code_input.insert('insert', m_code)
    sleep(1)


def m2():
    global start, start1
    start = 1.0
    start1 = 1.0
    with open("./模板2.html", "r", encoding="utf-8")as f:
        m_code = f.read()
    code_input.delete("1.0", END)
    code_input.insert('insert', m_code)
    sleep(1)


def m3():
    global start, start1
    start = 1.0
    start1 = 1.0
    with open("./模板3.html", "r", encoding="utf-8")as f:
        m_code = f.read()
    code_input.delete("1.0", END)
    code_input.insert('insert', m_code)
    sleep(1)


# 关于、帮助
info = '''名称:HTML编辑器
作者：王铭瑄
版本:3.3.1
更新日志:
2023/5/1:新增——自动填充
2023/6/10:修复——文件编码bug(UnicodeDecodeError: 'gbk' codec can't decode byte 0xa5 in position 926: illegal multibyte sequence)
2023/6/11:新增——格式化、自动修复
2023/6/12:新增——关于、帮助
2023/6/18:新增——保存代码为图片、保存网页预览
2023/6/19:新增——在线调试
2023/6/20:修复——在线调试编码bug
2023/7/8:新增——代码压缩
2023/8/7:调整——黑客代码风格颜色
2023/8/8:调整——自动填充候选框位置
2023/9/9:修复——自动填充bug
'''
help_info = '''1.输入操作
复制          Ctrl+C
粘贴          Ctrl+V
剪切          Ctrl+X
撤销          Ctrl+Z
恢复          Ctrl+Y
查找          Ctrl+f
2.文件操作
保存          Ctrl+S
另存为        Alt+C
打开          Ctrl+O
3.代码操作
预览          Ctrl+R
检查          Ctrl+C
格式化        Ctrl+G
自动修复      Ctrl+F
             
'''


def show_info(*args):
    messagebox.showinfo("关于", info)


def show_help(*args):
    messagebox.showinfo("帮助", help_info)


# 主程序(窗口)
# global code_input,css_code_input,css,open_path
root = tk.Tk()
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
x = int(w / 2 - 400)
y = int(h / 2 - 300)
root.attributes("-topmost", 1)
root.title("HTML编辑器")
# root.geometry("800x600+330+335")
root.geometry("%sx%s+%s+%s" % (w, h, x, y))
root.state('zoomed')
root.protocol("WM_DELETE_WINDOW", update_x)
line_num_text_l = tk.StringVar()
'''main_menu = Menu(root)
file_manage = Menu(main_menu,tearoff=0)
main_menu.add_cascade(label="文件",menu=main_menu)
file_manage.add_command(label="保存",command=save_html_code)
file_manage.add_command(label="HTML另存为",command=save_copy)
file_manage.add_command(label="打开",command=open_html)'''
# 菜单
cmds = tk.Menu(root)
file = tk.Menu(cmds, tearoff=0)
cmds.add_cascade(label="文件", menu=file)
file.add_command(label="保存(Ctrl+S)", command=save_html_code)
file.add_command(label="保存网页预览图", command=save_img)
file.add_command(label="保存代码为图片", command=code_to_image)
file.add_command(label="另存为(Alt+C)", command=save_copy)
file.add_command(label="打开(Ctrl+P)", command=open_html)
file.add_command(label="压缩代码", command=compress_html)
# file.add_command(label="自动保存",command=pool_auto_save)
# file.add_command(label="取消自动保存",command=cancel_auto_save)

test = tk.Menu(cmds, tearoff=0)
cmds.add_cascade(label="测试", menu=test)
test.add_command(label="预览(R)", command=run_html)
test.add_command(label="检查", command=check)
test.add_command(label="在线调试", command=online_debug)

order_file = tk.Menu(cmds, tearoff=0)
cmds.add_cascade(label="其它脚本", menu=order_file)
order_file.add_command(label="添加css文件", command=add_css_file)
order_file.add_command(label="添加js文件", command=add_js_file)

setcolor = tk.Menu(cmds, tearoff=0)
cmds.add_cascade(label="主题", menu=setcolor)
setcolor.add_command(label="字体颜色", command=t_color)
setcolor.add_command(label="背景颜色", command=bg_color)
setcolor.add_command(label="浅色", command=reset_color)
setcolor.add_command(label="黑客代码(深色)", command=green_code_color)

quick_tag = tk.Menu(cmds, tearoff=0)
cmds.add_cascade(label="快捷标签", menu=quick_tag)
quick_tag.add_command(label="<!DOCTYPE html>", command=doctype)
quick_tag.add_command(label="h1", command=h1)
quick_tag.add_command(label="h2", command=h2)
quick_tag.add_command(label="h3", command=h3)
quick_tag.add_command(label="h4", command=h4)
quick_tag.add_command(label="h5", command=h5)
quick_tag.add_command(label="p", command=p)
quick_tag.add_command(label="html", command=html)
quick_tag.add_command(label="head", command=head)
quick_tag.add_command(label="title", command=title_tag)
quick_tag.add_command(label="body", command=body)
quick_tag.add_command(label="link", command=link)
quick_tag.add_command(label="script", command=script)
quick_tag.add_command(label="form", command=form)
quick_tag.add_command(label="input", command=input_tag)
quick_tag.add_command(label="设置编码语言", command=set_lang)
quick_tag.add_command(label="设置屏幕适配", command=set_srceen_size)
quick_tag.add_command(label="空标签", command=empty_tag)

quick_properties_html = tk.Menu(cmds, tearoff=0)
cmds.add_cascade(label="常用属性", menu=quick_properties_html)
quick_properties_html.add_command(label="类", command=class_)
quick_properties_html.add_command(label="id", command=id_)
quick_properties_html.add_command(label="name", command=name)
quick_properties_html.add_command(label="action", command=action)
quick_properties_html.add_command(label="style", command=style)
quick_properties_html.add_command(label="hidden", command=hidden)
quick_properties_html.add_command(label="title", command=title)
quick_properties_html.add_command(label="accesskey", command=accesskey)


file = tk.Menu(cmds, tearoff=0)
cmds.add_cascade(label="模板", menu=file)
file.add_command(label="表单模板", command=m1)
file.add_command(label="相册模板", command=m2)
file.add_command(label="个人主页模板", command=m3)

help = tk.Menu(cmds, tearoff=0)
cmds.add_cascade(label="帮助", menu=help)
help.add_command(label="帮助", command=show_help)
help.add_command(label="关于", command=show_info)


root.config(menu=cmds)


def showPopoutMenu(w, menu):
    def popout(event):
        menu.post(event.x + w.winfo_rootx(), event.y + w.winfo_rooty())
        w.update()
    w.bind('<Button-3>', popout)


line_num = 0
line_num_text = ""
# line_num_l = tk.Label(root,text=line_num_text)
# line_num_l.pack()
'''button_save = Button(root,text="保存",command=save_html_code).place(y=0,x=0)
button_open = Button(root,text="打开",command=open_html).place(y=0,x=40)
button_save_copy = Button(root,text="HTML另存为",command=save_copy).place(y=0,x=80)
button_run = Button(root,text="运行",command=run_html).place(y=0,x=165)
button_add_css = Button(root,text="添加css文件",command=add_css_file).place(y=0,x=205)
button_add_js = Button(root,text="添加js文件",command=add_js_file).place(y=0,x=290)'''
code_input = tk.Text(root, undo=True, maxundo=10,
                     font=('微软雅黑', 10), borderwidth=0)
line_text = Text(root, font=('微软雅黑', 10, 'bold'), takefocus=0, cursor='arrow', state='disabled',
             bd=0, width=8)
scroll = tk.Scrollbar(root)
#line_text.pack(fill=Y, side=LEFT, pady=30)
code_input.pack(side=TOP, fill=BOTH, expand=True)
line_text.tag_config("nct", justify='center')
scroll.pack(fill=Y, side=RIGHT, pady=30)

listbox = tk.Listbox(root, width=50, font=('微软雅黑', 10), fg='orange')

line_label = tk.Label(root, textvariable=line_num_text_l,
                      font=('微软雅黑', 10))


r_menu = tk.Menu(root)
r_menu.add_cascade(label='保存(S)', command=save_html_code)
r_menu.add_cascade(label='打开(P)', command=open_html)
r_menu.add_cascade(label='重做(D)', command=redo)
r_menu.add_cascade(label='运行(R)', command=run_html)
r_menu.add_cascade(label='撤销(Z)', command=cancel)
r_menu.add_cascade(label='恢复(Y)', command=recovery)
r_menu.add_cascade(label='格式化(G)', command=format)
r_menu.add_cascade(label='自动修复(内测)(F)', command=fix)
showPopoutMenu(code_input, r_menu)
default_code = '''<!DOCTYPE html>
<html lang="zh">
    <head>
        <meta charset="utf-8">
        <title>Hello World!</title>
    </head>
    <body>
        <p>This is a test message</p>
    </body>
</html>
'''
global on_closing
code_input.insert("end", default_code)
# root.protocol("WM_DELETE_WINDOW",ask_save_html)
root.bind('<Control s>', save_html_code)
root.bind('<Control S>', save_html_code)
root.bind('<Control p>', open_html)
root.bind('<Control P>', open_html)
root.bind('<Control r>', run_html)
root.bind('<Control R>', run_html)
root.bind('<Alt c>', save_copy)
root.bind('<Alt C>', save_copy)
root.bind('<Control z>', cancel)
root.bind('<Control Z>', cancel)
root.bind('<Control y>', recovery)
root.bind('<Control Y>', recovery)
root.bind('<Control d>', redo)
root.bind('<Control D>', redo)
root.bind('<Control G>', format)
root.bind('<Control g>', format)
root.bind('<Control F>', fix)
root.bind('<Control f>', find_text)
code_input.bind('<Key>', on_key_pressed)

# root.update()

code_input.tag_configure("tag", foreground="orange")
code_input.tag_configure("info", background="yellow")
code_input.tag_configure("error", background="red")
code_input.tag_configure("find", background="#FF6600")
# code_input.tag_configure("properties", foreground="yellow")
# properties_list = ["class","id","name","action","title","style","value","hidden","accesskey","onclick","onload"]
# properties_pos_dict = {}
start = 1.0
start1 = 1.0
root.update()
green_code_color()
n = 0
input_keys = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '`', '-', '=', '[', ']', '\\', ';', "'", ',', '.', '/',
    ' ', 'tab', 'enter', 'backspace'
]
while c:
    '''for tag in code_input.tag_names():00
        code_input.tag_remove("tag","1.0","end")'''
    # try:
    tag_start_pos = code_input.search("<", start, stopindex=END)
    tag_end_pos = code_input.search(">", start1, stopindex=END)
    '''except Exception as e:
        n = 0
        print(e)
        start = 1.0
        start1 = 1.0'''
    if not tag_start_pos or not tag_end_pos:
        if any(keyboard.is_pressed(key) for key in input_keys) and n >= 100:
            # if n==50:
            for tag in code_input.tag_names():
                code_input.tag_remove("tag", "1.0", "end")
            n = 0
        else:
            n += 1
            pass
        start = 1.0
        start1 = 1.0
        sleep(0.01)
    else:
        tag_end_pos = str(getIndex(code_input, tag_end_pos)[
                          0]) + "." + str(getIndex(code_input, tag_end_pos)[1] + 1)
        # print(pos1)
        code_input.tag_add("tag", tag_start_pos, str(tag_end_pos))
        start = tag_start_pos + "+1c"
        start1 = str(tag_end_pos) + "+1c"

    line_num_text = "共" + \
        str(get_line_num()[0]) + "行," + str(get_line_num()[1]) + "个字符"
    line_num_text_l.set(line_num_text)
    # print(line_line_text)
    root.update()


root.mainloop()
#for tag in code_input.tag_names():
#    code_input.tag_remove("tag", "1.0", "end")
