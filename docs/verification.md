# Verifikasi implementasi

27 Oktober 2026. Pengujian lokal melalui Nuxt dev server dan Flask; tidak menjalankan build Docker atau build produksi.

- PASS — `npm run typecheck`.
- PASS — `python3 -m pytest backend/tests -q`: 4 tes.
- PASS — Inferensi TFLite asli lewat Flask untuk satu foto Raw dan satu foto Ripe; HTTP 200. Bukan pengukuran akurasi model.
- PASS — Proxy Nuxt → Flask → model: HTTP 200.
- PASS — Swagger UI dan JSON OpenAPI: HTTP 200.
- PASS — Playwright Chromium: lebar 320, 390, 768, 1024, 1440; `scrollWidth <= innerWidth`.
- PASS — Browser: unggah → prediksi asli → hasil, riwayat tersimpan setelah reload, hapus riwayat, halaman metode, hamburger dan Escape.
- PASS — Browser: unggahan teks ditolak; respons 503 menghasilkan pesan kesalahan.
- PASS — Tidak ada pageerror pada rangkaian pengujian browser.
- PASS — Screenshot desktop/mobile diperiksa secara visual; artefak `desktop.png` dan `mobile.png`.

## Antislop delivery gate

### Hard gate

- R-02 PASS: salinan UI tidak mengandung em dash.
- R-03 PASS: pemeriksaan overflow browser pada lima ukuran layar.
- R-17 PASS: ringkasan dihitung dari riwayat prediksi pengguna, tanpa statistik contoh.
- R-18 PASS: tidak ada testimonial.
- R-23 PASS: palet dan navigasi mengikuti permintaan pengguna; ikon berasal dari set yang tersedia, tanpa gambar baru atau profil rekaan.
- R-24 PASS: empat navigasi merender halaman yang tersedia.
- R-25 PASS: warna teks utama diuji dengan contrast-check.py; snow/red 5.86:1, muted/pale 5.06:1, green/pale 5.48:1, sidebar secondary/red 5.20:1.
- R-26 PASS: tombol memiliki handler nyata; alur utama diuji melalui browser.
- R-27 PASS: empty, loading, dan error ditulis pada prediksi dan riwayat; error upload dan server diuji.
- R-28 PASS: tidak ada FAQ.
- R-32 PASS: tombol native, focus-visible, skip link, focus trap drawer, dan Escape; Escape diuji di browser.
- R-33 PASS: perilaku ditulis pada sumber Vue/Flask dan stylesheet proyek, tanpa injeksi runtime.
- R-34 PASS: hanya tema terang yang diminta dan disediakan.
- R-35 PASS: aplikasi dijalankan; alur browser dan screenshot tercatat di atas. Tidak ada build Docker.
- R-36 PASS: tidak ada klaim keamanan, akurasi, atau kinerja buatan.
- R-37 PASS: arah pengguna merah PowerPoint/snow white, mobile, sidebar dan metode diterapkan; keputusan dicatat di DESIGN.md.
- R-38 PASS: semua hasil berasal dari API; belum ada prediksi berarti ringkasan nol.

### Purpose gate

- R-01 PASS: tanpa gradien/glow; warna mengikuti arahan pengguna.
- R-04 PASS: ikon ScanLine, History, BookOpen, dan tanaman sesuai fungsi; alasan di DESIGN.md.
- R-06 PASS: font sistem untuk keterbacaan; tanpa label kapital berjarak lebar.
- R-07 PASS: tanpa grid dekoratif atau dot pattern.
- R-08 PASS: panah CTA menandai perpindahan menuju prediksi/metode; alasan di DESIGN.md.
- R-09 PASS: label model/kategori menyatakan informasi nyata.
- R-10 PASS: tanpa glassmorphism.
- R-12 PASS: panel menggunakan pembatas, tanpa bayangan besar.
- R-13 PASS: tanpa glow.
- R-14 PASS: ringkasan metrik seragam untuk perbandingan; panel proses dan model memiliki struktur sesuai konten.
- R-19 PASS: gerak hanya untuk drawer dan loading; reduced motion tersedia.
- R-22 PASS: ikon Sprout menandai konteks tanaman; tidak ada ilustrasi generik eksternal.

### Liveliness

- PASS: ENERGY 2 / RHYTHM 2 / MOTION 1 tercatat di DESIGN.md.
- PASS: variasi banner, ringkasan, proses, dan metadata sesuai hierarki informasi.
- PASS: heading dan tindakan prediksi menjadi fokus dashboard; hasil menjadi fokus halaman prediksi.
- PASS: jarak memisahkan navigasi, input, hasil, dan metode.
- PASS: merah sebagai aksen identitas/tindakan; hijau sebagai konteks tanaman.
- PASS: motif tanaman dan istilah Raw/Ripe dipakai konsisten.
- PASS: arahan merah/snow white dan pola mobile diumumkan sebelum implementasi.

### Craftsmanship dan quality locks

- C-1 PASS: warna, tipografi, ikon, dan hierarki memiliki alasan tertulis di DESIGN.md.
- C-2 PASS: handler navigasi, pemilihan berkas, prediksi, dan penghapusan tersedia.
- C-3 PASS: bagian utama menjelaskan input, model, hasil, dan catatan penelitian.
- C-4 PASS: lima breakpoint dan status error/empty diuji; keyboard ditunjang kontrol native, focus trap, dan Escape.
- C-5 PASS: tidak ada klaim atau testimonial buatan.
- R-05 PASS: komposisi mengikuti tahap analisis citra dan informasi model.
- R-11 PASS: radius kecil untuk panel/tombol, lingkaran hanya nomor langkah.
- R-15 PASS: CTA menyebut tindakan: prediksi, unggah foto, hapus riwayat.
- R-16 PASS: salinan menjelaskan fungsi dan batasan, tanpa klaim pemasaran.
- R-20 PASS: kematangan padi, Raw/Ripe, metode MobileNetV2, dan palet pengguna membentuk konteks khusus proyek.
- R-21 PASS: tema terang mengikuti snow white yang diminta.
- R-29 PASS: sistem merah, snow white, hijau zaitun, dan warna netral teks.
- R-30 PASS: tanpa peniruan identitas produk lain.
- R-31 PASS: alasan keputusan utama tercatat di DESIGN.md.

Batas verifikasi: tidak menguji pembaca layar perangkat fisik, kalibrasi probabilitas, akurasi dataset penuh, build produksi, atau container Docker.

## Compact layout and GitHub shortcut revision

- PASS — The app stays centered at a maximum width of 480 px on desktop and fills narrower phone viewports. Checked with Chromium at 320, 390, 768, 1024, and 1440 px; no horizontal overflow.
- PASS — Hamburger navigation and Escape work at all five viewport sizes. The sidebar is hidden and removed from keyboard navigation when closed.
- PASS — The fixed repository link targets https://github.com/ragraze/agrisense-dashboard and opens a new tab. It has no visible text or close control, and retains an accessible name.
- PASS — Computed browser styles confirm a 52 × 52 px circular black button (#111) with a white icon (#fff). White/black contrast is approximately 18.9:1. Its single shadow distinguishes a floating action from scrolling content.
- PASS — Final mobile and desktop screenshots were refreshed. No browser pageerrors occurred during the revision checks.
- PASS — Frontend type checking passed after the Vue changes. README is now in English and covers setup, architecture, API usage, configuration, data handling, Docker, model interpretation, testing, and troubleshooting.
- PASS — Existing delivery-gate checks above remain applicable; palette and mobile-canvas direction now reflect the user's explicit revisions in DESIGN.md.

The development servers remain running. No Docker build or deployment was performed.

## Model evaluation and sidebar revision

- PASS — Removed the sidebar's “Pelajari model” action, project-description paragraph, icon above “Metode penelitian”, and “Dari citra, kenali padi” footer. Browser checks confirm those elements are absent.
- PASS — Ran `backend/evaluate.py` against the actual TFLite model and all 189 test images (88 Raw, 101 Ripe), with zero skipped. Confusion matrix: `[[85, 3], [6, 95]]`; 180 correct, 9 incorrect, accuracy 95.238095%.
- PASS — Serving and evaluation share `inference.infer_image`, including input normalization, resize method, and logit interpretation. Existing prediction tests and real-image browser prediction still pass after extraction.
- PASS — Six backend tests cover API validation, inference preprocessing, failure states, evaluation report availability/corruption, model-fingerprint mismatch, known confusion-matrix metrics, and zero-denominator handling.
- PASS — Frontend type checking passed with the evaluation component and navigation entry.
- PASS — `/api/evaluation` works directly through Flask and through Nuxt; the Swagger specification lists the endpoint. Report sample count, prediction count, matrix total, and accuracy agree.
- PASS — Chromium checks at 320, 390, 768, and 1440 px: actual metrics and matrix visible, compact layout retained, no horizontal overflow or browser pageerrors.
- PASS — Browser checks cover report download, expandable metric definitions and fingerprints, unavailable-report error, retry, and prediction regression. `docs/evaluation.png` records the rendered page.
- PASS — Accuracy and macro/per-class metrics come from a saved report, not placeholders. Timestamp, model/dataset hashes, split sizes, mapping, and preprocessing are included for reproducibility.
- PASS — Interpretation limits are visible: folder labels are not independently audited; exact-byte duplicate checks cannot establish split independence or field performance. No identical-byte overlap with the provided train/valid data was found.
- PASS — Evaluation panel colors reuse the checked palette; table headers, axis descriptions, and explicit correct/incorrect labels avoid color-only meaning. Native details/download/retry controls have working behavior.
- PASS — Design decisions are recorded in DESIGN.md and the English README includes reproduction instructions. Existing Antislop gate items still apply to unchanged parts. No build or Docker execution was performed.

## Dataset tab and history heading

- PASS — Added Dataset navigation and a data view backed by `/api/dataset`. Counts were generated from local image files: 989 total; Raw 488, Ripe 501; training 600, validation 200, test 189. No placeholder statistics.
- PASS — `backend/dataset_report.py` creates a timestamped inventory, included with backend reports for Docker without shipping the dataset. Source/license/export preprocessing match the included dataset READMEs.
- PASS — Seven backend tests now include inventory counts, ignored non-image extensions, report retrieval, missing report, and corrupt report behavior. Frontend type checking passes.
- PASS — Browser checks at 320, 390, 768, and 1440 px confirm the data loads and no horizontal overflow. Error/retry and the source link work; no pageerrors. Screenshot: `docs/dataset.png`.
- PASS — Removed “Riwayat di perangkat ini”; verified absent in the browser. Clear-history behavior remains available when records exist.
- PASS — Delivery gate: counts are traceable to inventory; existing checked color tokens and native controls are reused; loading/error/retry states are implemented; screenshot recorded and unchanged gate checks remain applicable. No build or Docker execution.

## Consolidated prediction results and dashboard cleanup

- PASS — Removed the separate history tab and analysis panel. The prediction page now has one combined results/history section after the upload form. Latest result opens automatically; older results use native expandable details.
- PASS — Browser integration with real model: first prediction produces one result; a second prediction adds one older record without a duplicate analysis panel. Older details expand, records survive reload, clear-history works, and no pageerrors occur.
- PASS — No horizontal overflow at 320, 390, 768, or 1440 px. Screenshot: docs/prediction.png. Existing accessible native details, status text, and checked colors are retained.
- PASS — Dashboard source/license link removed; source attribution remains on Dataset. Dashboard introductory heading, description, and “Prediksi baru” button removed per user direction. Other dashboard prediction entry actions remain functional.
- PASS — Frontend type checking passed after all changes. No Docker build executed. Existing delivery-gate evidence remains applicable to unchanged areas.
