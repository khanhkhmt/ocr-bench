# Trạng thái server — 2026-10-09 07:06 UTC

**Còn sống** · định kỳ

- máy: `30e5ec664f3a` · up 5 hours, 9 minutes
- ngrok (SSH): tcp://6.tcp.ngrok.io:18183
- code: `4380c7f htr_test: Ketaba nền fp16 — bỏ qua kiểm tra torchao của peft (Colab có torchao 0.10 cũ → ImportError)` (nhánh `thu-2-model-htr`)
- ổ /kaggle/working: overlay         113G   59G   55G  52% /
- prompt đã nhận gần nhất: `(chưa có)`

## GPU
```
Tesla T4, 8765 MiB, 15360 MiB, 96 %
139051, 8762 MiB, /kaggle/working/venvs/dots/bin/python
```

## Phiên tmux
```
hop_thu: 1 windows (created Fri Oct  9 06:26:44 2026)
htr: 1 windows (created Fri Oct  9 04:01:05 2026)
htr_cd: 1 windows (created Fri Oct  9 07:03:02 2026)
```

## htr_chan_doan_ketaba_fp16.log (sửa 3 phút trước)
```
== ketaba fp16 lô 1
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1791529394.407889  139051 cpu_feature_guard.cc:227] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1791529398.116533  139051 cudart_stub.cc:31] Could not find cuda drivers on your machine, GPU will not be used.
`torch_dtype` is deprecated! Use `dtype` instead!
The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
```

## htr_chan_doan_ketaba.log (sửa 19 phút trước)
```
  File "/usr/local/lib/python3.13/dist-packages/peft/tuners/lora/torchao.py", line 160, in dispatch_torchao
    if not is_torchao_available():
           ~~~~~~~~~~~~~~~~~~~~^^
  File "/usr/local/lib/python3.13/dist-packages/peft/import_utils.py", line 162, in is_torchao_available
    raise ImportError(
    ...<2 lines>...
    )
ImportError: Found an incompatible version of torchao. Found version 0.10.0, but only versions above 0.16.0 are supported
```

## htr_bench_n500.log (sửa 44 phút trước)
```
   ketaba: 176/500 · 25.56 s/dòng
✔ GITHUB: đã đẩy lên nhánh results-htr/htr_eval_n500 (commit 13c49d0) — đang chấm ketaba 176/500
   ketaba: 192/500 · 25.77 s/dòng
   ketaba: 208/500 · 25.52 s/dòng
✔ GITHUB: đã đẩy lên nhánh results-htr/htr_eval_n500 (commit 8c050f6) — đang chấm ketaba 208/500
   ketaba: 224/500 · 25.44 s/dòng
   ketaba: 240/500 · 25.35 s/dòng
✔ GITHUB: đã đẩy lên nhánh results-htr/htr_eval_n500 (commit 41e1d5a) — đang chấm ketaba 240/500
```

## htr_bench_lo1.log (sửa 184 phút trước)
```
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1791518552.124373   58405 cpu_feature_guard.cc:227] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1791518554.975189   58405 cudart_stub.cc:31] Could not find cuda drivers on your machine, GPU will not be used.
`torch_dtype` is deprecated! Use `dtype` instead!
== baseer: nạp 48s, còn 2671 dòng
The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
```

## htr_chan_doan.log (sửa 228 phút trước)
```
- **nhãn**: النواب استقالت واذا نالتها تربعت في الحكم وباشرت اعمالها في حزم ورصانة اما ان الملك يطلع
  - fp16:16: الناس تربعت في الحكم وما شرت أعمالها في حرب ورحصات أما أن الملك يعلم
  - fp16:1: النواف استقالت وإذا هم فالنها تربعت في الحكم وما شرت أعمالها في عرض ورحصاته أما أن الملك يعلم
  - fp32:1: النواف استقالت وإذا هم فالنها تربعت في الحكم وما شرت أعمالها في عرض ورحصاته أما أن الملك يعلم
- **nhãn**: جسدها ويغترف منه من كل ناحية وصوب ويشعر انه بلع كل ما يشتهي
  - fp16:16: جسدها ويفترف لغته من كل ناحية وصوب ويشعر أنه بلغ كل ما يشهي.جسدها ويفترف لغته من كل ناحية وصوب ويشعر أنه بلغ كل ما يشتهي.
  - fp16:1: جسدها ويفترف لغته من كل ناحية وصوب ويشعر أنه بلغ كل ما يشتهي.
  - fp32:1: جسدها ويفترف لغته من كل ناحية وصوب ويشعر أنه بلغ كل ما يشتهي.
```

