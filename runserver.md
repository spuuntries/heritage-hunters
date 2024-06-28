# Dokumen Teknis Server

Berikut adalah dokumentasi teknis untuk menjalankan server Heritage Hunters dari sumber kode.

## Setup

1. Pastikan bahwa terinstall Python >=3.9 pada sistem operasi anda.
2. Buka powershell atau terminal pada direktori sumber kode, lalu ketikkan dan enter:

```python3
pip install -r requirements.txt
```

3. Kemudian, pindahkan ke dalam direktori sumber server (`cd server`), lalu ketikkan dan enter:

```python3
sanic main:app main.py
```

Sekarang server seharusnya sudah berjalan. Anda dapat melihat URL server pada header sanic.

```
    Sanic v23.12.1
Goin' Fast @ <URL DI SINI>
```

Untuk membuka server ke luar localhost, anda dapat menggunakan command

```python3
sanic main:app main.py -H 0.0.0.0
```

Ini akan membuka server ke network LAN, dan client lain dapat berkoneksi ke server anda dengan menggunakan IP LAN anda. (Dengan port yang tercantum pada URL)

## Settings

Dalam server, anda dapat mengubah beberapa pengaturan mengenai runtime dari server. Anda dapat melihat setting yang tersedia dalam [server/.env.example](./server/.env.example).

Untuk membuat server menggunakannya, anda dapat meng-copy file tersebut menjadi `.env` pada direktori server.

### Penjelasan Settings

`JWTSECRET`: Secret dari JWT yang digunakan untuk sistem autentikasi.  
`QUEUESIZE`: Ukuran dari Queue sebelum player didistribusikan kedalam room.  
