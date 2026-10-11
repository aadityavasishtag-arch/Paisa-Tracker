document.addEventListener("DOMContentLoaded", () => {
  // Confirm before removing a record.
  document.querySelectorAll(".delete-form").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm("Delete this expense? This action cannot be undone.")) {
        event.preventDefault();
      }
    });
  });

  // Fill and open the edit dialog for the selected transaction.
  const dialog = document.getElementById("edit-dialog");
  const editForm = document.getElementById("edit-form");
  document.querySelectorAll(".edit-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.getElementById("edit-date").value = button.dataset.date;
      document.getElementById("edit-category").value = button.dataset.category;
      document.getElementById("edit-description").value = button.dataset.description;
      document.getElementById("edit-amount").value = button.dataset.amount;
      editForm.action = `/edit/${button.dataset.id}`;
      dialog.showModal();
    });
  });

  document.getElementById("close-dialog").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  // Keep the amount field friendly on mobile devices.
  const amount = document.getElementById("amount");
  amount.addEventListener("input", () => {
    if (Number(amount.value) < 0) amount.setCustomValidity("Amount must be positive.");
    else amount.setCustomValidity("");
  });

  // Fade out status messages after a short delay without hiding them from assistive tech abruptly.
  document.querySelectorAll(".flash").forEach((message) => {
    window.setTimeout(() => {
      message.style.transition = "opacity .4s";
      message.style.opacity = "0";
      window.setTimeout(() => message.remove(), 450);
    }, 4500);
  });
});
