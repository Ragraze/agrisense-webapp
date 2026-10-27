<script setup lang="ts">
import { RefreshCw, Download, CircleHelp, LoaderCircle } from 'lucide-vue-next'
type ClassMetrics = { precision: number; recall: number; f1: number; support: number }
type Evaluation = {
  accuracy: number; macro_avg: { precision: number; recall: number; f1: number }
  sample_count: number; correct_count: number; skipped_count: number
  labels: string[]; confusion_matrix: number[][]; per_class: Record<string, ClassMetrics>
  evaluated_at: string; model_sha256: string; dataset_sha256: string
  exact_duplicate_test_images: number; exact_test_overlap_with_train_valid: number
}
const report = ref<Evaluation | null>(null)
const loading = ref(false)
const error = ref('')
const percent = (value: number) => new Intl.NumberFormat('id-ID', { style: 'percent', maximumFractionDigits: 1 }).format(value)
const evaluatedAt = computed(() => report.value ? new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(report.value.evaluated_at)) : '')
async function load() {
  loading.value = true; error.value = ''
  try { report.value = await $fetch<Evaluation>('/api/evaluation', { timeout: 15000 }) }
  catch (e: any) { report.value = null; error.value = e.data?.error || 'Laporan belum dapat dimuat. Periksa koneksi backend, lalu coba lagi.' }
  finally { loading.value = false }
}
onMounted(load)
</script>

<template>
  <div class="evaluation" :aria-busy="loading">
    <section v-if="loading" class="panel empty-result" role="status"><LoaderCircle class="spin" :size="32" /><h2>Memuat hasil evaluasi</h2><p>Mengambil laporan pengujian model yang tersimpan.</p></section>
    <section v-else-if="error" class="panel"><h2>Laporan belum tersedia</h2><p role="alert" class="error">{{ error }}</p><button class="secondary" @click="load"><RefreshCw :size="17" /> Muat ulang laporan</button></section>
    <template v-else-if="report">
      <section class="panel evaluation-summary"><span class="section-kicker">Dataset uji · MobileNetV2</span><h2>Seberapa baik model<br>mengenali kematangan?</h2><p>Hasil inferensi pada <strong>{{ report.sample_count }} gambar</strong> di <code>dataset/test</code>, menggunakan label folder sebagai acuan.</p><div class="evaluation-score"><strong>{{ percent(report.accuracy) }}</strong><span>Akurasi dataset uji</span></div><p class="helper">{{ report.correct_count }} benar · {{ report.sample_count - report.correct_count }} salah · {{ report.skipped_count }} dilewati</p><small class="evaluation-date">Dievaluasi {{ evaluatedAt }}</small></section>
      <section class="evaluation-metrics" aria-label="Rata-rata macro"><article><span>Precision macro</span><strong>{{ percent(report.macro_avg.precision) }}</strong></article><article><span>Recall macro</span><strong>{{ percent(report.macro_avg.recall) }}</strong></article><article><span>F1-score macro</span><strong>{{ percent(report.macro_avg.f1) }}</strong></article></section>
      <p class="helper evaluation-caption">Macro memberi bobot yang sama untuk kelas Raw dan Ripe, meskipun jumlah gambarnya berbeda.</p>
      <section class="panel"><h2>Confusion matrix</h2><p class="helper">Baris = label sebenarnya. Kolom = prediksi model. Sel diagonal menunjukkan prediksi benar.</p><table class="confusion-table"><caption>Jumlah gambar per label dan prediksi</caption><thead><tr><th scope="col">Aktual ↓<br>Prediksi →</th><th v-for="label in report.labels" :key="label" scope="col">{{ label }}</th></tr></thead><tbody><tr v-for="(row, i) in report.confusion_matrix" :key="i"><th scope="row">{{ report.labels[i] }}</th><td v-for="(count, j) in row" :key="j" :class="{ correct: i === j }"><strong>{{ count }}</strong><small>{{ i === j ? 'Benar' : 'Salah' }}</small></td></tr></tbody></table></section>
      <section class="panel"><h2>Hasil per kelas</h2><article v-for="label in report.labels" :key="label" class="class-report"><header><strong>{{ label === 'Raw' ? 'Raw · Belum matang' : 'Ripe · Matang' }}</strong><span>{{ report.per_class[label]?.support }} gambar</span></header><dl><div><dt>Precision</dt><dd>{{ percent(report.per_class[label]!.precision) }}</dd></div><div><dt>Recall</dt><dd>{{ percent(report.per_class[label]!.recall) }}</dd></div><div><dt>F1-score</dt><dd>{{ percent(report.per_class[label]!.f1) }}</dd></div></dl></article><details class="metric-explanation"><summary>Bagaimana membaca metrik ini?</summary><p><b>Precision:</b> dari semua prediksi suatu kelas, berapa bagian yang benar.</p><p><b>Recall:</b> dari semua gambar asli suatu kelas, berapa bagian yang berhasil dikenali.</p><p><b>F1-score:</b> rata-rata harmonik precision dan recall. Nilai lebih tinggi menunjukkan hasil lebih baik pada dataset ini.</p></details></section>
      <section class="panel evaluation-notes"><div class="panel-heading"><h2>Konteks pengujian</h2><CircleHelp :size="19" /></div><p>Model dan praproses sama dengan fitur prediksi: RGB, ukuran input 160 × 160, normalisasi −1 hingga 1. Logit &gt; 0 dipetakan ke Ripe, selainnya Raw.</p><dl><div><dt>Duplikat identik di data uji</dt><dd>{{ report.exact_duplicate_test_images }}</dd></div><div><dt>Gambar uji identik dengan train/valid</dt><dd>{{ report.exact_test_overlap_with_train_valid }}</dd></div></dl><p>Pemeriksaan duplikat hanya membandingkan isi berkas yang identik. Gambar augmentasi, hasil resize, dan frame video berdekatan masih dapat saling berkaitan. Independensi pembagian dataset belum diverifikasi.</p><p>Label mengikuti folder dataset dan belum diaudit secara independen. Hasil ini bukan jaminan akurasi di lapangan atau penentu tanggal panen.</p><details class="metric-explanation"><summary>Identitas laporan</summary><p>SHA-256 model</p><code class="report-hash">{{ report.model_sha256 }}</code><p>SHA-256 manifest dataset uji</p><code class="report-hash">{{ report.dataset_sha256 }}</code></details><a class="secondary full-width" href="/api/evaluation" download="agrisense-evaluation.json"><Download :size="17" /> Unduh laporan JSON</a><p class="helper">Laporan tersimpan dari evaluasi offline, bukan dihitung ulang ketika halaman dibuka. Model aktif diverifikasi menggunakan hash.</p></section>
    </template>
  </div>
</template>
