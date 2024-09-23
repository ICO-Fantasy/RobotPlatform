from datetime import datetime

from reportlab.graphics.charts.barcharts import VerticalBarChart  # 图表类
from reportlab.graphics.charts.legends import Legend  # 图例类
from reportlab.graphics.shapes import Drawing  # 绘图工具
from reportlab.lib import colors  # 颜色模块
from reportlab.lib.pagesizes import letter  # 页面的标志尺寸 (8.5*inch, 11*inch)
from reportlab.lib.styles import getSampleStyleSheet  # 文本样式
from reportlab.lib.units import cm  # 单位：cm
from reportlab.pdfbase import pdfmetrics  # 注册字体
from reportlab.pdfbase.ttfonts import TTFont  # 字体类
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table  # 报告内容相关类

# 注册字体 (提前准备好字体文件，如果同一个文件需要多种字体可以注册多个)
pdfmetrics.registerFont(TTFont("SimSun", r"C:\Windows\Fonts\simsun.ttc"))


class Graphs:
    # 绘制标题
    @staticmethod
    def draw_title(title: str):
        # 获取所有样式表
        style = getSampleStyleSheet()
        # 拿到标题样式
        ct = style["Heading1"]
        # 单独设置样式相关属性
        ct.fontName = "SimSun"  # 字体名
        ct.fontSize = 80  # 字体大小
        ct.leading = 110  # 行间距
        ct.textColor = colors.black  # 字体颜色
        ct.alignment = 1  # 居中
        ct.bold = True
        # 创建标题对应的段落，并且返回
        return Paragraph(title, ct)

    # 绘制小标题
    @staticmethod
    def draw_little_title(title: str):
        # 获取所有样式表
        style = getSampleStyleSheet()
        # 拿到标题样式
        ct = style["Normal"]
        # 单独设置样式相关属性
        ct.fontName = "SimSun"  # 字体名
        ct.fontSize = 50  # 字体大小
        ct.leading = 80  # 行间距
        ct.textColor = colors.black  # 字体颜色
        ct.alignment = 1  # 居中
        # 创建标题对应的段落，并且返回
        return Paragraph(title, ct)

    # 绘制表格
    @staticmethod
    def draw_table(*args, col_width=100):
        # 列宽度
        style = [
            ("FONTNAME", (0, 0), (-1, -1), "SimSun"),  # 字体
            ("FONTSIZE", (0, 0), (-1, 0), 12),  # 第一行的字体大小
            ("FONTSIZE", (0, 1), (-1, -1), 10),  # 第二行到最后一行的字体大小
            ("BACKGROUND", (0, 0), (-1, 0), "#d5dae6"),  # 设置第一行背景颜色
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 第一行水平居中
            ("ALIGN", (0, 1), (-1, -1), "CENTER"),  # 第二行到最后一行水平居中
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # 所有表格上下居中对齐
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),  # 设置表格内文字颜色
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),  # 设置表格框线为 grey 色，线宽为 0.5
            # ('SPAN', (0, 1), (0, 2)),  # 合并第一列二三行
            # ('SPAN', (0, 3), (0, 4)),  # 合并第一列三四行
            # ('SPAN', (0, 5), (0, 6)),  # 合并第一列五六行
            # ('SPAN', (0, 7), (0, 8)),  # 合并第一列五六行
        ]
        table = Table(args, colWidths=col_width, style=style)
        return table

    @staticmethod
    def draw_footer(canvas, doc):
        # 获取当前时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 创建页脚字符串
        footer_text = f"创建时间：{now}"
        # 设置字体
        canvas.setFont("SimSun", 10)
        # 在底部中心位置绘制页脚
        canvas.drawCentredString(letter[0] / 2, 30, footer_text)


if __name__ == "__main__":
    # 创建内容对应的空列表
    content = list()

    # 添加标题
    content.append(Graphs.draw_title("物料信息表"))

    # 添加小标题
    content.append(Graphs.draw_title(""))
    content.append(Graphs.draw_little_title("物料基本信息"))
    # 添加表格
    data = [["名称", "长度", "半径", "厚度", "数量"], ["pipe-01", "100", "12", "1.5", "2"]]
    content.append(Graphs.draw_table(*data, col_width=100))

    # 添加小标题
    content.append(Graphs.draw_title(""))
    content.append(Graphs.draw_little_title("管件 XYZR"))
    # 添加表格
    data = [["x", "y", "z", "r"], ["111", "111", "111", "111"], ["222", "222", "222", "222"], ["333", "333", "333", "333"]]
    content.append(Graphs.draw_table(*data))

    # 生成 pdf 文件
    doc = SimpleDocTemplate("output_report_chinese.pdf", pagesize=letter)
    # doc.build(content)
    # 将页脚方法添加到页脚
    doc.build(content, onFirstPage=Graphs.draw_footer, onLaterPages=Graphs.draw_footer)
