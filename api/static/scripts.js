let currentPage = 0;
const limit = 10;

document.addEventListener("DOMContentLoaded", function() {
    loadData();

    document.getElementById("search").addEventListener("input", function() {
        currentPage = 0;
        loadData();
    });

    document.getElementById("prev-page").addEventListener("click", function(e) {
        e.preventDefault();
        if (currentPage > 0) {
            currentPage--;
            loadData();
        }
    });

    document.getElementById("next-page").addEventListener("click", function(e) {
        e.preventDefault();
        currentPage++;
        loadData();
    });
});

function loadData() {
    const searchQuery = document.getElementById("search").value;
    const url = `/metadata/?skip=${currentPage * limit}&limit=${limit}&search=${searchQuery}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("data-container");
            container.innerHTML = "";

            const table = document.createElement("table");
            table.className = "table table-striped";

            const header = document.createElement("tr");
            const headers = ["ID", "Dataset Name", "Schema", "Data Types", "Description", "Usage", "Lineage"];
            headers.forEach(text => {
                const th = document.createElement("th");
                th.textContent = text;
                header.appendChild(th);
            });
            table.appendChild(header);

            data.forEach(item => {
                const row = document.createElement("tr");
                row.addEventListener("click", () => {
                    window.location.href = `/data/${item.id}`;
                });
                Object.values(item).forEach(text => {
                    const td = document.createElement("td");
                    td.textContent = text;
                    row.appendChild(td);
                });
                table.appendChild(row);
            });

            container.appendChild(table);
        })
        .catch(error => {
            console.error("Error fetching data:", error);
            const container = document.getElementById("data-container");
            container.textContent = "Error loading data.";
        });
}
