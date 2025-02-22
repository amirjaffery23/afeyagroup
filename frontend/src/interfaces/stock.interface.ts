// src/interfaces/stock.interface.ts
export interface StockPortfolio {
    logo: string;
    name: string;
    stock_symbol: string;
    quantity: number;
    purchase_price: number;
    purchase_date: string | Date;  // ✅ Allow both types
  }
  