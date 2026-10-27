<script setup lang="ts">
import { Leaf, LayoutDashboard, ScanLine, History, BookOpen, Menu, X, ArrowUpRight, Upload, ImagePlus, ChevronRight, CircleHelp, Sprout, FileImage, LoaderCircle, Trash2, ChartNoAxesCombined, Database } from 'lucide-vue-next'
type Prediction = { label: string; title: string; confidence: number; probabilities: Record<string, number>; note: string; filename: string; date: string }
const tabs = [{ id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard }, { id: 'predict', label: 'Prediksi padi', icon: ScanLine }, { id: 'evaluation', label: 'Evaluasi model', icon: ChartNoAxesCombined }, { id: 'dataset', label: 'Dataset', icon: Database }]
const active = ref('dashboard')
const drawer = ref(false)
const sidebar = ref<HTMLElement>()
const menuButton = ref<HTMLButtonElement>()
const fileInput = ref<HTMLInputElement>()
const selected = ref<File | null>(null)
const preview = ref('')
const error = ref('')
const busy = ref(false)
const records = ref<Prediction[]>([])
const storageError = ref('')
const service = ref<'checking' | 'online' | 'offline'>('checking')
const title = computed(() => tabs.find(t => t.id === active.value)?.label)
const ripeCount = computed(() => records.value.filter(r => r.label === 'Ripe').length)
function navigate(id: string) { active.value = id; closeDrawer() }
function closeDrawer() { const wasOpen = drawer.value; drawer.value = false; if (wasOpen) nextTick(() => menuButton.value?.focus()) }
watch(drawer, async open => { document.body.style.overflow = open ? 'hidden' : ''; if (open) { await nextTick(); sidebar.value?.querySelector<HTMLButtonElement>('button')?.focus() } })
function trap(event: KeyboardEvent) {
  if (!drawer.value) return
  if (event.key === 'Escape') { closeDrawer(); return }
  if (event.key !== 'Tab') return
  const items = sidebar.value?.querySelectorAll<HTMLElement>('button, a[href]')
  if (!items?.length) return
  const first = items[0], last = items[items.length - 1]
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus() }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus() }
}
function choose(file?: File) {
  if (busy.value) return
  error.value = ''
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) { error.value = 'Pilih gambar JPG, PNG, atau WebP.'; return }
  if (file.size > 8 * 1024 * 1024) { error.value = 'Ukuran gambar maksimal 8 MB.'; return }
  if (preview.value) URL.revokeObjectURL(preview.value)
  selected.value = file; preview.value = URL.createObjectURL(file)
}
function clearPhoto() {
  if (busy.value) return
  if (preview.value) URL.revokeObjectURL(preview.value)
  selected.value = null; preview.value = ''; error.value = ''
  if (fileInput.value) fileInput.value.value = ''
}
function drop(event: DragEvent) { choose(event.dataTransfer?.files[0]) }
function persist() { try { localStorage.setItem('agrisense-history', JSON.stringify(records.value)) } catch { storageError.value = 'Riwayat hanya tersedia di sesi ini karena penyimpanan browser tidak tersedia.' } }
async function predict() {
  if (!selected.value || busy.value) return
  busy.value = true; error.value = ''
  const body = new FormData(); body.append('image', selected.value)
  try {
    const data = await $fetch<Omit<Prediction, 'filename' | 'date'>>('/api/predict', { method: 'POST', body, timeout: 120000 })
    const prediction: Prediction = { ...data, filename: selected.value.name, date: new Date().toISOString() }
    records.value = [prediction, ...records.value].slice(0, 50); persist(); service.value = 'online'
  } catch (e: any) { error.value = e.data?.error || 'Prediksi gagal. Pastikan backend Flask aktif, lalu coba lagi.' }
  finally { busy.value = false }
}
function clearHistory() { records.value = []; persist() }
function date(value: string) { return new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }).format(new Date(value)) }
onMounted(async () => {
  try { const saved = JSON.parse(localStorage.getItem('agrisense-history') || '[]'); if (Array.isArray(saved)) records.value = saved.filter(r => r && ['Raw','Ripe'].includes(r.label) && typeof r.filename === 'string' && Number.isFinite(r.confidence) && !isNaN(Date.parse(r.date))).slice(0,50) } catch { storageError.value = 'Riwayat tersimpan tidak dapat dibaca.' }
  try { const health = await $fetch<{ model_available: boolean }>('/api/health', { timeout: 5000 }); service.value = health.model_available ? 'online' : 'offline' } catch { service.value = 'offline' }
  window.addEventListener('keydown', trap)
})
onBeforeUnmount(() => { if (preview.value) URL.revokeObjectURL(preview.value); document.body.style.overflow = ''; window.removeEventListener('keydown', trap) })
</script>

<template>
  <div class="app-shell">
  <a class="skip" href="#main">Lewati ke konten</a>
  <button v-if="drawer" class="scrim" aria-label="Tutup navigasi" tabindex="-1" @click="closeDrawer" />
  <aside id="navigation" ref="sidebar" class="sidebar" :class="{ open: drawer }" :role="drawer ? 'dialog' : undefined" :aria-modal="drawer || undefined" aria-label="Navigasi utama">
    <div class="brand"><span class="brand-icon"><Leaf :size="24" /></span><span>agrisense<span class="brand-dot">.</span><small>Deteksi kematangan tanaman padi</small></span><button class="close-menu icon-button" aria-label="Tutup navigasi" @click="closeDrawer"><X /></button></div>
    <nav><button v-for="tab in tabs" :key="tab.id" :class="{ selected: active === tab.id }" :aria-current="active === tab.id ? 'page' : undefined" @click="navigate(tab.id)"><component :is="tab.icon" :size="20" /><span>{{ tab.label }}</span><ChevronRight v-if="active === tab.id" :size="16" /></button></nav>
    <div class="sidebar-bottom"><div class="research"><span class="research-title">Metode penelitian</span><b class="research-model">MobileNetV2 + TFLite</b><p>Transfer learning untuk mengenali kematangan padi melalui citra.</p></div></div>
  </aside>
  <div class="workspace" :inert="drawer || undefined">
    <header class="topbar"><div class="breadcrumb"><button ref="menuButton" class="icon-button hamburger" aria-label="Buka navigasi" aria-controls="navigation" :aria-expanded="drawer" @click="drawer = true"><Menu /></button><strong>AgriSense</strong></div><a class="github-button" href="https://github.com/ragraze/agrisense-webapp" target="_blank" rel="noopener noreferrer" aria-label="Lihat kode sumber AgriSense di GitHub (tab baru)">
      <img src="/github.svg" width="18" height="18" alt="" aria-hidden="true">
      <span>GitHub</span>
    </a></header>
    <main id="main" tabindex="-1">
      <div v-if="active !== 'dashboard'" class="page-heading"><div><h1>{{ title }}</h1><p>{{ active === 'predict' ? 'Unggah foto padi untuk menjalankan klasifikasi model.' : active === 'evaluation' ? 'Hasil pengujian model pada dataset uji proyek.' : active === 'dataset' ? 'Komposisi citra padi dan sumber data penelitian.' : 'Kenali pendekatan dan batasan model yang digunakan.' }}</p></div></div>
      <template v-if="active === 'dashboard'">
        <section class="overview-banner"><div class="banner-content"><span class="section-kicker">Klasifikasi kematangan padi</span><h2>Satu foto untuk<br>melihat lebih dekat.</h2><p>Gunakan citra malai padi untuk mengenali<br class="desktop-break"> kategori matang atau belum matang.</p></div><div class="grain-illustration" aria-hidden="true"><Sprout :size="190" :stroke-width="0.75" /><span>Oryza sativa</span></div></section>

        <div class="dashboard-columns"><section class="panel"><div class="panel-heading"><h2>Mulai dari foto padi</h2><span class="step-number">01 → 03</span></div><div class="steps"><div><span>01</span><section><h3>Siapkan citra</h3><p>Foto malai padi dengan cahaya cukup dan fokus yang jelas.</p></section></div><div><span>02</span><section><h3>Jalankan prediksi</h3><p>Unggah foto dan biarkan model membaca ciri visualnya.</p></section></div><div><span>03</span><section><h3>Tinjau hasilnya</h3><p>Lihat kategori kematangan dan probabilitas model.</p></section></div></div><button class="secondary full-width" @click="navigate('predict')"><Upload :size="18" /> Unggah foto padi <ArrowUpRight :size="17" /></button></section><section class="panel model-panel"><div class="panel-heading"><h2>Di balik prediksi</h2><BookOpen :size="19" /></div><span class="model-tag">Model klasifikasi citra</span><h3>MobileNetV2</h3><p>Transfer learning untuk mempelajari ciri visual kematangan padi.</p><dl><div><dt>Kategori keluaran</dt><dd>Raw & Ripe</dd></div><div><dt>Sumber model</dt><dd>TensorFlow Lite</dd></div><div><dt>Status berkas model</dt><dd class="service-state">{{ service === 'checking' ? 'Memeriksa…' : service === 'online' ? 'Tersedia' : 'Tidak terhubung' }}</dd></div></dl></section></div>
      </template>
      <template v-if="active === 'predict'">
        <section class="metrics" aria-label="Ringkasan prediksi"><article><span>Total prediksi <ScanLine :size="18" /></span><strong>{{ records.length.toString().padStart(2, '0') }}</strong><small>Tersimpan di browser ini</small></article><article><span>Padi matang <Sprout :size="18" /></span><strong>{{ ripeCount.toString().padStart(2, '0') }}<em>Ripe</em></strong><small>Hasil klasifikasi matang</small></article><article><span>Padi belum matang <Leaf :size="18" /></span><strong>{{ (records.length - ripeCount).toString().padStart(2, '0') }}<em>Raw</em></strong><small>Hasil klasifikasi belum matang</small></article></section>
        <div class="prediction-grid"><section class="panel"><div class="panel-heading"><h2>Citra padi</h2></div><button class="dropzone" :disabled="busy" @click="fileInput?.click()" @dragover.prevent @drop.prevent="drop"><img v-if="preview" :src="preview" alt="Pratinjau citra padi yang dipilih"><template v-else><ImagePlus :size="38" :stroke-width="1.3" /><strong>Pilih foto padi</strong><span>atau seret gambar ke sini</span></template><small>{{ selected ? 'Ketuk untuk mengganti foto' : 'JPG, PNG, WebP · Maksimal 8 MB' }}</small></button><input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" class="visually-hidden" :disabled="busy" aria-label="Pilih gambar padi" @change="choose(($event.target as HTMLInputElement).files?.[0])"><p v-if="selected" class="filename"><FileImage :size="17" />{{ selected.name }}</p><button v-if="selected" type="button" class="text-link" :disabled="busy" @click="clearPhoto"><Trash2 :size="17" />Hapus foto</button><p v-if="error" role="alert" class="error">{{ error }}</p><button class="primary full-width" :disabled="!selected || busy" @click="predict"><LoaderCircle v-if="busy" class="spin" :size="18" /><ScanLine v-else :size="18" />{{ busy ? 'Menganalisis gambar…' : 'Prediksi kematangan' }}</button><p class="helper">Gunakan foto malai padi. Gambar dikirim ke server untuk dianalisis dan tidak disimpan oleh aplikasi.</p></section></div>
      </template>
      <section v-if="active === 'predict'" class="panel prediction-history" :aria-busy="busy">
        <div class="panel-heading"><h2>Hasil prediksi</h2><button v-if="records.length" class="text-link" :disabled="busy" @click="clearHistory"><Trash2 :size="17" /> Hapus riwayat</button></div>
        <p v-if="storageError" role="status" class="helper">{{ storageError }}</p>
        <p v-if="busy" class="prediction-status" role="status"><LoaderCircle class="spin" :size="18" /> Model sedang membaca citra…</p>
        <div v-if="!records.length && !busy" class="empty-result"><History :size="42" :stroke-width="1" /><h3>Belum ada prediksi</h3><p>Pilih foto padi di atas, lalu jalankan prediksi. Hasil dan riwayatnya akan tersimpan di sini.</p></div>
        <p v-if="records.length" class="helper" role="status">{{ records.length }} hasil tersimpan di browser ini. Hasil terbaru berada di atas.</p>
        <details v-for="(record, index) in records" :key="record.date + index" class="prediction-record" :open="index === 0">
          <summary><span class="record-heading"><strong>{{ record.title }}</strong><small>{{ record.filename }}</small><small>{{ date(record.date) }}</small></span><span class="record-confidence">{{ (record.confidence * 100).toFixed(1) }}%</span><ChevronRight :size="18" class="record-chevron" aria-hidden="true" /></summary>
          <div class="record-analysis"><span class="model-tag">{{ record.label }}</span><p class="helper">Probabilitas kategori terpilih</p><strong class="confidence">{{ (record.confidence * 100).toFixed(1) }}<small>%</small></strong><div v-for="(value, label) in record.probabilities" :key="label" class="probability"><div><span>{{ label === 'Ripe' ? 'Matang' : 'Belum matang' }}</span><b>{{ (value * 100).toFixed(1) }}%</b></div><meter :value="value" min="0" max="1" :aria-label="label === 'Ripe' ? 'Probabilitas matang' : 'Probabilitas belum matang'">{{ value }}</meter></div><p class="result-note"><CircleHelp :size="19" />{{ record.note }}</p></div>
        </details>
      </section>
      <DatasetPanel v-if="active === 'dataset'" />
      <EvaluationPanel v-if="active === 'evaluation'" />
      <template v-if="active === 'dashboard'"><section id="research-method" class="panel method-intro dashboard-method"><span class="section-kicker">Metode penelitian</span><h2>Transfer learning.<br>Fokus pada kematangan padi.</h2><p>AgriSense menggunakan MobileNetV2 sebagai ekstraktor fitur citra. Lapisan klasifikasi menghasilkan satu skor untuk membedakan padi belum matang (Raw) dan matang (Ripe).</p><div class="method-flow"><span>Foto padi</span><ChevronRight :size="18" /><span>Praproses citra</span><ChevronRight :size="18" /><span>MobileNetV2</span><ChevronRight :size="18" /><span>Raw / Ripe</span></div></section><div class="dashboard-columns"><section class="panel"><h2>Praproses & interpretasi</h2><p>Citra dikoreksi orientasinya, diubah menjadi RGB, lalu disesuaikan dengan dimensi input model. Notebook pelatihan menggunakan 160 × 160 piksel dan normalisasi pixel / 127.5 − 1.</p><p>Model dilatih dengan binary cross-entropy dari logit. Skor di atas nol dipetakan ke Ripe, mengikuti notebook proyek. Probabilitas dihitung dengan fungsi sigmoid.</p></section><section class="panel"><h2>Batasan penelitian</h2><p>Probabilitas model bukan ukuran akurasi. Pencahayaan, sudut pengambilan, dan latar foto dapat memengaruhi hasil.</p><p>Label matang tidak menetapkan tanggal panen. Periksa kondisi padi secara langsung sebelum mengambil keputusan.</p></section></div></template>
      <footer class="page-footer"><span><Leaf :size="14" /> AgriSense</span><span>MobileNetV2 / TensorFlow Lite</span></footer>
    </main>

  </div>
  </div>
</template>
