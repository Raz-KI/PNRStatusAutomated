from playwright.sync_api import sync_playwright
import pytesseract
import smtplib
from email.message import EmailMessage
import ssl
from apscheduler.schedulers.blocking import BlockingScheduler

def send_mail(message):
    smtp_server = "smtp.gmail.com"
    port = 465  # SSL port
    sender_email = "kikegaane@gmail.com"  # Use your Gmail address
    receiver_email = "zahidashaikh84@gmail.com"  # Receiver's email
    password = "yirp vucy yfvh avfp"  # App password generated from Google
    subject = "PNR status "
    body = "{}".format(message)
    # Create the email message
    em = EmailMessage()
    em['From'] = sender_email
    em['To'] = receiver_email
    em['Subject'] = subject
    em.set_content(body)
    # Send the email securely using SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(em)

def captcha_solver():
    img_path1 = 'captcha.png'
    text = pytesseract.image_to_string(img_path1,lang='eng')
    print(text)
    to_remove = ["?","="]
    for i in text:
        if i in to_remove:
            text =text.replace(i,'')
    return eval(text)

def get_status(pnr_list):
    status_list = []
    with sync_playwright() as p:
        for pnr in pnr_list:
            try:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto("https://www.indianrail.gov.in/enquiry/PNR/PnrEnquiry.html?locale=en")
                page.fill("#inputPnrNo",str(pnr))
                page.locator("#modal1").click()
                page.locator("#CaptchaImgID").screenshot(path="captcha.png")
                ans = captcha_solver()
                page.wait_for_timeout(3000)
                page.fill("#inputCaptcha", str(ans))
                page.locator("#submitPnrNo").click()
                passenger_titles = page.locator("#psgnDetailsTable>>tbody")
                message = (passenger_titles.inner_text())
                page.wait_for_timeout(6000)
                status_list.append(pnr)
                status_list.append(message)
            except:
                print(status_list)
    formatted = ""
    for i in range(0, len(status_list), 2):
        pnr = status_list[i]
        info = status_list[i + 1].replace('\t', ' | ').strip()
        formatted += f"PNR: {pnr}\n{info}\n\n"
    print(formatted)
    send_mail(formatted)
    print("Mail sent")
    
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    pnr_list = [8631710095, 8631710226, 2333243180, 2929302136]
    scheduler.add_job(lambda: get_status(pnr_list), 'interval', minutes=1440)
    print("Scheduler started. Press Ctrl+C to exit.")
    scheduler.start()