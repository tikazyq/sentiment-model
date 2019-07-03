<template>
  <div class="app-container">
    <el-dialog
      :visible.sync="dialogVisible"
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
      <el-table
        :data="tableData"
        stripe
      >
        <el-table-column
          prop="source"
          label="来源"
          width="80"
        >
          <template slot-scope="scope">
            <div class="small-text">
              {{scope.row.source}}
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="ts"
          label="时间"
          width="150"
        >
          <template slot-scope="scope">
            <div class="small-text">
              {{scope.row.ts}}
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="text"
          label="新闻"
          min-width="400"
          width="auto"
        >
          <template slot-scope="scope">
            <p class="text" @click="showDetail(scope.row)">
              {{scope.row.title ? scope.row.title : scope.row.text}}
            </p>
          </template>
        </el-table-column>
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
      pageSize: 10,
      dialogVisible: false,
      activeRow: {}
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
    },
    showDetail(row) {
      this.activeRow = row
      this.dialogVisible = true
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

  .text {
    cursor: pointer;
  }

  .text:hover {
    text-decoration: underline;
  }

  .small-text {
    font-size: 12px;
  }

  .dialog-text {
    max-height: 480px;
    overflow-y: auto;
  }
</style>
