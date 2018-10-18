# -*- coding: utf-8 -*-
import paramiko
import os
import time
import re
import sys
from settings import login_config

reload(sys)
sys.setdefaultencoding('utf-8')


# 通过密钥登陆服务器
def login_server_by_rsa():
    try:
        server_ssh = paramiko.SSHClient()
        server_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(login_config["keypath"])
        server_ssh.connect(hostname=login_config["hostip"],
                           port=login_config["hostport"],
                           username=login_config["username"],
                           pkey=pkey)
        return server_ssh
    except Exception, e:
        print e


# 通过密码登陆服务器
def login_server_by_pwd():
    try:
        server_ssh = paramiko.SSHClient()
        server_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print login_config["username"]
        server_ssh.connect(hostname=login_config["hostip"],
                           port=login_config["hostport"],
                           username=login_config["username"],
                           password=login_config["userpwd"])
        return server_ssh
    except Exception, e:
        print e


# 获得root权限
def authenticating_channel(login_ssh):
    channel = login_ssh.invoke_shell()
    try:
        print '............Authenticating............'
        channel.send("su %s\n" % login_config["rootusr"])
        buff = ''
        while not buff.endswith('Password: '):
            resp = channel.recv(10000)
            buff += resp
        print buff
        channel.send("%s\n" % login_config["rootpwd"])
        buff = ''
        while not buff.endswith('# '):
            resp = channel.recv(10000)
            buff += resp
        print buff
    except Exception, e:
        print e
        channel.close()
        login_ssh.close()
    return channel


# 获取服务器时间
def get_server_time():
    ssh = login_server_by_pwd()
    stdin, stdout, stderr = ssh.exec_command('date +%Y-%m-%d\ %H:%M:%S')
    servertime = stdout.read()
    ssh.close()
    return servertime


# 重置服务器时间
def restore_server_time():
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    modify_server_time(local_time)


# 修改服务器时间
def modify_server_time(newtime):
    ssh = login_server_by_pwd()
    channel = authenticating_channel(ssh)
    print '............Sending ModifyTime Commander............'
    channel.send("date -s \"%s\" \n" % newtime)
    buff = ''
    while not buff.endswith('# '):
        resp = channel.recv(10000)
        buff += resp
    print buff.decode('utf-8')
    ssh.close()


# 获取文件配置
def get_serverconfig_lists():
    ssh = login_server_by_pwd()
    # execute command
    stdin, stdout, stderr = ssh.exec_command(
        'ls -lR /home/configs/ |  grep ^- | awk \'{ print $9 }\'')
    file_list = stdout.read().split("\n")[:-1]
    return file_list


# 读取配置
def read_serverconfig(filename):
    ssh = login_server_by_pwd()
    # execute command
    try:
        stdin, stdout, stderr = ssh.exec_command(
            'cd /home/configs/; find \"$PWD\" -name ' + filename + ' | xargs cat')
        read = stdout.read().decode('utf-8')
        return read
    except Exception, e:
        print e


# 删除配置文件
def delete_config(filename):
    ssh = login_server_by_pwd()
    # delete config
    channel = authenticating_channel(ssh)
    try:
        print '............Sending Delete Commander............'
        channel.send('cd /home/configs/; find \"$PWD\" -name ' + filename + ' | xargs rm \n')
        buff = ''
        while not buff.endswith('# '):
            resp = channel.recv(10000)
            buff += resp
        print buff
    except e:
        print e
        ssh.close()
    ssh.close()
    return 'Successful Delete'


# 重启某个进程，调用shell脚本
def rebootserver():
    ssh = login_server_by_pwd()
    channel = authenticating_channel(ssh)
    # reboot game server
    print '............Sending Reboot Commander............'
    channel.send("bash /home/reboot.sh restart; echo \"quit:$?\" \n")
    resp = ''
    while not resp.endswith('# '):
        resp = channel.recv(10000)
        print resp
        quit_num = re.findall("quit:(\d+)", resp, re.M)
        if len(quit_num) > 0:
            if quit_num[0] == '0':
                ssh.close()
                return "Successful Rebooted!"
            else:
                ssh.close()
                return "Unsuccessful Rebooted!"
    ssh.close()


# 修改配置文件
def generate_config_upload_file(filename, json_str):
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename).replace('\\', '/')
    # 登陆服务器
    ssh = login_server_by_pwd()
    # 获得配置文件所在的位置
    stdin, stdout, stderr = ssh.exec_command('cd /home/configs/; find \"$PWD\" -name ' + filename)
    to_path = stdout.read()
    # 本地产生一个json文件的配置
    with open(local_path, 'w') as config_file:
        config_file.write(json_str)
    # 上传配置文件
    my_server_path = "/home/configs/" + filename
    try:
        transport = ssh.get_transport()
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, my_server_path)
        os.remove(local_path)
    except Exception, e:
        print e
        ssh.close()
        os.remove(local_path)
        return 'Unsuccessful Upload'
    sftp.close()
    # 将文件从自己的项目文件夹转移到配置文件夹下
    #channel = authenticating_channel(ssh)
    #print '............Sending Upload Commander............'
    #channel.send("cp /home/configs/" + filename + " " + to_path + "\n")
    #buff = ''
    #while not buff.endswith('# '):
    #    resp = channel.recv(10000)
    #    buff += resp
    #print buff
    ssh.close()
    return 'Successful Upload'


# 获得服务器的日志
def get_filter_log(filter_list):
    ssh = login_server_by_pwd()
    # 筛选日志的时期
    filter_date = filter_list[1].replace('-', '')
    _filter_date = filter_list[1]
    # 筛选日志的时间
    filter_content = filter_list[0]
    # 筛选日志的时间范围
    time_range = filter_list[2]
    beg_time, end_time = re.findall("\d+", time_range)
    beg_time = int(beg_time)
    end_time = int(end_time)
    if beg_time > end_time:
        beg_time, end_time = end_time, beg_time
    # 根据首尾时间生成每个单独时间用于日志帅选
    time_list = ["%02d" % num for num in range(beg_time, end_time)]
    filter_time = ''
    # 可被Linux执行的命令行
    for _time in time_list:
        filter_time += (_filter_date + ' ' + _time + ':|')
    filter_time = filter_time[:-1]
    # 检查是否存在该天的日志
    stdin, stdout, stderr = ssh.exec_command('find /home/logs -name *' + filter_date + '*.txt')
    istxt = bool(len(stdout.read()))
    # 如果存在改天的日志
    if istxt:
        # 如果有需要进一步筛选内容
        if filter_content:
            filter_command = 'find /home/logs -name "*' \
                             + filter_date + '*.txt" | xargs cat | grep -E \'' \
                             + filter_time + '\' | grep -i ' + filter_content
        else:
            filter_command = 'find /home/logs -name "*' \
                             + filter_date + '*.txt" | xargs cat | grep -E \'' + filter_time + '\''
            print filter_command
        stdin, stdout, stderr = ssh.exec_command(filter_command)
        raw_log = stdout.read()
        log = re.findall("\[(.*?)\]\[(.*?)\],({.*})", raw_log)
        return log
