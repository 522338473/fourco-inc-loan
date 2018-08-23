HOME_HOST = 'test.fourcoloan.home.ptteng.com/login'
HOME_HOST_ONLINE = 'zd.fourco-inc.com/login'
PARAMS = '?source={source}&sub={sub}&template={template}'
TEST_MODEL = False


def smsTemplate(string):
    return '【360贷款】您的验证码为' + string + ',请在10分钟内填写。'


class constant:
    code = {
        0: 'success',
        -1: '未填写个人资料',
        -2: '密码错误',
        -10: '参数缺失',
        -20: '未登录',
        -30: '数据不存在',
        -40: '名字已存在',
        -50: '当前账户无此权限',
        -60: '改角色下有关联账号，请取消关联后操作',
        -1000: '请输入正确的手机号',
        -1001: '短信发送失败',
        -1002: '您今日发送短信验证码已到达上限，请明日再试',
        -1003: '验证码已发送，请1分钟后再试',
        -1004: '验证码不正确',
        -1004: '验证码不正确',
        -1005: '验证码已过期，请重新获取',
        -1041: '产品名称已存在',
        -1042: 'url或者rate不能为空',
        -1043: '产品类型为空',
        -1044: '产品未配置',
        -1050: '媒介名称已存在',
        -1051: '请求方法应该是GET',
        -1052: '请求方法应该是POST',
        -1053: '请求方法应该是DELETE',
        -10000: '服务器出现问题，请稍后再试'

    }
    key = 'ptteng.com'
    smsAccout = 'bjsgyz-1'
    smsPwd = '0f8e84'

    smsUrl = 'http://sms.800617.com:4400/sms/SendSMS.aspx'

    zdAPI = 'http://www.bankexx.com.cn/member/add'
    userContent = {
        'estate': {
            1: '有房', 2: '有房有贷', 3: '无房'
        },
        'car': {
            1: '有车', 2: '有车有贷', 3: '无车'
        },
        'card': {
            1: '有信用卡', 2: '无信用卡'
        },
        'lifeInsurance': {
            1: '有保险', 2: '无保险'
        },
        'feeInsurance': {
            1: '不足2400', 2: '大于2400'
        },
        'livingTime': {
            1: '不足6个月', 2: '6个月以上'
        },
        'profession': {
            1: '白领', 2: '公务员', 3: '私企'
        },
    }

