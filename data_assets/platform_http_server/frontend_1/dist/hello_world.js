const loadOperationIdBtn = document.getElementById("load-operation-id");
const operationIdEl = document.getElementById("operation-id");

loadOperationIdBtn.addEventListener("click", async () => {
  operationIdEl.textContent = await fetchLatestOperationId();
});

/**
 * A dummy function that simulates fetching data.
 * It returns a hardcoded operation ID after a short delay to mimic a network request.
 */
async function fetchLatestOperationId() {
  operationIdEl.textContent = "Loading..."; // Provide immediate user feedback

  // Simulate a network delay of 500 milliseconds.
  await new Promise((resolve) => setTimeout(resolve, 500));

  try {
    // This is our hardcoded dummy data. In a real scenario, this would
    // come from a fetch() call to a server.
    const dummyData = {
      operations: [
        { name: "dummy-op-id-1a2b3c-4d5e6f" },
        { name: "another-dummy-op" },
      ],
    };

    // Simulate a successful response.
    if (
      Array.isArray(dummyData.operations) &&
      dummyData.operations.length > 0
    ) {
      return dummyData.operations[0].name;
    } else {
      return "No operation ID found";
    }
  } catch (e) {
    console.error("Dummy fetch failed (this shouldn't happen):", e);
    return "(error, see console for details)";
  }
}
