from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime
import time

# === Tiện ích ===
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# === Survey Context để tái sử dụng driver/wait/logger ===
class SurveyContext:
    def __init__(self, entry, logger, submit):
        self.entry = entry
        self.logger = logger
        self.submit = submit
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get("https://survey.alchemer.com/s3/8374879/C9954-DCSI-2025-July-2025")
        self.wait = WebDriverWait(self.driver, 15)

    def close(self):
        self.driver.quit()

# === Các hành động form dùng ctx ===
def click_next_button(ctx):
    try:
        ctx.wait.until(EC.presence_of_element_located((By.ID, "sg_NextButton")))
        
        # Thử lại nếu gặp stale element
        for _ in range(3):  # thử lại 3 lần
            try:
                next_button = ctx.wait.until(EC.element_to_be_clickable((By.ID, "sg_NextButton")))
                ctx.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                next_button.click()
                return
            except StaleElementReferenceException:
                ctx.logger.log(f"[{now()}] - ⚠️ - Gặp lỗi stale element, thử lại...")
                time.sleep(0.5)  # đợi DOM ổn định
        
        ctx.logger.log(f"[{now()}] - ❌ - Vẫn lỗi stale element sau 3 lần thử.")
    
    except Exception as e:
        ctx.logger.log(f"[{now()}] - ❌ - Lỗi khi bấm nút Next: {e}")


def click_element(ctx, element_id):
    ctx.wait.until(EC.presence_of_element_located((By.ID, element_id)))
    ctx.driver.find_element(By.ID, element_id).click()

def select_rating(ctx, value, question_label="Q"):
    rating_value = str(value).strip()
    for attempt in range(3):
        try:
            ctx.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "atmrating-btn")))
            buttons = ctx.driver.find_elements(By.CLASS_NAME, "atmrating-btn")
            for btn in buttons:
                if btn.get_attribute("data-value") == rating_value:
                    ctx.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    btn.click()
                    ctx.logger.log(f"[{now()}] - O - {question_label}: {rating_value}")
                    click_next_button(ctx)
                    return  # Thành công, kết thúc hàm
            else:
                ctx.logger.log(f"[{now()}] - X - Không tìm thấy nút cho {question_label}: {rating_value}")
        except Exception as e:
            ctx.logger.log(f"[{now()}] - X - Lỗi khi chọn {question_label} (lần {attempt+1}): {e}")
        time.sleep(1)  # Đợi 1 giây trước lần thử tiếp theo

    # Nếu sau 3 lần vẫn thất bại, thử click_next_button và kết thúc
    click_next_button(ctx)

def select_yes_no(ctx, value, yes_id, no_id, question_label):
    val = str(value).strip().lower()
    if val in ["có", "yes", "true", "1"]:
        click_element(ctx, yes_id)
        ctx.logger.log(f"[{now()}] - O - {question_label}: Có")
    else:
        click_element(ctx, no_id)
        ctx.logger.log(f"[{now()}] - O - {question_label}: Không")
    click_next_button(ctx)

def select_yes_no_maybe(ctx, value, yes_id, no_id, maybe_id, question_label):
    val = str(value).strip().lower()
    if val in ["có", "yes", "true", "1"]:
        click_element(ctx, yes_id)
        ctx.logger.log(f"[{now()}] - O - {question_label}: Có")
    elif val in ["không", "no", "false", "0"]:
        click_element(ctx, no_id)
        ctx.logger.log(f"[{now()}] - O - {question_label}: Không")
    else:
        click_element(ctx, maybe_id)
        ctx.logger.log(f"[{now()}] - O - {question_label}: Không rõ")
    click_next_button(ctx)

def fill_contact_info(ctx):
    ctx.wait.until(EC.presence_of_element_located((By.ID, "sgE-8374879-29-53-11062"))).send_keys(ctx.entry.ten_dv)
    ctx.wait.until(EC.presence_of_element_located((By.ID, "sgE-8374879-29-53-11064"))).send_keys(ctx.entry.sdt)
    ctx.logger.log(f"[{now()}] - O - Tên: {ctx.entry.ten_dv}, SĐT: {ctx.entry.sdt}")

def fill_q2_feedback(ctx):
    try:
        # Q2 Hài lòng
        box1 = ctx.driver.find_element(By.ID, "sgE-8374879-66-114-element")
        box1.clear()
        box1.send_keys(ctx.entry.q2_hai_long if ctx.entry.q2_hai_long != "x" else "Không có")
        ctx.logger.log(f"[{now()}] - O - Q2 Hài lòng: {ctx.entry.q2_hai_long}")

        # Nếu Q1 > 8 thì bỏ qua Q2 chưa hài lòng
        if int(ctx.entry.q1) > 8:
            return

        box2 = ctx.driver.find_element(By.ID, "sgE-8374879-66-118-element")
        box2.clear()
        box2.send_keys(ctx.entry.q2_chua_hai_long if ctx.entry.q2_chua_hai_long != "x" else "Không có")
        ctx.logger.log(f"[{now()}] - O - Q2 Chưa hài lòng: {ctx.entry.q2_chua_hai_long}")
    except Exception as e:
        ctx.logger.log(f"[{now()}] - X - Lỗi Q2: {e}")

# === Hàm chính để điền khảo sát ===
def fill_survey(entry, logger, submit=False):
    ctx = SurveyContext(entry, logger, submit)
    try:
        logger.log(f"[{now()}] - {entry.stt} - Bắt đầu khảo sát cho: {entry.ten_dv}")
        ctx.driver.find_element(By.ID, "sgE-8374879-1-2-10001").send_keys(entry.msbch)
        logger.log(f"[{now()}] - O - Mã BCH: {entry.msbch}")
        ctx.driver.find_element(By.ID, "sgE-8374879-1-2-10002").send_keys("N24255")
        logger.log(f"[{now()}] - O - Mã số PVV: N24255")
        ctx.driver.find_element(By.ID, "sgE-8374879-1-2-10003").send_keys("Nguyễn Kiều Anh")
        logger.log(f"[{now()}] - O - Họ tên PVV: Nguyễn Kiều Anh")
        click_next_button(ctx)

        click_element(ctx, "sgE-8374879-13-17-10028")  # Khu vực
        logger.log(f"[{now()}] - O - Khu vực: HA NOI")
        click_next_button(ctx)

        ctx.wait.until(EC.presence_of_element_located((By.ID, "sgE-8374879-31-59-element"))).send_keys(entry.s4_head)
        logger.log(f"[{now()}] - O - Mã đại lý: {entry.s4_head}")
        click_next_button(ctx)
        click_next_button(ctx)

        gender_id = "sgE-8374879-40-73-11934" if entry.gioi_tinh.lower() in ["nữ", "nu"] else "sgE-8374879-40-73-11935"
        click_element(ctx, gender_id)
        logger.log(f"[{now()}] - O - Giới tính: {entry.gioi_tinh}")
        click_next_button(ctx)

        click_element(ctx, "sgE-8374879-41-74-11936")
        logger.log(f"[{now()}] - O - Đúng thông tin")
        click_next_button(ctx)
        
        click_element(ctx, "sgE-8374879-42-76-11943")
        logger.log(f"[{now()}] - O - Đồng ý")
        click_next_button(ctx)

        
        click_element(ctx, "sgE-8374879-44-78-11945")
        logger.log(f"[{now()}] - O - Đồng ý")
        
        click_next_button(ctx)

        click_element(ctx, "sgE-8374879-45-80-11947")
        logger.log(f"[{now()}] - O - Có")
        click_next_button(ctx)

        click_element(ctx, "sgE-8374879-46-82-11951")
        logger.log(f"[{now()}] - O - Đúng hệ thống")
        click_next_button(ctx)

        Select(ctx.driver.find_element(By.ID, "sgE-8374879-47-110-element")).select_by_visible_text(entry.tinh_song)
        click_element(ctx, "sgE-8374879-47-85-11955")
        logger.log(f"[{now()}] - O - Đúng hệ thống")
        click_next_button(ctx)

        click_next_button(ctx)  # Start survey
        select_rating(ctx, entry.q1, "Q1")
        fill_q2_feedback(ctx)
        click_next_button(ctx)
        select_rating(ctx, entry.q3, "Q3")
        select_rating(ctx, entry.q4, "Q4")
        select_yes_no_maybe(ctx, entry.q5, "sgE-8374879-53-96-12010", "sgE-8374879-53-96-12011", "sgE-8374879-53-96-12062", "Q5")
        select_rating(ctx, entry.q6, "Q6")
        select_yes_no(ctx, entry.q7, "sgE-8374879-55-97-12012", "sgE-8374879-55-97-12013", "Q7")
        select_rating(ctx, entry.q8, "Q8")
        select_yes_no(ctx, entry.q9, "sgE-8374879-59-101-12029", "sgE-8374879-59-101-12030", "Q9")
        select_rating(ctx, entry.q10, "Q10")
        select_yes_no(ctx, entry.q12, "sgE-8374879-61-105-12046", "sgE-8374879-61-105-12047", "Q12")
        if entry.q12.strip().lower() in ["có", "yes", "1"]:
            select_rating(ctx, entry.q13, "Q13")
        select_yes_no_maybe(ctx, entry.q15, "sgE-8374879-65-122-12153", "sgE-8374879-65-122-12154", "sgE-8374879-65-122-12155", "Q15")

        click_next_button(ctx)
        fill_contact_info(ctx)

        if submit:
            click_next_button(ctx)
            logger.log(f"[{now()}] - ▲ - Đã ghi nhận: {entry.ten_dv}")
            with open("Submited.txt", "a", encoding="utf-8") as f:
                f.write(f"{entry.ten_dv}\n")
            
    finally:
        ctx.close()

# === Chạy toàn bộ khảo sát ===
def run_survey(logger, selected_entries, submit=False, progress_callback=None):
    total = len(selected_entries)
    logger.log(f"[{now()}] - § - Tổng số khảo sát: {total}")
    for idx, entry in enumerate(selected_entries, start=1):
        
        fill_survey(entry, logger, submit=submit)
        logger.log(f"[{now()}] - ♥ - Hoàn thành khảo sát cho: {entry.ten_dv}")

        if progress_callback:
            progress_callback(idx, total)

    logger.log(f"[{now()}] - ♦ - Đã hoàn thành tất cả khảo sát.")
