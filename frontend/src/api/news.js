import request from '../utils/request'

export function getList(params) {
  if (!params) params = {}
  // params.page_size = 999999
  // params.page_num = 1
  return request({
    url: '/news',
    method: 'get',
    params
  })
}

export function setNews(data) {
  return request({
    url: '/news/' + data._id,
    method: 'post',
    data
  })
}
