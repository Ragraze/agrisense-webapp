# Arah desain

Arahan pengguna: webapp mobile untuk dashboard penelitian, sidebar merah PowerPoint dan snow white, tab berikon, hamburger, bagian metode penelitian tebal dan deskripsi proyek di bawah sidebar.

Implementasi: merah #B23724 sebagai identitas navigasi dan tindakan utama, snow white #FFFAFA untuk area kerja. Hijau zaitun untuk konteks tanaman dan hasil. Font sistem menjaga keterbacaan. ENERGY 2 / RHYTHM 2 / MOTION 1: hierarki judul yang jelas, ruang antarbagian, gerak hanya pada drawer dan loading.

Prinsip Apple Design yang diterapkan pada web: target sentuh minimal 44px, label aksesibel, fokus keyboard, drawer dengan penahanan fokus dan Escape, ukuran responsif, status loading/error/empty, serta dukungan reduced motion. Tidak meniru konvensi aplikasi native secara utuh.

Ikon berasal dari satu set Lucide. Sprout digunakan sebagai elemen konteks tanaman dari set yang sama. Tidak ada aset raster baru. Ringkasan dashboard berasal dari hasil prediksi pengguna, bukan statistik contoh.

Ikon navigasi menandai tujuan yang diminta: LayoutDashboard untuk ringkasan, ScanLine untuk prediksi citra, History untuk hasil terdahulu, dan BookOpen untuk metode penelitian. Panah pada CTA menunjukkan perpindahan halaman, bukan dekorasi status. Panel hijau pucat mengelompokkan langkah analisis tanaman, sedangkan garis tipis membatasi metadata dan ringkasan tanpa elevasi palsu.

Revisi pengguna: kanvas mobile tetap sempit pada desktop seperti pola web Pintarnya; maksimum 480px, ditengahkan, hamburger pada semua ukuran. Tombol GitHub mengambang menggantikan pola promosi popup yang disebut pengguna, tanpa tombol tutup; menuju repo origin. Bayangan hanya pada tautan mengambang untuk memisahkannya dari konten saat scrolling.

Penyempurnaan tombol GitHub: lingkaran putih 52px dengan ikon hitam saja, seperti tombol scroll-to-top. Label tujuan tetap tersedia untuk pembaca layar; tanpa teks visual dan tanpa silang.

Koreksi warna pengguna: tombol GitHub berlatar hitam #111 dengan ikon putih #fff. Bentuk lingkaran dan perilaku tautan tetap sama.

Evaluasi model: satu skor akurasi menjadi fokus, diikuti metrik macro, confusion matrix dengan sumbu eksplisit, laporan per kelas, dan batasan. Sel diagonal hijau pucat menandai prediksi benar; label Benar/Salah memastikan makna tidak bergantung pada warna. Data berasal dari inferensi seluruh dataset/test, dengan timestamp dan fingerprint agar hasil dapat ditelusuri. Tidak menggunakan angka contoh atau menyamakan probabilitas satu gambar dengan akurasi model.

Penyederhanaan sidebar sesuai arahan pengguna: hilangkan tombol Pelajari model, deskripsi proyek tambahan, ikon di atas judul metode, dan slogan footer. Judul Metode penelitian dan penjelasan MobileNetV2 tetap dipertahankan.

Dataset: fokus pada jumlah gambar nyata, kelas Raw/Ripe, split training/validasi/test, serta atribusi sumber. Angka berasal dari inventaris lokal bertanggal. Tidak memakai data contoh, tidak mengklaim kualitas label hanya berdasarkan jumlah berkas. Komposisi vertikal mempertahankan kanvas mobile pada semua ukuran layar.
