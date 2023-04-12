from app.home.target.models import Blacklist
from app.home.domain.models import Domain
from app.home.subdomain.models import Subdomain
from app.home.port.models import Port
from app.home.http.models import Http
from app.home.dirb.models import Dirb
from app.home.vuln.models import Vuln
from app.home.utils import *
import time
from app import db
import IPy
import re
import xlwt

#保存域名
def savedomain(domain_name, id, current_user):
    domain_list = domain_name.split('\r\n')
    for i in domain_list:
        if(Domain.query.filter(Domain.domain_name == i).count() > 0):
            continue
        if(i.strip() == ''):
            continue
        domain = Domain()
        domain.domain_name = i.strip()
        domain.domain_target = id
        domain.domain_subdomain_status = False
        domain.domain_user = str(current_user)
        domain.domain_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
        db.session.add(domain)
        db.session.commit()
    return 

#保存黑名单
def saveblacklist(black_name, id):
    black_list = black_name.split('\r\n')
    for i in black_list:
        if(Blacklist.query.filter(Blacklist.black_name == i).count() > 0):
            continue
        if i == '':
            pass
        if(i.strip()):
            blacklist = Blacklist()
            blacklist.black_name = i.strip()
            blacklist.black_target = id
            blacklist.black_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
            db.session.add(blacklist)
            db.session.commit()
            blacklist_remove(i,id)
    return

#保存精准域名或ip信息
def savesubdomain(subdomain_name, id, current_user):
    subdomain_list = subdomain_name.split('\r\n')
    for i in subdomain_list:
        isdomain = re.search( r'[a-zA-Z]', i)
        if(isdomain):
            try:
                subdomain = Subdomain()
                subdomain.subdomain_name = i.strip()
                subdomain.subdomain_target = id
                subdomain.subdomain_http_status = False
                subdomain.subdomain_port_status = False
                subdomain.subdomain_tool = "Add by user"
                subdomain.subdomain_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
                subdomain.subdomain_user = str(current_user)
                subdomain.subdomain_ip = "nothing"
                subdomain.subdomain_info = "nothing"
                subdomain.subdomain_new = 0
                db.session.add(subdomain)
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()
        else:
            saveip(i,id,current_user)

    return

#保存ip
def saveip(ip_name, id, current_user):
    subdomain_list = ip_name.split('\r\n')
    subdomain_last_list = []
    for i in subdomain_list:
        if("-" in i):
            try:
                subdomain_last_list += getip1(i)
            except Exception as e:
                print(e)
        elif("/" in i):
            try:
                subdomain_last_list = subdomain_last_list + getip2(i)
            except Exception as e:
                print(e)
        else:
            subdomain_last_list.append(i)
    for i in subdomain_last_list:
        i = str(i).strip()
        if(not i):
            continue
        #黑名单过滤
        if(black_list_query(id, '', i)):
            continue
        i = i.replace("'","\'")
        try:
            subdomain = Subdomain()
            subdomain.subdomain_name = i
            subdomain.subdomain_target = id
            subdomain.subdomain_http_status = False
            subdomain.subdomain_port_status = False
            subdomain.subdomain_tool = "Add by user"
            subdomain.subdomain_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
            subdomain.subdomain_user = str(current_user)
            subdomain.subdomain_ip = i
            subdomain.subdomain_info = "UNKNOW"
            subdomain.subdomain_new = 0
            db.session.add(subdomain)
            db.session.commit()
        except Exception as e:
                print(e)
                db.session.rollback()
    return

#删除属于添加黑名单的信息(有待完善)
def blacklist_remove(black, target_id):
    if("domain:" in black):
        b = black.split("domain:")[1]
        try:
            result = Subdomain.query.filter(Subdomain.subdomain_name.like("{}".format(b)), Subdomain.subdomain_target == target_id).all()
            [db.session.delete(r) for r in result]
            result = Port.query.filter(Port.port_domain.like("{}".format(b)), Port.port_target == target_id).all()
            [db.session.delete(r) for r in result]
            result = Http.query.filter(Http.http_name.like("{}".format(b)), Http.http_target == target_id).all()
            [db.session.delete(r) for r in result]
            result = Dirb.query.filter(Dirb.dir_base.like("{}".format(b)), Dirb.dir_target == target_id).all()
            [db.session.delete(r) for r in result]
            result = Vuln.query.filter(Vuln.vuln_name.like("{}".format(b)), Vuln.vuln_target == target_id).all()
            [db.session.delete(r) for r in result]
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
    if("ip:" in black):
        b = black.split("ip:")[1]
        try:
            result = Subdomain.query.filter(Subdomain.subdomain_ip.like("%{}%".format(b)), Subdomain.subdomain_target == target_id).all()
            [db.session.delete(r) for r in result]
            result = Port.query.filter(Port.port_ip.like("%{}%".format(b)), Port.port_target == target_id).all()
            [db.session.delete(r) for r in result]
            result = Http.query.filter(Http.http_name.like("%{}%".format(b)), Http.http_target == target_id).all()
            [db.session.delete(r) for r in result]
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
    if("title:" in black):
        b = black.split("title:")[1]
        try:
            result = Http.query.filter(Http.http_title.like("%{}%".format(b)), Http.http_target == target_id).all()
            [db.session.delete(r) for r in result]
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()



#获取/24带子网掩码的ip
def getip2(ips):
    ip = IPy.IP(ips)
    return list(ip)

#获取带-的ip列表
def getip1(ip):
    last = ""
    test = ip.split('.')
    zone = []
    result = []
    count = 0
    for i in test:
        if("-" not in i):
            last = last + i + '.'
        if("-" in i):
            last = last + 'temp' + str(count) + '.'
            zone.append(int(i.split("-")[0]))
            zone.append(int(i.split("-")[1]))
            count = count + 1

    last = last[:-1]

    if len(zone) == 2: 
        for i in range(zone[0], zone[1] + 1):
            result.append(last.replace("temp0", str(i)))

    if len(zone) == 4:
        for i in range(zone[0], zone[1] + 1):
            for j in range(zone[2], zone[3] + 1):
                temp = last.replace("temp0", str(i))
                temp = temp.replace("temp1", str(j))
                result.append(temp)

    if len(zone) == 6:
        for i in range(zone[0], zone[1] + 1):
            for j in range(zone[2], zone[3] + 1):
                for k in range(zone[4], zone[5] + 1):
                    temp = last.replace("temp0", str(i))
                    temp = temp.replace("temp1", str(j))
                    temp = temp.replace("temp2", str(k))
                    result.append(temp)

    if len(zone) == 8:
        for i in range(zone[0], zone[1] + 1):
            for j in range(zone[2], zone[3] + 1):
                for k in range(zone[4], zone[5] + 1):
                    for v in range(zone[6], zone[7] + 1):
                        temp = last.replace("temp0", str(i))
                        temp = temp.replace("temp1", str(j))
                        temp = temp.replace("temp2", str(k))
                        temp = temp.replace("temp3", str(v))
                        result.append(temp)
    return result


def ip_addr(id):
    dic = {}
    sub = db.session.query(Subdomain.subdomain_ip).filter(Subdomain.subdomain_target == id).all()
    for ip in sub:
        ip = queryToDict(ip)['subdomain_ip']
        if(',' in ip):
            continue
        ip = '.'.join(ip.split('.')[:-1])
        if ip not in dic:
            dic[ip] = 1
        else:
            dic[ip] = dic[ip] + 1

    # for i in len(dic):
    #     for j in i + 1:
    #         if(dic)

    return sorted(dic.items(), key = lambda kv:(kv[1], kv[0]), reverse = True)


#导出Excel
def output_excel(target_id):
    style = xlwt.easyxf('font: bold on')
    output_file = "/tmp/扫描结果.xls"
    workbook = xlwt.Workbook()
    # sheet_doamin = workbook.add_sheet('主域名',cell_overwrite_ok=True)
    sheet_subdoamin = workbook.add_sheet('子域名',cell_overwrite_ok=True)
    sheet_port = workbook.add_sheet('端口',cell_overwrite_ok=True)
    sheet_url = workbook.add_sheet('站点',cell_overwrite_ok=True)
    sheet_dirb = workbook.add_sheet('目录',cell_overwrite_ok=True)
    sheet_vuln = workbook.add_sheet('漏洞',cell_overwrite_ok=True)
    # sheet_doamin.write(0,0,'主域名',style)
    # sheet_doamin.col(1).width = 256 * 15
    # sheet_doamin.write(0,1,'采集时间',style)
    # sheet_doamin.col(1).width = 256 * 20
    sheet_subdoamin.write(0,0,'子域名',style)
    sheet_subdoamin.col(0).width = 256 * 35
    # sheet_subdoamin.write(0,1,'ip',style)
    # sheet_subdoamin.col(1).width = 256 * 50
    # sheet_subdoamin.write(0,2,'解析',style)
    # sheet_subdoamin.col(2).width = 256 * 10
    sheet_subdoamin.write(0,3,'时间',style)
    sheet_subdoamin.col(3).width = 256 * 20
    sheet_port.write(0,0,'域名',style)
    sheet_port.col(0).width = 256 * 35
    sheet_port.write(0,1,'ip',style)
    sheet_port.col(1).width = 256 * 18
    sheet_port.write(0,2,'端口',style)
    sheet_port.col(2).width = 256 * 10
    sheet_port.write(0,3,'服务',style)
    sheet_port.col(3).width = 256 * 15
    sheet_port.write(0,4,'时间',style)
    sheet_port.col(4).width = 256 * 20
    sheet_url.write(0,0,'web',style)
    sheet_url.col(0).width = 256 * 60
    # sheet_url.write(0,1,'标题',style)
    # sheet_url.col(1).width = 256 * 30
    # sheet_url.write(0,2,'响应码',style)
    # sheet_url.col(2).width = 256 * 10
    sheet_url.write(0,3,'长度',style)
    sheet_url.col(3).width = 256 * 10
    sheet_url.write(0,4,'指纹',style)
    sheet_url.col(4).width = 256 * 30
    sheet_url.write(0,5,'时间',style)
    sheet_url.col(5).width = 256 * 20
    sheet_dirb.write(0,0,'目标',style)
    sheet_dirb.col(0).width = 256 * 60
    # sheet_dirb.write(0,1,'标题',style)
    # sheet_dirb.col(1).width = 256 * 30
    sheet_dirb.write(0,2,'响应',style)
    sheet_dirb.col(2).width = 256 * 10
    # sheet_dirb.write(0,3,'长度',style)
    # sheet_dirb.col(3).width = 256 * 10
    sheet_dirb.write(0,4,'时间',style)
    sheet_dirb.col(4).width = 256 * 20
    sheet_vuln.write(0,0,'漏洞等级',style)
    sheet_vuln.write(0,1,'漏洞名',style)
    sheet_vuln.col(1).width = 256 * 30
    sheet_vuln.write(0,2,'漏洞POC',style)
    sheet_vuln.col(2).width = 256 * 60
    sheet_vuln.write(0,3,'时间',style)
    sheet_vuln.col(3).width = 256 * 20
    
    # row = 1
    # for domain_info in Domain.query.filter(Domain.domain_target == target_id).all():
    #     sheet_doamin.write(row,0,domain_info.domain_name)
    #     sheet_doamin.write(row,1,domain_info.domain_time)
    #     row = row + 1
    row = 1
    for subdomain_info in Subdomain.query.filter(Subdomain.subdomain_target == target_id).all():
        sheet_subdoamin.write(row,0,subdomain_info.subdomain_name)
        sheet_subdoamin.write(row,1,subdomain_info.subdomain_ip)
        sheet_subdoamin.write(row,2,subdomain_info.subdomain_info)
        sheet_subdoamin.write(row,3,subdomain_info.subdomain_time)
        row = row + 1
    row = 1
    for port_info in Port.query.filter(Port.port_target == target_id).all():
        sheet_port.write(row,0,port_info.port_domain)
        sheet_port.write(row,1,port_info.port_ip)
        sheet_port.write(row,2,port_info.port_port)
        sheet_port.write(row,3,port_info.port_server)
        sheet_port.write(row,4,port_info.port_time)
        row = row + 1
    row = 1
    for url_info in Http.query.filter(Http.http_target == target_id).all():
        sheet_url.write(row,0,url_info.http_schema + "://" + url_info.http_name)
        sheet_url.write(row,1,url_info.http_title)
        sheet_url.write(row,2,url_info.http_status)
        sheet_url.write(row,3,url_info.http_length)
        sheet_url.write(row,4,url_info.http_finger)
        sheet_url.write(row,5,url_info.http_time)
        row = row + 1
    row = 1
    for dirb_info in Dirb.query.filter(Dirb.dir_target == target_id).all():
        sheet_dirb.write(row,0,dirb_info.dir_base)
        sheet_dirb.write(row,1,dirb_info.dir_title)
        sheet_dirb.write(row,2,dirb_info.dir_status)
        sheet_dirb.write(row,3,dirb_info.dir_length)
        sheet_dirb.write(row,4,dirb_info.dir_time)
        row = row + 1
    row = 1
    for vuln_info in Vuln.query.filter(Vuln.vuln_target == target_id).all():
        sheet_vuln.write(row,0,vuln_info.vuln_level)
        sheet_vuln.write(row,1,vuln_info.vuln_info)
        sheet_vuln.write(row,2,vuln_info.vuln_poc)
        sheet_vuln.write(row,3,vuln_info.vuln_time)
        row = row + 1
    
    workbook.save(output_file)
    