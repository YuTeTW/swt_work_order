import os

from openpyxl.styles import Alignment
from sqlalchemy import and_
from sqlalchemy.orm import aliased

from app.models.domain.order import Order
from app.models.domain.order_issue import OrderIssue
from app.models.domain.user import User
from app.models.domain.user_mark_order import UserMarkOrder

import jpype
import asposecells


def get_order_db(db, user_id):
    # Create aliases for joined tables
    engineer_alias = aliased(User)
    reporter_alias = aliased(User)

    # Specify the primary table for the query using .select_from()
    order_db = db.query(Order, engineer_alias.name, reporter_alias.name, OrderIssue.name,
                        UserMarkOrder.mark).select_from(Order)

    # Join with the aliased tables
    order_db = order_db.outerjoin(
        engineer_alias, Order.engineer_id == engineer_alias.id
    ).outerjoin(
        reporter_alias, Order.reporter_id == reporter_alias.id
    ).outerjoin(
        OrderIssue, Order.order_issue_id == OrderIssue.id
    ).outerjoin(
        UserMarkOrder, and_(
            UserMarkOrder.order_id == Order.id,
            UserMarkOrder.user_id == user_id
        )
    )
    return order_db


def edit_excel(worksheet, order_db):
    from openpyxl.styles.alignment import Alignment
    from openpyxl.styles.borders import Border, Side
    # Create a list of weekday names to use in the report
    week_name = ["一", "二", "三", "四", "五", "六", "日"]

    # Set alignment for the cells
    align = Alignment(horizontal='center', vertical='center')

    # Set border
    thin_border = Border(bottom=Side(style='thin'))

    # 初始化上一行日期
    prev_date = None
    start_row = 3

    # Iterate over the query results and populate the worksheet
    for idx, (order, engineer_name, reporter_name, issue_name, mark) in enumerate(order_db, start=4):
        curr_date = order.created_at.date()

        # Merge cells with the same date
        if curr_date != prev_date:
            # Get the end row for the merged cells
            end_row = idx - 1

            # Merge cells and write the date
            # 日期
            worksheet.merge_cells(
                start_row=start_row,
                start_column=2,
                end_row=end_row,
                end_column=2
            )

            # Merge cells and write the day of the week
            # 星期
            worksheet.merge_cells(
                start_row=start_row,
                start_column=3,
                end_row=end_row,
                end_column=3
            )

            # Update the start row for the next merged cells
            start_row = idx

            # Update the previous date
            prev_date = curr_date

            # align
            worksheet[f"B{start_row}"].alignment = align
            worksheet[f"C{start_row}"].alignment = align

            # write line
            worksheet[f"B{start_row}"].border = thin_border
            worksheet[f"C{start_row}"].border = thin_border

        # Check if this is the last row
        if idx == len(list(order_db)) + 3:
            end_row = idx

            # 日期
            worksheet.merge_cells(
                start_row=start_row,
                start_column=2,
                end_row=end_row,
                end_column=2
            )

            # 星期
            worksheet.merge_cells(
                start_row=start_row,
                start_column=3,
                end_row=end_row,
                end_column=3
            )

        # Get the weekday name from the order date
        weekday_name = week_name[order.created_at.weekday()]

        # write the data into the merge
        worksheet.cell(row=start_row, column=2, value=prev_date)
        worksheet.cell(row=start_row, column=3, value=weekday_name)

        # 提報人
        worksheet[f"D{idx}"] = reporter_name
        worksheet[f"D{idx}"].alignment = align
        worksheet[f"D{idx}"].border = thin_border

        # 項目
        worksheet[f"E{idx}"] = issue_name
        worksheet[f"E{idx}"].alignment = align
        worksheet[f"E{idx}"].border = thin_border

        # 處理方式
        worksheet[f"F{idx}"] = "1"
        worksheet[f"F{idx}"].alignment = align
        worksheet[f"F{idx}"].border = thin_border

        order_status_name = {
            0: "未處理",
            1: "處理中",
            2: "已處理",
            3: "結單",

        }
        # 程序
        worksheet[f"G{idx}"] = order_status_name[order.status]
        worksheet[f"G{idx}"].alignment = align
        worksheet[f"G{idx}"].border = thin_border


async def get_report(db, user_id):
    import openpyxl
    from asposecells.api import Workbook, FileFormatType, PdfSaveOptions


    order_db = get_order_db(db, user_id)

    # Create directory for report files if it doesn't exist
    report_dir = os.path.join(os.getcwd(), "db_image/order/report/")
    os.makedirs(report_dir, exist_ok=True)

    # Load the Excel workbook
    workbook = openpyxl.load_workbook('order.xlsx')

    # Select the worksheet to edit
    worksheet = workbook['EFAY - 2023 JAN']

    # write data into excel
    edit_excel(worksheet, order_db)


    # Save the modified workbook as an Excel file
    workbook.save(os.path.join(report_dir, "order_report.xlsx"))
    #
    # Convert the Excel file to PDF using Aspose.Cells API
    workbook = Workbook(os.path.join(report_dir, "order_report.xlsx"))
    save_options = PdfSaveOptions()
    save_options.setOnePagePerSheet(True)
    workbook.save(os.path.join(report_dir, "order.pdf"), save_options)