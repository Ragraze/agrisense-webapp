<script setup lang="ts">
import { ArrowUpRight, RefreshCw, LoaderCircle } from 'lucide-vue-next'
type Dataset = {
  name: string; version: string; total: number; labels: string[]; license: string
  class_totals: Record<string, number>; splits: { name: string; counts: Record<string, number>; total: number }[]
  generated_at: string; exported_at: string
}
const report = ref<Dataset | null>(null)
const loading = ref(false)
const error = ref('')
const names: Record<string, string> = { train: 'Training', valid: 'Validasi', test: 'Test' }
const purposes: Record<string, string> = { train: 'Melatih model mengenali ciri kematangan padi.', valid: 'Memantau performa selama pengembangan model.', test: 'Mengukur hasil klasifikasi pada halaman Evaluasi model.' }
const number = (value: number) => new Intl.NumberFormat('id-ID').format(value)
const percent = (value: number) => new Intl.NumberFormat('id-ID', { style: 'percent', maximumFractionDigits: 1 }).format(value)
const date = (value: string) => new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium' }).format(new Date(value))
async function load() {
  loading.value = true; error.value = ''
  try { report.value = await $fetch<Dataset>('/api/dataset', { timeout: 15000 }) }
  catch (e: any) { report.value = null; error.value = e.data?.error || 'Informasi dataset gagal dimuat. Periksa koneksi backend dan coba lagi.' }
  finally { loading.value = false }
}
onMounted(load)
</script>

<template>
  <div class="dataset-view" :aria-busy="loading">
    <section v-if="loading" class="panel empty-result" role="status"><LoaderCircle :size="32" class="spin" /><h2>Memuat informasi dataset</h2><p>Mengambil inventaris gambar penelitian.</p></section>
    <section v-else-if="error" class="panel"><h2>Dataset belum dapat ditampilkan</h2><p class="error" role="alert">{{ error }}</p><button class="secondary" @click="load"><RefreshCw :size="17" /> Muat ulang dataset</button></section>
    <template v-else-if="report">
      <section class="panel dataset-overview"><span class="section-kicker">Paddy · Versi {{ report.version }}</span><h2>Data di balik<br>klasifikasi padi.</h2><strong class="dataset-total">{{ number(report.total) }}<small>gambar padi</small></strong><p>Dua kelas kematangan, terbagi ke dalam data training, validasi, dan test.</p><div class="dataset-classes"><div v-for="label in report.labels" :key="label"><span>{{ label }}</span><strong>{{ number(report.class_totals[label]!) }}</strong><small>{{ label === 'Raw' ? 'Belum matang' : 'Matang' }}</small></div></div></section>
      <section class="panel"><h2>Pembagian dataset</h2><p class="helper">Jumlah berkas gambar di setiap folder dataset proyek.</p><article v-for="split in report.splits" :key="split.name" class="dataset-split"><header><h3>{{ names[split.name] }}</h3><span>{{ number(split.total) }} gambar <b>{{ percent(split.total / report.total) }}</b></span></header><p>{{ purposes[split.name] }}</p><dl><div v-for="label in report.labels" :key="label"><dt>{{ label }}</dt><dd>{{ number(split.counts[label]!) }}</dd></div></dl></article><p class="helper">Inventaris dibuat {{ date(report.generated_at) }}. Angka merupakan snapshot berkas saat inventaris dibuat.</p></section>
      <section class="panel"><h2>Label kelas</h2><article class="dataset-label"><strong>Raw · Belum matang</strong><p>Citra padi pada folder Raw, dengan label belum matang.</p></article><article class="dataset-label"><strong>Ripe · Matang</strong><p>Citra padi pada folder Ripe, dengan label matang.</p></article><p class="helper">Label mengikuti nama folder sumber, bukan hasil prediksi model. Label belum diaudit secara independen.</p></section>
      <section class="panel dataset-source"><h2>Sumber & pengolahan</h2><dl><div><dt>Dataset</dt><dd>{{ report.name }} v{{ report.version }}</dd></div><div><dt>Platform</dt><dd>Roboflow Universe</dd></div><div><dt>Lisensi data</dt><dd>{{ report.license }}</dd></div><div><dt>Ekspor sumber</dt><dd>{{ date(report.exported_at) }}</dd></div></dl><p>README ekspor mencatat koreksi orientasi otomatis dan resize menjadi 640 × 640 piksel dengan metode stretch. Tidak ada augmentasi saat ekspor yang didokumentasikan.</p><p>Sebelum inferensi, aplikasi menyesuaikan citra ke input model 160 × 160 piksel dan normalisasi −1 hingga 1.</p><a class="secondary full-width" href="https://universe.roboflow.com/agrisense-dataset/paddy-o34tk" target="_blank" rel="noopener noreferrer">Buka dataset di Roboflow <ArrowUpRight :size="17" /></a><p class="helper">Atribusi berdasarkan README dataset proyek. Hubungan antar-frame atau gambar serupa lintas split belum diverifikasi; hasil evaluasi tidak otomatis mewakili kondisi lapangan.</p></section>
    </template>
  </div>
</template>
