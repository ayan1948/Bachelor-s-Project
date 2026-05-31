<script>
    import { onMount } from 'svelte';
    import { token } from '../../stores';

    let tests = [];
    let selectedTestId = "0";
    let selectedTest = null;
    let titleInput = "";
    let descriptionInput = "";
    let items = [];
    
    // UI state
    let message = "";
    let messageType = "";
    let showDeleteModal = false;
    let selectedFiles = [];
    let channels = [
        { id: 'ch1', label: 'Channel 1', checked: false, disabled: true },
        { id: 'ch2', label: 'Channel 2', checked: false, disabled: true },
        { id: 'ch3', label: 'Channel 3', checked: false, disabled: true },
        { id: 'ch4', label: 'Channel 4', checked: false, disabled: true }
    ];

    // Chart.js reference and cache
    let canvas;
    let chart;
    let datasetCache = {};
    let colorNames = ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56'];

    onMount(async () => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            token.set(storedToken);
            await fetchTests(storedToken);
        } else {
            window.location.href = '/login';
        }
    });

    async function fetchTests(storedToken) {
        try {
            const response = await fetch('http://127.0.0.1:5000/tests/', {
                headers: {
                    'Authorization': `Bearer ${storedToken}`
                }
            });
            if (response.ok) {
                tests = await response.json();
            } else if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = '/login';
            }
        } catch (error) {
            console.error("Failed to fetch tests:", error);
            showFeedback("Failed to load tests from server", "danger");
        }
    }

    function handleTestSelect() {
        if (selectedTestId === "0") {
            selectedTest = null;
            titleInput = "";
            descriptionInput = "";
            items = [];
            selectedFiles = [];
            channels = channels.map(ch => ({ ...ch, checked: false, disabled: true }));
            if (chart) {
                chart.destroy();
                chart = null;
            }
            return;
        }

        selectedTest = tests.find(t => t.id === parseInt(selectedTestId));
        if (selectedTest) {
            titleInput = selectedTest.title;
            descriptionInput = selectedTest.description || "";
            items = selectedTest.items || [];
            selectedFiles = [];
            
            // Set channels state based on test definition
            channels[0].disabled = !selectedTest.ch1;
            channels[0].checked = selectedTest.ch1;
            channels[1].disabled = !selectedTest.ch2;
            channels[1].checked = selectedTest.ch2;
            channels[2].disabled = !selectedTest.ch3;
            channels[2].checked = selectedTest.ch3;
            channels[3].disabled = !selectedTest.ch4;
            channels[3].checked = selectedTest.ch4;

            datasetCache = {};
            if (chart) {
                chart.destroy();
                chart = null;
            }
        }
    }

    async function handleUpdate() {
        const storedToken = localStorage.getItem('token');
        if (!storedToken || !selectedTest) return;

        try {
            const response = await fetch(`http://127.0.0.1:5000/tests/${selectedTest.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${storedToken}`
                },
                body: JSON.stringify({
                    title: titleInput,
                    description: descriptionInput,
                    ch1: selectedTest.ch1,
                    ch2: selectedTest.ch2,
                    ch3: selectedTest.ch3,
                    ch4: selectedTest.ch4,
                    iteration: selectedTest.iteration
                })
            });

            if (response.ok) {
                showFeedback("Test updated successfully!", "success");
                await fetchTests(storedToken);
                // Keep selected test but update references
                selectedTestId = String(selectedTest.id);
                selectedTest = tests.find(t => t.id === parseInt(selectedTestId));
            } else {
                showFeedback("Failed to update test.", "danger");
            }
        } catch (error) {
            console.error("Update error:", error);
            showFeedback("An error occurred during update.", "danger");
        }
    }

    async function handleDelete() {
        const storedToken = localStorage.getItem('token');
        if (!storedToken || !selectedTest) return;

        try {
            const response = await fetch(`http://127.0.0.1:5000/tests/${selectedTest.id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${storedToken}`
                }
            });

            if (response.ok) {
                showFeedback("Test deleted successfully", "warning");
                showDeleteModal = false;
                selectedTestId = "0";
                selectedTest = null;
                await fetchTests(storedToken);
                handleTestSelect();
            } else {
                showFeedback("Failed to delete test", "danger");
            }
        } catch (error) {
            console.error("Delete error:", error);
            showFeedback("An error occurred during deletion", "danger");
        }
    }

    function showFeedback(msg, type) {
        message = msg;
        messageType = type;
        setTimeout(() => {
            message = "";
        }, 4000);
    }

    async function handleFileSelection(event) {
        // Collect all selected options
        const selectElement = event.target;
        selectedFiles = Array.from(selectElement.selectedOptions).map(opt => opt.value);
        await updateChart();
    }

    async function updateChart() {
        if (!selectedTest || selectedFiles.length === 0) {
            if (chart) {
                chart.destroy();
                chart = null;
            }
            return;
        }

        // 1. Fetch time axis if not in cache
        let timeLabels = datasetCache['time'];
        if (!timeLabels) {
            try {
                const response = await fetch(`http://127.0.0.1:5000/review/${selectedTest.title}/time`);
                if (response.ok) {
                    const data = await response.json();
                    timeLabels = data.time;
                    datasetCache['time'] = timeLabels;
                } else {
                    console.error("Failed to load time data");
                    return;
                }
            } catch (error) {
                console.error("Error fetching time:", error);
                return;
            }
        }

        // 2. Fetch selected trace files if not in cache
        for (const file of selectedFiles) {
            const caseName = file.endsWith('.csv') ? file.substring(0, file.length - 4) : file;
            if (!datasetCache[caseName]) {
                try {
                    const response = await fetch(`http://127.0.0.1:5000/review/${selectedTest.title}/${caseName}`);
                    if (response.ok) {
                        datasetCache[caseName] = await response.json();
                    } else {
                        console.error(`Failed to load data for trace: ${caseName}`);
                    }
                } catch (error) {
                    console.error(`Error fetching trace ${caseName}:`, error);
                }
            }
        }

        // 3. Construct datasets for active channels
        const chartDatasets = [];
        let datasetIndex = 0;

        for (const file of selectedFiles) {
            const caseName = file.endsWith('.csv') ? file.substring(0, file.length - 4) : file;
            const dataObj = datasetCache[caseName];
            if (!dataObj) continue;

            channels.forEach((ch, idx) => {
                // If channel is enabled on test AND checked in UI
                if (!ch.disabled && ch.checked) {
                    const color = colorNames[datasetIndex % colorNames.length];
                    datasetIndex++;
                    
                    chartDatasets.push({
                        label: `${caseName} Ch: ${idx + 1}`,
                        backgroundColor: color,
                        borderColor: color,
                        data: dataObj[ch.id] || [],
                        fill: false,
                        pointRadius: 0,
                        borderWidth: 1.5
                    });
                }
            });
        }

        // 4. Draw or update chart
        if (!chart && window.Chart) {
            const ctx = canvas.getContext('2d');
            chart = new window.Chart(ctx, {
                type: 'line',
                data: {
                    labels: timeLabels,
                    datasets: chartDatasets
                },
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: `Measurement Traces for ${selectedTest.title}`
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Time (s)'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Voltage / Current (V)'
                            }
                        }
                    }
                }
            });
        } else if (chart) {
            chart.data.labels = timeLabels;
            chart.data.datasets = chartDatasets;
            chart.update();
        }
    }

    function toggleChannel(idx) {
        channels[idx].checked = !channels[idx].checked;
        updateChart();
    }
</script>

<svelte:head>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</svelte:head>

<div class="row">
    <div class="col-md-8">
        {#if message}
            <div role="alert" class="alert alert-{messageType} alert-dismissible fade show">
                {message}
            </div>
        {/if}

        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Choose Test Case</h5>
                <div class="form-group mb-3">
                    <select class="custom-select form-control" bind:value={selectedTestId} on:change={handleTestSelect}>
                        <option value="0">Select a test</option>
                        {#each tests as test}
                            <option value={String(test.id)}>{test.title}</option>
                        {/each}
                    </select>
                </div>

                {#if selectedTest}
                    <div class="card p-3 bg-light">
                        <div class="form-group mb-3">
                            <label class="form-control-label font-weight-bold" for="test-title">Test Title</label>
                            <input class="form-control form-control-lg" id="test-title" type="text" bind:value={titleInput} />
                        </div>
                        <div class="form-group mb-3">
                            <label class="form-control-label font-weight-bold" for="test-desc">Description</label>
                            <textarea class="form-control" id="test-desc" rows="3" bind:value={descriptionInput}></textarea>
                        </div>
                        <div class="form-group mt-3 d-flex justify-content-between">
                            <button class="btn btn-outline-info" on:click={handleUpdate}>Save Changes</button>
                            <button type="button" class="btn btn-outline-danger" on:click={() => showDeleteModal = true}>Delete</button>
                        </div>
                    </div>
                {/if}
            </div>
        </div>

        {#if selectedTest}
            <div class="card text-center mb-3">
                <div class="card-body">
                    <h5 class="card-title text-left border-bottom pb-2">Traces</h5>
                    <div class="row">
                        <div class="col-sm-6 text-left">
                            <div class="card h-100">
                                <div class="card-header font-weight-bold">Files</div>
                                <div class="card-body p-2">
                                    <select multiple class="form-control select-files" style="height: 150px;" on:change={handleFileSelection}>
                                        {#each items as item}
                                            <option value={item}>{item}</option>
                                        {/each}
                                    </select>
                                    <small class="form-text text-muted mt-1">Hold Ctrl/Cmd to select multiple files.</small>
                                </div>
                            </div>
                        </div>

                        <div class="col-sm-6 text-left">
                            <div class="card h-100">
                                <div class="card-header font-weight-bold">Channels</div>
                                <div class="card-body d-flex flex-column justify-content-around">
                                    {#each channels as ch, idx}
                                        <div class="form-check p-1">
                                            <input type="checkbox" 
                                                   class="form-check-input" 
                                                   id={ch.id} 
                                                   checked={ch.checked} 
                                                   disabled={ch.disabled}
                                                   on:change={() => toggleChannel(idx)} />
                                            <label class="form-check-label {ch.disabled ? 'text-muted' : ''}" for={ch.id}>
                                                {ch.label} {#if ch.disabled}<small>(inactive)</small>{/if}
                                            </label>
                                        </div>
                                    {/each}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {/if}
    </div>

    <div class="col-md-4">
        {#if selectedTest}
            <div class="content-section card p-3 mb-3 bg-light">
                <h3>Info</h3>
                <p class='text-muted'>
                    Captured on:<br>
                    <strong>{new Date(selectedTest.moment).toLocaleString()}</strong>
                </p>
                <p class='text-muted'>
                    Iterations: <strong>{selectedTest.iteration}</strong>
                </p>
                <a class="btn btn-outline-dark btn-sm btn-block mt-3" 
                   href="http://127.0.0.1:5000/get_plot/{selectedTest.title}">
                    Download Zip
                </a>
            </div>
        {/if}
    </div>
</div>

{#if selectedTest}
    <div class="card mb-3 mt-4" style="display: {selectedFiles.length > 0 ? 'block' : 'none'};">
        <div class="card-body">
            <canvas bind:this={canvas}></canvas>
        </div>
    </div>
{/if}

<!-- Svelte Native Modal -->
{#if showDeleteModal}
    <div class="modal fade show d-block" style="background: rgba(0,0,0,0.5);" tabindex="-1" role="dialog">
        <div class="modal-dialog modal-dialog-centered" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Delete Test</h5>
                    <button type="button" class="close" aria-label="Close" on:click={() => showDeleteModal = false}>
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to delete the test <strong>{selectedTest?.title}</strong>? This will permanently delete all records and stored results files.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" on:click={() => showDeleteModal = false}>Cancel</button>
                    <button type="button" class="btn btn-danger" on:click={handleDelete}>Delete Permanently</button>
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    .select-files option {
        padding: 6px 12px;
    }
</style>