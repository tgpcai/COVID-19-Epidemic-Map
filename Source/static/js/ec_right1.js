var ec_right1 = echarts.init(document.getElementById("r1"),"dark");

option_right1 = {
	title: {
		text: '非湖北地区城市确诊TOP5',
		textStyle: {
			color: 'white'
		},
		left: 'left'
	},
	// grid: {
	// 	left: 50,
	// 	top: 50,
	// 	right: 0,
	// 	width: '87%',
	// 	height: 320,
	// },
	color: ['#3398DB'],
	tooltip: {
		trigger: 'axis',
		axisPointer: {
			type: 'shadow'
		}
	},
	//全局字体样式
	// textStyle: {
	// 	fontFamily: 'PingFangSC-Medium',
	// 	fontSize: 12,
	// 	color: '#858E96',
	// 	lineHeight: 12
	// },
	xAxis: {
		type: 'category',
		//                              scale:true,
		data: []
	},
	yAxis: {
		type: 'value',
		//坐标轴刻度设置
		},
	series: [{
		type: 'bar',
		data: [],
		barMaxWidth: "50%"
	}]
};
ec_right1.setOption(option_right1)
