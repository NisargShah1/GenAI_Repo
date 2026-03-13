import fs from 'fs';
import ExcelJS from 'exceljs';

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

  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  const sheet = sheetName ? workbook.getWorksheet(sheetName) : workbook.worksheets[0];
  if (!sheet) {
    throw new Error(`Sheet "${sheetName}" not found in ${filePath}`);
  }

  const data = [];
  const keys = [];

  sheet.eachRow((row, rowNumber) => {
    if (rowNumber === 1) {
      // Assuming first row contains headers
      row.eachCell((cell, colNumber) => {
        keys[colNumber] = cell.value;
      });
    } else {
      const rowData = {};
      row.eachCell((cell, colNumber) => {
        if (keys[colNumber]) {
          rowData[keys[colNumber]] = cell.value;
        }
      });
      data.push(rowData);
    }
  });
  
  return data;
}

/**
 * Write or update a specific cell in an Excel spreadsheet.
 * @param {string} filePath - Path to the .xlsx file.
 * @param {string} sheetName - The name of the sheet.
 * @param {string} cellAddress - The cell address (e.g., 'A1', 'B2').
 * @param {string|number} value - The value to write to the cell.
 */
export async function writeCell(filePath, sheetName, cellAddress, value) {
  console.log(`📝 [Excel] Writing value "${value}" to cell ${cellAddress} in sheet "${sheetName}" of ${filePath}`);
  
  const workbook = new ExcelJS.Workbook();
  
  if (fs.existsSync(filePath)) {
    await workbook.xlsx.readFile(filePath);
  }

  let sheet = workbook.getWorksheet(sheetName);
  if (!sheet) {
    // If the sheet doesn't exist, create an empty one
    sheet = workbook.addWorksheet(sheetName);
  }

  // Update the specific cell
  const cell = sheet.getCell(cellAddress);
  cell.value = value;

  await workbook.xlsx.writeFile(filePath);
  
  return `Successfully wrote "${value}" to ${cellAddress} in ${filePath}`;
}
