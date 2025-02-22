<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import BreadcrumbDefault from "@/components/Breadcrumbs/BreadcrumbDefault.vue";
import TableOne from "@/components/Tables/TableOne.vue";
import TableTwo from "@/components/Tables/TableTwo.vue";
import TableThree from "@/components/Tables/TableThree.vue";
import DefaultLayout from "@/layouts/DefaultLayout.vue";

const pageTitle = ref("Tables");
const portfolioData = ref([]);
const columns = ref([
  "Company Name",
  "Quantity",
  "Purchase Price",
  "Purchase Date",
  "Stock Symbol",
]);

const fetchPortfolioData = async () => {
  try {
    const response = await axios.get("/api/stocks/");
    console.log("Fetched portfolio data:", response.data); // Log the fetched data
    portfolioData.value = response.data.map((stock: any) => ({
      name: stock.stock_name || "Unknown", // Ensure correct field name
      quantity: stock.quantity || 0,
      purchase_price: stock.purchase_price || 0,
      purchase_date: stock.purchase_date
        ? new Date(stock.purchase_date).toISOString().split("T")[0]
        : "N/A", // Ensure correct date format
      stock_symbol: stock.stock_symbol || "N/A",
    }));
  } catch (error) {
    console.error("Error fetching portfolio data:", error);
  }
};

onMounted(() => {
  fetchPortfolioData();
});
</script>

<template>
  <DefaultLayout>
    <!-- Breadcrumb Start -->
    <BreadcrumbDefault :pageTitle="pageTitle" />
    <!-- Breadcrumb End -->

    <div class="flex flex-col gap-10">
      <TableOne :portfolioData="portfolioData" :columns="columns" />
      <TableTwo />
      <TableThree />
    </div>
  </DefaultLayout>
</template>
