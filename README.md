# bulk-renamer

Klasördeki dosyaları toplu yeniden adlandırmak için masaüstü uygulaması.

## Özellikler

- Önek / sonek ekle
- Bul & değiştir
- Regex ile yeniden adlandır
- Numara şablonu ile adlandır (`{n}_{name}` gibi)
- Uzantı filtresi (sadece `.jpg`, `.png` vb.)
- Canlı önizleme — uygulamadan önce sonucu gör
- Geri al — son işlemi tek tıkla sıfırla

## Çalıştırma

Python 3.8+ gereklidir. Ekstra bağımlılık yok — sadece standart kütüphane.

```bash
python bulk_renamer.py
```

## .exe olarak derleme

```bash
pip install pyinstaller
build.bat
```

`dist/bulk-renamer.exe` oluşur.

## Lisans

MIT
