# Dokumen Teknis Client

Berikut adalah dokumentasi teknis untuk menjalankan client Heritage Hunters dari sumber kode.

## Setup

1. Pastikan bahwa terinstall Python >=3.9 pada sistem operasi anda.
2. Buka powershell atau terminal pada direktori sumber kode, lalu ketikkan dan enter:

```python3
pip install -r requirements.txt
```

3. Kemudian, pindahkan ke dalam direktori sumber client (`cd client`), lalu ketikkan dan enter:

```python3
python main.py
```

Client sekarang seharusnya sudah berjalan sebagaimana binary. Anda dapat menggunakannya dengan server custom menggunakan flag `--custom`.

```python3
python main.py --custom
```
