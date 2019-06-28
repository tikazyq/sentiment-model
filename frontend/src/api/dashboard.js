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

export function getIndexList(params) {
  if (!params) params = {}
  return request({
    url: '/stock/index_basic',
    method: 'get',
    params
  })
}

