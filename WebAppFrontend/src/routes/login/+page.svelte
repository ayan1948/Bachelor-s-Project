<script>
    import { token } from '../../stores.js';
    import { goto } from '$app/navigation';

    let username = '';
    let password = '';
    let error = '';

    async function login() {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch('http://127.0.0.1:5000/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                token.set(data.access_token);
                localStorage.setItem('token', data.access_token);
                goto('/');
            } else {
                const errorData = await response.json();
                error = errorData.detail || 'Login failed';
            }
        } catch (e) {
            error = 'An error occurred. Please try again.';
        }
    }
</script>

<div class="content-section">
    <form on:submit|preventDefault={login}>
        <fieldset class="form-group">
            <legend class="border-bottom mb-4">Log In</legend>
            {#if error}
                <div class="alert alert-danger">{error}</div>
            {/if}
            <div class="form-group">
                <label class="form-control-label" for="username">Username</label>
                <input type="text" id="username" class="form-control form-control-lg" bind:value={username} required>
            </div>
            <div class="form-group">
                <label class="form-control-label" for="password">Password</label>
                <input type="password" id="password" class="form-control form-control-lg" bind:value={password} required>
            </div>
        </fieldset>
        <div class="form-group">
            <button type="submit" class="btn btn-outline-info">Log In</button>
            <small class="text-muted ml-2">
                <a href="/reset_password">Forgot Password?</a>
            </small>
        </div>
    </form>
</div>
<div class="border-top pt-3">
    <small class="text-muted">
        Need An Account? <a class="ml-2" href="/register">Sign Up Now</a>
    </small>
</div>