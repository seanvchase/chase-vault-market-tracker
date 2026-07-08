from io import BytesIO
import pandas as pd


def create_inventory_excel(inventory_data):
    """
    Creates an Excel file from inventory data and returns it as bytes.
    Streamlit can use these bytes to create a download button.
    """

    output = BytesIO()

    df = pd.DataFrame(inventory_data)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory")

        workbook = writer.book
        worksheet = writer.sheets["Inventory"]

        # Make columns easier to read
        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            adjusted_width = max_length + 2
            worksheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)

    return output
