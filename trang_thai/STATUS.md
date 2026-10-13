# Trạng thái server — 2026-10-13 01:39 UTC

**Còn sống** · định kỳ

- máy: `d02e12ab8bf8` · up 10 hours, 18 minutes
- ngrok (SSH): tcp://6.tcp.ngrok.io:18183
- code: `848923f htr_test: cham_ft.sh (chấm adapter ft* trên Omar / Muharaf người viết lạ / Muharaf test + đối chứng) và lay_kq_cu.sh (lấy jsonl đã chấm từ results-htr) — để agent chạy từ repo, không phải dán heredoc` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: /dev/loop2       20G  5.1G   15G  26% /kaggle/working
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 8399 MiB, 15360 MiB, 28 %
Tesla T4, 7707 MiB, 15360 MiB, 36 %
138351, 434 MiB, /kaggle/working/venvs/dots/bin/python
138337, 7962 MiB, /kaggle/working/venvs/dots/bin/python
138351, 7704 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
c3: 1 windows (created Tue Oct 13 01:23:40 2026)
c4: 1 windows (created Tue Oct 13 01:23:41 2026)
hop_thu: 1 windows (created Tue Oct 13 01:18:35 2026)
```

## Việc (giám sát)

| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |
|---|---|---:|---:|---|---|
| c3 | đang chạy | 1 | 0 | 2026-10-13 01:23 UTC | `   baseer_ft3: 256/500 · 3.34 s/dòng` |
| c4 | đang chạy | 1 | 0 | 2026-10-13 01:23 UTC | `   baseer_ft4: 256/500 · 3.46 s/dòng` |

## c4.log (sửa 0 phút trước)
```
   baseer_ft4: 160/500 · 3.52 s/dòng
   baseer_ft4: 176/500 · 3.48 s/dòng
   baseer_ft4: 192/500 · 3.52 s/dòng
✔ GITHUB: đã đẩy lên nhánh results-htr/htr_eval_n500 (commit 906222a) — đang chấm baseer_ft4 192/500
   baseer_ft4: 208/500 · 3.51 s/dòng
   baseer_ft4: 224/500 · 3.50 s/dòng
   baseer_ft4: 240/500 · 3.50 s/dòng
   baseer_ft4: 256/500 · 3.46 s/dòng
```

## c3.log (sửa 1 phút trước)
```
   baseer_ft3: 160/500 · 3.37 s/dòng
   baseer_ft3: 176/500 · 3.34 s/dòng
   baseer_ft3: 192/500 · 3.37 s/dòng
   baseer_ft3: 208/500 · 3.36 s/dòng
✔ GITHUB: đã đẩy lên nhánh results-htr/htr_eval_n500 (commit b11ba8a) — đang chấm baseer_ft3 208/500
   baseer_ft3: 224/500 · 3.37 s/dòng
   baseer_ft3: 240/500 · 3.37 s/dòng
   baseer_ft3: 256/500 · 3.34 s/dòng
```

