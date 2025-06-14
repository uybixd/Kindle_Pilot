**Kindle Pilot**



**Kindle Pilot** is a lightweight remote control utility for Kindle devices. It enables remote page-turning via SSH by replaying recorded touch gestures. No additional hardware is required.



[🇨🇳 中文说明](README.zh.md)



------



**✨ Features**

​	•	Remote page turning through SSH

​	•	Screen orientation detection

​	•	Modular structure and JSON configuration

> ⚠️ **Requirements**
>
> - Your Kindle must be jailbroken.
> - You need to install either **UsbNetLite** or **UsbNet** on the Kindle to enable SSH access.
> - If running from source, Python 3.8+ must be installed on your computer.
>

**🚀 Getting Started**



**1. Clone this repository**

```
git clone https://github.com/uybixd/Kindle_Pilot.git
cd Kindle_Pilot
```

**2. Install Python dependencies**

```
pip install -r requirements.txt
```

**3. Edit config file**



Edit config/user_config.json and fill in your Kindle’s IP address, username, and password.



**4. Run the controller**

```
python main.py
```

You will be guided to record page-turning gestures and verify them one by one.



**📁 Project Structure**

```
Kindle_Pilot/
├── config/           # Config files
├── utils/            # Logic modules: SSH, device detection, command sending
├── tests/            # Pytest unit tests
├── i18n/             # Internationalization (coming soon)
├── main.py           # Main entry
└── requirements.txt  # Dependencies
```





------



**📄 License**



MIT License. Feel free to use, share, and contribute.
