<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

// Define props for the component
defineProps({
  label: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    required: true,
  },
  placeholder: {
    type: String,
    default: '',
  },
  id: {
    type: String,
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
  modelValue: {
    type: [String, Number],
    required: true,
  },
});

// Define emits for the component
const emit = defineEmits(['update:modelValue']);

// Handle input event
function handleInput(event: Event) {
  const target = event.target as HTMLInputElement | null;
  if (target) {
    emit('update:modelValue', target.value);
  }
}
</script>

<template>
  <div class="mb-4">
    <!-- Input Label -->
    <label :for="id" class="mb-2.5 block font-medium text-black dark:text-white">
      {{ label }}
    </label>
    <div class="relative">
      <!-- Input Field -->
      <input
        :id="id"
        :name="name"
        :type="type"
        :placeholder="placeholder"
        :value="modelValue"
        @input="handleInput"
        class="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary text-black dark:text-white"
      />
      <!-- Slot for Custom Elements -->
      <span class="absolute right-4 top-4">
        <slot></slot>
      </span>
    </div>
  </div>
</template>
