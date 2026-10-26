"""Read-only peer import; adversarial image decoder probe stays in memory."""
import runpy, struct, zlib
m = runpy.run_path('Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py', run_name='codex_review')
def chunk(kind, data):
    return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data)&0xffffffff)
# Actual image: x-coordinate grayscale gradient, RGB8, PNG Sub filter.
w,h=256,128
raw=b''.join(b'\x01'+b'\x00\x00\x00'+b'\x01\x01\x01'*(w-1) for _ in range(h))
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
print('raw_decoder_sub_filter_lit_gradient=',m['decode_png_variance_raw'](png))
print('actual_crop_gradient_expected_mean=127, stddev~44; decoder must undo PNG filters')
print('black_real_frame=',m['verify_image_file']('Docs/BossCombatReview/Execution/Claude/Evidence/exports/cap_camera_run1/black_frame_with_camera.png'))
for cap,folder in [('01','CAP01_A5'),('02','CAP02_A4'),('05','CAP05_Telegraph'),('06','CAP06_Recovery')]:
    log=f'Docs/BossCombatReview/Execution/Claude/Evidence/exports/cap_optB_run1/{folder}_optB_run.log'
    data=m['CaptureTelemetryParser'].parse_log_text(open(log,encoding='utf-8').read()).get('CAP-'+cap,{})
    result=getattr(m['CaptureEvaluator'],'evaluate_cap'+cap)(data,image_dir='Saved/Screenshots/'+folder)
    print(cap,result['status'],result['metrics'],result['rejections'][:1])
