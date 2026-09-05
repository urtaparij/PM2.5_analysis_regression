เปรียบเทียบ PM2.5 ระหว่างเชียงใหม่ (ภูมิประเทศแอ่งกระทะ) กับน่าน (ภูมิประเทศภูเขาซับซ้อน มีการเผาไร่เกษตรบนที่สูง) และทำนาย PM2.5 เฉลี่ยรายวันของวันถัดไป (regression)

## การติดตั้ง

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

ต้องการ Python 3.10 ขึ้นไป

## วิธีรัน (ตามลำดับ)

```
python src/fetch_data.py
python src/fetch_firms.py
python src/prepare_data.py
python src/analyse.py
python src/model.py
python src/compare_air4thai.py
```

- `fetch_data.py` ดึงข้อมูล PM2.5/มลพิษ และสภาพอากาศรายชั่วโมงของทั้งสองพื้นที่จาก Open-Meteo Air Quality API และ Archive API (2023-01-01 ถึงวันที่รัน) บันทึกเป็น raw CSV ไว้ที่ `data/raw/`
- `fetch_firms.py` ดึงข้อมูลจุดความร้อนจากไฟ (fire hotspot) จาก NASA FIRMS สำหรับทั้งสองพื้นที่ (ฤดูเผา 2023-2026) ไว้ที่ `data/raw/` ต้องมี FIRMS MAP_KEY ฟรี เก็บไว้ในไฟล์ `.env` ที่เครื่อง ในรูปแบบ `FIRMS_MAP_KEY=your_key_here` (ไม่ได้ commit เข้า git — ดู `.gitignore`) ขั้นตอนนี้เป็นทางเลือก ใช้สนับสนุนการอภิปรายใน Part D ของรายงานเท่านั้น ไม่ได้ใช้ใน `model.py`
  **ถ้าไม่มี FIRMS_MAP_KEY ของตัวเอง ให้ข้ามขั้นตอนนี้ไปได้เลย** — repo นี้มีข้อมูล FIRMS ที่ดึงไว้แล้วอยู่ใน `data/raw/firms_*.csv` ซึ่ง `analyse.py` ใช้ต่อได้ทันทีโดยไม่ต้องรันสคริปต์นี้ซ้ำ (สคริปต์ตรวจสอบแล้วว่าถ้า API ปฏิเสธ key จะไม่เขียนทับไฟล์เดิม แต่ก็จะไม่ได้ข้อมูลใหม่เพิ่มเช่นกัน)

## หมายเหตุเกี่ยวกับ API ที่ใช้

- **Open-Meteo** (Air Quality + Archive API): ไม่ต้องใช้ key, ฟรี, จำกัดประมาณ 10,000 calls/วัน ไม่ต้องตั้งค่าอะไรเพิ่ม
- **NASA FIRMS**: ขอ MAP_KEY ฟรีได้ที่ `https://firms.modaps.eosdis.nasa.gov/api/map_key/` (**ไม่ใช่** `firms.modis.gov` ที่ปรากฏในเอกสารเก่าหลายที่ — โดเมนนั้น resolve ไม่ได้แล้ว ตรวจสอบแล้วเมื่อ 2026-09) จำกัด 5,000 transactions/10 นาที (ดูสถานะการใช้งานได้จากหน้าเดียวกันหลัง login) โค้ดในโปรเจกต์นี้ใช้ประมาณ 144 requests ต่อการรันหนึ่งครั้ง ต่ำกว่า limit มาก และ `source=VIIRS_SNPP_SP` รับ `day_range` สูงสุดแค่ 5 (ไม่ใช่ 10 แบบ NRT source อื่น)
- **Air4Thai**: ไม่ต้องใช้ key แต่ endpoint นี้ redirect ไป https ด้วย certificate chain ที่ไม่สมบูรณ์ (ตามที่ระบุในเอกสารของผู้ให้บริการ) `src/compare_air4thai.py` จึงเรียกด้วย `verify=False` โดยตั้งใจ ไม่ใช่ข้อผิดพลาด
- `prepare_data.py` รวมข้อมูลมลพิษกับสภาพอากาศของแต่ละพื้นที่ด้วย timestamp, ตัดวันที่ fetch ข้อมูล (ซึ่งมีค่า forecast ปนกับค่าจริง) ทิ้ง, aggregate ข้อมูลรายชั่วโมงเป็นรายวัน, บันทึกเป็น `data/processed/{location}_daily.csv`
- `analyse.py` สร้างกราฟทั้งหมดใน `outputs/figures/` และสถิติเชิงพรรณนาใน `outputs/results/`
- `model.py` เทรน persistence baseline และโมเดล linear regression (แยกต่อพื้นที่) เพื่อทำนาย PM2.5 เฉลี่ยรายวันของวันถัดไป โดยใช้ time-ordered train/test split และ TimeSeriesSplit cross-validation บันทึกผลลัพธ์ไว้ที่ `outputs/results/`
- `compare_air4thai.py` ดึงค่าปัจจุบันจากสถานี Air4Thai ที่ใกล้แต่ละพื้นที่ที่สุด เทียบกับค่าประมาณของ Open-Meteo ณ เวลาเดียวกัน บันทึกเป็น `outputs/results/air4thai_comparison.csv` (checkpoint C6 ในรายงาน) เป็นอิสระจาก pipeline การสร้างโมเดล รันเมื่อไรก็ได้

การรัน `fetch_data.py` และ `fetch_firms.py` ซ้ำในวันหลังจะได้ไฟล์ที่ต่างออกไป เพราะจะมีข้อมูลสะสมเพิ่มขึ้นตั้งแต่ครั้งที่รันครั้งแรก (ช่วงที่ขอคือ 2023-01-01 ถึงวันที่รันเสมอ)

## โครงสร้าง repository

```
README.md
requirements.txt
src/
  fetch_data.py         ดึงข้อมูลดิบ บันทึกไปที่ data/raw/
  fetch_firms.py         ดึงข้อมูลจุดความร้อนจาก NASA FIRMS บันทึกไปที่ data/raw/
  prepare_data.py         ทำความสะอาด รวมข้อมูล สร้าง feature
  analyse.py                กราฟและสถิติเชิงพรรณนา
  model.py                    baseline, training, evaluation
data/
  raw/                          ข้อมูลตามที่ API ส่งมาเป๊ะๆ
  processed/                    ข้อมูลที่ป้อนเข้าโมเดล
outputs/
  figures/                       fig01_*.png ... fig08_*.png
  results/                       ไฟล์ CSV ของ metrics และสถิติเชิงพรรณนา
report/
  report.pdf
```

## การเปิดเผยการใช้ AI

ดูหน้าสุดท้ายของ `report/report.pdf`
