<template>
  <div class="app-container">
    <el-row>
      <div class="metric-list">
        <div class="metric-item">
          <el-col>
            <div class="title">{{info.name}}</div>
            <div class="value">{{info.ts_code}}</div>
          </el-col>
        </div>
        <div class="metric-item pos">
          <el-col :span="8">
            <div class="title">正面新闻</div>
            <div class="value">{{newsStats['1']}}</div>
          </el-col>
          <el-col :span="16">
            <div id="metric-pos-chart" class="chart"/>
          </el-col>
        </div>
        <div class="metric-item neg">
          <el-col :span="8">
            <div class="title">负面新闻</div>
            <div class="value">{{newsStats['-1']}}</div>
          </el-col>
          <el-col :span="16">
            <div id="metric-neg-chart" class="chart"/>
          </el-col>
        </div>
        <div class="metric-item" v-if="type === 'stock'">
          <el-col>
            <div class="info">总市值: <span class="info-value">{{stockBasic.total_mv}}</span></div>
            <div class="info">总股本: <span class="info-value">{{stockBasic.total_share}}</span></div>
            <div class="info">市盈率: <span class="info-value">{{stockBasic.pe}}</span></div>
          </el-col>
        </div>
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
                @select="onSelectCode"
              />
              <el-button size="small" type="primary" @click="getData">查询</el-button>
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
        <h4 class="title">正面新闻</h4>
        <news-list :news-list="posNewsList"/>
      </el-col>
      <el-col :span="12" style="padding-left: 10px;">
        <h4 class="title">负面新闻</h4>
        <news-list :news-list="negNewsList"/>
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
  getStockIndexList,
  getIndexDaily,
  getNewsStats,
  getStock,
  getStockIndex,
  getNews,
  getStockDailyBasic
} from '../../api/dashboard'
import NewsList from '../../components/List/NewsList'

const upColor = '#ec0000'
const downColor = '#00da3c'

export default {
  name: 'Dashboard',
  components: { NewsList },
  data() {
    return {
      chart: undefined,
      type: 'stock',
      code: '600000.SH',
      stockList: [],
      stockIndexList: [],
      dailyList: [],
      newsStats: {
        '-1': 0,
        '0': 0,
        '1': 0
      },
      newsDaily: {
        '-1': [],
        '0': [],
        '1': []
      },
      newsList: [],
      stockBasic: {},
      info: {
        ts_code: '',
        name: ''
      },
      dateRange: [
        dayjs().subtract(1, 'month'),
        dayjs().subtract(0, 'd')
      ]
    }
  },
  computed: {
    posNewsList() {
      return this.newsList
        .filter(d => {
          if (d.class !== undefined) return d.class === 1
          return d.class_pred === 1
        })
        .sort((a, b) => a.proba_pred > b.proba_pred ? -1 : 1)
    },
    negNewsList() {
      return this.newsList
        .filter(d => {
          if (d.class !== undefined) return d.class === -1
          return d.class_pred === -1
        })
        .sort((a, b) => a.proba_pred > b.proba_pred ? -1 : 1)
    }
  },
  watch: {
    type() {
    },
    code() {
    },
    dateRange() {
      this.getData()
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
            left: '5%',
            right: '0%',
            top: '5%',
            height: '50%'
          },
          {
            left: '5%',
            right: '0%',
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
        ],
        markPoint: {
          itemStyle: {
            normal: { color: 'rgb(41,60,85)' }
          },
          data: this.newsDaily['1']
            .filter(d => d.value > 0)
            .map(d => {
              const dateList = this.dailyList.map(d => d.trade_date)
              const idx = dateList.indexOf(d.date)
              if (idx === -1) return { coord: [0, 0], value: undefined }
              return {
                coord: [d.date, this.dailyList[idx].close],
                value: d.value
              }
            })
        }
      }
      this.chart.setOption(option)
      this.chart.on('click', ev => {
      })
    },
    renderMetricPosChart() {
      this._renderMetricChart('metric-pos-chart', '1')
    },
    renderMetricNegChart() {
      this._renderMetricChart('metric-neg-chart', '-1')
    },
    _renderMetricChart(id, cls) {
      this.posChart = echarts.init(this.$el.querySelector('#' + id))
      const option = {
        yAxis: {
          type: 'value',
          show: false
        },
        xAxis: {
          type: 'category',
          data: this.newsDaily[cls].map(d => d.date),
          show: false
        },
        series: [
          {
            type: 'line',
            showSymbol: false,
            smooth: true,
            lineStyle: {
              color: cls === '1' ? upColor : downColor
            },
            data: this.newsDaily[cls].map(d => d.value)
          }
        ]
      }
      this.posChart.setOption(option)
    },
    getStockIndexList() {
      const params = {}
      getStockIndexList(params).then(data => {
        this.stockIndexList = data.items
      })
    },
    getStockList() {
      const params = {}
      getStockList(params).then(data => {
        this.stockList = data.items
      })
    },
    async getDaily() {
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
      const data = this.type === 'index' ? this.stockIndexList : this.stockList
      cb(
        data
          .filter(d => {
            if (d.name.includes(queryString)) return true
            if (d.ts_code.includes(queryString)) return true
          })
          .map(d => {
            d.value = d.name + ' (' + d.ts_code + ')'
            return d
          })
          .filter((d, i) => i < 10)
      )
    },
    onSelectCode({ ts_code }) {
      this.code = ts_code
      this.getData()
    },
    async getNewsStats() {
      const params = {}
      params.start_date = dayjs(this.dateRange[0]).format('YYYYMMDD')
      params.end_date = dayjs(this.dateRange[1]).format('YYYYMMDD')
      if (this.type === 'stock') {
        params.ts_code = this.code
      }
      getNewsStats(params).then(data => {
        const clsList = ['-1', '0', '1']
        clsList.forEach(cls => {
          this.$set(this.newsStats, cls, data.data[cls] || 0)
          this.$set(this.newsDaily, cls, data.daily[cls].sort((a, b) => a.date < b.date ? -1 : 1) || [])
        })

        this.renderMetricPosChart()
        this.renderMetricNegChart()
      })
    },
    async getData() {
      await this.getInfo()
      await this.getNewsStats()
      await this.getDaily()
      await this.getNews()
      if (this.type === 'stock') await this.getStockDailyBasic()
    },
    async getInfo() {
      const params = {}
      params._id = this.code
      const func = this.type === 'index' ? getStockIndex : getStock
      func(params).then(data => {
        this.info = data || {
          name: '',
          ts_code: this.code
        }
      })
    },
    async getNews() {
      const params = {}
      params.code = this.code
      getNews(params).then(data => {
        this.newsList = data.items
      })
    },
    async getStockDailyBasic() {
      const params = {}
      params.ts_code = this.code
      params.start_date = dayjs().subtract(1, 'week').format('YYYYMMDD')
      getStockDailyBasic(params).then(data => {
        this.stockBasic = data.items[0]
      })
    }
  },
  created() {
    if (this.$route.query.type) this.type = this.$route.query.type
    if (this.$route.query.code) this.code = this.$route.query.code
    this.getStockIndexList()
    this.getStockList()
    this.getData()
  }
}
</script>

<style scoped>
  .metric-list {
    /*border: 1px solid grey;*/
    height: 100px;
  }

  #k-chart {
    height: 400px;
    width: 100%;
  }

  .k-chart {
    margin-top: 20px;
    /*border: 1px solid grey;*/
  }

  .control {
    display: flex;
    justify-content: space-between;
  }

  .metric-list {
    display: flex;
  }

  .metric-item {
    height: 100px;
    flex-basis: 25%;
    display: flex;
    align-items: center;
    padding-right: 5%;
  }

  .metric-item .title {
    font-size: 14px;
    font-weight: 600;
    color: #555;
  }

  .metric-item .value {
    font-size: 32px;
    color: #555;
    font-weight: 600;
  }

  .metric-item .info {
    font-size: 14px;
    color: #555;
  }

  .metric-item .info .info-value {
    text-align: right;
    display: inline-block;
    width: 100px;
  }

  .metric-item .chart {
    width: 100%;
    height: 80px;
  }

  h4.title {
    color: #555;
  }
</style>
