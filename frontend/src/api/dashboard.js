import request from '../utils/request'

export function getStockDaily(params) {
  if (!params) params = {}
  return request({
    url: '/stock/daily',
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
