<template>
  <div class="app-container">
    <el-row>
      <div class="metric-list">
        Metric List
      </div>
    </el-row>
    <el-row>
      <div class="">
        <el-select
          v-model="stockCode"
          filterable
        >
          <el-option
            v-for="op in stockList"
            :key="op.ts_code"
            :label="`${op.name} (${op.ts_code})`"
            :value="op.ts_code"
          />
        </el-select>
      </div>
      <div class="k-chart">
        Daily K-Chart
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
import {
  getStockList,
  getStockDaily,
} from '../../api/dashboard'

export default {
  name: 'Dashboard',
  data() {
    return {
      stockCode: '',
      stockList: [],
      dailyList: []
    }
  },
  methods: {
    getStockList() {
      const params = {}
      params.exchange = 'SSE'
      // params.ts_code = this.stockCode
      // params.start_date = dayjs().subtract(30, 'd').format('YYYYMMDD')
      // params.end_date = dayjs().subtract(0, 'd').format('YYYYMMDD')
      getStockList(params).then(data => {
        this.stockList = data.items
      })
    },
    getStockDaily() {
      const params = {}
      params.ts_code = this.stockCode
      params.start_date = dayjs().subtract(30, 'd').format('YYYYMMDD')
      params.end_date = dayjs().subtract(0, 'd').format('YYYYMMDD')
      getStockDaily(params).then(data => {
        this.stockList = data.items
      })
    }
  },
  created() {
    // this.getStockList()
  }
}
</script>

<style scoped>
  .metric-list {
    border: 1px solid grey;
    height: 150px;
  }

  .k-chart {
    margin-top: 20px;
    border: 1px solid grey;
    height: 400px;
  }

  .news-list {
    margin-top: 20px;
    border: 1px solid grey;
    height: 400px;
  }
</style>
