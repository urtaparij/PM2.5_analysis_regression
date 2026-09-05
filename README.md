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
- `fetch_firms.py` ดึงข้อมูลจุดความร้อนจากไฟ (fire hotspot) จาก NASA FIRMS สำหรับทั้งสองพื้นที่ (ฤดูเผา 2023-2026) ไว้ที่ `data/raw/` ต้องมี FIRMS MAP_KEY ฟรี (https://firms.modis.gov/api/map_key/) เก็บไว้ในไฟล์ `.env` ที่เครื่อง ในรูปแบบ `FIRMS_MAP_KEY=your_key_here` (ไม่ได้ commit เข้า git — ดู `.gitignore`) ขั้นตอนนี้เป็นทางเลือก ใช้สนับสนุนการอภิปรายใน Part D ของรายงานเท่านั้น ไม่ได้ใช้ใน `model.py`
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
