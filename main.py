# -*- coding: UTF-8 -*-

import requests
import re
import random
import socket
import struct
import time
import os
import urllib.parse

def url_encode(data):
    """URL编码"""
    return urllib.parse.quote(data)

def url_decode(data):
    """URL解码"""
    return urllib.parse.unquote(data)

def login(account, password):
    PHONE_PATTERN = r"(^(1)\d{10}$)"
    if re.match(PHONE_PATTERN, account):
        account = f"+86{account}"
        third_name = "huami_phone"
    else:
        third_name = "huami"

    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "MiFit/6.12.0 (MCE16; Android 16; Density/1.5)",
        "app_name": "com.xiaomi.hm.health",
    }
    url1 = "https://api-user.huami.com/registrations/" + account + "/tokens"
    data1 = f"client_id=HuaMi&country_code=CN&json_response=true&name={account}&password={password}&redirect_uri=https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html&state=REDIRECTION&token=access"
    res1 = requests.post(url1, data=data1, headers=headers)

    if res1.status_code == 200:
        res1 = res1.json()
        if "access" in res1:
            code = res1["access"]
        else:
            print(f"错误:用户名或密码不正确")
            return None, None
    elif res1.status_code == 429:
        print(f"错误:请求过于频繁，请稍后再试")
        return None, None
    else:
        print(f"登录失败:Access Code={res1.status_code}")
        return None, None

    url2 = "https://account.huami.com/v2/client/login"
    data2 = f"app_name=com.xiaomi.hm.health&country_code=CN&code={code}&device_id=02:00:00:00:00:00&device_model=android_phone&app_version=6.12.0&grant_type=access_token&allow_registration=false&source=com.xiaomi.hm.health&third_name={third_name}"
    res2 = requests.post(url2, data=data2, headers=headers)

    if res2.status_code == 200:
        res2 = res2.json()
        login_token = res2["token_info"]["login_token"]
        user_id = res2["token_info"]["user_id"]
        #print(res2)
        return login_token, user_id
    else:
        print(f"登录失败:Login Code={res2.status_code}")
        return None, None

def get_app_token(login_token):
    """获取 app_token"""
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "MiFit/6.12.0 (MCE16; Android 16; Density/1.5)",
        "app_name": "com.xiaomi.hm.health",
    }
    url = f"https://account-cn.huami.com/v1/client/app_tokens?login_token={login_token}"
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        res_data = res.json()
        if "token_info" in res_data:
            return res_data["token_info"]["app_token"]
        else:
            print("错误:无法获取 app_token")
            return None
    else:
        print(f"错误:获取 app_token 失败，状态码: {res.status_code}")
        return None

def change_steps(account, user_id, app_token, steps):
    """修改步数"""
    timestamp = get_timestamp()
    if timestamp is None:
        print("警告: NTP 时间获取失败，使用系统时间")
        timestamp = time.time()
    
    seconds = int(timestamp)
    dateToday = time.strftime("%F")
    deviceID = "0000000000000000"

    dataJSON = "%5b%7b%22data_hr%22%3a%22%2f%2f%2f%2f%2f%2f9L%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fVv%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f0v%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f9e%2f%2f%2f%2f%2f0n%2fa%2f%2f%2fS%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f0b%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f1FK%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fR%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f9PTFFpaf9L%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fR%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f0j%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f9K%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fOv%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fzf%2f%2f%2f86%2fzr%2fOv88%2fzf%2fPf%2f%2f%2f0v%2fS%2f8%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fSf%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fz3%2f%2f%2f%2f%2f%2f0r%2fOv%2f%2f%2f%2f%2f%2fS%2f9L%2fzb%2fSf9K%2f0v%2fRf9H%2fzj%2fSf9K%2f0%2f%2fN%2f%2f%2f%2f0D%2fSf83%2fzr%2fPf9M%2f0v%2fOv9e%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fS%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fzv%2f%2fz7%2fO%2f83%2fzv%2fN%2f83%2fzr%2fN%2f86%2fz%2f%2fNv83%2fzn%2fXv84%2fzr%2fPP84%2fzj%2fN%2f9e%2fzr%2fN%2f89%2f03%2fP%2f89%2fz3%2fQ%2f9N%2f0v%2fTv9C%2f0H%2fOf9D%2fzz%2fOf88%2fz%2f%2fPP9A%2fzr%2fN%2f86%2fzz%2fNv87%2f0D%2fOv84%2f0v%2fO%2f84%2fzf%2fMP83%2fzH%2fNv83%2fzf%2fN%2f84%2fzf%2fOf82%2fzf%2fOP83%2fzb%2fMv81%2fzX%2fR%2f9L%2f0v%2fO%2f9I%2f0T%2fS%2f9A%2fzn%2fPf89%2fzn%2fNf9K%2f07%2fN%2f83%2fzn%2fNv83%2fzv%2fO%2f9A%2f0H%2fOf8%2f%2fzj%2fPP83%2fzj%2fS%2f87%2fzj%2fNv84%2fzf%2fOf83%2fzf%2fOf83%2fzb%2fNv9L%2fzj%2fNv82%2fzb%2fN%2f85%2fzf%2fN%2f9J%2fzf%2fNv83%2fzj%2fNv84%2f0r%2fSv83%2fzf%2fMP%2f%2f%2fzb%2fMv82%2fzb%2fOf85%2fz7%2fNv8%2f%2f0r%2fS%2f85%2f0H%2fQP9B%2f0D%2fNf89%2fzj%2fOv83%2fzv%2fNv8%2f%2f0f%2fSv9O%2f0ZeXv%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f1X%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f9B%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fTP%2f%2f%2f1b%2f%2f%2f%2f%2f%2f0%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f%2f9N%2f%2f%2f%2f%2f%2f%2f%2f%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%2fv7%2b%22%2c%22date%22%3a%22%7bdateToday%7d%22%2c%22data%22%3a%5b%7b%22start%22%3a0%2c%22stop%22%3a1439%2c%22value%22%3a%22UA8AUBQAUAwAUBoAUAEAYCcAUBkAUB4AUBgAUCAAUAEAUBkAUAwAYAsAYB8AYB0AYBgAYCoAYBgAYB4AUCcAUBsAUB8AUBwAUBIAYBkAYB8AUBoAUBMAUCEAUCIAYBYAUBwAUCAAUBgAUCAAUBcAYBsAYCUAATIPYD0KECQAYDMAYB0AYAsAYCAAYDwAYCIAYB0AYBcAYCQAYB0AYBAAYCMAYAoAYCIAYCEAYCYAYBsAYBUAYAYAYCIAYCMAUB0AUCAAUBYAUCoAUBEAUC8AUB0AUBYAUDMAUDoAUBkAUC0AUBQAUBwAUA0AUBsAUAoAUCEAUBYAUAwAUB4AUAwAUCcAUCYAUCwKYDUAAUUlEC8IYEMAYEgAYDoAYBAAUAMAUBkAWgAAWgAAWgAAWgAAWgAAUAgAWgAAUBAAUAQAUA4AUA8AUAkAUAIAUAYAUAcAUAIAWgAAUAQAUAkAUAEAUBkAUCUAWgAAUAYAUBEAWgAAUBYAWgAAUAYAWgAAWgAAWgAAWgAAUBcAUAcAWgAAUBUAUAoAUAIAWgAAUAQAUAYAUCgAWgAAUAgAWgAAWgAAUAwAWwAAXCMAUBQAWwAAUAIAWgAAWgAAWgAAWgAAWgAAWgAAWgAAWgAAWREAWQIAUAMAWSEAUDoAUDIAUB8AUCEAUC4AXB4AUA4AWgAAUBIAUA8AUBAAUCUAUCIAUAMAUAEAUAsAUAMAUCwAUBYAWgAAWgAAWgAAWgAAWgAAWgAAUAYAWgAAWgAAWgAAUAYAWwAAWgAAUAYAXAQAUAMAUBsAUBcAUCAAWwAAWgAAWgAAWgAAWgAAUBgAUB4AWgAAUAcAUAwAWQIAWQkAUAEAUAIAWgAAUAoAWgAAUAYAUB0AWgAAWgAAUAkAWgAAWSwAUBIAWgAAUC4AWSYAWgAAUAYAUAoAUAkAUAIAUAcAWgAAUAEAUBEAUBgAUBcAWRYAUA0AWSgAUB4AUDQAUBoAXA4AUA8AUBwAUA8AUA4AUA4AWgAAUAIAUCMAWgAAUCwAUBgAUAYAUAAAUAAAUAAAUAAAUAAAUAAAUAAAUAAAUAAAWwAAUAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAeSEAeQ8AcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcBcAcAAAcAAAcCYOcBUAUAAAUAAAUAAAUAAAUAUAUAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcCgAeQAAcAAAcAAAcAAAcAAAcAAAcAYAcAAAcBgAeQAAcAAAcAAAegAAegAAcAAAcAcAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcCkAeQAAcAcAcAAAcAAAcAwAcAAAcAAAcAIAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcCIAeQAAcAAAcAAAcAAAcAAAcAAAeRwAeQAAWgAAUAAAUAAAUAAAUAAAUAAAcAAAcAAAcBoAeScAeQAAegAAcBkAeQAAUAAAUAAAUAAAUAAAUAAAUAAAcAAAcAAAcAAAcAAAcAAAcAAAegAAegAAcAAAcAAAcBgAeQAAcAAAcAAAcAAAcAAAcAAAcAkAegAAegAAcAcAcAAAcAcAcAAAcAAAcAAAcAAAcA8AeQAAcAAAcAAAeRQAcAwAUAAAUAAAUAAAUAAAUAAAUAAAcAAAcBEAcA0AcAAAWQsAUAAAUAAAUAAAUAAAUAAAcAAAcAoAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAYAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcBYAegAAcAAAcAAAegAAcAcAcAAAcAAAcAAAcAAAcAAAeRkAegAAegAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAEAcAAAcAAAcAAAcAUAcAQAcAAAcBIAeQAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcBsAcAAAcAAAcBcAeQAAUAAAUAAAUAAAUAAAUAAAUBQAcBYAUAAAUAAAUAoAWRYAWTQAWQAAUAAAUAAAUAAAcAAAcAAAcAAAcAAAcAAAcAMAcAAAcAQAcAAAcAAAcAAAcDMAeSIAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcBQAeQwAcAAAcAAAcAAAcAMAcAAAeSoAcA8AcDMAcAYAeQoAcAwAcFQAcEMAeVIAaTYAbBcNYAsAYBIAYAIAYAIAYBUAYCwAYBMAYDYAYCkAYDcAUCoAUCcAUAUAUBAAWgAAYBoAYBcAYCgAUAMAUAYAUBYAUA4AUBgAUAgAUAgAUAsAUAsAUA4AUAMAUAYAUAQAUBIAASsSUDAAUDAAUBAAYAYAUBAAUAUAUCAAUBoAUCAAUBAAUAoAYAIAUAQAUAgAUCcAUAsAUCIAUCUAUAoAUA4AUB8AUBkAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAA%22%2c%22tz%22%3a32%2c%22did%22%3a%22%7bdeviceID%7d%22%2c%22src%22%3a24%7d%5d%2c%22summary%22%3a%22%7b%5c%22v%5c%22%3a6%2c%5c%22slp%5c%22%3a%7b%5c%22st%5c%22%3a0%2c%5c%22ed%5c%22%3a0%2c%5c%22dp%5c%22%3a0%2c%5c%22lt%5c%22%3a0%2c%5c%22wk%5c%22%3a0%2c%5c%22usrSt%5c%22%3a-1440%2c%5c%22usrEd%5c%22%3a-1440%2c%5c%22wc%5c%22%3a0%2c%5c%22is%5c%22%3a0%2c%5c%22lb%5c%22%3a0%2c%5c%22to%5c%22%3a0%2c%5c%22dt%5c%22%3a0%2c%5c%22rhr%5c%22%3a0%2c%5c%22ss%5c%22%3a0%7d%2c%5c%22stp%5c%22%3a%7b%5c%22ttl%5c%22%3a%7bsteps%7d%2c%5c%22dis%5c%22%3a0%2c%5c%22cal%5c%22%3a0%2c%5c%22wk%5c%22%3a0%2c%5c%22rn%5c%22%3a0%2c%5c%22runDist%5c%22%3a0%2c%5c%22runCal%5c%22%3a0%2c%5c%22stage%5c%22%3a%5b%5d%7d%2c%5c%22goal%5c%22%3a0%2c%5c%22tz%5c%22%3a%5c%2228800%5c%22%7d%22%2c%22source%22%3a24%2c%22type%22%3a0%7d%5d"
  
    headers0 = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "MiFit/6.12.0 (MCE16; Android 16; Density/1.5)",
        "app_name": "com.xiaomi.hm.health",
        "apptoken": app_token,
    }
    url0 = f"https://api-mifit-cn.huami.com/v1/data/band_data.json?&t={timestamp}"
    data0 = f"userid={user_id}&last_sync_data_time={seconds}&device_type=0&last_deviceid={deviceID}&data_json={dataJSON}"
    
    try:
        res0 = requests.post(url0, data=data0, headers=headers0)
        res0_data = res0.json()
        print(f"账号：{account} 步数：{steps} 提交结果：{res0_data}")
        return True
    except Exception as e:
        print(f"提交步数失败：{e}")
        return False

def get_timestamp():
    """通过中国授时中心 NTP 服务器获取时间戳"""
    try:
        NTP_SERVER = 'ntp.ntsc.ac.cn'
        PORT = 123
        NTP_FORMAT = '!12I'
        NTP_DELTA = 2208988800
        
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(5)
        
        data = bytearray(48)
        data[0] = 0x1B
        
        client.sendto(data, (NTP_SERVER, PORT))
        data, address = client.recvfrom(1024)
        
        if data:
            unpacked = struct.unpack(NTP_FORMAT, data[:48])
            timestamp = unpacked[10] - NTP_DELTA
            return float(timestamp)
        
        return None
        
    except socket.timeout:
        print("错误:连接 NTP 服务器超时")
        return None
    except socket.gaierror:
        print("错误:无法解析 NTP 服务器地址")
        return None
    except Exception as e:
        print(f"错误:获取时间戳失败 - {e}")
        return None
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    # 从环境变量获取账号密码
    ACCOUNT = os.environ.get("ACCOUNT", "")
    PASSWORD = os.environ.get("PASSWORD", "")
    
    # 随机步数范围
    RandomMin = 25000
    RandomMax = 55000
    
    # 账号配置：每个账号可以设置固定步数或使用随机范围
    account = [
        [ACCOUNT, PASSWORD, None],  # None表示使用随机步数
        #['账号2', '密码2', None],   # 使用随机步数
        #['账号3', '密码3', 45000],  # 固定步数45000
    ]
    
    for i in account:
        account_name = i[0]
        password = i[1]
        step = i[2]
        
        # 如果步数为None则使用随机步数
        if step is None:
            step = random.randint(RandomMin, RandomMax)
            print(f"账号 {account_name} 使用随机步数: {step}")
        else:
            print(f"账号 {account_name} 使用固定步数: {step}")
        
        # 登录获取token
        login_token, userid = login(account_name, password)
        if not login_token:
            print(f'账号 {account_name} 登录失败')
            continue
        
        # 获取app_token
        app_token = get_app_token(login_token)
        if not app_token:
            print(f'账号 {account_name} 获取app_token失败')
            continue
        
        # 修改步数
        result = change_steps(account_name, userid, app_token, str(step))
        if result:
            print(f'账号 {account_name} 步数修改成功')
        else:
            print(f'账号 {account_name} 步数修改失败')
        
        print("-" * 50)
