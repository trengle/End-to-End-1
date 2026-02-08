const EC2_IP = "54.183.97.74"
const API_BASE = `http://${EC2_IP}:5000`; // AWS backend - tested 
const latestEl = document.getElementById("latest");
const form = document.getElementById("greeting-form");
const input = document.getElementById("greeting-input");
const deleteBtn = document.getElementById("delete-btn");

// Load the latest greeting when the page opens
function loadLatest() {
  fetch(`${API_BASE}/api/greetings/latest`)
    .then(res => res.json())
    .then(data => {
      latestEl.textContent = data.latest || "No greetings yet!";
    })
    .catch(() => {
      latestEl.textContent = "Error loading greeting";
    });
}

// Handle form submission (POST)
form.addEventListener("submit", (e) => {
  e.preventDefault();

  const message = input.value.trim();
  if (!message) return;

  fetch(`${API_BASE}/api/greetings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  })
    .then(() => {
      input.value = "";
      loadLatest();
    });
});

// Handle delete button (DELETE)
deleteBtn.addEventListener("click", () => {
  fetch(`${API_BASE}/api/greetings`, { method: "DELETE" })
    .then(() => loadLatest());
});

// Initial load
loadLatest();
