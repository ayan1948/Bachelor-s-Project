<script>
    import { onMount } from 'svelte';
    import { token } from '../stores';

    let tests = [];
    let authenticated = false;

    onMount(async () => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            token.set(storedToken);
            authenticated = true;
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
                    authenticated = false;
                }
            } catch (error) {
                console.error("Failed to fetch tests:", error);
            }
        }
    });
</script>

<main role="main" class="inner cover">
    <h1 class="cover-heading">Welcome</h1>
    {#if authenticated && tests.length > 0}
        <p class="lead">
            Total tests Conducted: <span>{tests.length}</span>
            Last Test was Conducted on <span>{new Date(tests[tests.length - 1].moment).toLocaleString()}</span>
        </p>
    {:else if authenticated}
        <p class="lead">No tests conducted yet.</p>
    {:else}
        <p class="lead">Please Sign In or Sign Up to access the Functionality</p>
    {/if}
</main>