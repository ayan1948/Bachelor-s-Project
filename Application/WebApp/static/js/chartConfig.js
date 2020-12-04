const chartConfig = {
  type: "line",
  data: {
    labels: [],
    datasets: [],
  },
  options: {
    responsive: true,
    title: {
      display: true,
      text: "Plot",
    },
    tooltips: {
      enabled: false,
    },
    scales: {
      xAxes: [
        {
          display: true,
          scaleLabel: {
            display: true,
            labelString: "Time",
          },
        },
      ],
      yAxes: [
        {
          display: true,
          scaleLabel: {
            display: true,
            labelString: "Electricity",
          },
        },
      ],
    },
  },
};
