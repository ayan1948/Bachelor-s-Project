let select = document.getElementById("tests");
let downloaded = document.getElementById("downloaded");
let title = document.getElementById("title");
let description = document.getElementById("description");
let timing = document.getElementById("timing");
let submit = document.getElementById("submit");
let deleted = document.getElementById("deleted");
let channels = document.querySelectorAll("input[type='checkbox']");
let options, captureName;
const datasetCache = {};

submit.disabled = true;
deleted.disabled = true;
title.disabled = true;
description.disabled = true;
downloaded.classList.add("disabled");
channels.forEach((check) => (check.disabled = true));

function update_list() {
  let child = options.lastElementChild;
  while (child) {
    options.removeChild(child);
    child = options.lastElementChild;
  }
  if (select.value !== "0") {
    test[select.value].items.forEach((item) => {
      const choice = document.createElement("option");
      choice.appendChild(document.createTextNode(item.toString()));
      choice.value = item.toString();
      choice.className = "text-muted";
      options.appendChild(choice);
    });
    registerOptionsList();
  }
}

function update_checkbox() {
  if (select.value !== "0") {
    channels.forEach((check, i) => {
      check.checked = test[select.value].channels[i];
      check.disabled = !check.checked;
    });
    registerChannelsList();
  } else channels.forEach((check) => (check.disabled = true));
}

let colorNames = Object.keys(window.chartColors);

function get_label_for_channel_and_option(option, channel_index) {
  return option + " Ch: " + (channel_index + 1);
}

function update_option() {
  Object.values(options)
    .filter((option) => !option.selected)
    .forEach((option) => {
      const label = option.value;
      channels.forEach((channel, i) => {
        chartConfig.data.datasets = chartConfig.data.datasets.filter(
          (data) => data.label !== get_label_for_channel_and_option(label, i)
        );
      });
      window.chart.update();
    });
  Object.values(options)
    .filter((option) => option.selected)
    .forEach((option) => {
      const label = option.value;
      const inCache = datasetCache[captureName]
        ? datasetCache[captureName].filter((data) => data.label.includes(label))
        : [];
      if (!inCache.length) {
        fetchData(label);
      } else {
        channels.forEach((channel, i) => {
          if (
            !channel.disabled &&
            !chartConfig.data.datasets.some(
              (set) => set.label === get_label_for_channel_and_option(label, i)
            )
          ) {
            const recordInCache = inCache.find(
              (data) =>
                data.label === get_label_for_channel_and_option(label, i)
            );
            addToChartDataset(
              recordInCache.data,
              recordInCache.label,
              channel.checked
            );
          }
        });
        window.chart.update();
      }
    });
}

function update_ch(channel, i) {
  if (channel.checked) {
    chartConfig.data.datasets.forEach((data) => {
      if (data.label.includes("Ch: " + (i + 1))) data.hidden = false;
    });
  } else if (!channel.checked) {
    chartConfig.data.datasets.forEach((data) => {
      if (data.label.includes("Ch: " + (i + 1))) data.hidden = true;
    });
  }
  window.chart.update();
}

function graph() {
  document.getElementById("card").style.display = "";
  const ctx = document.getElementById("canvas").getContext("2d");
  chartConfig.data.datasets = [];
  chartConfig.data.labels = [];
  fetch("/review/" + title.value + "/" + "time")
    .then(response => {
      if (response.status === 200) {
        response.json().then((data) => {
          chartConfig.data.labels = data["time"];
        });
      } else console.log(`Wrong response status: ${response.status}`);
    })
    .catch((error) => console.log(error));
  window.chart = new Chart(ctx, chartConfig);
}

function addToChartDataset(data, labelText, checked) {
  const colorName =
    colorNames[chartConfig.data.datasets.length % colorNames.length];
  const color = window.chartColors[colorName];
  chartConfig.data.datasets.push({
    label: labelText,
    backgroundColor: color,
    borderColor: color,
    data: data,
    fill: false,
    hidden: !checked,
    pointRadius: 0,
  });
  window.chart.update();
}

function registerChannelsList() {
  channels.forEach((channel, i) => {
    channel.onchange = () => update_ch(channel, i);
  });
}

function registerOptionsList() {
  options.onchange = () => update_option();
}

function fetchAllData() {
  Object.values(options).forEach((option) => {
    const label = option.value;
    if (
      !datasetCache[captureName].some(
        (data) =>
          data.label ===
          get_label_for_channel_and_option(
            label,
            Array.from(channels).filter((ch) => !ch.disabled)[0]
          )
      )
    ) {
      fetchData(label);
    }
  });
}

function fetchData(label) {
  fetch("/review/" + title.value + "/" + label.substring(0, label.length - 4))
    .then((response) => {
      if (response.status === 200) {
        response.json().then((data) => {
          channels.forEach((channel, i) => {
            if (!channel.disabled) {
              const labelName = get_label_for_channel_and_option(label, i);
              if (!datasetCache[captureName]) {
                datasetCache[captureName] = [];
              }
              datasetCache[captureName].push({
                label: labelName,
                data: data["ch" + (i + 1)],
              });
              addToChartDataset(
                data["ch" + (i + 1)],
                get_label_for_channel_and_option(label, i),
                channel.checked
              );
            }
          });
        });
      } else console.log(`Wrong response status: ${response.status}`);
    })
    .catch((error) => console.log(error));
}

select.onchange = () => {
  title.value = test[select.value].title;
  description.value = test[select.value].description;
  timing.textContent = test[select.value].time;
  options = document.getElementById("test_select");
  captureName = select.value;
  update_list(title.value);

  update_checkbox(title.value);
  if (select.value !== "0") {
    downloaded.classList.remove("disabled");
    downloaded.href = "/get_plot/" + title.value;
    title.disabled = false;
    description.disabled = false;
    submit.disabled = false;
    deleted.disabled = false;
    graph();
  } else {
    document.getElementById("card").style.display = "none";
    downloaded.classList.add("disabled");
    downloaded.href = "#";
    title.disabled = true;
    description.disabled = true;
    submit.disabled = true;
    deleted.disabled = true;
    fetchAllData();
  }
};
