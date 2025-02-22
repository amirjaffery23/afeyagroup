<script setup lang="ts">
import DataStatsOne from "@/components/DataStats/DataStatsOne.vue";
import ChartOne from "@/components/Charts/ChartOne.vue";
import ChartThree from "@/components/Charts/ChartThree.vue";
import ChartTwo from "@/components/Charts/ChartTwo.vue";
import ChatCard from "@/components/ChatCard.vue";
import MapOne from "@/components/Maps/MapOne.vue";
import TableOne from "@/components/Tables/TableOne.vue";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
import { ref, onMounted } from "vue";
import axios from "axios";

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
    <div
      class="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6 xl:grid-cols-4 2xl:gap-7.5"
    >
      <DataStatsOne />
    </div>

    <div class="mt-4 grid grid-cols-12 gap-4 md:mt-6 md:gap-6 2xl:mt-7.5 2xl:gap-7.5">
      <!-- ====== Chart One Start -->
      <ChartOne />
      <!-- ====== Chart One End -->

      <!-- ====== Chart Two Start -->
      <ChartTwo />
      <!-- ====== Chart Two End -->

      <!-- ====== Chart Three Start -->
      <ChartThree />
      <!-- ====== Chart Three End -->

      <!-- ====== Map One Start -->
      <MapOne />
      <!-- ====== Map One End -->

      <!-- ====== Table One Start -->
      <div class="col-span-12 xl:col-span-8">
        <TableOne :portfolioData="portfolioData" :columns="columns" />
      </div>
      <!-- ====== Table One End -->

      <!-- ====== Chat Card Start -->
      <ChatCard />
      <!-- ====== Chat Card End -->
    </div>
  </DefaultLayout>
</template>
