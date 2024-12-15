import { ref } from 'vue';
// Reactive states for alert
const showError = ref(false);
const errorMessage = ref('');
// Function to show the alert
const showAlert = (message) => {
    errorMessage.value = message;
    showError.value = true;
};
// Function to close the alert
const closeAlert = () => {
    showError.value = false;
    errorMessage.value = '';
};
export { showError, errorMessage, showAlert, closeAlert };
