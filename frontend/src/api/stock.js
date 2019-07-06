import request from '../utils/request'

export function getStockDaily(params) {
  if (!params) params = {}
  return request({
    url: '/stock/daily',
    method: 'get',
    params
  })
}

export function getIndexDaily(params) {
  if (!params) params = {}
  return request({
    url: '/stock/index_daily',
    method: 'get',
    params
  })
}

export function getStockList(params) {
  if (!params) params = {}
  return request({
    url: '/stock/stock_basic',
    method: 'get',
    params
  })
}

export function getStockListStats(params) {
  if (!params) params = {}
  return request({
    url: '/stats/get_stock_list',
    method: 'get',
    params
  })
}

export function getIndustryListStats(params) {
  if (!params) params = {}
  return request({
    url: '/stats/get_industry_list',
    method: 'get',
    params
  })
}

export function getStockIndexList(params) {
  if (!params) params = {}
  params.page_size = 999999
  return request({
    url: '/stock_indexes',
    method: 'get',
    params
  })
}

export function getNewsStats(params) {
  if (!params) params = {}
  return request({
    url: '/stats/get_news_stats',
    method: 'get',
    params
  })
}

export function getStock(params) {
  if (!params) params = {}
  return request({
    url: '/stocks/' + params._id,
    method: 'get',
    params
  })
}

export function getStockIndex(params) {
  if (!params) params = {}
  return request({
    url: '/stock_indexes/' + params._id,
    method: 'get',
    params
  })
}

export function getStockDailyBasic(params) {
  if (!params) params = {}
  return request({
    url: '/stock/daily_basic',
    method: 'get',
    params
  })
}

export function getNews(params) {
  if (!params) params = {}
  params.page_size = 999999
  params.filter = JSON.stringify({
    stocks: params.code,
    class_final: {
      $in: [-1, 1]
    }
  })
  params.sort_key = 'ts'
  return request({
    url: '/news',
    method: 'get',
    params
  })
}
