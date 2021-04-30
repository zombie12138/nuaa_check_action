# encoding=utf-8
import traceback
import re
import json
import sys
import time
import traceback
import requests
from send_mail import send_mail
# from requests_toolbelt.utils import dump

try_times = 1   # 失败这么多次后就直接不管了
delay = 2   # 访问页面前的延迟，为了防止过快访问网站被封IP


# 登陆并且返回json形式的cookie，如果登陆失败返回空串
# 先访问/uc/wap/login，获得eai-sess和UUkey，然后带着她访问/uc/wap/login/check
def login(stu_number, password):
    cookies = ''
    for _ in range(try_times):
        try:
            time.sleep(delay)
            response = requests.get(
                'https://m.nuaa.edu.cn/uc/wap/login', cookies=cookies)
            print('get login page:', response.status_code)

            # cookies = response.headers['Set-Cookie']
            # cookies = re.search(r'eai-sess=([a-zA-Z0-9]+)', cookies).group(0)
            cookies = dict(response.cookies)

            time.sleep(delay)
            response = requests.get('https://m.nuaa.edu.cn/uc/wap/login/check', cookies=cookies,
                                    data='username={}&password={}'.format(stu_number, password))
            print('login...:', response.status_code)

            # cookies2 = response.headers['Set-Cookie']
            # cookies = cookies + '; ' + \
            #     re.search(r'UUkey=([a-zA-Z0-9]+)', cookies2).group(0)
            cookies.update(dict(response.cookies))
            
            # print(cookies)
            print(response.text)
            return cookies, '登陆结果：' + response.text + '\n'
        except:
            print('login failed.')
            traceback.print_exc()
            pass
    # raise Exception('lOGIN FAIL')
    return {}, '登陆结果：login faild,请检查账号密码\n'

# longitude: 经度； latitude: 纬度
# 根据经纬度访问高德API，并且返回打卡时候“geo_api_info”字段的值
def get_address_info(longitude, latitude):
    for _ in range(try_times):
        try:
            time.sleep(delay)
            response = requests.get(
                'https://restapi.amap.com/v3/geocode/regeo', params={
                    'key': '729923f88542d91590470f613adb27b5',
                    's': 'rsv3',
                    'location': str(longitude) + ',' + str(latitude)
                })
            geo_data = json.loads(response.text)
            geo_data = geo_data['regeocode']
            geo_api_info = {
                "type": "complete",
                "position": {
                    "Q": latitude,
                    "R": longitude,
                    "lng": longitude,
                    "lat": latitude
                },
                "location_type": "html5",
                "message": "Get ipLocation failed.Get geolocation success.Convert Success.Get address success.",
                "accuracy": 102,    # ???
                "isConverted": True,    # ?
                "status": 1,
                "addressComponent": {
                    "citycode": geo_data['addressComponent']['citycode'],
                    "adcode": geo_data['addressComponent']['adcode'],
                    "businessAreas": [],
                    "neighborhoodType": "",
                    "neighborhood": "",
                    "building": "",
                    "buildingType": "",
                    "street": geo_data['addressComponent']['streetNumber']['street'],
                    "streetNumber": geo_data['addressComponent']["streetNumber"]['number'],
                    "country": geo_data['addressComponent']['country'],
                    "province": geo_data['addressComponent']['province'],
                    "city": geo_data['addressComponent']['city'],
                    "district": geo_data['addressComponent']['district'],
                    "township": geo_data['addressComponent']['township']
                },
                "formattedAddress": geo_data['formatted_address'],
                "roads": [],
                "crosses": [],
                "pois": [],
                "info": "SUCCESS"
            }
            return geo_api_info
        except:
            traceback.print_exc()
    return geo_api_info
    # print(dump.dump_all(response).decode('utf-8'))

def get_post_data(geo_api_info, in_school):
    my_province = geo_api_info['addressComponent']['province']
    my_city = geo_api_info['addressComponent']['city']
    my_district = geo_api_info['addressComponent']['district']
    my_address = geo_api_info['formattedAddress']
    # cities like Chongqing or Beijing do not have "city"
    # which makes my_city is equal to []
    # triggers error: must be str, not list
    if my_city == []:
        my_area = my_province + ' ' + my_district
    else:
        my_area = my_province + ' ' + my_city + ' ' + my_district

    if in_school:
        return {
            "sfzhux": "0",
            "zhuxdz": "",
            "szgj": "",
            "szcs": "",
            "szgjcs": "",
            "sfjwfh": "0",
            "sfyjsjwfh": "0",
            "sfjcjwfh": "0",
            "sflznjcjwfh": "0",
            "sflqjkm": "0",
            "jkmys": "0",
            "sfjtgfxdq": "0",
            'address': my_address,
            'geo_api_info': json.dumps(geo_api_info, separators=(',', ':')),
            'area': my_area,
            'province': my_province,
            'city': my_city,
            "fxzrwjtw": "",
            "fxjrcjtw": "1",
            "fxjrzjtw": "",
            "sfzx": "1",    # 是否在校
            "sfcyglq": "0",
            "sfcxtz": "0",
            "sftjwz": "0",
            "sftjhb": "0",
            "sfjcwhry": "0",
            "sfjchbry": "0"
        }
    else:
        return {
            # 待跟新
            'sfzhux': '0',      # 是否住校
            'zhuxdz': '',       # 住校地址
            'szgj': '',         # 所在国家
            'szcs': '',         # 所在城市
            'szgjcs': '',       # 所在国家城市
            'sfjwfh': '0',      # 今日是否从境外中高风险地区返回？
            'sfyjsjwfh': '0',   # 今日是否有家属从境外中高风险地区返回？
            'sfjcjwfh': '0',    # 是否接触境外返华
            'sflznjcjwfh': '0',  # 今日是否与从境外中高风险地区返回的人员有过密切接触（不含已经解除隔离的境外返回人员）？
            'sflqjkm': '4',     # 是否拥有苏康码？
            'jkmys': '1',       # 当前苏康码颜色是？
            'sfjtgfxdq': '0',   # 今日是否到过或者经停中高风险地区？
            'tw': '2',          # 今日体温范围
            'sfcxtz': '0',      # 今日是否出现发热、乏力、干咳、呼吸困难等症状？
            'sfjcbh': '0',      # 今日是否接触疑似/确诊人群？
            'sfcxzysx': '0',
            'qksm': '',         # 情况说明
            'sfyyjc': '0',      # 是否到相关医院或门诊检查？
            'jcjgqr': '0',      # 检查结果属于以下哪种情况
            'remark': '',
            'address': my_address,
            'geo_api_info': json.dumps(geo_api_info, separators=(',', ':')),
            'area': my_area,
            'province': my_province,
            'city': my_city,
            'sfzx': '0',        # 今日是否在校？
            'sfjcwhry': '0',    # 今日是否与来自武汉市的人员有过密切接触？
            'sfjchbry': '0',    # 今日是否与来自湖北其他地区（不含武汉市）的人员有过密切接触？
            'sfcyglq': '0',     # 是否处于隔离期/医学观察期（含特殊情况需要居家观察的）？
            'gllx': '',         # 隔离/医学观察场所
            'glksrq': '',       # 隔离/医学观察开始时间
            'jcbhlx': '',       # 接触人群类型
            'jcbhrq': '',       # 接触时间
            'bztcyy': '',       # 当前地点与上次不在同一城市，原因如下
            'sftjhb': '0',      # 今日是否到过或者经停湖北其他地区（除武汉）？
            'sftjwh': '0',      # 今日是否到过武汉（交通工具经停、人没有下车不算）？
            'sftjwz': '0',      # 今日是否到过或者经停温州？
            'sfjcwzry': '0',    # 今日是否与来自温州市的人员有过密切接触？
            'jcjg': '',         # 检测结果
            'date': time.strftime("%Y%m%d", time.localtime()),  # 打卡年月日一共8位
            # 'uid': uid,  # UID
            # 'created': round(time.time()),  # 时间戳
            'jcqzrq': '',
            'sfjcqz': '',
            'szsqsfybl': '0',
            'sfsqhzjkk': '0',
            'sqhzjkkys': '',
            'sfygtjzzfj': '0',
            'gtjzzfjsj': '',
            'created_uid': '0',
            # 'id': id,  # 打卡的ID，其实这个没影响的
            'gwszdd': '',
            'sfyqjzgc': '',
            'jrsfqzys': '',
            'jrsfqzfy': '',
            'ismoved': '0'
        }


# 签到，返回True成功，否则失败
def check(cookies, geo_api_info, in_school):
    data = get_post_data(geo_api_info, in_school)
    if in_school:
        url = 'https://m.nuaa.edu.cn/ncov/wap/nuaa/save'
    else:
        url = 'https://m.nuaa.edu.cn/ncov/wap/default/save'
    msg =  "校内打卡: " if in_school else "校外打卡: "
    msg += '\n' + '位置：' + geo_api_info['formattedAddress'] + '\n'
    for _ in range(try_times):
        try:
            time.sleep(delay)
            
            response = requests.post(url, data=data, cookies=cookies)
            print('sign statue code:', response.status_code)

            response.encoding = 'utf-8'

            if response.text.find('成功') >= 0:
                print('打卡成功')
                msg += '打卡成功' + '\n'
                return True, msg
            else:
                print('打卡失败')
        except:
            traceback.print_exc()
    msg += '打卡成功' + '\n'
    return False, msg


def send_result(config, recever, result, messgae):
    mail_sender = config['mail_sender']
    smtp_password = config['smtp_password']
    smtp_host = config['smtp_host']
    if result == True:
        send_mail(mail_sender, smtp_password, smtp_host,
                  recever, messgae, '打卡成功', '主人', '打卡姬')
    else:
        send_mail(mail_sender, smtp_password, smtp_host,
                  recever, messgae, '打卡失败', '主人', '打卡姬')

def main():
    try:
        config = sys.stdin.read()
        config = json.loads(config)
    except:
        print('Json配置错误')
        return

    for student in config['students']:
        result = False  # 打卡结果，False表示没有打上
        stu_number = student['stu_number']
        password = student['password']
        # 默认布在校
        in_school = False if 'in_school' not in student else student['in_school']
        if in_school and 'campus' in student:
            # 通过校区设置经纬度
            campus_dict = {'mgg': (118.820824, 32.03514),
                           'tmh': (119.481185, 31.373404),
                           'jjl': (118.791946, 31.938129)}
            longitude, latitude = campus_dict[student['campus']]   
        else:
            longitude = student['longitude']
            latitude = student['latitude']
        mail = '' if 'mail' not in student else student['mail']
        
        message = ''
        message1 = ''
        print('--------------------------------------')
        try:
            cookies, message = login(stu_number, password)
            geo_api_info = get_address_info(longitude, latitude)
            result, message1 = check(cookies, geo_api_info, in_school)
            message += message1
        except:
            print('发生异常')
            message += '发生异常'
        if mail != '':
            send_result(config, mail, result, message)


if __name__ == '__main__':
    main()
