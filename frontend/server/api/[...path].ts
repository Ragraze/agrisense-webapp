export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event)
  const path = getRouterParam(event, 'path') || ''
  return proxyRequest(event, `${config.apiBase}/api/${path}${getRequestURL(event).search}`)
})
