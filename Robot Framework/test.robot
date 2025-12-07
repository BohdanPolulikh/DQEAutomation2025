*** Settings ***
Library    SeleniumLibrary
Library    helper.py

*** Variables ***
${ROOT_FOLDER}          ${CURDIR}/..
${PARQUET_FOLDER}       ${ROOT_FOLDER}/parquet_data_local/facility_type_avg_time_spent_per_visit_date
${REPORT_FILE}          ${ROOT_FOLDER}/generated_report/report.html
${FILTER_DATE}          2025-11-18

*** Test Cases ***
Compare HTML Table With Parquet
    Open Browser    ${REPORT_FILE}    chrome
    ${table}=    Get WebElement    //div[contains(@class,'plot-container')]
    ${df_html}=    Read Html Table To Dataframe    ${table}
    ${df_parquet}=    Read Parquet Folder    ${PARQUET_FOLDER}    ${FILTER_DATE}
    ${differences}=    Compare DataFrames    ${df_html}    ${df_parquet}
    Run Keyword If    ${differences}    Fail    ${differences}
    [Teardown]    Close Browser
