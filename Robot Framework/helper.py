import pandas as pd
from selenium.webdriver.remote.webelement import WebElement
from robot.api.deco import keyword

@keyword("Read Html Table To Dataframe")
def read_html_table_to_dataframe(container_element: WebElement):
    column_selector = "g.table-control-view g.y-column"
    column_elements = container_element.find_elements("css selector", column_selector)

    if not column_elements:
        raise AssertionError(
            f"No Plotly columns found using selector: {column_selector}"
        )

    columns_data = []

    for col in column_elements:
        try:
            header_group = col.find_element("css selector", "g#header")
            header_text_el = header_group.find_element(
                "css selector", "g.cell-text-holder text.cell-text"
            )
            header = header_text_el.text.strip()
        except Exception:
            header = "unknown"

        cell_selector = (
            "g[id^='cells'] g.column-cells g.column-cell "
            "g.cell-text-holder text.cell-text"
        )
        cell_elems = col.find_elements("css selector", cell_selector)

        values = [el.text.strip() for el in cell_elems]

        columns_data.append({"header": header, "values": values})

    row_count = min(len(col["values"]) for col in columns_data)
    headers = [col["header"] for col in columns_data]

    rows = []
    for i in range(row_count):
        row = [col["values"][i] for col in columns_data]
        rows.append(row)

    df = pd.DataFrame(rows, columns=headers)
    return df

@keyword("Read Parquet Folder")
def read_parquet_folder(folder_path: str, start_date: str = None):
    df = pd.read_parquet(folder_path)
    if start_date:
        df = df[df['visit_date'] >= start_date]

    return df

@keyword("Compare DataFrames")
def compare_dataframes(df_html: pd.DataFrame, df_parquet: pd.DataFrame):
    df_html.columns = df_html.columns.str.strip().str.lower().str.replace(' ', '_')
    df_parquet.columns = df_parquet.columns.str.strip().str.lower().str.replace(' ', '_')
    df_html = df_html.rename(columns={'average_time_spent': 'avg_time_spent'})
    df_parquet = df_parquet.loc[:, df_html.columns]

    df_html['visit_date'] = pd.to_datetime(df_html['visit_date'])
    df_parquet['visit_date'] = pd.to_datetime(df_parquet['visit_date'])

    df_html = df_html.sort_values(by=['facility_type','visit_date']).reset_index(drop=True)
    df_parquet = df_parquet.sort_values(by=['facility_type','visit_date']).reset_index(drop=True)

    merged = df_html.merge(
        df_parquet,
        how='outer',
        on=['facility_type','visit_date'],
        indicator=True,
        suffixes=('_html','_parquet')
    )

    messages = []

    for _, row in merged.iterrows():
        merge_status = row['_merge']
        facility = row['facility_type']
        visit_date = row['visit_date'].date() if hasattr(row['visit_date'], 'date') else row['visit_date']

        if merge_status == 'left_only':
            messages.append(f"Average Time Spent in Facility Type {facility} on {visit_date} is extra in HTML table report.")
        elif merge_status == 'right_only':
            messages.append(f"Average Time Spent in Facility Type {facility} on {visit_date} is missing in HTML table report.")
        else:
            val_html = row.get('avg_time_spent_html')
            val_parquet = row.get('avg_time_spent_parquet')
            
            if pd.notna(val_html) and pd.notna(val_parquet):
                if float(val_html) != float(val_parquet):
                    messages.append(
                        f"Facility Type {facility} on {visit_date} has different Average Time Spent: HTML={val_html} Parquet={val_parquet}"
                    )

    return messages if messages else None
