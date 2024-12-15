<template>
  <DefaultLayout>
    <BreadcrumbDefault :pageTitle="pageTitle" />
    
    <!-- Display errors -->
    <AlertError v-if="errors.length" :errors="errors" />
    
    <!-- Display success message -->
    <AlertSuccess
      v-if="successMessage"
      title="Account Created Successfully"
      :message="successMessage"
    />

    <DefaultAuthCard subtitle="Start for free" title="Sign Up to AFEYA Group">
      <form @submit.prevent="createAccount">
        <InputGroup 
          id="name"
          name="name"
          label="Name" 
          type="text" 
          placeholder="Enter your full name" 
          v-model="name" 
        />
        <InputGroup
          id="email" 
          name="email"
          label="Email Address"
          type="email"
          placeholder="Enter your email"
          v-model="email"
        />
        <InputGroup 
          id="password" 
          name="password"
          label="Password" 
          type="password" 
          placeholder="Enter your password" 
          v-model="password" 
        />
        <InputGroup 
          id="confirm-password"
          name="confirm-password"  
          label="Re-type Password" 
          type="password" 
          placeholder="Re-enter your password" 
          v-model="confirmPassword" 
        />
        <div class="mb-5 mt-6">
          <input
            type="submit"
            value="Create account"
            class="w-full cursor-pointer rounded-lg border border-primary bg-primary p-4 font-medium text-white transition hover:bg-opacity-90"
          />
        </div>
      </form>
    </DefaultAuthCard>
  </DefaultLayout>
</template>

<script setup lang="ts">
import DefaultLayout from '@/layouts/DefaultLayout.vue';
import BreadcrumbDefault from '@/components/Breadcrumbs/BreadcrumbDefault.vue';
import DefaultAuthCard from '@/components/Auths/DefaultAuthCard.vue';
import InputGroup from '@/components/Auths/InputGroup.vue';
import AlertError from '@/components/Alerts/AlertError.vue';
import AlertSuccess from '@/components/Alerts/AlertSuccess.vue';

import { ref } from 'vue';

const pageTitle = ref('Sign Up');

// Form fields
const name = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');

// Messages
const errors = ref<string[]>([]);
const successMessage = ref<string | null>(null); // Success message state

// Form submission handler
const createAccount = async () => {
  errors.value = []; // Clear previous errors
  successMessage.value = null; // Clear previous success messages

  // Validate form fields
  if (!name.value || !email.value || !password.value || !confirmPassword.value) {
    errors.value.push('All fields are required!');
    return;
  }
  if (password.value !== confirmPassword.value) {
    errors.value.push('Passwords do not match!');
    return;
  }

  const userData = {
    name: name.value,
    email: email.value,
    password: password.value,
  };

  try {
    const response = await fetch('/api/users/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorDetails = await response.json();
      console.error('Error details:', errorDetails);

      // Add backend error to the errors array
      errors.value.push(errorDetails.detail || 'Failed to create account.');
      return;
    }

    const result = await response.json();
    console.log('Success:', result);

    // Display success message
    successMessage.value = 'Your account has been successfully created.';

    // Clear form fields
    name.value = '';
    email.value = '';
    password.value = '';
    confirmPassword.value = '';
  } catch (error) {
    console.error('Error during request:', error);
    errors.value.push('An unexpected error occurred. Please try again.');
  }
};
</script>
