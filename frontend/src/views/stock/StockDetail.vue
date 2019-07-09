<template>
  <div class="app-container">
    <el-dialog
      :visible.sync="dialogVisible"
      width="80%"
    >
      <h4 v-if="activeRow.title">
        {{activeRow.title}}
      </h4>
      <p class="dialog-text">
        {{activeRow.text}}
      </p>
      <template slot="footer">
        <el-button
          type="danger"
          :plain="activeRow.class!==1"
          icon="el-icon-top"
          @click="selectUp(activeRow)"
        />
        <el-button
          type="info"
          :plain="activeRow.class!==0"
          icon="el-icon-minus"
          @click="selectFlat(activeRow)"
        />
        <el-button
          type="success"
          :plain="activeRow.class!==-1"
          icon="el-icon-bottom"
          @click="selectDown(activeRow)"
        />
        <el-button type="primary" @click="dialogVisible = false">确定</el-button>
      </template>
    </el-dialog>

    <el-row>
      <div class="metric-list" v-loading="loading">
        <div class="metric-item">
          <el-col>
            <div class="title">
              {{info.name}}
              <span class="sub-title"> ({{info.market}} / {{info.industry}} / {{info.area}})</span>
            </div>
            <div class="value">
              {{info.ts_code}}
            </div>
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
          <el-col :span="9">
            <div class="title">操作建议</div>
            <div class="value" :class="getRecomClass(recomStats.overall)">{{getRecomText(recomStats.overall)}}</div>
          </el-col>
          <el-col :span="15">
            <ul class="reason-list">
              <li class="reason-item" :class="getReasonItemClass(recomStats.news)">
                <i class="fa" :class="getReasonItemIconClass(recomStats.news)"></i>
                {{getReasonItemText('news')}}
              </li>
              <li class="reason-item" :class="getReasonItemClass(recomStats.position)">
                <i class="fa" :class="getReasonItemIconClass(recomStats.position)"></i>
                {{getReasonItemText('position')}}
              </li>
              <li class="reason-item" :class="getReasonItemClass(recomStats.trend)">
                <i class="fa" :class="getReasonItemIconClass(recomStats.trend)"></i>
                {{getReasonItemText('trend')}}
              </li>
            </ul>
          </el-col>
        </div>
      </div>
    </el-row>
    <el-row>
      <div class="k-chart" v-loading="loading" @resize="renderDaily">
        <el-row>
          <div class="control">
            <div class="left">
              <!--<el-select-->
              <!--v-model="type"-->
              <!--size="small"-->
              <!--style="width: 100px"-->
              <!--&gt;-->
              <!--<el-option value="index" label="指数"/>-->
              <!--<el-option value="stock" label="股票"/>-->
              <!--</el-select>-->
              <el-autocomplete
                v-model="code"
                size="small"
                :fetch-suggestions="fetchCodeSuggestions"
                @select="onSelectCode"
              />
              <!--<el-button size="small" type="primary" @click="getData">查询</el-button>-->
            </div>
            <div class="right">
              <ul class="date-range-list">
                <li v-for="d in dateRangeList" :key="d">
                  <a :class="getDateRangeClass(d)" href="javascript:" @click="onDateRangeClick(d)">{{d}}天</a>
                </li>
              </ul>
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
        <h4 class="title">正面新闻 <span class="count">({{posNewsList.length}}条)</span></h4>
        <news-list v-loading="loading" :news-list="posNewsList" @click="onClickNewsItem"/>
      </el-col>
      <el-col :span="12" style="padding-left: 10px;">
        <h4 class="title">负面新闻 <span class="count">({{negNewsList.length}}条)</span></h4>
        <news-list v-loading="loading" :news-list="negNewsList" @click="onClickNewsItem"/>
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
  getStockDailyBasic,
  getNewsItem
} from '../../api/stock'
import {
  setNews
} from '../../api/news'
import NewsList from '../../components/List/NewsList'

const upColor = '#ec0000'
const downColor = '#00da3c'

export default {
  name: 'Dashboard',
  components: { NewsList },
  data() {
    return {
      loading: false,
      chart: undefined,
      type: 'stock',
      code: '600000.SH',
      stockList: [],
      stockIndexList: [],
      dailyList: [],
      newsStats: {
        '-1': 0,
        '1': 0
      },
      newsDaily: {
        '-1': [],
        '1': []
      },
      newsList: [],
      stockBasic: {},
      info: {
        ts_code: '',
        name: ''
      },
      recomStats: {
        news: undefined,
        position: undefined,
        trend: undefined,
        overall: undefined
      },
      dateRange: [
        dayjs().subtract(30, 'd'),
        dayjs().subtract(0, 'd')
      ],
      dateRangeList: [
        7,
        14,
        30,
        60,
        90,
        180
      ],
      activeRow: {},
      dialogVisible: false
    }
  },
  computed: {
    posNewsList() {
      return this.newsList
        .filter(d => {
          const dt = dayjs(d.ts).format('YYYYMMDD')
          return dayjs(this.dateRange[0]).format('YYYYMMDD') <= dt &&
            dt < dayjs(this.dateRange[1]).add(1, 'day').format('YYYYMMDD')
        })
        .filter(d => {
          return d.class_final === 1
        })
    },
    negNewsList() {
      return this.newsList
        .filter(d => {
          const dt = dayjs(d.ts).format('YYYYMMDD')
          return dayjs(this.dateRange[0]).format('YYYYMMDD') <= dt &&
            dt < dayjs(this.dateRange[1]).add(1, 'day').format('YYYYMMDD')
        })
        .filter(d => {
          return d.class_final === -1
        })
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
      const dataPos = this.newsDaily['1'].map(d => d.count)
      const dataNeg = this.newsDaily['-1'].map(d => -d.count)
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
            // scale: true,
            gridIndex: 1,
            axisLabel: { show: true },
            axisLine: { show: true },
            axisTick: { show: true },
            splitLine: { show: false },
            splitArea: { show: true }
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
            axisLine: { show: true },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ],
        grid: [
          {
            left: '5%',
            right: '0%',
            top: '5%',
            height: '55%'
          },
          {
            left: '5%',
            right: '0%',
            top: '70%',
            height: '25%'
          }
        ],
        series: [
          {
            name: '股价',
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
          // {
          //   type: 'bar',
          //   gridIndex: 1,
          //   xAxisIndex: 1,
          //   yAxisIndex: 1,
          //   data: dataVol
          // },
          {
            name: '正面新闻',
            type: 'bar',
            barWidth: '50%',
            stack: true,
            gridIndex: 1,
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: dataPos,
            itemStyle: {
              color: upColor
            }
          },
          {
            name: '负面新闻',
            type: 'bar',
            barWidth: '50%',
            stack: true,
            gridIndex: 1,
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: dataNeg,
            itemStyle: {
              color: downColor
            }
          }
        ]
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
    getDaily() {
      return new Promise((resolve, reject) => {
        let func
        const params = {}
        if (this.type === 'index') {
          func = getIndexDaily
          params.ts_code = this.code
          params.start_date = dayjs(this.dateRange[0]).format('YYYYMMDD')
          params.end_date = dayjs(this.dateRange[1]).format('YYYYMMDD')
        } else {
          func = getStockDaily
          params.filter = {
            ts_code: this.code,
            trade_date: {
              $gte: dayjs(this.dateRange[0]).format('YYYYMMDD'),
              $lte: dayjs(this.dateRange[1]).format('YYYYMMDD')
            }
          }
          params.page_size = 999999
        }
        func(params).then(data => {
          this.dailyList = data.items
          this.dailyList.sort((a, b) => a.trade_date < b.trade_date ? -1 : 1)
          resolve()
        })
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
      this.loading = true
      const params = {}
      params.start_date = dayjs(this.dateRange[0]).format('YYYYMMDD')
      params.end_date = dayjs(this.dateRange[1]).format('YYYYMMDD')
      if (this.type === 'stock') {
        params.ts_code = this.code
      }
      getNewsStats(params).then(data => {
        const clsList = ['-1', '1']
        clsList.forEach(cls => {
          this.$set(this.newsStats, cls, data.stats[cls])
          this.$set(
            this.newsDaily,
            cls,
            data.daily_stats[cls]
              .map(d => {
                d.value = d.count
                return d
              })
              .sort((a, b) => a.date < b.date ? -1 : 1)
          )
        })

        // 新闻列表
        this.newsList = data.news

        // 操作建议
        this.recomStats = data.recom

        // 正负新闻图
        this.renderMetricPosChart()
        this.renderMetricNegChart()

        // 每日数据图
        this.renderDaily()

        this.loading = false
      })
    },
    async getData() {
      await this.getInfo()
      await this.getDaily().then(() => {
        this.getNewsStats()
      })
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
    async getStockDailyBasic() {
      const params = {}
      params.ts_code = this.code
      params.start_date = dayjs().subtract(1, 'week').format('YYYYMMDD')
      getStockDailyBasic(params).then(data => {
        this.stockBasic = data.items[0]
      })
    },
    async getNewsItem(id) {
      const params = {}
      params.id = id
      getNewsItem(params).then(data => {
        this.activeRow = data
        this.dialogVisible = true
      })
    },
    onClickNewsItem(id) {
      this.getNewsItem(id)
    },
    getReasonItemClass(value) {
      if (value > 0) {
        return 'pos'
      } else if (value === 0) {
        return 'med'
      } else if (value < 0) {
        return 'neg'
      } else {
        return ''
      }
    },
    getReasonItemIconClass(value) {
      if (value > 0) {
        return 'fa-arrow-up'
      } else if (value === 0) {
        return 'fa-minus'
      } else if (value < 0) {
        return 'fa-arrow-down'
      } else {
        return ''
      }
    },
    getReasonItemText(type) {
      if (type === 'news') {
        if (this.recomStats.news > 0) {
          return '新闻舆情偏正面'
        } else if (this.recomStats.news === 0) {
          return '新闻舆情偏中性'
        } else if (this.recomStats.news < 0) {
          return '新闻舆情偏负面'
        } else {
          return ''
        }
      } else if (type === 'position') {
        if (this.recomStats.position > 0) {
          return '股价为低位'
        } else if (this.recomStats.position === 0) {
          return '股价为中位'
        } else if (this.recomStats.position < 0) {
          return '股价为高位'
        } else {
          return ''
        }
      } else if (type === 'trend') {
        if (this.recomStats.trend > 0) {
          return '股价趋势为涨'
        } else if (this.recomStats.trend === 0) {
          return '股价趋势为平稳'
        } else if (this.recomStats.trend < 0) {
          return '股价趋势为跌'
        } else {
          return ''
        }
      } else {
        return ''
      }
    },
    getRecomClass(value) {
      if (value > 0) {
        return 'buy'
      } else if (value === 0) {
        return 'hold'
      } else if (value < 0) {
        return 'sell'
      } else {
        return ''
      }
    },
    getRecomText(value) {
      if (value > 0) {
        return '买入'
      } else if (value === 0) {
        return '持有'
      } else if (value < 0) {
        return '卖出'
      } else {
        return ''
      }
    },
    _select(row) {
      const data = {}
      data._id = row._id
      data.class = row.class
      setNews(data).then(data => {
        this.$message.success('A news item has been tagged')
      })
    },
    selectUp(row) {
      this.$set(row, 'class', 1)
      this._select(row)
    },
    selectFlat(row) {
      this.$set(row, 'class', 0)
      this._select(row)
    },
    selectDown(row) {
      this.$set(row, 'class', -1)
      this._select(row)
    },
    getDateRangeClass(days) {
      return dayjs(this.dateRange[1]).diff(this.dateRange[0], 'day') === days ? 'active' : ''
    },
    onDateRangeClick(days) {
      this.dateRange = [
        dayjs().subtract(days, 'd'),
        dayjs().subtract(0, 'd')
      ]
    }
  },
  created() {
    if (this.$route.query.type) this.type = this.$route.query.type
    if (this.$route.query.code) this.code = this.$route.query.code
    this.getStockIndexList()
    this.getStockList()
    this.getData()
  },
  mounted() {
  }
}
</script>

<style scoped>
  #k-chart {
    height: 480px;
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
    height: 60px;
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
    display: flex;
    align-items: center;
  }

  .metric-item .value.buy {
    color: #ec0000;
  }

  .metric-item .value.hold {
    color: #E6A23C;
  }

  .metric-item .value.sell {
    color: #00da3c;
  }

  .metric-item .value i {
    font-size: 14px;
    color: #555;
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
    margin: 0;
    padding-top: 20px;
    padding-bottom: 0;
    color: #555;
  }

  .sub-title {
    font-weight: 300;
    font-size: 12px;
  }

  .reason-list {
    list-style: none;
    padding: 0 0 0 10px;
    margin: 0;
  }

  .reason-list .reason-item {
    color: #555;
    font-size: 11px;
    line-height: 1.2;
  }

  .reason-list .reason-item i {
    text-align: center;
    width: 12px;
  }

  .reason-list .reason-item.pos i {
    color: #ec0000;
  }

  .reason-list .reason-item.med i {
    color: #E6A23C;
  }

  .reason-list .reason-item.neg i {
    color: #00da3c;
  }

  .date-range-list {
    margin: 0;
    padding: 0;
    list-style: none;
    display: flex;
    font-size: 12px;
  }

  .date-range-list > li > a {
    color: #555;
    padding: 0 10px 0 0;
  }

  .date-range-list > li > a.active,
  .date-range-list > li > a:hover {
    color: #409EFF;
  }

  .control .left {
    display: flex;
    align-items: center;
  }

  .control .right {
    display: flex;
    align-items: center;
  }
</style>
