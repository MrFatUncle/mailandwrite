import time
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib
import random
import smtplib
import sys
from email.mime.text import MIMEText

# 输入邮件地址, 口令和POP3服务器地址:
# email = input('Email: ')
# password = input('Password: ')
# pop3_server = input('POP3 server: ')

# 新浪邮箱测试通过, 密码使用登陆密码
# email = "18937905850@sina.cn"
# password = "password"
# pop3_server = "pop.sina.cn"


# qq邮箱测试通过， 使用授权码， 使用ssl
# email = "bestfuture25@qq.com"
# password = "titeexrfwjutbhhg"
# pop3_server = "pop.qq.com"


class Email:
    # 验证码
    code = "123456"
    # 总计接收30分钟
    total_receive_minutes = 30

    def __init__(self, account, mail_postfix, password, pop3_server, smtp_server, target_email, subject, info, model):
        self.account = account
        self.password = password
        self.pop3_server = pop3_server
        self.smtp_server = smtp_server
        self.target_email = target_email
        self.info = info
        self.subject = subject
        self.mail_postfix = mail_postfix
        self.model = model

    def guess_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    def decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def print_info(self, msg, indent=0):
        if indent == 0:
            for header in ['From', 'To', 'Subject']:
                value = msg.get(header, '')
                if value:
                    if header == 'Subject':
                        value = self.decode_str(value)
                    else:
                        hdr, addr = parseaddr(value)
                        name = self.decode_str(hdr)
                        value = u'%s <%s>' % (name, addr)
                print('%s%s: %s' % ('  ' * indent, header, value))
        if (msg.is_multipart()):
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                print('%spart %s' % ('  ' * indent, n))
                print('%s--------------------' % ('  ' * indent))
                self.print_info(part, indent + 1)
        else:
            content_type = msg.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                content = msg.get_payload(decode=True)
                charset = self.guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                print('%sText: %s' % ('  ' * indent, content + '...'))
            else:
                print('%sAttachment: %s' % ('  ' * indent, content_type))

    def main(self):
        # send_server = self.mail_send_server()
        receive_server = self.mail_receive_server()
        # self.send_mail(send_server)
        # send_server.close()
        # 收邮件并检查code
        result = self.receive_check(receive_server)
        if result:
            print("check mail success")
        receive_server.quit()

    def receive_mail(self, server, receive_index):

        # stat()返回邮件数量和占用空间:
        print('Messages: %s. Size: %s' % server.stat())
        # list()返回所有邮件的编号:
        resp, mails, octets = server.list()
        # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
        print(mails)
        # 获取最新一封邮件, 注意索引号从1开始:
        index = len(mails)
        if len(mails) < 1:
            return "none"
        if len(mails) < receive_index:
            return "index out of range"
        resp, lines, octets = server.retr(index)
        # lines存储了邮件的原始文本的每一行,
        # 可以获得整个邮件的原始文本:
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        # 稍后解析出邮件:
        msg = Parser().parsestr(msg_content)
        self.print_info(msg)
        # 可以根据邮件索引号直接从服务器删除邮件:
        # server.dele(index)
        # 关闭连接:
        return msg

    # 生成code并发送邮件
    def send_mail(self, server):

        code = self.model + "_" + self.range_code()
        code_info = "此次校验码为：" + code + "，请直接将此校验码回复即可。30分钟内有效"
        all_info = self.info + code_info
        # 生成code并发送
        me = self.account + "<" + self.account + "@" + self.mail_postfix + ">"
        msg = MIMEText(all_info)
        msg['Subject'] = self.subject
        msg['From'] = me
        msg['to'] = self.target_email
        server.sendmail(me, self.target_email, msg.as_string())

    def mail_receive_server(self):
        # 连接到POP3服务器:
        # server = poplib.POP3(pop3_server)
        # qq需要使用ssl
        server = poplib.POP3_SSL(pop3_server)
        # 可以打开或关闭调试信息:
        server.set_debuglevel(1)
        # 可选:打印POP3服务器的欢迎文字:
        print(server.getwelcome().decode('utf-8'))
        # 身份认证:
        server.user(account)
        server.pass_(password)
        return server

    def receive_check(self, server):
        # 每10秒收一次邮件
        first_msg = self.receive_mail_first(server)
        second = 0
        while self.receive_check(server):
            second += 10
            time.sleep(10)
            if second >= self.total_receive_minutes * 60:
                return False

        return True

    def receive_check(self, server):
        result = False

        for index in range(1, 6):
            receive_code = self.receive_mail(server, index)
            if receive_code == self.code:
                return True
        return result

    def receive_mail_first(self, server):
        first_msg = self.receive_mail(server, 1)
        return first_msg

    def range_code(self):
        code = ""
        for i in range(6):
            ch = chr(random.randrange(ord('0'), ord('9') + 1))
            code += ch
        self.code = code
        return code

    def mail_send_server(self):
        server = smtplib.SMTP_SSL(self.smtp_server)
        server.connect(self.smtp_server)
        server.login(self.account, self.password)
        return server


if __name__ == '__main__':
    smtp_server = 'smtp.qq.com'
    target_email = "123@qq.com"
    account = "123"
    mail_postfix = 'qq.com'
    password = "123"
    pop3_server = "pop.qq.com"
    Email(account, mail_postfix, password, pop3_server, smtp_server, target_email, sys.argv[1], sys.argv[2], sys.argv[3]).main()
