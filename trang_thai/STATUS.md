# Trạng thái server — 2026-10-14 03:43 UTC

**Còn sống** · định kỳ

- máy: `68056ead96f7` · up 1 hour
- ngrok (SSH): tcp://8.tcp.ngrok.io:26650
- code: `bc0d024 README htr_train / htr_test: bảng các bản đã huấn luyện (ft1–ft4, độ mạnh, nơi để adapter), cách chạy dữ liệu → huấn luyện → chấm qua hộp thư, --hf-ckpt, tập người viết lạ, cham_ft.sh, hop_thu` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  816M   19G   5% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 8399 MiB, 15360 MiB, 36 %
Tesla T4, 7687 MiB, 15360 MiB, 31 %
9759, 7962 MiB, /kaggle/working/venvs/dots/bin/python
10051, 434 MiB, /kaggle/working/venvs/dots/bin/python
10051, 7684 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
c3: 1 windows (created Wed Oct 14 03:00:09 2026)
c4: 1 windows (created Wed Oct 14 03:00:16 2026)
hop_thu: 1 windows (created Wed Oct 14 02:55:28 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| dl | XONG | 1 | 0 | 2026-10-14 02:58 UTC | `✔ train 19997 · val 998 → /tmp/htr_data` |
| c3 | đang chạy | 1 | 0 | 2026-10-14 03:00 UTC | `   baseer_ft3: 448/500 · 2.73 s/dòng` |
| c4 | đang chạy | 1 | 0 | 2026-10-14 03:00 UTC | `   baseer_ft4: 432/500 · 2.76 s/dòng` |

## c4.log (sửa 0 phút trước)
```
   baseer_ft4: 320/500 · 2.62 s/dòng
   baseer_ft4: 336/500 · 2.64 s/dòng
   baseer_ft4: 352/500 · 2.67 s/dòng
   baseer_ft4: 368/500 · 2.66 s/dòng
   baseer_ft4: 384/500 · 2.70 s/dòng
   baseer_ft4: 400/500 · 2.70 s/dòng
   baseer_ft4: 416/500 · 2.71 s/dòng
   baseer_ft4: 432/500 · 2.76 s/dòng
```

## c3.log (sửa 1 phút trước)
```
   baseer_ft3: 336/500 · 2.61 s/dòng
   baseer_ft3: 352/500 · 2.63 s/dòng
   baseer_ft3: 368/500 · 2.62 s/dòng
   baseer_ft3: 384/500 · 2.66 s/dòng
   baseer_ft3: 400/500 · 2.66 s/dòng
   baseer_ft3: 416/500 · 2.67 s/dòng
   baseer_ft3: 432/500 · 2.73 s/dòng
   baseer_ft3: 448/500 · 2.73 s/dòng
```

## dl.log (sửa 45 phút trước)
```
  train: 22092 dòng
  validation: 1069 dòng
✔ 23161 dòng → /tmp/htr_data/muharaf  ·  xem: /tmp/htr_data/muharaf/xem_mau.html
== giữ riêng nhóm Muharaf: 2015, AnF, BEK, Baddour, ME, SB, YFS
== muharaf
   train 20568 · val 1030 · bỏ vì trùng nhãn tập chấm 603
   GIỮ RIÊNG 1562 dòng → /tmp/htr_data/giu_lai_muharaf
✔ train 19997 · val 998 → /tmp/htr_data
```

