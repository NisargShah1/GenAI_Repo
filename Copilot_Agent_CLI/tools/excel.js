import fs from 'fs';
import * as xlsx from 'xlsx';

/**
 * Read data from an Excel spreadsheet.
 * @param {string} filePath - Path to the .xlsx file.
 * @param {string} sheetName - The name of the sheet to read. If omitted, reads the first sheet.
 * @returns {Array<Object>} The rows of the sheet as JSON objects.
 */
export async function readSheet(filePath, sheetName) {
  console.log(`📊 [Excel] Reading sheet "${sheetName || 'default'}" from ${filePath}`);
  
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  const workbook = xlsx.readFile(filePath);
  const targetSheet = sheetName ? workbook.SheetNames.find(n => n === sheetName) : workbook.SheetNames[0];

  if (!targetSheet) {
    throw new Error(`Sheet "${sheetName}" not found in ${filePath}`);
  }

  const sheet = workbook.Sheets[targetSheet];
  const data = xlsx.utils.sheet_to_json(sheet);
  
  return data;
}

/**
 * Write or update a specific cell in an Excel spreadsheet.
 * @param {string} filePath - Path to the .xlsx file.
 * @param {string} sheetName - The name of the sheet.
 * @param {string} cell - The cell address (e.g., 'A1', 'B2').
 * @param {string|number} value - The value to write to the cell.
 */
export async function writeCell(filePath, sheetName, cell, value) {
  console.log(`📝 [Excel] Writing value "${value}" to cell ${cell} in sheet "${sheetName}" of ${filePath}`);
  
  let workbook;
  if (fs.existsSync(filePath)) {
    workbook = xlsx.readFile(filePath);
  } else {
    // If the file doesn't exist, create a new workbook
    workbook = xlsx.utils.book_new();
  }

  let sheet = workbook.Sheets[sheetName];
  if (!sheet) {
    // If the sheet doesn't exist, create an empty one
    sheet = {};
    xlsx.utils.book_append_sheet(workbook, sheet, sheetName);
  }

  // Update the specific cell
  sheet[cell] = { v: value };

  // Update the sheet range if the new cell falls outside the current range
  const range = sheet['!ref'] ? xlsx.utils.decode_range(sheet['!ref']) : { s: { c: 0, r: 0 }, e: { c: 0, r: 0 } };
  const cellAddress = xlsx.utils.decode_cell(cell);
  
  if (cellAddress.c > range.e.c) range.e.c = cellAddress.c;
  if (cellAddress.r > range.e.r) range.e.r = cellAddress.r;
  
  sheet['!ref'] = xlsx.utils.encode_range(range);

  xlsx.writeFile(workbook, filePath);
  
  return `Successfully wrote "${value}" to ${cell} in ${filePath}`;
}
