<template>
  <div class="app-container">
    <el-row>
      <div class="metric-list">
        <el-col :span="3">
          <div class="">
            000001.SH
          </div>
        </el-col>
        <el-col :span="3">
          <div class="">正面新闻</div>
          <div class="">{{newsStats['1']}}</div>
        </el-col>
        <el-col :span="3">
          <div class="">负面新闻</div>
          <div class="">{{newsStats['-1']}}</div>
        </el-col>
        <el-col :span="3">
        </el-col>
      </div>
    </el-row>
    <el-row>
      <div class="k-chart">
        <el-row>
          <div class="control">
            <div class="left">
              <el-select
                v-model="type"
                size="small"
              >
                <el-option value="index" label="指数"/>
                <el-option value="stock" label="股票"/>
              </el-select>
              <el-autocomplete
                v-model="code"
                size="small"
                :fetch-suggestions="fetchCodeSuggestions"
              />
              <el-button size="small" type="primary" @click="getDaily">查询</el-button>
            </div>
            <div class="right">
              <el-date-picker
                type="daterange"
                v-model="dateRange"
                size="small"
              />
            </div>
          </div>
        </el-row>
        <div id="k-chart"/>
      </div>
    </el-row>
    <el-row>
      <el-col :span="12" style="padding-right: 10px;">
        <div class="news-list">
          Positive News List
        </div>
      </el-col>
      <el-col :span="12" style="padding-left: 10px;">
        <div class="news-list">
          Negative News List
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import dayjs from 'dayjs'
import echarts from 'echarts'
import {
  getStockList,
  getStockDaily,
  getIndexList,
  getIndexDaily,
  getNewsStats
} from '../../api/dashboard'

const upColor = '#ec0000'
const downColor = '#00da3c'

export default {
  name: 'Dashboard',
  data() {
    return {
      chart: undefined,
      type: 'index',
      code: '000001.SH',
      stockList: [],
      indexList: [
        { ts_code: '000001.SH', name: '上证指数' }
      ],
      dailyList: [],
      newsStats: {},
      dateRange: [
        dayjs().subtract(3, 'month'),
        dayjs().subtract(0, 'd')
      ]
    }
  },
  watch: {
    type() {
      this.code = ''
    },
    code() {
    }
  },
  methods: {
    renderDaily() {
      this.chart = echarts.init(this.$el.querySelector('#k-chart'))
      const xData = this.dailyList.map(d => d.trade_date)
      const data = this.dailyList
        .map(d => [
          d.open,
          d.close,
          d.high,
          d.low
        ])
      const dataVol = this.dailyList.map(d => {
        const r = {
          value: d.vol,
          itemStyle: {
            color: undefined
          }
        }
        if (d.open >= d.close) {
          r.itemStyle.color = downColor
        } else {
          r.itemStyle.color = upColor
        }
        return r
        // return d.vol
      })
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        yAxis: [
          {
            type: 'value',
            scale: true,
            splitArea: {
              show: true
            }
          },
          {
            scale: true,
            gridIndex: 1,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ],
        xAxis: [
          {
            data: xData
          },
          {
            gridIndex: 1,
            data: xData,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ],

        grid: [
          {
            left: '10%',
            right: '8%',
            height: '50%'
          },
          {
            left: '10%',
            right: '8%',
            top: '73%',
            height: '16%'
          }
        ],
        series: [
          {
            type: 'k',
            data,
            gridIndex: 0,
            itemStyle: {
              normal: {
                color: upColor,
                color0: downColor,
                borderColor: null,
                borderColor0: null
              }
            }
          },
          {
            type: 'bar',
            gridIndex: 1,
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: dataVol
          }
        ]
      }
      this.chart.setOption(option)
    },
    getIndexList() {
      const params = {}
      getIndexList(params).then(data => {
        this.stockList = data.items
      })
    },
    getStockList() {
      const params = {}
      getStockList(params).then(data => {
        this.stockList = data.items
      })
    },
    getDaily() {
      const params = {}
      params.ts_code = this.code
      params.start_date = dayjs(this.dateRange[0]).format('YYYYMMDD')
      params.end_date = dayjs(this.dateRange[1]).format('YYYYMMDD')
      const func = this.type === 'index' ? getIndexDaily : getStockDaily
      func(params).then(data => {
        this.dailyList = data.items
        this.dailyList.sort((a, b) => a.trade_date < b.trade_date ? -1 : 1)
        this.renderDaily()
      })
    },
    fetchCodeSuggestions(queryString, cb) {
      const data = this.type === 'index' ? this.indexList : this.stockList
      cb(
        data
          .filter(d => {
            if (d.name.includes(queryString)) return true
            if (d.ts_code.includes(queryString)) return true
          })
          .map(d => {
            d.value = d.ts_code
            return d
          })
      )
    },
    getNewsStats() {
      const params = {}
      params.start_date = dayjs(this.dateRange[0]).format('YYYYMMDD')
      params.end_date = dayjs(this.dateRange[1]).format('YYYYMMDD')
      getNewsStats(params).then(data => {
        this.newsStats = data.data
      })
    },
    getData() {
      this.getDaily()
      this.getNewsStats()
    }
  },
  created() {
    this.getStockList()
    this.getData()
  }
}
</script>

<style scoped>
  .metric-list {
    border: 1px solid grey;
    height: 150px;
  }

  #k-chart {
    height: 400px;
    width: 100%;
  }

  .k-chart {
    margin-top: 20px;
    border: 1px solid grey;
  }

  .news-list {
    margin-top: 20px;
    border: 1px solid grey;
    height: 400px;
  }

  .control {
    display: flex;
    justify-content: space-between;
  }
</style>
