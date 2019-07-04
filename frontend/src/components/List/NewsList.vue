<template>
  <ul class="news-list">
    <li
      v-for="n in newsList"
      :key="n._id"
      class="news-item"
    >
      <div class="time">
        {{n.ts}}
      </div>
      <div class="text">
        {{n.title ? n.title : n.text}}
      </div>
    </li>
  </ul>
</template>

<script>
import dayjs from 'dayjs'

export default {
  name: 'NewsList',
  props: {
    newsList: {
      type: Array,
      default() {
        return []
      }
    }
  },
  methods: {
    dayjs(value) {
      return dayjs(value)
    }
  }
}
</script>

<style scoped>
  .news-list {
    border: 1px solid #999;
    border-radius: 5px;
    margin: 5px 0;
    padding: 0;
    list-style: none;
    height: 480px;
    overflow-y: auto;
  }

  .news-item {
    /*margin: 5px;*/
    padding: 5px;
    display: flex;
  }

  .news-item:nth-of-type(odd) {
    background: #eee;
  }

  .news-item:hover {
    background: rgb(245, 245, 245);
    cursor: pointer;
  }

  .news-item .text {
    font-size: 12px;
    color: #555;
    flex-basis: calc(100% - 60px);
    padding-left: 10px;
  }

  .news-item .time {
    font-size: 11px;
    color: #999;
    text-align: right;
    flex-basis: 60px;
  }
</style>
