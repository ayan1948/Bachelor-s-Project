<script>
    import '../app.css';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';

    let isAuthenticated = false; // We'll manage this with stores/context later

    // Check authentication status (dummy logic for now)
    onMount(() => {
        isAuthenticated = localStorage.getItem('token') !== null;
    });

    function logout() {
        localStorage.removeItem('token');
        isAuthenticated = false;
        window.location.href = '/login';
    }
</script>

<svelte:head>
    <title>DASHBOARD - {$page.data.title || 'home'}</title>
    <!-- We'll need a way to load these statically or bundle them. Let's assume they're in static/ for now or replaced by app.css -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="/main.css">

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</svelte:head>

<header class="site-header">
    <nav class="navbar navbar-expand-md navbar-dark bg-steel fixed-top">
        <div class="container">
            <a class="navbar-brand mr-4" href="/">DASHBOARD</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarToggle" aria-controls="navbarToggle" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarToggle">
                <div class="navbar-nav mr-auto">
                    {#if isAuthenticated}
                        <a class="nav-item nav-link" href="/start">Start</a>
                        <a class="nav-item nav-link" href="/review">Review</a>
                    {/if}
                </div>
                <!-- Navbar Right Side -->
                <div class="nav navbar-nav navbar-right">
                    {#if isAuthenticated}
                        <a class="nav-item nav-link" href="/account">Account</a>
                        <a class="nav-item nav-link" href="#" on:click|preventDefault={logout}>Logout</a>
                    {:else}
                        <a class="nav-item nav-link" href="/login">Login</a>
                        <a class="nav-item nav-link" href="/register">Register</a>
                    {/if}
                </div>
            </div>
        </div>
    </nav>
</header>

<main role="main" class="container">
    <div class="row">
        <div class="col-md-8">
            <slot />
        </div>
        <div class="col-md-4">
            <!-- Sidebar content goes here if needed per page -->
            <slot name="sidebar" />
        </div>
    </div>
    <!-- Graph content goes here if needed per page -->
    <slot name="graph" />
</main>