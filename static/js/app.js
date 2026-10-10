// Confirm destructive actions before submitting a delete form.
document.querySelectorAll(".delete-form").forEach((form) => {
  form.addEventListener("submit", (event) => {
    const confirmed = window.confirm("Delete this patient record? This action cannot be undone.");
    if (!confirmed) event.preventDefault();
  });
});

// Check password confirmation on the registration page for quicker feedback.
const registerForm = document.querySelector('form[action=""]');
const password = document.querySelector("#password");
const confirmPassword = document.querySelector("#confirm_password");
if (registerForm && password && confirmPassword) {
  registerForm.addEventListener("submit", (event) => {
    if (password.value !== confirmPassword.value) {
      event.preventDefault();
      confirmPassword.setCustomValidity("Passwords do not match.");
      confirmPassword.reportValidity();
    }
  });
  confirmPassword.addEventListener("input", () => confirmPassword.setCustomValidity(""));
}
