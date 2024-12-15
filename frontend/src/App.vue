<script setup lang="ts">
import { RouterView } from 'vue-router';
import AlertError from '@/components/Alerts/AlertError.vue';
import { showError, errorMessage, closeAlert } from '@/utils/alertHandler';
</script>

<template>
  <div id="app">
    <!-- Custom AlertError component -->
    <AlertError v-if="showError" :message="errorMessage" @close="closeAlert" />
    <RouterView />
  </div>
</template>
