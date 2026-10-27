export default defineNuxtConfig({
  compatibilityDate: '2025-10-01',
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  runtimeConfig: { apiBase: 'http://127.0.0.1:5000' },
  app: { head: { title: 'AgriSense · Kematangan padi', htmlAttrs: { lang: 'id' }, meta: [{ name: 'description', content: 'Dashboard penelitian kematangan padi menggunakan MobileNetV2.' }, { name: 'theme-color', content: '#B23724' }] } }
})
