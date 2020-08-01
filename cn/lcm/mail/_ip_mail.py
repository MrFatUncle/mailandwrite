#!/usr/bin/python 
# -*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText
import sys

mail_host = 'smtp.qq.com'  # smtp地址如果不知可以百度如“163邮箱smtp地址”
mail_user = '******'  # 此账号密码是用来给人发送邮件的
mail_pass = '******'  # 此账号密码是用来给人发送邮件的
mail_postfix = 'qq.com'  # 邮箱地址，smtp地址删去smtp字符如“163.com”


def send_mail(to_list, subject, content):
    me = mail_user + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = me
    msg['to'] = to_list

    try:
        s = smtplib.SMTP_SSL(mail_host)
        s.connect(mail_host)
        s.login(mail_user, mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except Exception as e:
        print(str(e))
        return False


if __name__ == "__main__":
    send_mail(sys.argv[1], sys.argv[2], sys.argv[3])
