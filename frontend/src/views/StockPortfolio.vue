<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import BreadcrumbDefault from "@/components/Breadcrumbs/BreadcrumbDefault.vue";
import TableOne from "@/components/Tables/TableOne.vue";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
import type { StockPortfolio } from "@/interfaces/stock.interface";

const pageTitle = ref("Stock Portfolio");
const tableData = ref<StockPortfolio[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Ensure BASE_API_URL is correctly set
const BASE_API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
console.log("[DEBUG] BASE_API_URL:", BASE_API_URL);

// Function to fetch stocks from backend
const fetchStocks = async () => {
  try {
    isLoading.value = true;
    console.log("[DEBUG] Fetching stocks from:", `${BASE_API_URL}/api/stocks/`);

    const response = await axios.get(`${BASE_API_URL}/api/stocks/`, {
      headers: { Accept: "application/json" },
    });

    console.log("[DEBUG] API Response:", response.data);

    tableData.value = response.data.map((stock: any) => ({
      logo: stock.logo || "",
      name: stock.stock_name || "Unknown", // Ensure correct field name
      stock_symbol: stock.stock_symbol || "N/A",
      quantity: stock.quantity || 0,
      purchase_price: stock.purchase_price || 0,
      purchase_date: stock.purchase_date
        ? new Date(stock.purchase_date).toISOString().split("T")[0]
        : "N/A", // Ensure correct date format
    }));

    isLoading.value = false;
  } catch (err: any) {
    console.error("[ERROR] Fetching stocks failed:", err);
    error.value =
      err.response?.data?.detail || err.message || "An unknown error occurred";
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
        <div v-if="isLoading" class="text-center py-4">Loading stocks...</div>

        <!-- Error State -->
        <div v-else-if="error" class="text-red-500 text-center py-4">
          Error: {{ error }}
        </div>

        <!-- Stocks Table -->
        <TableOne
          v-else
          :portfolioData="tableData"
          :columns="[
            'Company Name',
            'Quantity',
            'Purchase Price',
            'Purchase Date',
            'Stock Symbol',
          ]"
        />
      </div>
    </div>
  </DefaultLayout>
</template>
