from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
import nameMap
from jieba.analyse import extract_tags
import decimal
import string
import utils

app = Flask(__name__)


@app.route('/time')
def get_time():
    # 计算当前时间
    return utils.get_time()


@app.route('/c1')
def get_c1_data():
    data = utils.get_c1_data()
    return jsonify({"confirm": int(data[0]), "suspect": int(data[1]), "heal": int(data[2]), "dead": int(data[3])})


# 之所以得把数据变为字典然后在变为res列表的原因在于我们得到的数据的格式必须和ec_center.js中的mydata数据格式相同
@app.route('/c2')
def get_c2_data():
    res = []
    for tap in utils.get_c2_data():
        res.append({"name": tap[0], "value": int(tap[1])})
    return jsonify({"data": res})


@app.route('/l1')
def get_l1_data():
    data = utils.get_l1_data()
    day, confirm, suspect, heal, dead = [], [], [], [], []
    # 从data列表索引7开始，因为data[0:7]某些属性的值为none
    for a, b, c, d, e in data[7:]:
        day.append(a.strftime("%m-%d"))
        confirm.append(b)
        suspect.append(c)
        heal.append(d)
        dead.append(e)
    return jsonify({"day": day, "confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead})


@app.route('/l2')
def get_l2_data():
    data = utils.get_l2_data()
    day, confirm_add, suspect_add = [], [], []
    # 从data列表索引7开始，因为data[0:7]某些属性的值为none
    for a, b, c in data[7:]:
        day.append(a.strftime("%m-%d"))
        confirm_add.append(b)
        suspect_add.append(c)
    return jsonify({"day": day, "confirm_add": confirm_add, "suspect_add": suspect_add})


@app.route('/r1')
def get_r1_data():
    data = utils.get_r1_data()
    city, confirm = [], []
    for i in data:
        city.append(i[0])
        confirm.append(int(i[1]))
    return jsonify({"city": city, "confirm": confirm})


@app.route('/r2')
def get_r2_data():
    data = utils.get_r2_data()
    d = []
    for i in data:
        k = i[0].rstrip(string.digits)
        v = i[0][len(k):]
        ks = extract_tags(k)
        for j in ks:
            if not j.isdigit():
                d.append({"name": j, "value": v})
    return jsonify({"kws": d})

# 世界疫情地图
@app.route('/world')
def world():
    return render_template('world.html')


# 获取world数据，世界疫情地图
@app.route('/get_world')
def get_world():
    res = []
    global_dict = utils.get_world()
    for tup in global_dict:
        res.append({'name': tup, 'value': global_dict[tup]})
    # 获取中国累计确诊人数
    china_data = utils.get_c1_data()[0]
    res.append({'name': '中国', 'value': int(china_data)})
    return jsonify({'data': res, 'name': nameMap.namemap})



@app.route('/')
def hello_world():
    return render_template("main.html")


@app.route('/login')
def hello_world2():
    name = request.values.get("name")
    pwd = request.values.get("pwd")
    return f'name={name}.pwd={pwd}'


@app.route('/ajax',methods=["get","post"])
def hello_world4():
    print(request.values.get("name"))
    print(request.values.get("score"))
    return '10000'


@app.route('/abc')
def hello_world1():
    id = request.values.get("id")
    return f"""
    <form action = "/login">
        账号：<input name = "name"><br>
        密码：<input name = "pwd">
        <input type="submit">
    </form>
    """


@app.route('/tem')
def hello_word3():
    return render_template("index.html")



if __name__ == '__main__':
    app.run()
