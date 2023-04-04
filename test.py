import wx
import requests
import requests.exceptions
import json
import os
from socket import gethostname
from zipfile import ZipFile

class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='AI神经网络计算分布式节点客户端', size=(620, 500))

        # 设置窗口居中
        self.Centre()

        # 创建选项卡
        self.notebook = wx.Notebook(self, id=wx.ID_ANY)

        # 创建当前状态页面
        self.create_current_status_page()

        # 创建超频页面
        self.create_overclock_page()

        # 创建其他设置页面
        self.create_other_settings_page()

        # 创建帮助页面
        self.create_help_page()

        # 加载 Hyper 参数
        self.load_hyperparameters()

        # 设置窗口关闭方法
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # 读取"C:\\aicalculator\\user.conf"加载
        config_file = "C:\\aicalculator\\user.conf"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = json.load(f)
                # Update values of relevant controls
                self.machine_name_edit.SetValue(config.get("machine_name", ""))
                self.tag_edit.SetValue(config.get("tag", ""))
                self.hyper_combo.SetValue(config.get("hyper", ""))

    def create_current_status_page(self):
        # 创建当前状态页面
        page = wx.Panel(parent=self.notebook, id=wx.ID_ANY)
        self.notebook.AddPage(page, "当前状态")

        # 创建机器名标签及文本框
        machine_name_lbl = wx.StaticText(parent=page, id=wx.ID_ANY, label="本机名：", pos=(50, 30))
        machine_name_edit = wx.TextCtrl(parent=page, id=wx.ID_ANY, value=gethostname(), pos=(120, 25), size=(150, -1))

        # 计算核心标签及下拉框
        hyper_lbl = wx.StaticText(parent=page, id=wx.ID_ANY, label="计算核心：", pos=(50, 70), size=(60, -1))
        hyper_combo = wx.ComboBox(parent=page, id=wx.ID_ANY, pos=(120, 65), size=(150, -1), style=wx.CB_READONLY)
        hyper_combo.Bind(wx.EVT_COMBOBOX, self.on_hyperparameter_triggered)

        # 创建参数标签及文本框
        tag_lbl = wx.StaticText(parent=page, id=wx.ID_ANY, label="计算参数：", pos=(50, 110))
        tag_edit = wx.TextCtrl(parent=page, id=wx.ID_ANY, value="", pos=(120, 105), size=(420, -1),
                               style=wx.TE_MULTILINE)

        # 创建开始按钮及状态标签
        status_btn = wx.ToggleButton(parent=page, id=wx.ID_ANY, label="开始", pos=(450, 20), size=(90, 60))
        status_lbl = wx.StaticText(parent=page, id=wx.ID_ANY, label="状态：等待开始...", pos=(320, 35))

        # 创建显示端口标签及文本框
        port_lbl = wx.StaticText(parent=page, id=wx.ID_ANY, label="已启动端口：", pos=(50, 160))
        port_display = wx.TextCtrl(parent=page, id=wx.ID_ANY, value="", pos=(50, 180), size=(490, 220),
                                   style=wx.TE_MULTILINE | wx.TE_READONLY)

        # 保存控件对象到 self
        self.current_status_page = page
        self.machine_name_edit = machine_name_edit
        self.tag_edit = tag_edit
        self.status_btn = status_btn
        self.status_lbl = status_lbl
        self.port_display = port_display
        self.hyper_combo = hyper_combo

        # 绑定开始按钮事件
        self.status_btn.Bind(wx.EVT_TOGGLEBUTTON, self.on_start_button_toggled)

    def create_overclock_page(self):
        # 创建超频页面
        page = wx.Panel(parent=self.notebook, id=wx.ID_ANY)
        self.notebook.AddPage(page, "超频")

        # TODO: 添加超频页面控件

        # 保存控件对象到 self
        self.overclock_page = page

    def create_other_settings_page(self):
        # 创建其他设置页面
        page = wx.Panel(parent=self.notebook, id=wx.ID_ANY)
        self.notebook.AddPage(page, "其他设置")

        # TODO: 添加其他设置页面控件

        # 保存控件对象到 self
        self.other_settings_page = page

    def create_help_page(self):
        # 创建帮助页面
        page = wx.Panel(parent=self.notebook, id=wx.ID_ANY)
        self.notebook.AddPage(page, "帮助")

        # 创建帮助页面控件
        help_lbl = wx.StaticText(parent=page, id=wx.ID_ANY, label="帮助信息", pos=(50, 50), size=(200, -1))
        help_textctrl = wx.TextCtrl(parent=page, id=wx.ID_ANY, value="", pos=(50, 80), size=(490, 260),
                                    style=wx.TE_MULTILINE | wx.TE_READONLY)

        # TODO: 添加帮助页面内容

        # 保存控件对象到 self
        self.help_page = page
        self.help_textctrl = help_textctrl

    def load_hyperparameters(self):
        self.hyper_combo.Clear()

        # 获取 计算核心参数并更新下拉框
        url = 'http://43.154.126.224/hx/hx.ver'
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                raise requests.exceptions.RequestException(f'更新数据失败，状态码{resp.status_code}')
            hyperparams = []
            for line in resp.text.strip().split('\n'):
                name, value, other = line.split()
                hyperparams.append({"name": name, "value": value, "other": other})
        except requests.exceptions.RequestException as exc:
            wx.MessageBox(f"无法从 {url} 获取数据：{exc}", "通信错误", wx.OK | wx.ICON_WARNING)
            hyperparams = [{"name": "默认参数1", "value": 1},
                           {"name": "默认参数2", "value": 2}]

        if hyperparams:
            for param in hyperparams:
                hyper_name = param['name']
                self.hyper_combo.Append(hyper_name, param)
        else:
            self.hyper_combo.Append('无匹配项')

    def on_hyperparameter_triggered(self, event):
        # 处理下拉框选择事件
        selection = self.hyper_combo.GetSelection()
        if selection != wx.NOT_FOUND:
            hyperparameter = self.hyper_combo.GetClientData(selection)
            print('Clicked Hyper Parameter:', hyperparameter)

    def on_start_button_toggled(self, event):
        # 处理开始按钮事件
        if event.GetEventObject().GetValue():
            self.status_lbl.SetLabel("状态：正在工作")
            self.status_btn.SetLabel("停止")
            self.create_folders()
            self.save_user_settings()
            self.download_and_extract_files()
        else:
            self.status_lbl.SetLabel("状态：等待开始")
            self.status_btn.SetLabel("开始")

    def create_folders(self):
        # 创建磁盘根目录下的aicalculator文件夹及其core子文件夹
        if not os.path.exists("C:\\aicalculator"):
            os.mkdir("C:\\aicalculator")
        if not os.path.exists("C:\\aicalculator\\core"):
            os.mkdir("C:\\aicalculator\\core")

    def save_user_settings(self):
        # 保存当前用户的设置到json文件
        data = {'machine_name': self.machine_name_edit.GetValue(),
                'hyper_name': self.hyper_combo.GetValue(),
                'tag': self.tag_edit.GetValue()}
        with open("C:\\aicalculator\\user.conf", "w") as f:
            json.dump(data, f)

    def download_and_extract_files(self):
        # 获取当前下拉框选择的计算参数的下载链接，并下载该文件保存到core目录下并解压到core目录下
        selection = self.hyper_combo.GetSelection()
        if selection != wx.NOT_FOUND:
            hyperparameter = self.hyper_combo.GetClientData(selection)
            hyperlink = hyperparameter['value']
            filename = hyperlink.split("/")[-1]
            file_path = f'C:\\aicalculator\\core\\{filename}'
            if not os.path.exists(file_path):
                try:
                    resp = requests.get(hyperlink)
                    with open(file_path, 'wb') as f:
                        f.write(resp.content)
                except requests.exceptions.RequestException as e:
                    wx.MessageBox(f"下载文件错误：{e}", "下载错误", wx.OK | wx.ICON_WARNING)

            with ZipFile(file_path, 'r') as zipObj:
                zipObj.extractall("C:\\aicalculator\\core")

    def on_close(self, event):
        # 处理窗口关闭事件
        dlg = wx.MessageDialog(self, "确定要退出吗？", "警告", wx.YES_NO | wx.ICON_WARNING)
        if dlg.ShowModal() == wx.ID_YES:
            self.Destroy()
        dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    window = MainWindow()
    window.Show()
    app.MainLoop()