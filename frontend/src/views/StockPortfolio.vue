<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import BreadcrumbDefault from '@/components/Breadcrumbs/BreadcrumbDefault.vue';
import TableOne from '@/components/Tables/TableOne.vue';
import DefaultLayout from '@/layouts/DefaultLayout.vue';
import type { StockPortfolio } from '@/interfaces/stock.interface';

const pageTitle = ref('Stock Portfolio');
const tableData = ref<StockPortfolio[]>([]); // Updated prop to match type
const isLoading = ref(true);
const error = ref<string | null>(null);

// Base API URL from environment variables
const BASE_API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';
console.log(BASE_API_URL);
// Function to fetch stocks from backend
const fetchStocks = async () => {
  try {
    isLoading.value = true;
    const response = await axios.get(`${BASE_API_URL}/api/stocks/`);
    console.log(response);
    tableData.value = response.data.map((stock: any) => ({
      logo: stock.logo || '',
      name: stock.name || 'Unknown',
      stock_symbol: stock.stock_symbol || 'N/A',
      quantity: stock.quantity || 0,
      purchase_price: stock.purchase_price || 0,
      purchase_date: new Date(stock.purchase_date) || new Date(),
    }));
    isLoading.value = false;
  } catch (err: unknown) {
    if (err instanceof Error) {
      error.value = err.message;
    } else {
      error.value = 'An unknown error occurred';
    }
    isLoading.value = false;
  }
};

// Fetch stocks when component mounts
onMounted(fetchStocks);
</script>

<template>
  <DefaultLayout>
    <BreadcrumbDefault :pageTitle="pageTitle" />
    
    <div class="flex flex-col gap-10">
      <div class="bg-white p-4 rounded-lg shadow">
        <h2 class="text-lg font-semibold">Your Stocks</h2>
        
        <!-- Loading State -->
        <div v-if="isLoading" class="text-center py-4">
          Loading stocks...
        </div>
        
        <!-- Error State -->
        <div v-else-if="error" class="text-red-500 text-center py-4">
          Error: {{ error }}
        </div>
        
        <!-- Stocks Table -->
        <TableOne 
          v-else 
          :portfolioData="tableData" 
          :columns="['Name', 'Quantity', 'Purchase Price', 'Purchase Date', 'Stock Symbol']"
        />
      </div>
    </div>
  </DefaultLayout>
</template>