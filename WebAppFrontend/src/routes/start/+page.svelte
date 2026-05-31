<script>
    import { onMount } from 'svelte';
    import { token } from '../../stores';
    import io from 'socket.io-client';

    let title = '';
    let description = '';
    let iteration = '';
    let ch1 = false;
    let ch2 = false;
    let ch3 = false;
    let ch4 = false;

    let socket;
    let isConnected = false; // Simulated device connection
    let alertDisplay = 'none';
    let alertType = '';
    let alertContent = '';
    let progressDisplay = 'none';
    let progressWidth = '0%';
    let timingText = '';

    let startDisabled = false;
    let pauseDisabled = true;

    onMount(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            token.set(storedToken);

            // Connect to Socket.IO backend
            socket = io('http://127.0.0.1:5000', {
                path: '/socket.io',
                transports: ['websocket'],
            });

            socket.on('connect', () => {
                console.log('Connected to socket');
                socket.emit('connection', { data: 'I am connected!' });
            });

            socket.on('result', (data) => {
                const total = parseInt(iteration) || 1;
                const count = (data / total) * 100;
                progressWidth = count + '%';
                timingText = `${data}/${total}`;
            });

            socket.on('status', (result) => {
                if (result.status === 'danger') {
                    alertDisplay = 'block';
                    alertType = 'alert-danger';
                    alertContent = 'There is something wrong with the device!';
                    startDisabled = false;
                    pauseDisabled = true;
                    progressDisplay = 'none';
                } else {
                    alertDisplay = 'block';
                    alertType = 'alert-warning';
                    alertContent = 'Stopped!';
                    startDisabled = false;
                    pauseDisabled = true;
                    progressDisplay = 'none';
                }
            });

            socket.on('redirect', (link) => {
                window.location.href = link.destination;
            });
        }
    });

    function connectDevice() {
        if (socket) {
            const form = { connect: true, start: false, stop: false };
            socket.emit('form', JSON.stringify(form));
            // Assuming the backend handles connection and sets device state,
            // for simplicity in frontend we might assume it connected.
            isConnected = true;
        }
    }

    function startTest() {
        alertDisplay = 'none';
        startDisabled = true;
        pauseDisabled = false;
        progressDisplay = 'block';

        if (socket) {
            const form = {
                token: localStorage.getItem('token'),
                title,
                description,
                iterations: parseInt(iteration),
                ch1, ch2, ch3, ch4,
                start: true,
                stop: false
            };
            socket.emit('form', JSON.stringify(form));
        }
    }

    function stopTest() {
        alertDisplay = 'none';
        startDisabled = false;
        pauseDisabled = true;
        progressDisplay = 'none';

        if (socket) {
            const form = { start: false, stop: true };
            socket.emit('form', JSON.stringify(form));
        }
    }
</script>

<div class="row">
    <div class="col-md-8">
        <div id="alert" role="alert" style="display: {alertDisplay};" class={`alert alert-dismissible fade show ${alertType}`}>
            {alertContent}
        </div>

        <div class="content-section">
            <fieldset class="form-group">
                <legend class="border-bottom mb-4">Start your Test</legend>
                {#if !isConnected}
                    <button class="btn btn-primary mb-3" on:click={connectDevice}>Connect Device</button>
                {/if}

                <div class="form-group">
                    <label class="form-control-label" for="title">Title</label>
                    <input class="form-control form-control-lg" id="title" bind:value={title} required type="text">
                </div>
                <div class="form-group">
                    <label class="form-control-label" for="description">Description</label>
                    <textarea class="form-control form-control-lg" id="description" bind:value={description}></textarea>
                </div>
                <div class="form-group">
                    <label class="form-control-label" for="iteration">Iterations</label>
                    <input class="form-control form-control-lg" id="iteration" bind:value={iteration} required type="number">
                </div>
                <div class="form-check">
                    <input class="form-check-input" id="ch1" type="checkbox" bind:checked={ch1}>
                    <label class="form-check-label" for="ch1">Channel 1</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" id="ch2" type="checkbox" bind:checked={ch2}>
                    <label class="form-check-label" for="ch2">Channel 2</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" id="ch3" type="checkbox" bind:checked={ch3}>
                    <label class="form-check-label" for="ch3">Channel 3</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" id="ch4" type="checkbox" bind:checked={ch4}>
                    <label class="form-check-label" for="ch4">Channel 4</label>
                </div>
            </fieldset>

            <div class="form-group">
                <button class="btn btn-success" on:click|preventDefault={startTest} disabled={startDisabled || !isConnected}>Start</button>
                <button class="btn btn-danger" on:click|preventDefault={stopTest} disabled={pauseDisabled || !isConnected}>Stop</button>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <div class="content-section" style="display: {progressDisplay};">
            <div class="progress">
                <div class="progress-bar progress-bar-striped bg-steel progress-bar-animated" role="progressbar" style="width: {progressWidth};"></div>
            </div>
            <p class='text-muted'>Captures: <span>{timingText}</span></p>
        </div>
    </div>
</div>