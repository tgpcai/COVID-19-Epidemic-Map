// 更新世界疫情地图
function get_world() {
    $.ajax({
        url:"/get_world",
        success:function(data){
            print("dddddddddddddd")
            worldMap_option.series[0].nameMap = data.name
            worldMap_option.series[0].data = data.data
		    worldMap.setOption(worldMap_option)
        },
        error:function f() {

        }
    })
}

//访问时获取数据
get_world();

//停留页面时每一小时刷新一次数据
setInterval(get_world,1000*60*60);