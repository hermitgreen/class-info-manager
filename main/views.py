from main.methods import *
import os
import requests
from sqlalchemy import extract, and_
from flask import jsonify, request, render_template, Blueprint


# 蓝图加载视图函数
blue = Blueprint('blue', __name__)


# hello world
@blue.route('/')
def hello_world():
    return render_template('index.html')


@blue.route('/users')
def users():
    s = "users:[{'id': '1', 'name': 'Rocky', 'age': '38'},{'id': '2', 'name': 'Steve', 'age': '50'},{'id': '3', 'name': 'Melinda', 'age': '38'},]"
    return jsonify(s)

# 删除成绩
@blue.route('/delete_grade', methods=['POST'])
def delete_grade():
    data = get_data()
    openid = data.get('openid')
    text = data.get('text')
    g = Grade.query.filter_by(openid=openid, text=text).first()
    if g:
        delete(g)
    return jsonify("delete grade success")


# 删除活动
@blue.route('/delete_active', methods=['POST'])
def delete_active():
    data = get_data()
    openid = data.get('openid')
    text = data.get('text')
    if not is_admin(openid):
        return jsonify("not admin!")
    a = Active.query.filter_by(creator=openid, text=text).first()
    delete(a)
    return jsonify("delete active success")


# 删除投票
@blue.route('/delete_vote', methods=['POST'])
def delete_vote():
    data = get_data()
    openid = data.get('openid')
    text = data.get('text')
    if not is_admin(openid):
        return jsonify("not admin!")
    v = Vote.query.filter_by(creator=openid, text=text).first()
    delete(v)
    return jsonify("delete vote success")


# 删除个人日程
@blue.route('/delete_schedule', methods=['POST'])
def delete_schedule():
    data = get_data()
    openid = data.get('openid')
    text = data.get('text')
    s = Schedule.query.filter_by(openid=openid, text=text).first()
    delete(s)
    return jsonify("delete schedule success")


# 删除班级日程
@blue.route('/delete_class_schedule', methods=['POST'])
def delete_class_schedule():
    data = get_data()
    openid = data.get('openid')
    text = data.get('text')
    if not is_admin(openid):
        return jsonify("not admin!")
    s = ClassSchedule.query.filter_by(openid=openid, text=text).first()
    delete(s)
    return jsonify("delete class schedule success")


# 获取时间热力表
@blue.route('/get_free_time', methods=['POST'])
def get_free_time():
    data = get_data()
    openid = data.get('openid')
    ts = data.get('time')
    tt = datetime.strptime(ts, '%Y-%m-%d')
    zero = time(0, 0, 0)
    tm = datetime.combine(tt, zero)
    start = tm
    end = start + timedelta(days=7)
    print("-------")
    print(start)
    print("-------")
    print(end)
    group = get_group_by_openid(openid)
    ss = Schedule.query.filter(and_(Schedule.group == group,
                                    Schedule.time > start,
                                    Schedule.time < end
                                    )).all()

    cs = ClassSchedule.query.filter(and_(ClassSchedule.group == group,
                                         ClassSchedule.time > start,
                                         ClassSchedule.time < end
                                         )).all()

    acs = Active.query.filter(and_(Active.group == group,
                                   Active.time > start,
                                   Active.time < end
                                   )).all()

    rnt = dict()
    for i in range(0, 7):
        rnt[i] = dict()
        for j in range(1, 8):
            rnt[i][j] = 0
    resolve_time(start, ss, rnt)
    resolve_time(start, cs, rnt)
    resolve_time(start, acs, rnt)

    tmp = list()
    for x in rnt:
        for y in rnt[x]:
            tmp.append(rnt[x][y])
    return jsonify(tmp)


# 创建日程
@blue.route('/create_schedule', methods=['POST'])
def create_schedule():
    data = get_data()
    openid = data.get('openid')
    text = data.get('text')
    tm = data.get('time')
    s = Schedule(openid=openid, text=text, time=tm,
                 group=get_group_by_openid(openid))
    submit(s)
    return jsonify("create schedule success")


# 创建班级日程
@blue.route('/create_class_schedule', methods=['POST'])
def create_class_schedule():
    data = get_data()
    openid = data.get('openid')
    text = data.get('text')
    tm = data.get('time')
    s = ClassSchedule(openid=openid, text=text, time=tm,
                      group=get_group_by_openid(openid))
    submit(s)
    return jsonify("create class schedule success")


# 更新用户信息 每次更新传name的时候要同步更新User表中的name,即键为字符串name,name这个值存两份
@blue.route('/update_user_info', methods=['POST'])
def update_user_info():
    data = get_data()
    openid = data.get('openid')
    infos = data.get('info')

    for i in infos:
        name = i
        text = infos[i]
        info = UserInfo.query.filter(
            and_(UserInfo.openid == openid, UserInfo.name == name)).first()
        if info:
            info.text = text
            submit(info)
            print("------update")
        else:
            info = UserInfo(openid=openid, name=name, text=text)
            submit(info)
            print("------create")

    user_name = UserInfo.query.filter(
        and_(UserInfo.openid == openid, UserInfo.name == "name")).first()
    u = User.query.filter_by(openid=openid).first()
    if user_name:
        u.name = user_name.text
        submit(u)

    return jsonify("update user info success")


# 回传用户信息
@blue.route('/search_user_info', methods=['POST'])
def search_user_info():
    data = get_data()
    openid = data.get('openid')

    data_list = []
    infos = UserInfo.query.filter_by(openid=openid).all()

    if infos:
        for i in infos:
            data_dict = dict()
            data_dict['name'] = i.name
            data_dict['text'] = i.text
            data_list.append(data_dict)

    return jsonify(data_list)


# 查询成绩
@blue.route('/search_grade', methods=['POST', 'GET'])
def search_grade():
    data = get_data()
    openid = data.get('openid')

    data_list = []
    gs = Grade.query.filter_by(openid=openid).all()

    if gs:
        for i in gs:
            data_dict = dict()
            data_dict['name'] = i.name
            data_dict['grade'] = i.grade
            data_list.append(data_dict)
    print("--------------")
    print(data_list)
    return jsonify(data_list)


# 回传班级所有人的成绩
@blue.route('/search_class_grade', methods=['POST'])
def search_class_grade():
    data = get_data()
    openid = data.get('openid')
    group = get_group_by_openid(openid)

    if is_admin(openid):
        data_dict_list_dict = get_grade_info(group)
        return jsonify(data_dict_list_dict)
    else:
        return jsonify("not Admin!")


# 回传数据分析结果
@blue.route('/search_grade_analyse', methods=['POST'])
def search_grade_analyse():
    data = get_data()
    openid = data.get('openid')
    group = get_group_by_openid(openid)

    if is_admin(openid):
        data_dict_list_dict = get_grade_info(group)
        analyse_result = dict()
        for user in data_dict_list_dict:
            for info in user:
                for d in info:
                    analyse_result[d['name']] = dict()
                    analyse_result[d['name']]['total'] += d['grade']
                    analyse_result[d['name']]['num'] += 1
                    analyse_result[d['name']]['avg'] = \
                        analyse_result[d['name']]['total'] / \
                        analyse_result[d['name']]['num']
        return jsonify(analyse_result)
    else:
        return jsonify("not Admin!")


# 更新成绩
@blue.route('/update_grade', methods=['POST'])
def update_grade():
    data = get_data()
    openid = data.get('openid')
    gs = data.get('grade')

    ds = Grade.query.filter_by(openid=openid).all()
    for i in ds:
        delete(i)

    print('-----------')
    print(gs)
    for i in gs:
        name = i['name']
        grade = i['grade']
        g = Grade.query.filter(and_(Grade.name == name,
                                    Grade.openid == openid)).first()
        if g:
            g.grade = grade
            submit(g)
            print("------update")
        else:
            g = Grade(openid=openid, name=name, grade=grade)
            submit(g)
            print("------create")

    return jsonify("update grade success")


# 找参与过的所有东西
@blue.route('/search_participate', methods=['POST'])
def search_participate():
    data = get_data()
    openid = data.get('openid')
    group = get_group_by_openid(openid)

    i = Index.query.filter_by(openid=openid)
    data_list = []
    if i:
        for t in i:
            data_dict = dict()
            data_dict['text'] = t.text
            data_dict['type'] = t.type
            data_dict['id'] = 'part'
            data_dict['time'] = t.time
            data_list.append(data_dict)

    c = Creator.query.filter_by(openid=openid)
    if c:
        for t in c:
            data_dict = dict()
            data_dict['text'] = t.text
            data_dict['type'] = t.type
            data_dict['id'] = 'create'
            data_dict['time'] = t.time
            data_list.append(data_dict)

    data_list.extend(search_group_active(group, openid))

    return jsonify(data_list)


# 创建投票
@blue.route('/create_vote', methods=['POST'])
def create_vote():
    data = get_data()
    text = data.get('text')
    content = data.get('content')
    openid = data.get('openid')
    tm = data.get('time')
    ty = data.get('type')
    group = get_group_by_openid(openid)

    v = Vote(time=tm, text=text, group=group, creator=openid, type=ty)
    submit(v)

    name = get_nickname(openid)
    c = Creator(openid=openid, name=name, text=text, type="vote", time=tm)
    submit(c)

    for i in content:
        c = Choice(text=i, belong=v.text, num=0)
        submit(c)

    return jsonify("create vote success")


# 投票
@blue.route('/vote', methods=['POST'])
def vote():
    data = get_data()
    print('-----------')
    print(data)
    text = data.get('text')
    openid = data.get('openid')
    choose = data.get('choose')
    print("-----------vote title")
    print(text)
    print("choose")
    print(choose)
    for i in choose:
        t = Index(text=text, openid=openid, choose=choose,
                  type="vote", time=datetime.now())
        print("-----------create index")
        print(text)
        submit(t)
        c = Choice.query.filter_by(text=i).first()
        print("----------")
        print(c.num)
        c.num = int(c.num) + 1
        submit(c)
    return jsonify("vote success")


# 回传投票结果
@blue.route('/search_vote_result', methods=['POST'])
def search_vote_result():
    data = get_data()
    text = data.get('text')
    openid = data.get('openid')
    print('-----')
    print(text)
    if not is_admin(openid):
        return jsonify("not admin!")
    total = 0
    v = Vote.query.filter_by(text=text).first()
    group = get_group_by_openid(openid)
    us = User.query.filter_by(group=group).all()
    t = int()
    for i in us:
        if i:
            t = t+1
    data_dict = dict()
    data_dict['class_member'] = t
    if v:
        cs = Choice.query.filter_by(belong=text).all()
        for i in cs:
            data_dict[i.text] = i.num
            total += i.num
        data_dict["total"] = total
        return jsonify(data_dict)
    else:
        return jsonify("no such vote")


# 返回班级成员
@blue.route('/search_class_member', methods=['POST'])
def search_class_member():
    data = get_data()
    openid = data.get('openid')

    group = get_group_by_openid(openid)
    us = User.query.filter_by(group=group).all()
    data_list = []

    if us:
        for i in us:
            data_dict = dict()
            ad = Admin.query.filter_by(openid=i.openid).first()
            if ad and ad.group == i.group:
                data_dict['admin'] = 'admin'
            else:
                data_dict['admin'] = 'user'

            data_dict['name'] = i.name
            data_list.append(data_dict)

    return jsonify(data_list)


# 填表
@blue.route('/receive_excel_file', methods=['POST'])
def receive_excel_file():
    openid = request.values.to_dict().get('openid')
    group = get_group_by_openid(openid)
    f = request.files.get('filePath')
    root = os.getcwd()
    path = os.path.join(root, group, openid)
    f.save(path)
    print("----------", path)
    return jsonify("saved")


# 按用户组列出所有活动
@blue.route('/search_active_by_group', methods=['POST'])
def search_active_by_group():
    data = get_data()
    openid = data.get('openid')

    group = get_group_by_openid(openid)
    data_list = search_group_active(group, openid)

    ss = Schedule.query.filter_by(openid=openid).all()
    if ss:
        for i in ss:
            data_dict = dict()
            data_dict['type'] = "schedule"
            data_dict['text'] = i.text
            data_dict['time'] = i.time
            data_dict['id'] = 'private'
            data_list.append(data_dict)

    return jsonify(data_list)


# 发布动态
@blue.route('/release_active', methods=['POST'])
def release_active():
    data = get_data()
    openid = data.get('openid')
    text = data.get('text')
    title = data.get('title')
    tm = data.get('time')

    group = get_group_by_openid(openid)
    a = Active(group=group, text=text, time=tm, title=title)
    submit(a)

    name = get_nickname(openid)
    c = Creator(openid=openid, name=name, text=text, type="active", time=tm)
    submit(c)

    us = User.query.filter_by(group=group)
    if us:
        for i in us:
            t = Index(openid=i.openid, text=text,
                      type="active", time=datetime.now())
            submit(t)

    return jsonify(a.text)


# 按日期列出所有活动
@blue.route('/search_active_by_date', methods=['POST'])
def search_active_by_date():
    data = get_data()
    openid = data.get('openid')
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')

    g = get_group_by_openid(openid)
    us = User.query.filter_by(group=g).all()
    t = int()
    for i in us:
        if i:
            t = t+1

    data_list = []
    a = Active.query.filter(and_(extract('year', Active.time) == year,
                                 extract('month', Active.time) == month,
                                 extract('day', Active.time) == day,
                                 Active.group == g
                                 )).all()

    if a:
        for i in a:
            data_dict = dict()
            data_dict['type'] = 'active'
            data_dict['text'] = i.text
            data_dict['title'] = i.title
            data_dict['time'] = i.time
            data_dict['class_member'] = t
            data_list.append(data_dict)

    v = Vote.query.filter(and_(extract('year', Active.time) == year,
                               extract('month', Active.time) == month,
                               extract('day', Active.time) == day,
                               Vote.group == g
                               )).all()
    if v:
        for i in v:
            data_dict = dict()
            data_dict['type'] = 'vote'
            data_dict['vote_type'] = i.type
            data_dict['title'] = i.text
            data_dict['time'] = i.time
            data_list.append(data_dict)

    s = Schedule.query.filter(and_(extract('year', Active.time) == year,
                                   extract('month', Active.time) == month,
                                   extract('day', Active.time) == day,
                                   Schedule.openid == openid
                                   )).all()
    if s:
        for i in s:
            data_dict = dict()
            data_dict['type'] = 'schedule'
            data_dict['text'] = i.text
            data_dict['time'] = i.time
            data_list.append(data_dict)
    print("------------")
    print(data_list)
    return jsonify(data_list)


# 接收用户code,返回用户实例,如果没有,调用api获取openid并且创建用户
@blue.route('/login', methods=['POST'])
def login():
    data = get_data()
    code = data.get('code')
    appid = data.get('appid')
    secret = data.get('secret')

    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=' \
          + appid + '&secret=' + secret + '&js_code=' + code + \
          '&grant_type=authorization_code'
    response = requests.get(url)
    uid = eval(response.text)['openid']
    us = User.query.filter_by(openid=uid).first()
    if us:
        return jsonify(uid, "already", us.group)
    else:
        return jsonify(uid, "first", None)


# 创建班级
@blue.route('/create_class', methods=['POST'])
def create_class():
    data = get_data()
    name = data.get('name')
    openid = data.get('openid')
    nick_name = data.get('nickname')

    check_group = Group.query.filter_by(name=name).first()
    if check_group:
        return jsonify("group had created")

    c = Group(name=name, creator=openid)
    submit(c)

    u = User(openid=openid, group=name, name=nick_name)

    submit(u)

    a = Admin(openid=openid, group=name)
    submit(a)

    return jsonify("create class success")


# 搜索班级
@blue.route('/search_class', methods=['POST'])
def search_class():
    data = get_data()
    key = data.get('keyword')

    data_list = []
    cs = Group.query.filter(Group.name.like(
        "%" + key + "%") if key is not None else "").all()
    if cs:
        for i in cs:
            data_list.append(i.name)

    return jsonify(data_list)


# 加入班级
@blue.route('/add_class', methods=['POST'])
def add_class():
    data = get_data()
    name = data.get('name')
    openid = data.get('openid')
    nick_name = data.get('nickname')
    print("---------------")
    print(name)
    print("---------------")
    print(nick_name)
    u = User(openid=openid, group=name, name=nick_name)
    submit(u)
    return jsonify("add class success")


# 初始化数据库,删除所有表并重新生成
# 仅测试环境可用
# @blue.route('/init')
def init():
    db.drop_all()
    db.create_all()
    c = Group(name="物联171")
    submit(c)
    return jsonify('init success')
