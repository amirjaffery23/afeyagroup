declare module '@/utils/alertHandler' {
    import { Ref } from 'vue';
  
    // Reactive states for alert
    export const showError: Ref<boolean>;
    export const errorMessage: Ref<string>;
  
    // Function to show the alert
    export function showAlert(message: string): void;
  
    // Function to close the alert
    export function closeAlert(): void;
  }
  
  