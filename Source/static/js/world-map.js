// 基于准备好的dom，初始化echarts实例
let worldMap = echarts.init(document.getElementById('world'))
// 监听屏幕变化自动缩放图表

var mydata = []

window.addEventListener('resize', function () {
worldMap.resize()
})
data = {

}
// 绘制图表
worldMap_option = {
// 图表主标题
    title: {
      // text: '全球疫情地图', // 主标题文本，支持使用 \n 换行
      top: 20, // 定位 值: 'top', 'middle', 'bottom' 也可以是具体的值或者百分比
      left: 'center', // 值: 'left', 'center', 'right' 同上
      textStyle: { // 文本样式
        fontSize: 28,
        fontWeight: 600,
        color: '#333'
      }
    },
    backgroundColor:'#333',
    // 提示框组件
    tooltip: {
      trigger: 'item', // 触发类型, 数据项图形触发，主要在散点图，饼图等无类目轴的图表中使用
    },
    // 视觉映射组件
    visualMap: {
      type: 'piecewise', // continuous 类型为连续型  piecewise 类型为分段型
      show: true, // 是否显示 visualMap-continuous 组件 如果设置为 false，不会显示，但是数据映射的功能还存在
      // 文本样式
      x:'10%',
      y:'65%',
      textStyle: {
        fontSize: 18,
        color: '#fff'
      },
        // backgroundColor:'#FD6666',
      realtime: false, // 拖拽时，是否实时更新
      calculable: true, // 是否显示拖拽用的手柄
      // 定义 在选中范围中 的视觉元素
      splitList:[
        {start:1,end:4999},
        {start:5000,end:49999},
        {start:50000,end:199999},
        {start:200000,end:500000},
        {start:500000,end:999999},
          {start:1000000},
      ],
      inRange: {
        // color: ['#a4b0be', '#F5DEB3','#F0E68C','#FF6347', '#FFFF00', '#FD7272'] // 图元的颜色#F9DCD1
        //   color: ['#60a3bc', '#6a89cc','#4a69bd','#1e3799', '#0c2461']
          color: ['#f8c291', '#f6b93b','#e58e26','#e55039', '#eb2f06', '#9B1A1A']
      }
    },
    series: [
             {
                type: 'map', // 类型
                // 系列名称，用于tooltip的显示，legend 的图例筛选 在 setOption 更新数据和配置项时用于指定对应的系列
                name: '累计确诊',
                mapType: 'world', // 地图类型
                // 是否开启鼠标缩放和平移漫游 默认不开启 如果只想要开启缩放或者平移，可以设置成 'scale' 或者 'move' 设置成 true 为都开启
                roam: false,
                // 当前视角的缩放比例
                zoom : 1.2,
                // 地图区域的多边形 图形样式
                itemStyle: {
                  areaColor: '#fad390', // 地图区域的颜色 如果设置了visualMap，areaColor属性将不起作用
                  borderWidth: 0.5, // 描边线宽 为 0 时无描边
                  borderColor: '#333', // 图形的描边颜色 支持的颜色格式同 color，不支持回调函数
                  borderType: 'solid' // 描边类型，默认为实线，支持 'solid', 'dashed', 'dotted'
                },
                // 高亮状态下的多边形和标签样式
                emphasis: {
                  label: {
                        show: true, // 是否显示标签
                        fontSize:16,
                        fontWeight:600,
                        color: '#fff' // 文字的颜色 如果设置为 'auto'，则为视觉映射得到的颜色，如系列色FD6666
                  },

                  itemStyle: {
                    areaColor: '#FD6666' // 地图区域的颜色
                  }
                },

            // 自定义地区的名称映射
                nameMap: name,
                // 地图系列中的数据内容数组 数组项可以为单个数值
                data: mydata,
            },
        ]
};

worldMap.setOption(worldMap_option)
// 定时显示提示框和高亮效果
// let index = -1
// setInterval(function () {
//   // 隐藏提示框
//   worldMap.dispatchAction({
//     type: 'hideTip',
//     seriesIndex: 0,
//     dataIndex: index
//   })
//   // 显示提示框
//   worldMap.dispatchAction({
//     type: 'showTip',
//     seriesIndex: 0,
//     dataIndex: index + 1
//   })
//   // 取消高亮指定的数据图形
//   worldMap.dispatchAction({
//     type: 'downplay',
//     seriesIndex: 0,
//     dataIndex: index
//   })
//   // 高亮指定的数据图形
//   worldMap.dispatchAction({
//     type: 'highlight',
//     seriesIndex: 0,
//     dataIndex: index + 1
//   })
//   index++
//   if (index > data.length - 1) {
//     index = -1
//   }
// }, 1500)
