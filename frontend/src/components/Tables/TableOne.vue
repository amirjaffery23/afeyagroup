<script setup lang="ts">
import { ref, defineProps, computed, watch, onMounted } from "vue";
import axios from "axios";
import type { StockPortfolio } from "../../interfaces/stock.interface";

const props = defineProps<{
  portfolioData: StockPortfolio[];
  columns?: string[];
}>();

const columnOrder = ref(
  props.columns ?? [
    "Stock Name",
    "Quantity",
    "Purchase Price",
    "Purchase Date",
    "Stock Symbol",
  ]
);
const showForm = ref(false);
const showMenu = ref(false);
const selectedStock = ref<StockPortfolio | null>(null);
const menuPosition = ref({ x: 0, y: 0 });
const isUpdating = ref(false);
const stockForm = ref({
  stock_name: "",
  quantity: 0,
  purchase_price: 0.0,
  purchase_date: "",
  stock_symbol: "",
});
const stockData = ref(null);
const errorMessage = ref("");
const portfolioData = ref<StockPortfolio[]>(props.portfolioData);

// Ensure correct date format
const formattedPortfolioData = computed(() =>
  portfolioData.value.map((stock) => ({
    ...stock,
    name: stock.name, // ✅ Ensure name is mapped correctly even after deletion
    purchase_date: new Date(stock.purchase_date).toLocaleDateString(), // Fix date conversion
  }))
);

// Watch for changes in props and update portfolioData
watch(
  () => props.portfolioData,
  (newData) => {
    portfolioData.value = newData;
  },
  { deep: true }
);

const fetchPortfolioData = async () => {
  try {
    const response = await axios.get("/api/stocks/");
    portfolioData.value = response.data;
  } catch (error) {
    console.error("Error fetching portfolio data:", error);
  }
};

// Handle right-click event to show context menu
const handleRightClick = (event: MouseEvent, stock: StockPortfolio) => {
  event.preventDefault();
  selectedStock.value = stock;
  menuPosition.value = { x: event.clientX, y: event.clientY };
  showMenu.value = true;
};

// Handle adding a new stock
const addStock = () => {
  stockForm.value = {
    stock_name: "",
    quantity: 0,
    purchase_price: 0.0,
    purchase_date: "",
    stock_symbol: "",
  };
  isUpdating.value = false;
  showForm.value = true;
};

// Handle Update selection
const updateStock = () => {
  if (selectedStock.value) {
    stockForm.value = {
      stock_name: selectedStock.value.name,
      quantity: selectedStock.value.quantity,
      purchase_price: parseFloat(selectedStock.value.purchase_price.toString()), // ✅ Convert to float
      purchase_date: new Date(selectedStock.value.purchase_date)
        .toISOString()
        .split("T")[0],
      stock_symbol: selectedStock.value.stock_symbol,
    };
    isUpdating.value = true;
    showForm.value = true;
  }
  showMenu.value = false;
};

// Handle Delete selection
const deleteStock = async () => {
  if (!selectedStock.value) return;
  try {
    await axios.delete(`/api/stocks/${selectedStock.value.stock_symbol}`);
    alert("Stock deleted successfully!");
    await fetchPortfolioData(); // ✅ Refresh table after deletion
  } catch (error) {
    console.error("Error deleting stock:", error);
    errorMessage.value = "Error deleting stock.";
  }
  showMenu.value = false;
};

// Submit stock data to PostgreSQL
const submitStock = async () => {
  try {
    const url = isUpdating.value
      ? `/api/stocks/${stockForm.value.stock_symbol}`
      : "/api/stocks/";
    const method = isUpdating.value ? "put" : "post";
    // ✅ Log request data to confirm correct field names
    console.log("Submitting stock:", JSON.stringify(stockForm.value, null, 2));
    await axios({ method, url, data: stockForm.value });
    alert(
      isUpdating.value ? "Stock updated successfully!" : "Stock created successfully!"
    );

    stockForm.value = {
      // ✅ Reset form for new entries
      stock_name: "",
      quantity: 0,
      purchase_price: 0.0,
      purchase_date: "",
      stock_symbol: "",
    };

    await fetchPortfolioData(); // ✅ Refresh table with new data
  } catch (error) {
    console.error("Error submitting stock:", error);
    errorMessage.value = "Error submitting stock data.";
  }
};

// Handle Cancel selection
const cancelAction = () => {
  showMenu.value = false;
};

const dragStart = (event: DragEvent, index: number) => {
  event.dataTransfer?.setData("text/plain", index.toString());
};

const drop = (event: DragEvent, index: number) => {
  const draggedIndex = Number(event.dataTransfer?.getData("text/plain"));
  const movedItem = columnOrder.value.splice(draggedIndex, 1)[0];
  columnOrder.value.splice(index, 0, movedItem);
};
</script>

<template>
  <div class="rounded-sm border border-stroke bg-white px-5 pt-6 pb-2.5 shadow-default">
    <div class="flex justify-between items-center mb-4">
      <h4 class="text-xl font-semibold text-black">Your Stock Portfolio</h4>
      <button @click="addStock" class="bg-blue-500 text-white px-4 py-2 rounded">
        Add Stock
      </button>
    </div>

    <div class="flex flex-col">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="(column, index) in columnOrder"
              :key="index"
              draggable="true"
              @dragstart="dragStart($event, index)"
              @dragover.prevent
              @drop="drop($event, index)"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              {{ column }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="stock in formattedPortfolioData"
            :key="stock.stock_symbol"
            @contextmenu="handleRightClick($event, stock)"
          >
            <td class="px-6 py-4 whitespace-nowrap">{{ stock.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ stock.quantity }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ stock.purchase_price }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ stock.purchase_date }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ stock.stock_symbol }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Context Menu -->
    <div
      v-if="showMenu"
      :style="{ top: menuPosition.y + 'px', left: menuPosition.x + 'px' }"
      class="absolute bg-white border border-gray-300 shadow-lg rounded"
    >
      <ul>
        <li @click="addStock" class="px-4 py-2 hover:bg-gray-200 cursor-pointer">
          Add Stock
        </li>
        <li @click="updateStock" class="px-4 py-2 hover:bg-gray-200 cursor-pointer">
          Update
        </li>
        <li @click="deleteStock" class="px-4 py-2 hover:bg-gray-200 cursor-pointer">
          Delete
        </li>
        <li @click="cancelAction" class="px-4 py-2 hover:bg-gray-200 cursor-pointer">
          Cancel
        </li>
      </ul>
    </div>

    <!-- Edit Form Modal -->
    <div
      v-if="showForm"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
    >
      <div class="bg-white p-6 rounded shadow-lg">
        <h3 class="text-lg font-semibold mb-4">
          {{ isUpdating ? "Edit Stock" : "Add Stock" }}
        </h3>
        <form @submit.prevent="submitStock">
          <div class="mb-4">
            <label class="block text-gray-700">Stock Name</label>
            <input
              v-model="stockForm.stock_name"
              class="w-full border border-gray-300 p-2 rounded"
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700">Quantity</label>
            <input
              v-model="stockForm.quantity"
              type="number"
              class="w-full border border-gray-300 p-2 rounded"
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700">Purchase Price</label>
            <input
              v-model="stockForm.purchase_price"
              type="number"
              class="w-full border border-gray-300 p-2 rounded"
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700">Purchase Date</label>
            <input
              v-model="stockForm.purchase_date"
              type="date"
              class="w-full border border-gray-300 p-2 rounded"
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700">Stock Symbol</label>
            <input
              v-model="stockForm.stock_symbol"
              class="w-full border border-gray-300 p-2 rounded"
            />
          </div>
          <div class="flex justify-end">
            <button
              type="button"
              @click="showForm = false"
              class="bg-gray-500 text-white px-4 py-2 rounded mr-2"
            >
              Cancel
            </button>
            <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">
              {{ isUpdating ? "Update" : "Create" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
