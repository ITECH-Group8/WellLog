document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("chartCanvas").getContext("2d");
    let chart;
  
    function updateChart(type) {
      const dataSets = {
        overall: [30, 45, 60, 40, 50],
        running: [5, 10, 15, 20, 25],
        training: [3, 5, 8, 12, 15],
        sleep: [7, 6.5, 8, 7.5, 6],
        diet: [2000, 1800, 2200, 1900, 2100]
      };
      
      if (chart) chart.destroy();
      chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: ["Jan", "Feb", "Mar", "Apr", "May"],
          datasets: [{
            label: type.charAt(0).toUpperCase() + type.slice(1) + " Data",
            data: dataSets[type],
            borderColor: "blue",
            fill: false,
          }],
        },
      });
    }
  
    document.querySelectorAll(".nav-link").forEach(tab => {
      tab.addEventListener("click", function (e) {
        e.preventDefault();
        document.querySelector(".nav-link.active").classList.remove("active");
        this.classList.add("active");
        updateChart(this.getAttribute("data-type"));
      });
    });
  
    document.getElementById("addData").addEventListener("click", function () {
      new bootstrap.Modal(document.getElementById("addDataModal")).show();
    });
  
    document.getElementById("setGoals").addEventListener("click", function () {
      new bootstrap.Modal(document.getElementById("setGoalsModal")).show();
    });
  
    document.getElementById("addDataForm").addEventListener("submit", function (e) {
      e.preventDefault();
      alert("Data added successfully!");
      document.getElementById("addDataModal").querySelector(".btn-close").click();
    });
  
    document.getElementById("setGoalsForm").addEventListener("submit", function (e) {
      e.preventDefault();
      alert("Goals set successfully!");
      document.getElementById("setGoalsModal").querySelector(".btn-close").click();
    });
  
    document.getElementById("filterData").addEventListener("click", function () {
      alert("Filtering data between selected dates.");
    });
  
    updateChart("overall");
  });
  