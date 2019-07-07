<template>
  <div class="app-container">
    <el-tabs v-model="exchange" type="card">
      <el-tab-pane label="上海证券交易所" name="SH"></el-tab-pane>
      <el-tab-pane label="深证证券交易所" name="SZ"></el-tab-pane>
    </el-tabs>
    <div class="filter">
      <div class="left">
        <el-select
          v-model="market"
          size="small"
          filterable
        >
          <el-option label="全部" value="all"/>
          <el-option label="主板" value="主板"/>
          <el-option label="中小板" value="中小板"/>
          <el-option label="创业板" value="创业板"/>
        </el-select>
        <el-select
          v-model="industry"
          size="small"
          filterable
        >
          <el-option label="全部" value="all"/>
          <el-option v-for="op in industryList.filter(d => d)" :key="op" :label="op" :value="op"/>
          <el-option label="其他" value=""/>
        </el-select>
        <div class="summary">
          {{stockList.length}}支股票
        </div>
      </div>
      <div class="right">
        <el-date-picker
          type="daterange"
          v-model="dateRange"
          size="small"
        />
      </div>
    </div>
    <el-table
      v-loading="loading"
      class="table"
      :data="filteredStockList"
      border
      @row-click="onRowClick"
    >
      <el-table-column
        label="代码"
        prop="ts_code"
        width="100px"
      />
      <el-table-column
        label="名称"
        prop="name"
        width="100px"
      />
      <el-table-column
        label="类型"
        prop="market"
        width="100px"
      />
      <el-table-column
        label="行业"
        prop="industry"
        width="100px"
      />
      <el-table-column
        label="地区"
        prop="area"
        width="100px"
      />
      <el-table-column
        label="挂牌日期"
        prop="list_date"
        width="100px"
      />
      <el-table-column
        label="正面"
        prop="news_pos"
        width="100px"
      />
      <el-table-column
        label="负面"
        prop="news_neg"
        width="100px"
      />
      <el-table-column
        label="中性"
        prop="news_med"
        width="100px"
      />
      <el-table-column
        label="总新闻"
        prop="news_total"
        width="100px"
      />
    </el-table>
    <el-pagination
      :total="stockList.length"
      :page-size.sync="pageSize"
      :current-page.sync="pageNum"
    />
  </div>
</template>

<script>
import dayjs from 'dayjs'
import {
  getStockListStats,
  getIndustryListStats
} from '../../api/stock'

export default {
  name: 'StockList',
  data() {
    return {
      exchange: 'SH',
      market: 'all',
      industry: 'all',
      industryList: [],
      dateRange: [
        dayjs().subtract(1, 'month'),
        dayjs().subtract(0, 'd')
      ],
      pageNum: 1,
      pageSize: 50,
      stockList: []
    }
  },
  computed: {
    filteredStockList() {
      return this.stockList.filter((d, i) => {
        return this.pageSize * (this.pageNum - 1) <= i && i < this.pageSize * this.pageNum
      })
    }
  },
  watch: {
    exchange() {
      this.getStockListStats()
    },
    market() {
      this.getStockListStats()
    },
    industry() {
      this.getStockListStats()
    }
  },
  methods: {
    getStockListStats() {
      this.loading = true
      const params = {}
      params.exchange = this.exchange
      params.industry = this.industry === 'all' ? undefined : this.industry
      params.market = this.market === 'all' ? undefined : this.market
      params.start_date = dayjs(this.dateRange[0]).format('YYYYMMDD')
      params.end_date = dayjs(this.dateRange[1]).add(1, 'day').format('YYYYMMDD')
      getStockListStats(params)
        .then(data => {
          this.stockList = data.stocks
          this.loading = false
        })
    },
    getIndustryListStats() {
      getIndustryListStats().then(data => {
        this.industryList = data.industries
      })
    },
    onRowClick(row, column, event) {
      this.$router.push('/stock/detail?code=' + row.ts_code)
    }
  },
  created() {
    this.getIndustryListStats()
    this.getStockListStats()
  }
}
</script>

<style scoped>
  .filter {
    display: flex;
    justify-content: space-between;
  }

  .filter .left {
    align-items: center;
    display: flex;
  }

  .filter .left .el-select {
    margin-right: 10px;
  }

  .summary {
    color: #606266;
    font-size: 12px;
  }

  .el-table {
    min-height: 480px;
    margin-top: 10px;
    border-radius: 5px;
  }

  .el-table >>> .cell {
    font-size: 12px;
  }

  .el-table >>> th,
  .el-table >>> td {
    padding: 5px 0;
  }

  .el-table >>> tbody tr {
    cursor: pointer;
  }
</style>
