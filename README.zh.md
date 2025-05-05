**Kindle Pilot 中文说明**



**Kindle Pilot** 是一个轻量级的 Kindle 远程控制工具。通过 SSH 重放已录制的触控手势实现远程翻页，无需额外硬件即可操作。

补充一个视频教程：【教程-翻页笔/键盘 遥控 kindle翻页】 https://www.bilibili.com/video/BV1JsLDzAEH2/?share_source=copy_web&vd_source=d9f751aff1782643133f83d15e916fa8

windows版下载链接 蓝奏云：https://wwwb.lanzoup.com/b00zxpwq5i 密码：b9fb



[🌐 English Version](README.md)



------



**✨ 功能亮点**

​	•	通过 SSH 控制 Kindle 翻页

​	•	自动识别横竖屏幕方向

​	•	模块化结构，配置使用 JSON 格式



> ⚠️ **使用要求**
>
> - Kindle 设备需越狱；
> - Kindle 上需安装 **UsbNetLite** 或 **UsbNet** 插件以启用 SSH；
> - 如使用源码运行，需在电脑上安装 Python（推荐 3.8 及以上版本）。
>
> 💡 我们也提供**打包好的可执行文件**（无需安装 Python）：
>
> - 适用于 Windows x86 系统（支持 Windows 10 及以上）；
> - 适用于 macOS Apple Silicon（支持 macOS 13 及以上版本）。



**🚀 快速开始**



**1. 克隆项目仓库**

```
git clone https://github.com/uybixd/Kindle_Pilot.git
cd Kindle_Pilot
```

**2. 安装依赖项**

```
pip install -r requirements.txt
```

**3. 配置设备信息**



编辑 config/user_config.json 文件，填写 Kindle 的 IP 地址、用户名和密码。



**4. 启动控制器**

```
python main.py
```

系统将引导你录制翻页手势，并一一验证。



**📁 项目结构**

```
Kindle_Pilot/
├── config/           # 配置文件目录
├── utils/            # 核心逻辑模块（如 SSH、设备识别、命令发送）
├── tests/            # Pytest 单元测试
├── i18n/             # 多语言支持（开发中）
├── main.py           # 程序入口
└── requirements.txt  # 依赖项列表
```





------



**📄 开源协议**



本项目采用 MIT License 开源协议，欢迎自由使用、分享和贡献。