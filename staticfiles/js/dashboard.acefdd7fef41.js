$(document).ready(function () {
  $(".input-daterange").datepicker({
    format: "dd-mm-yyyy",
    todayHighlight: true,
  });
});

const renderChart = (data, labels) => {
  var cntx = document.getElementById("myChart2").getContext("2d");
  var myChart2 = new Chart(cntx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Students",
          data: data,
          backgroundColor: [
            "rgba(255, 99, 132, 0.2)",
            "rgba(54, 162, 235, 0.2)",
            "rgba(255, 206, 86, 0.2)",
            "rgba(75, 192, 192, 0.2)",
            "rgba(153, 102, 255, 0.2)",
            "rgba(255, 159, 64, 0.2)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
            "rgba(255, 159, 64, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
      options: {
        scales: {
            y: {
                beginAtZero: true
            }
        },
        title: {
            display: true,
            text: "Expenses per category",
      },
    },
  });
};

const getChartData = () => {
  fetch("/chart_data")
    .then((res) => res.json())
    .then((results) => {
      const students_data = results.data;
      const [labels, data] = [
        Object.keys(students_data),
        Object.values(students_data),
      ];
      renderChart(data, labels);
    });
};

document.onload = getChartData();
