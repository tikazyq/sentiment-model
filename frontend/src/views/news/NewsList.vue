<template>
  <div class="app-container">
    <el-row>
      <el-table
        :data="filteredTableData"
        stripe
      >
        <el-table-column
          prop="id"
          label="ID"
          width="120"
        />
        <el-table-column
          prop="text"
          label="Text"
          width="auto"
        />
        <el-table-column
          label="Action"
          width="200"
          fixed="right"
        >
          <template slot-scope="scope">
            <el-button
              type="danger"
              :plain="scope.row.class!==1"
              size="mini"
              icon="el-icon-top"
              @click="selectUp(scope.row)"
            />
            <el-button
              type="info"
              :plain="scope.row.class!==0"
              size="mini"
              icon="el-icon-minus"
              @click="selectFlat(scope.row)"
            />
            <el-button
              type="success"
              :plain="scope.row.class!==-1"
              size="mini"
              icon="el-icon-bottom"
              @click="selectDown(scope.row)"
            />
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        :current-page.sync="pageNum"
        :page-size.sync="pageSize"
        :total="tableData.length"
      />
    </el-row>
  </div>
</template>

<script>
import {
  getList,
  setNews
} from '../../api/news'

export default {
  name: 'NewsList',
  data() {
    return {
      tableData: [],
      pageNum: 1,
      pageSize: 10
    }
  },
  computed: {
    filteredTableData() {
      return this.tableData.filter((d, i) => {
        return this.pageSize * (this.pageNum - 1) <= i && i < this.pageSize * this.pageNum
      })
    }
  },
  methods: {
    getList() {
      getList().then(data => {
        this.tableData = data.items
      })
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
    }
  },
  created() {
    this.getList()
  }
}
</script>

<style scoped>
</style>
