# Burp-Site
<div align="center">
    <img src="/src/static/images/logo-2.png" width="300" style="margin: auto; display: block;"/>
</div>
<p align="justify">
    Burp-Site is a web-based application designed to enhance the process of web application security testing. It allows users to intercept, analyze, and manipulate HTTP requests and responses to identify potential vulnerabilities in web applications. Unlike traditional tools, Burp-Site is lightweight and runs seamlessly as a Docker service, eliminating the need for complex installation and configuration.
    <br><br>
    Built with Python and powered by Flask, Burp-Site offers a user-friendly interface and integrates essential features inspired by Burp Suite, such as HTTP History, Repeater, and Intruder. This tool is ideal for security researchers and penetration testers who need a straightforward yet powerful solution to conduct web application vulnerability testing.
</p>

### Installation
You can download Burp-Site by cloning the Git Repository:

```
git clone https://github.com/XToni007/Burp-Site.git
```

### Usage
To use Burp-Site, follow these steps:

1. Open the Burp-Site folder in your terminal or command prompt.
2. Run the command `./start.sh` to start the application.
3. In your web browser, navigate to `http://localhost:8000` to access the Burp-Site interface.
<img src="/src/static/images/homePage.png">

### Proxy Configuration

1. Set browser proxy with your device local address (example 127.0.0.1) and port 8080.
2. Navigate to `mitm.it` at your browser.
<img src="/src/static/images/mitm.it.png">
3. Download the certificate based on device or browser you use.
4. Install the certificate on your device or browser.


#### Important Notes:
- If you want to change the listener port, you can heading to run.py file and change the --listen-port. <img src="/src/static/images/change-port.png">
- Each time you change the source code, rebuild the docker by run ./start.sh
- If you rebuild the docker, you have to re-config the certificate into your devices.



