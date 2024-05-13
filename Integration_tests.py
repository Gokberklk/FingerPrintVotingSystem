from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest
import time

screenshots = "C://Users//USER//Desktop//School//GraduationProject//FingerPrintVotingSystem//Screenshots//"


# Adem Garip
def ID_check_success():
    time.sleep(5)
    driver.save_screenshot(screenshots+"screenshot1.png")
    enter_id = driver.find_element(By.ID, "voter_id")
    enter_id.send_keys("55555555555")
    driver.save_screenshot(screenshots + "screenshot10.png")
    check_id = driver.find_element(By.ID, "check_id")
    check_id.click()
    driver.save_screenshot(screenshots + "screenshot2.png")
    time.sleep(10)


def ID_check_fail():
    enter_id = driver.find_element(By.ID, "voter_id")
    enter_id.send_keys("11111111111")
    check_id = driver.find_element(By.ID, "check_id")
    check_id.click()
    time.sleep(10)


def check_Fingerprint_success():
    upload_finger = driver.find_element(By.ID, "voter_fingerprint")
    file = "C://Users//USER//Desktop//School//GraduationProject//FingerPrintVotingSystem//saved_image.bmp"
    upload_finger.send_keys(file)
    driver.save_screenshot(screenshots + "screenshot3.png")
    do_login = driver.find_element(By.ID, "do_login")
    do_login.click()
    driver.save_screenshot(screenshots + "screenshot4.png")
    time.sleep(10)


def check_Fingerprint_fail():
    upload_finger = driver.find_element(By.ID, "voter_fingerprint")
    file = "C://Users//USER//Desktop//School//GraduationProject//FingerPrintVotingSystem//1__M_Left_index_finger.BMP"
    upload_finger.send_keys(file)
    do_login = driver.find_element(By.ID, "do_login")
    do_login.click()
    time.sleep(10)


def successful_entry():
    ID_check_success()
    check_Fingerprint_success()


def successful_ID_Invalid_Image():
    ID_check_success()
    check_Fingerprint_fail()


def choose_election():
    driver.save_screenshot(screenshots + "screenshot5.png")
    election = driver.find_element(By.NAME, "20241")
    election.click()
    driver.save_screenshot(screenshots + "screenshot6.png")
    time.sleep(5)
    candidate = driver.find_element(By.ID, "22222222222")
    candidate.click()
    time.sleep(5)
    driver.save_screenshot(screenshots + "screenshot20.png")
    time.sleep(5)
    button = driver.find_element(By.CSS_SELECTOR, "button")
    button.click()
    driver.save_screenshot(screenshots + "screenshot7.png")
    time.sleep(8)


def vote_specific_election():  # voting a specific election
    successful_entry()
    choose_election()


def vote_all_and_try_login_again():
    successful_entry()
    choose_election()
    election = driver.find_element(By.NAME, "20242")
    election.click()
    time.sleep(5)
    candidate = driver.find_element(By.ID, "44444444444")
    candidate.click()
    time.sleep(5)
    button = driver.find_element(By.CSS_SELECTOR, "button")
    button.click()
    time.sleep(8)
    successful_entry()
    time.sleep(8)


def try_selecting_two_candidates():  # test this one
    successful_entry()
    election = driver.find_element(By.NAME, "20241")
    election.click()
    time.sleep(5)
    candidate = driver.find_element(By.ID, "22222222222")
    candidate.click()
    candidate = driver.find_element(By.ID, "33333333333")
    candidate.click()
    time.sleep(5)
    button = driver.find_element(By.CSS_SELECTOR, "button")
    button.click()
    time.sleep(8)


def admin_login():
    time.sleep(5)
    enter_id = driver.find_element(By.ID, "admin_id")
    enter_id.send_keys("11111111111")
    check_id = driver.find_element(By.ID, "check_id")
    check_id.click()
    time.sleep(10)


def admin_remove_election():  # works perfectly
    admin_login()
    elections_button = driver.find_element(By.CSS_SELECTOR, "#choose_election")
    elections_button.click()
    time.sleep(10)
    removed_election = driver.find_element(By.ID, "20243")
    removed_election.click()
    time.sleep(10)


def admin_update_election():
    admin_login()
    elections_button = driver.find_element(By.CSS_SELECTOR, "#choose_election")
    elections_button.click()
    time.sleep(5)
    update_button = driver.find_element(By.NAME, "20241")
    update_button.click()
    time.sleep(5)
    description = driver.find_element(By.ID, "tarea")
    description.clear()
    description.send_keys("Test success2")
    update_button2 = driver.find_element(By.ID, "update_election")
    update_button2.click()
    time.sleep(10)


def admin_add_election():  # successfully added
    admin_login()
    elections_button = driver.find_element(By.CSS_SELECTOR, "#choose_election")
    elections_button.click()
    time.sleep(5)
    add_election = driver.find_element(By.ID, "add_election")
    add_election.click()
    time.sleep(5)
    description = driver.find_element(By.ID, "tarea")
    description.clear()
    description.send_keys("AddTest")
    date = driver.find_element(By.ID, "date")
    date.clear()
    date.send_keys("20-06-2025")
    time.sleep(5)
    stime = driver.find_element(By.ID, "time")
    stime.clear()
    stime.send_keys("09:00:00")
    time.sleep(5)
    enddate = driver.find_element(By.ID, "endDate")
    enddate.clear()
    enddate.send_keys("25-06-2025")
    time.sleep(5)
    etime = driver.find_element(By.ID, "endTime")
    etime.clear()
    etime.send_keys("09:00:00")
    time.sleep(5)
    add_button = driver.find_element(By.ID, "add_button")
    add_button.click()
    time.sleep(10)


def admin_remove_candidate():  # works as well
    admin_login()
    elections_button = driver.find_element(By.CSS_SELECTOR, "#choose_candidate")
    elections_button.click()
    time.sleep(10)
    remove_candidate = driver.find_element(By.ID, "20241")
    remove_candidate.click()
    time.sleep(10)
    remove = driver.find_element(By.ID, "33333333333")
    remove.click()
    time.sleep(10)


def admin_add_candidate():  # works as well
    admin_login()
    elections_button = driver.find_element(By.CSS_SELECTOR, "#choose_candidate")
    elections_button.click()
    time.sleep(10)
    add_candidate = driver.find_element(By.NAME, "20241")
    add_candidate.click()
    time.sleep(10)
    add = driver.find_element(By.ID, "candidateID")
    add.clear()
    add.send_keys("33333333333")
    time.sleep(5)
    button = driver.find_element(By.ID, "candidate_add")
    button.click()
    time.sleep(20)


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:5000")
    vote_specific_election()

    driver.quit()
