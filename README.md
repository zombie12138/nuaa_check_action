# ⏳i南航自动打卡

## Description

- **多人打卡，一人设置，全家👨‍👨‍👦‍👦享福**
- **校外校外，一站打卡**
- **基于GitHub Action**
- **邮箱通知📧**

**免责声明：本项目仅仅可以学习研究，请遵守校内纪律和相关法规。如果出现信息错误等后果概不负责。**

本项目以 MIT 协议开源，详情请见 [LICENSE](./LICENSE) 文件。

有问题或发现错误可以提出issue与我🤺。

## Q&A

**Q:** 打卡的默认选项是什么?  
**A:** 默认选项为一切正常并且素康🐎为绿色💚，从浏览器抓的包，想自己抓用Fiddler或者BurpSuite。可以通过访问打卡页面获取之前的选项，但是太懒了，还没有做。

校外打卡参数如下
![options](./pic/options.png)

**Q:** 哪个网页里抓的包？  
**A:** <https://m.nuaa.edu.cn/ncov/wap/default>，校外打卡；<https://m.nuaa.edu.cn/ncov/wap/nuaa/index>，校内打卡。其中位置信息从<https://restapi.amap.com/v3/geocode/regeo?key=729923f88542d91590470f613adb27b5&s=rsv3&location=经度,纬度>获取。

**Q:** 为什么要用邮箱通知而不用Server酱之类的？  
**A:** 因为室友们实在太懒了，而且发给QQ邮箱效果也不错。

**Q:** 为什么要使用Github Action？  
**A:** 我也感觉如果用于打卡的话确实不好用。

**Q:** 我如何知道自己的经纬度？  
**A:** 由于上报定位使用高德地图的API，建议使用高德坐标拾取器更加准确<https://lbs.amap.com/console/show/picker>, 得到的是`经度,纬度`(比较大的是经度)。如果你是校内打卡，可以直接通过选择校区设置：将军路校区使用的是`118.791946,31.938129`，明故宫使用的是`118.820824,32.03514`，天目湖使用的是`119.481185,31.373404`。

## Usage

### Step.0 网页打卡检验一下

浏览器访问<https://m.nuaa.edu.cn/ncov/wap/nuaa/index>，登录进行打卡。其一是检验自己的账号密码是否正确，另外也有同学反应如果不网页打一次卡，脚本打卡过程中可能无法获取uid（尽管他不那么重要）

### Step.1 Fork

点击右上角Fork，Fork至自己的仓库

![fork](./pic/fork.png)

### Step.2 设置Secrets

设置Secrets，新建secret字段 **config**

![set_secret](./pic/set_secret.gif)

这是一个代表打卡信息的Json，

字段说明

|  KEY   | 类型 | 作用  |
|  ---  | --- | ---  |
| mail_sender  | 字符串 | 使用该邮件地址发送邮件提醒（如果所有人都不接受邮件可以不写） |
| smtp_password  | 字符串 | 邮件smtp的密码，不同于邮箱密码，请登录邮箱进行设置（如果所有人都不接受邮件可以不写） |
|  students  | 数组 |  收件人列表，可以一人或多人，每一项可包含下面字段  |
|  stu_number  | 字符串 |  打卡学生的学生学号  |
|  password  | 字符串 | 打卡学生教务密码  |
|  mail  | 字符串 | 打卡学生的收信箱，用于接收打卡提示（不写则不接收）  |
|  latitude  | 浮点数 | 纬度，通过高德地图获取的，具体获取见QA(如果你校内打卡且使用了campus，则不需要设置)  |
|  longitude  | 浮点数 | 经度，通过高德地图获取的，具体获取见QA(如果你校内打卡且使用了campus，则不需要设置)  |
|  in_school  | 布尔值 | 是否在校，**不设置的话，默认不在校** |
|  campus  |字符串| 校内打卡的校区，仅在in_school为true时候生效，值应为"mgg"、"tmh"或"jjl",对应明故宫、天目湖、将军路校区 |
| disable_id_uid |布尔值| 一般不设置。如果出现无法获得id uid的问题，可以使用这个参数并设置为true |

举个🌰吧叭

`082010101`校内打卡接收邮件，自己指定经纬度;`082010103`不接收邮件，校内打卡，使用将军路校区的纬度

``` json
{
    "mail_sender": "666666@qq.com",
    "smtp_password": "aaaaaaaaaaaaaaaa",
    "smtp_host": "smtp.qq.com",
    "students": [
        {
            "stu_number": "082010101",
            "password": "St13456",
            "mail": "666666@qq.com",
            "in_school": true,
            "latitude": 31.938129,
            "longitude":118.791946
        },
        {
            "stu_number": "082010103",
            "password": "St13456",
            "in_school": true,
            "campus": "jjl"
        }
    ]
}
```

下面的🌰中，都不会收到邮件。 `082010101`未设置`in_school` 默认校外打卡，由于无法获取uid故设置了`disable_id_uid`(没看明白可以忽略，一般不需要设置这个); `082010103`校内打卡，使用将军路校区默认经纬度

``` json
{
    "students": [
        {
            "stu_number": "082010101",
            "password": "St13456",
            "latitude": 39.5655665,
            "longitude":114.0484894,
            "disable_id_uid": true
        },
        {
            "stu_number": "082010103",
            "password": "St13456",
            "in_school": true,
            "campus": "jjl"
        }
    ]
}
```

QQ邮箱smtp密码获取如下：

![smtp1](./pic/smtp1.png)
然后下面选择开启pop3/smtp服务，得到smtp密码
![smtp2](./pic/smtp2.png)

### Step.3 开启Action

点击你的项目中的Action，开启Action；然后选择Check，点击`enable workflow`

![enable action](./pic/enable_action.gif)

### Step.4 测试

push打卡测试一下
![test1](./pic/test1.png)
![test2](./pic/test2.png)

如果成功就可以每天00：00打卡（准确时间会是00：23左右，任务会有的延迟）🌶

## Advancement

### 修改打卡时间

修改[python-app.yml](./.github/workflows/python-app.yml)的cron（具体设置方法可以使用搜索引擎搜索）
