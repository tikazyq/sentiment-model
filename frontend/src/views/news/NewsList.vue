<template>
  <div class="app-container">
    <el-row>
      <el-table
        :data="tableData"
        stripe
      >
        <el-table-column
          prop="id"
          label="ID"
          width="120"
        />
        <el-table-column
          prop="text"
          label="新闻"
          width="auto"
        />
        <el-table-column
          label="涉及股票"
          width="200"
        >
          <template slot-scope="scope">
            <el-tag size="mini" v-for="s in scope.row.stocks" :key="s" @click="clickStock(s)">
              {{s}}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="预测"
          width="100"
          align="center"
        >
          <template slot-scope="scope">
            <el-button
              plain
              size="mini"
              :type="getClassType(scope.row.class_pred)"
              :icon="getClassIcon(scope.row.class_pred)"
            />
          </template>
        </el-table-column>
        <el-table-column
          label="实际"
          width="200"
          fixed="right"
          align="center"
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
        :total="tableDataTotal"
        @current-change="getList"
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
  computed: {},
  methods: {
    getList() {
      const params = {
        page_size: this.pageSize,
        page_num: this.pageNum
      }
      getList(params).then(data => {
        this.tableData = data.items
        this.tableDataTotal = data.total_count
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
    },
    getClassType(cls) {
      if (cls === -1) {
        return 'success'
      } else if (cls === 0) {
        return 'info'
      } else if (cls === 1) {
        return 'danger'
      }
    },
    getClassIcon(cls) {
      if (cls === -1) {
        return 'el-icon-bottom'
      } else if (cls === 0) {
        return 'el-icon-minus'
      } else if (cls === 1) {
        return 'el-icon-top'
      }
    },
    clickStock(s) {
      this.$router.push({
        path: '/dashboard',
        query: {
          type: 'stock',
          code: s
        }
      })
    }
  },
  created() {
    this.getList()
  }
}
</script>

<style scoped>
  .el-tag {
    margin: 5px;
    cursor: pointer;
  }

  .el-tag:hover {
    text-decoration: underline;
  }
</style>
