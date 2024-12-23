<script setup lang="ts">
import { defineProps } from 'vue';
import type { StockPortfolio } from '../../interfaces/stock.interface';

const props = defineProps<{
  portfolioData: StockPortfolio[]; // Updated to use the correct prop name and type
  columns?: string[];
}>();
</script>

<template>
  <div class="rounded-sm border border-stroke bg-white px-5 pt-6 pb-2.5 shadow-default">
    <h4 class="mb-6 text-xl font-semibold text-black">Your Stock Portfolio</h4>

    <div class="flex flex-col">
      <!-- Dynamic Column Header -->
      <div class="grid grid-cols-3 rounded-sm bg-gray-2 sm:grid-cols-5">
        <div 
          v-for="(column, index) in props.columns" 
          :key="index" 
          class="p-2.5 text-center xl:p-5"
        >
          <h5 class="text-sm font-medium uppercase xsm:text-base">
            {{ column }}
          </h5>
        </div>
      </div>

      <!-- Stock Rows -->
      <div
        v-for="(portfolio, key) in props.portfolioData"
        :key="key"
        :class="`grid grid-cols-3 sm:grid-cols-5 ${
          key === props.portfolioData.length - 1 ? '' : 'border-b border-stroke'
        }`"
      >
        <!-- Portfolio Name and Logo -->
        <div class="flex items-center gap-3 p-2.5 xl:p-5">
          <div class="flex-shrink-0">
            <img :src="portfolio.logo" alt="Portfolio" class="w-10 h-10" />
          </div>
          <p class="text-black">{{ portfolio.name }}</p>
        </div>

        <!-- Quantity -->
        <div class="flex items-center justify-center p-2.5 xl:p-5">
          <p class="text-black">{{ portfolio.quantity }}</p>
        </div>

        <!-- Purchase Price -->
        <div class="flex items-center justify-center p-2.5 xl:p-5">
          <p class="text-meta-3">${{ portfolio.purchase_price.toFixed(2) }}</p>
        </div>

        <!-- Purchase Date -->
        <div class="hidden items-center justify-center p-2.5 sm:flex xl:p-5">
          <p class="text-black">{{ portfolio.purchase_date.toLocaleDateString() }}</p>
        </div>

        <!-- Stock Symbol -->
        <div class="hidden items-center justify-center p-2.5 sm:flex xl:p-5">
          <p class="text-meta-5">{{ portfolio.stock_symbol }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
