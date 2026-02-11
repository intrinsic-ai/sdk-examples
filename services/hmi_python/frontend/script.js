const loadOperationIdBtn = document.getElementById("load-operation-id");
const operationIdEl = document.getElementById("operation-id");

loadOperationIdBtn.addEventListener("click", async () => {
  operationIdEl.textContent = await fetchLatestOperationId();
});

async function fetchLatestOperationId() {
  try {
    const res = await fetch("api/executive/operations");
    const s = await res.json();
    if (Array.isArray(s.operations) && s.operations.length > 0) {
      return s.operations[0].name;
    } else {
      return "No operation ID found";
    }
  } catch (e) {
    console.error("Failed to get operations:", e);
    return "(error, see console for details)";
  }
}
