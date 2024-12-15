<template>
  <DefaultLayout>
    <BreadcrumbDefault :pageTitle="pageTitle" />

    <!-- Example AlertError usage -->
    <AlertError :errors="errorMessages" />

    <div class="content">
      <h1>Alerts Example</h1>
      <!-- Add other content or alerts examples here -->
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import DefaultLayout from '@/layouts/DefaultLayout.vue';
import BreadcrumbDefault from '@/components/Breadcrumbs/BreadcrumbDefault.vue';
import AlertError from '@/components/Alerts/AlertError.vue';

import { ref } from 'vue';

// Example page title
const pageTitle = ref('Alerts Example');

// Example errors
const errorMessages = ref<string[]>([
  'An error occurred while fetching data.',
  'Failed to save changes.',
]);

</script>
